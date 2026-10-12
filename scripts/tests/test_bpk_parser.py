from pathlib import Path

from lawtrail.bpk import parse_detail_html

FIXTURES_DIR = Path(__file__).parent / "fixtures"

PAGE_URL = "https://peraturan.bpk.go.id/Details/231405/permenaker-no-11-tahun-2022"


def load_fixture(name):
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parses_metadata_fields():
    html = load_fixture("bpk_permenaker_11_2022.html")
    data = parse_detail_html(html, PAGE_URL, bpk_id=231405)

    assert data["jenis"] == "Peraturan Menteri Ketenagakerjaan"
    assert data["nomor"] == "11"
    assert data["tahun"] == 2022
    assert data["status"] == "Berlaku"
    assert data["judul"].startswith("Peraturan Menteri Ketenagakerjaan  Nomor 11 Tahun 2022")
    assert data["primer"]["id_situs"] == 231405
    assert data["primer"]["url"] == PAGE_URL


def test_finds_full_text_pdf_download_link():
    html = load_fixture("bpk_permenaker_11_2022.html")
    data = parse_detail_html(html, PAGE_URL, bpk_id=231405)

    assert data["primer"]["pdf_url"] is not None
    assert data["primer"]["pdf_url"].startswith("https://peraturan.bpk.go.id/Download/")
    assert data["primer"]["pdf_url"].endswith(".pdf")


def test_parses_mencabut_relation_with_linked_target():
    html = load_fixture("bpk_permenaker_11_2022.html")
    data = parse_detail_html(html, PAGE_URL, bpk_id=231405)

    mencabut = [r for r in data["relations"] if r["type"] == "mencabut"]
    assert len(mencabut) == 1
    assert mencabut[0]["target_id"] == "permenaker-no-8-tahun-2015"
    assert mencabut[0]["target_url"] == "https://peraturan.bpk.go.id/Details/145979/permenaker-no-8-tahun-2015"
    assert mencabut[0]["sumber"] == "bpk"


def test_relation_without_link_keeps_text_and_null_target():
    html = load_fixture("bpk_uu_6_2023.html")
    data = parse_detail_html(html, "https://peraturan.bpk.go.id/Details/246523/uu-no-6-tahun-2023", bpk_id=246523)

    unlinked = [r for r in data["relations"] if r["type"] == "mencabut" and r["target_id"] is None]
    assert len(unlinked) == 1
    assert "Staatsblad" in unlinked[0]["target_title"]
