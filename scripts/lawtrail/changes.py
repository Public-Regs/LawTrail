"""Bandingkan data peraturan sebelum/sesudah scrape untuk menghasilkan entri
data/changes/{tanggal}.json -- dokumen baru, status berubah, relasi berubah,
PDF berubah, dan peraturan yang hilang dari daftar sumber.
"""


def _relation_set(data):
    return {
        (r["type"], r.get("target_id"), r.get("target_title"))
        for r in data.get("relations", [])
    }


def diff_regulation(reg_id, old, new):
    """old/new: dict peraturan (hasil parse) atau None kalau belum ada.
    Mengembalikan list entri perubahan (bisa lebih dari satu per peraturan).
    """
    entries = []

    if old is None:
        entries.append({"id": reg_id, "type": "baru", "detail": {"status": new.get("status")}})
        return entries

    if old.get("status") != new.get("status"):
        entries.append({
            "id": reg_id,
            "type": "status_berubah",
            "detail": {"sebelum": old.get("status"), "sesudah": new.get("status")},
        })

    old_relations = _relation_set(old)
    new_relations = _relation_set(new)
    added = new_relations - old_relations
    removed = old_relations - new_relations
    if added or removed:
        entries.append({
            "id": reg_id,
            "type": "relasi_berubah",
            "detail": {
                "ditambahkan": [{"type": t, "target_id": tid, "target_title": tt} for t, tid, tt in added],
                "dihapus": [{"type": t, "target_id": tid, "target_title": tt} for t, tid, tt in removed],
            },
        })

    old_hash = old.get("primer", {}).get("pdf_sha256")
    new_hash = new.get("primer", {}).get("pdf_sha256")
    if old_hash != new_hash and old_hash is not None and new_hash is not None:
        entries.append({
            "id": reg_id,
            "type": "pdf_berubah",
            "detail": {"sebelum": old_hash, "sesudah": new_hash},
        })

    return entries


def missing_entries(previous_ids, seen_ids):
    return [
        {"id": reg_id, "type": "hilang", "detail": {}}
        for reg_id in sorted(previous_ids - seen_ids)
    ]
