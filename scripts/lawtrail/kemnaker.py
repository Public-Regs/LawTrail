"""Best-effort cross-check against jdih.kemnaker.go.id (sumber pembanding).

Tidak dipakai sebagai sumber relasi utama -- hanya untuk membandingkan status
("Berlaku"/dicabut/dst.) peraturan yang sudah diambil dari peraturan.bpk.go.id.
Kalau peraturan yang cocok tidak ditemukan, fungsi di sini mengembalikan None;
ini bukan kegagalan, karena bukan setiap peraturan primer wajib ada di sini.
"""

import re
import time

from bs4 import BeautifulSoup

BASE_URL = "https://jdih.kemnaker.go.id"

# jdih.kemnaker.go.id kadang mengembalikan HTTP 200 dengan hasil pencarian
# kosong/parsial meski datanya sebenarnya ada (lihat docs/decisions.md,
# temuan Fase 1) -- bukan error HTTP, jadi tidak tertangkap retry generik di
# http_client.py. Di sini kita ulangi pencarian itu sendiri sebelum
# menyimpulkan "tidak ketemu".
NOT_FOUND_RETRIES = 3
NOT_FOUND_RETRY_DELAY_SECONDS = 3.0


def _search_once(session, nomor, tahun):
    expected_slug = f"peraturan-menteri-ketenagakerjaan-nomor-{nomor}-tahun-{tahun}"
    query = f"Peraturan Menteri Ketenagakerjaan Nomor {nomor} Tahun {tahun}"
    response = session.get(f"{BASE_URL}/peraturan", params={"keyword": query})
    soup = BeautifulSoup(response.text, "lxml")

    for anchor in soup.select('a[href*="/peraturan/detail/"]'):
        match = re.search(r"/peraturan/detail/(\d+)/([a-z0-9-]+)$", anchor["href"])
        if match and match.group(2) == expected_slug:
            return int(match.group(1)), f"{BASE_URL}/peraturan/detail/{match.group(1)}/{match.group(2)}"
    return None, None


def find_detail_url(session, nomor, tahun):
    for attempt in range(1, NOT_FOUND_RETRIES + 1):
        kemnaker_id, url = _search_once(session, nomor, tahun)
        if url is not None:
            return kemnaker_id, url
        if attempt < NOT_FOUND_RETRIES:
            time.sleep(NOT_FOUND_RETRY_DELAY_SECONDS)
    return None, None


def fetch_status(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    for row in soup.select("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2 and cells[0].get_text(strip=True) == "Status":
            return cells[1].get_text(" ", strip=True)
    return None


def cross_check(session, nomor, tahun, primer_status):
    kemnaker_id, url = find_detail_url(session, nomor, tahun)
    if url is None:
        return None

    status = fetch_status(session, url)
    return {
        "situs": "jdih.kemnaker.go.id",
        "id_situs": kemnaker_id,
        "url": url,
        "status": status,
        "status_cocok": status == primer_status if status else None,
    }
