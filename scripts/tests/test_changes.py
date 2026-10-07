from lawtrail.changes import diff_regulation, missing_entries


def make_regulation(status="Berlaku", relations=None, pdf_sha256="abc123"):
    return {
        "status": status,
        "relations": relations or [],
        "primer": {"pdf_sha256": pdf_sha256},
    }


def test_new_regulation_is_reported_as_baru():
    new = make_regulation()
    entries = diff_regulation("permenaker-no-1-tahun-2030", None, new)

    assert len(entries) == 1
    assert entries[0]["type"] == "baru"
    assert entries[0]["id"] == "permenaker-no-1-tahun-2030"


def test_no_changes_produces_no_entries():
    data = make_regulation()
    entries = diff_regulation("permenaker-no-1-tahun-2030", data, data)

    assert entries == []


def test_status_change_is_detected():
    old = make_regulation(status="Berlaku")
    new = make_regulation(status="Dicabut")
    entries = diff_regulation("permenaker-no-1-tahun-2030", old, new)

    status_changes = [e for e in entries if e["type"] == "status_berubah"]
    assert len(status_changes) == 1
    assert status_changes[0]["detail"] == {"sebelum": "Berlaku", "sesudah": "Dicabut"}


def test_relation_addition_and_removal_are_detected():
    old = make_regulation(relations=[
        {"type": "mencabut", "target_id": "permenaker-no-2-tahun-2020", "target_title": "Permenaker No. 2 Tahun 2020"},
    ])
    new = make_regulation(relations=[
        {"type": "mengubah", "target_id": "permenaker-no-3-tahun-2021", "target_title": "Permenaker No. 3 Tahun 2021"},
    ])
    entries = diff_regulation("permenaker-no-1-tahun-2030", old, new)

    relation_changes = [e for e in entries if e["type"] == "relasi_berubah"]
    assert len(relation_changes) == 1
    assert len(relation_changes[0]["detail"]["ditambahkan"]) == 1
    assert relation_changes[0]["detail"]["ditambahkan"][0]["target_id"] == "permenaker-no-3-tahun-2021"
    assert len(relation_changes[0]["detail"]["dihapus"]) == 1
    assert relation_changes[0]["detail"]["dihapus"][0]["target_id"] == "permenaker-no-2-tahun-2020"


def test_pdf_hash_change_is_detected():
    old = make_regulation(pdf_sha256="old-hash")
    new = make_regulation(pdf_sha256="new-hash")
    entries = diff_regulation("permenaker-no-1-tahun-2030", old, new)

    pdf_changes = [e for e in entries if e["type"] == "pdf_berubah"]
    assert len(pdf_changes) == 1
    assert pdf_changes[0]["detail"] == {"sebelum": "old-hash", "sesudah": "new-hash"}


def test_missing_entries_only_lists_ids_no_longer_seen():
    previous_ids = {"a", "b", "c"}
    seen_ids = {"a", "c"}
    entries = missing_entries(previous_ids, seen_ids)

    assert entries == [{"id": "b", "type": "hilang", "detail": {}}]
