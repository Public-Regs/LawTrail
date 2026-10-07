"""Entry point: crawl Peraturan Menteri Ketenagakerjaan from peraturan.bpk.go.id
(sumber primer), cross-check status against jdih.kemnaker.go.id (sumber
pembanding), tulis data/regulations/*.json + data/edges.json, dan catat
perubahan ke data/changes/{tanggal}.json.

Robots.txt kedua situs sudah diperiksa manual (lihat docs/source-recon.md):
path yang dipakai di sini (/Search, /Details, /peraturan) tidak dibatasi.

Peraturan yang baru pertama kali dilihat HANYA diambil kalau statusnya
"Berlaku". Tapi begitu sebuah peraturan pernah tersimpan, ia terus dilacak di
scrape-scrape berikutnya apa pun statusnya sekarang -- supaya transisi status
(misal Berlaku -> Dicabut) tercatat sebagai perubahan, bukan menghilang diam-
diam. Lihat docs/decisions.md.

Usage:
    python run_scrape.py [--no-kemnaker] [--limit N]
"""

import argparse
import datetime
import sys

from lawtrail import bpk, changes, kemnaker, storage
from lawtrail.http_client import PoliteSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-kemnaker", action="store_true",
                         help="Lewati cross-check ke jdih.kemnaker.go.id (lebih cepat untuk uji coba lokal).")
    parser.add_argument("--limit", type=int, default=None,
                         help="Batasi jumlah peraturan yang diproses (untuk uji coba).")
    args = parser.parse_args()

    session = PoliteSession()
    today = datetime.date.today().isoformat()

    previous_ids = storage.existing_regulation_ids()
    seen_ids = set()
    change_entries = []

    processed = 0
    changed = 0
    skipped_new_not_berlaku = 0
    kemnaker_matched = 0

    for bpk_id, slug in bpk.list_search_pages(session):
        if args.limit and processed >= args.limit:
            break

        print(f"[{processed + 1}] {slug} ...", file=sys.stderr)
        data, raw_html = bpk.fetch_detail(session, bpk_id, slug)
        processed += 1
        seen_ids.add(slug)

        already_tracked = slug in previous_ids
        if data.get("status") != "Berlaku" and not already_tracked:
            skipped_new_not_berlaku += 1
            continue

        data["primer"]["pdf_sha256"] = bpk.compute_pdf_sha256(session, data["primer"]["pdf_url"])

        if not args.no_kemnaker and data.get("nomor") and data.get("tahun"):
            pembanding = kemnaker.cross_check(session, data["nomor"], data["tahun"], data["status"])
            data["pembanding"] = pembanding
            if pembanding is not None:
                kemnaker_matched += 1
        else:
            data["pembanding"] = None

        data["id"] = slug

        old_data = storage.load_regulation(slug)
        change_entries.extend(changes.diff_regulation(slug, old_data, data))

        if storage.save_regulation(slug, data):
            changed += 1
        storage.save_raw_html(slug, raw_html)
        storage.update_last_checked(slug, today)

    # Deteksi "hilang" hanya valid kalau seluruh daftar sumber benar-benar
    # dijelajahi -- dengan --limit, banyak peraturan lama sengaja tidak
    # dikunjungi dan akan keliru tercatat "hilang" kalau ini tidak dilewati.
    if args.limit is None:
        change_entries.extend(changes.missing_entries(previous_ids, seen_ids))

    storage.rebuild_edges()
    wrote_changes = storage.save_changes_log(today, change_entries)

    print(
        f"Selesai. Diproses: {processed}, berubah: {changed}, "
        f"dilewati (baru & bukan Berlaku): {skipped_new_not_berlaku}, cocok di Kemnaker: {kemnaker_matched}, "
        f"entri perubahan: {len(change_entries)}"
        + (f" (ditulis ke data/changes/{today}.json)" if wrote_changes else " (tidak ada yang ditulis)") + ".",
        file=sys.stderr,
    )

    # Kalau crawler daftar peraturan.bpk.go.id tidak menemukan apa pun sama
    # sekali (dan ini bukan uji coba --limit), kemungkinan besar struktur
    # situs sumber berubah dan parser perlu diperbaiki -- gagal dengan jelas
    # di sini supaya GitHub Actions menandai run ini sebagai gagal dan
    # mengirim notifikasi, bukan diam-diam menulis 0 hasil setiap hari.
    if processed == 0 and args.limit is None:
        print(
            "GAGAL: tidak ada satu pun peraturan yang ditemukan di peraturan.bpk.go.id. "
            "Kemungkinan struktur situs sumber berubah -- periksa lawtrail/bpk.py.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
