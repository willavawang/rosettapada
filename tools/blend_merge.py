"""Merge two blind readings of a chapter into data/blend/chapters/NN-slug.json.

    python3 tools/blend_merge.py 1 pairs readingA.json readingB.json

Each line takes the higher of the two tiers; lines where the readers disagree are flagged.
The raw readings are copied to data/blend/readings/ for provenance.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from blend_packet import packet  # noqa: E402


def merge(chapter_no, slug, path_a, path_b):
    a, b = (json.loads(Path(p).read_text(encoding="utf-8")) for p in (path_a, path_b))
    src = packet(chapter_no)
    readings_dir = ROOT / "data/blend/readings"
    readings_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{chapter_no:02d}-{slug}"
    kept = []
    for tag, path in (("A", path_a), ("B", path_b)):
        target = readings_dir / f"{stem}-{tag}.json"
        shutil.copyfile(path, target)
        kept.append(str(target.relative_to(ROOT)))
    va = {v["no"]: v for v in a["verses"]}
    vb = {v["no"]: v for v in b["verses"]}
    verses = []
    for sv in src["verses"]:
        n = sv["no"]
        pali = sv["witnesses"]["pi"]["readings"][0]["lines"]
        ra, rb = va.get(n, {}), vb.get(n, {})
        la = {l["line"]: l for l in ra.get("lines", [])}
        lb = {l["line"]: l for l in rb.get("lines", [])}
        lines = []
        for i, text in enumerate(pali, 1):
            x, y = la.get(i, {}), lb.get(i, {})
            tiers = {"A": x.get("tier"), "B": y.get("tier")}
            known = [t for t in tiers.values() if isinstance(t, int)]
            tier = max(known) if known else 4
            flags = []
            if len(known) < 2:
                flags.append("missing reading")
            elif len(set(known)) > 1:
                flags.append("readers disagree")
            if "low" in (x.get("confidence"), y.get("confidence")):
                flags.append("low confidence")
            lines.append({
                "line": i,
                "pi": text,
                "gloss": {"A": x.get("gloss"), "B": y.get("gloss")},
                "aligned": {"A": x.get("aligned", {}), "B": y.get("aligned", {})},
                "witness_glosses": {"A": x.get("witness_glosses", {}), "B": y.get("witness_glosses", {})},
                "differences": {"A": x.get("differences", []), "B": y.get("differences", [])},
                "tiers": tiers,
                "reasons": {"A": x.get("tier_reason"), "B": y.get("tier_reason")},
                "confidence": {"A": x.get("confidence"), "B": y.get("confidence")},
                "candidates": {"A": x.get("candidates", []), "B": y.get("candidates", [])},
                "tier": tier,
                "flags": flags,
                "rules": [],
            })
        verses.append({
            "no": n,
            "witnesses": {k: w["status"] for k, w in sv["witnesses"].items()},
            "tier": max(l["tier"] for l in lines),
            "lines": lines,
            "extra": {"A": ra.get("extra", []), "B": rb.get("extra", [])},
            "notes": {"A": ra.get("notes"), "B": rb.get("notes")},
            "blend": None,
            "status": "read",
        })
    out = {
        "chapter": src["chapter"],
        "stage": "checkpoint-1",
        "readings": kept,
        "candidates": {"A": a.get("candidates", []), "B": b.get("candidates", [])},
        "verses": verses,
    }
    target = ROOT / "data/blend/chapters" / f"{stem}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return target, out


if __name__ == "__main__":
    target, out = merge(int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4])
    lines = [l for v in out["verses"] for l in v["lines"]]
    print(target.relative_to(ROOT), {t: sum(l["tier"] == t for l in lines) for t in (1, 2, 3, 4)},
          "disagree:", sum("readers disagree" in l["flags"] for l in lines))
