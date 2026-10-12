"""Read/write helpers for data/ and raw/, kept idempotent: a file is only
rewritten when its content actually changed, so a re-run against an
unchanged source produces no git diff.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGULATIONS_DIR = ROOT / "data" / "regulations"
EDGES_FILE = ROOT / "data" / "edges.json"
LAST_CHECKED_FILE = ROOT / "data" / "last-checked.json"
RAW_BPK_DIR = ROOT / "raw" / "bpk"
CHANGES_DIR = ROOT / "data" / "changes"


def _read_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_if_changed(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    new_content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == new_content:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def load_regulation(reg_id):
    return _read_json(REGULATIONS_DIR / f"{reg_id}.json", None)


def existing_regulation_ids():
    return {path.stem for path in REGULATIONS_DIR.glob("*.json")}


def save_regulation(reg_id, data):
    """Returns True if the regulation's own data (not counting last-checked) changed."""
    return _write_json_if_changed(REGULATIONS_DIR / f"{reg_id}.json", data)


def save_changes_log(date_str, entries):
    """Overwrites data/changes/{date_str}.json with the full list of entries
    found in that day's run. Writes nothing if there are no changes at all
    (no empty files for a no-op day).
    """
    if not entries:
        return False
    return _write_json_if_changed(CHANGES_DIR / f"{date_str}.json", entries)


def save_raw_html(reg_id, html):
    RAW_BPK_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_BPK_DIR / f"{reg_id}.html").write_text(html, encoding="utf-8")


def update_last_checked(reg_id, date_str):
    data = _read_json(LAST_CHECKED_FILE, {})
    data[reg_id] = date_str
    _write_json_if_changed(LAST_CHECKED_FILE, data)


def rebuild_edges():
    edges = []
    for path in sorted(REGULATIONS_DIR.glob("*.json")):
        reg = _read_json(path, {})
        reg_id = path.stem
        for relation in reg.get("relations", []):
            if not relation.get("target_id"):
                continue
            edges.append({
                "from": reg_id,
                "to": relation["target_id"],
                "type": relation["type"],
                "source": relation.get("sumber", "bpk"),
            })

    edges.sort(key=lambda e: (e["from"], e["to"], e["type"]))
    _write_json_if_changed(EDGES_FILE, edges)
