"""Entry point: crawl Peraturan Menteri Ketenagakerjaan from peraturan.bpk.go.id
(sumber primer), cross-check status against jdih.kemnaker.go.id (sumber
pembanding), and write data/regulations/*.json + data/edges.json.

Robots.txt kedua situs sudah diperiksa manual (lihat docs/source-recon.md):
path yang dipakai di sini (/Search, /Details, /peraturan) tidak dibatasi.

Usage:
    python run_scrape.py [--no-kemnaker] [--limit N]
"""

import argparse
import datetime
import sys

from lawtrail import bpk, kemnaker, storage
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

    processed = 0
    changed = 0
    skipped_not_berlaku = 0
    kemnaker_matched = 0

    for bpk_id, slug in bpk.list_search_pages(session):
        if args.limit and processed >= args.limit:
            break

        print(f"[{processed + 1}] {slug} ...", file=sys.stderr)
        data, raw_html = bpk.fetch_detail(session, bpk_id, slug)
        processed += 1

        if data.get("status") != "Berlaku":
            skipped_not_berlaku += 1
            continue

        if not args.no_kemnaker and data.get("nomor") and data.get("tahun"):
            pembanding = kemnaker.cross_check(session, data["nomor"], data["tahun"], data["status"])
            data["pembanding"] = pembanding
            if pembanding is not None:
                kemnaker_matched += 1
        else:
            data["pembanding"] = None

        data["id"] = slug
        if storage.save_regulation(slug, data):
            changed += 1
        storage.save_raw_html(slug, raw_html)
        storage.update_last_checked(slug, today)

    storage.rebuild_edges()

    print(
        f"Selesai. Diproses: {processed}, berubah: {changed}, "
        f"dilewati (bukan Berlaku): {skipped_not_berlaku}, cocok di Kemnaker: {kemnaker_matched}.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
