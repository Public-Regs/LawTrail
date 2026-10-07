"""Scraper for peraturan.bpk.go.id (sumber primer)."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_URL = "https://peraturan.bpk.go.id"
PERMENAKER_JENIS_ID = 105  # "Peraturan Menteri Ketenagakerjaan" di filter /Search?jenis=

RELATION_LABELS = {
    "Diubah dengan": "diubah_dengan",
    "Mencabut": "mencabut",
    "Dicabut dengan": "dicabut_dengan",
    "Menetapkan": "menetapkan",
    "Mengubah": "mengubah",
}

MONTHS_ID = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}


def list_search_pages(session, jenis_id=PERMENAKER_JENIS_ID):
    """Yield (bpk_id, slug) for every result across all pages of a /Search?jenis=... listing."""
    page = 1
    seen = set()
    while True:
        url = f"{BASE_URL}/Search?jenis={jenis_id}&p={page}"
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        links = soup.select('a.text-gray-600.text-decoration-none[href^="/Details/"]')
        if not links:
            break

        found_new = False
        for link in links:
            match = re.match(r"^/Details/(\d+)/([a-z0-9-]+)$", link["href"])
            if not match:
                continue
            bpk_id, slug = int(match.group(1)), match.group(2)
            if bpk_id in seen:
                continue
            seen.add(bpk_id)
            found_new = True
            yield bpk_id, slug

        if not found_new:
            break
        page += 1


def _parse_indonesian_date(text):
    text = text.strip().lower()
    match = re.match(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", text)
    if not match:
        return None
    day, month_name, year = match.groups()
    month = MONTHS_ID.get(month_name)
    if month is None:
        return None
    return f"{int(year):04d}-{month:02d}-{int(day):02d}"


def _metadata_fields(soup):
    fields = {}
    for label_div in soup.select("div.col-lg-3.fw-bold"):
        label = label_div.get_text(strip=True)
        value_div = label_div.find_next_sibling("div", class_="col-lg-9")
        if value_div is None:
            continue
        fields[label] = value_div.get_text(" ", strip=True)
    return fields


def _parse_relations(soup, page_url):
    relations = []
    for header_div in soup.select("div.col-12.fw-semibold.bg-light-primary.p-4"):
        label = header_div.get_text(strip=True).rstrip(" :").strip()
        relation_type = RELATION_LABELS.get(label)
        if relation_type is None:
            continue

        row = header_div.find_parent("div", class_="row")
        value_row = row.find_next_sibling("div", class_="row") if row else None
        if value_row is None:
            continue

        for li in value_row.select("ol > li"):
            anchor = li.find("a")
            if anchor and anchor.get("href"):
                match = re.match(r"^/Details/(\d+)/([a-z0-9-]+)$", anchor["href"])
                target_id = match.group(2) if match else None
                relations.append({
                    "type": relation_type,
                    "target_id": target_id,
                    "target_title": anchor.get_text(strip=True),
                    "target_url": urljoin(page_url, anchor["href"]),
                    "sumber": "bpk",
                })
            else:
                text = li.get_text(" ", strip=True)
                if text:
                    relations.append({
                        "type": relation_type,
                        "target_id": None,
                        "target_title": text,
                        "target_url": None,
                        "sumber": "bpk",
                    })
    return relations


def parse_detail_html(html, page_url, bpk_id):
    soup = BeautifulSoup(html, "lxml")
    fields = _metadata_fields(soup)

    pdf_anchor = soup.select_one('a[href^="/Download/"]')
    pdf_url = urljoin(page_url, pdf_anchor["href"]) if pdf_anchor else None

    subjek_raw = fields.get("Subjek", "")
    subjek = [line.strip() for line in subjek_raw.splitlines() if line.strip()]

    tahun_raw = fields.get("Tahun", "").strip()

    return {
        "jenis": fields.get("Bentuk"),
        "nomor": fields.get("Nomor"),
        "tahun": int(tahun_raw) if tahun_raw.isdigit() else None,
        "judul": fields.get("Judul"),
        "tempat_penetapan": fields.get("Tempat Penetapan"),
        "tanggal_penetapan": _parse_indonesian_date(fields.get("Tanggal Penetapan", "")),
        "tanggal_pengundangan": _parse_indonesian_date(fields.get("Tanggal Pengundangan", "")),
        "tanggal_berlaku": _parse_indonesian_date(fields.get("Tanggal Berlaku", "")),
        "status": fields.get("Status"),
        "subjek": subjek,
        "sumber_pengundangan": fields.get("Sumber"),
        "primer": {
            "situs": "peraturan.bpk.go.id",
            "id_situs": bpk_id,
            "url": page_url,
            "pdf_url": pdf_url,
        },
        "relations": _parse_relations(soup, page_url),
    }


def fetch_detail(session, bpk_id, slug):
    url = f"{BASE_URL}/Details/{bpk_id}/{slug}"
    response = session.get(url)
    data = parse_detail_html(response.text, url, bpk_id)
    return data, response.text
