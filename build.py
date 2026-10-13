# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Build the schema v2 catalogue documents from the per risk YAML sources.

The YAML files under catalogues/<family>/risks/ are the source. This assembles them into one JSON
document per family and the JSON is never edited by hand, so source and output cannot drift.

  uv run build.py                                   rebuild every family's committed JSON
  uv run build.py --check                           fail if any committed JSON differs from its sources
  uv run build.py bias                              rebuild one family
  uv run build.py bias --list                       print the risks of a family
  uv run build.py privacy --risks a,b               only those risks, weights split evenly among them
  uv run build.py privacy --weights a=3,b=1         those risks with those severities (normalised to sum 1)
  uv run build.py privacy --risks a,b --out my.json write somewhere other than the committed file

A risk is the stem of a file under risks/ (its plugin id).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml: run with `uv run build.py`")

ROOT = pathlib.Path(__file__).parent / "catalogues"
DEFAULTS = {"entity_kind": "assistant", "transform": "keep_real", "doc": 0, "requires_brain": False}
MODES = {"single_turn", "scripted_multi_turn", "adaptive_multi_turn"}
LANGUAGES = {"es", "en"}


def families() -> list[str]:
    return sorted(p.parent.name for p in ROOT.glob("*/risks"))


def available(family: str) -> list[str]:
    return sorted(p.stem for p in (ROOT / family / "risks").glob("*.yaml"))


def parse_ids(text: str) -> list[str]:
    ids = [r.strip() for r in text.split(",") if r.strip()]
    if not ids:
        sys.exit("--risks needs at least one risk id")
    repeated = sorted({r for r in ids if ids.count(r) > 1})
    if repeated:
        sys.exit(f"risks given more than once: {repeated}")
    return ids


def parse_weights(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for pair in text.split(","):
        name, _, value = pair.partition("=")
        name = name.strip()
        try:
            weight = float(value)
        except ValueError:
            sys.exit(f"--weights wants name=number pairs, got {pair!r}")
        if not math.isfinite(weight) or weight <= 0:
            sys.exit(f"--weights must be positive numbers, got {pair!r}")
        if name in out:
            sys.exit(f"--weights gives {name!r} more than once")
        out[name] = weight
    return out


def strategy(s: dict, plugin: str | None) -> dict:
    it = dict(s["interaction"])
    if it["mode"] == "adaptive_multi_turn":
        it.setdefault("attacker", "crescendo")
    return {"id": s["id"], "name": s["name"], "description": s["description"], "plugin": plugin, **DEFAULTS, "interaction": it}


def load(family: str, pid: str) -> dict:
    path = ROOT / family / "risks" / f"{pid}.yaml"
    where = path.relative_to(ROOT.parent)
    try:
        d = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        sys.exit(f"{where}: not valid YAML: {e}")
    if not isinstance(d, dict):
        sys.exit(f"{where}: expected a mapping with plugin, principle, attacks and controls")
    problems = []
    for key in ("plugin", "principle", "attacks", "controls"):
        if key not in d:
            problems.append(f"missing `{key}`")
    if not problems and not d["attacks"]:
        problems.append("`attacks` is empty")
    if not problems:
        for key in ("id", "name", "description"):
            if key not in d["plugin"]:
                problems.append(f"plugin is missing `{key}`")
        for key in ("id", "rubric"):
            if key not in d["principle"]:
                problems.append(f"principle is missing `{key}`")
        for i, s in enumerate((d["attacks"] or []) + (d["controls"] or [])):
            missing = [k for k in ("id", "name", "description", "interaction") if k not in s]
            if missing:
                problems.append(f"strategy {s.get('id', f'#{i + 1}')} is missing {missing}")
    if problems:
        sys.exit(f"{where}: " + "; ".join(problems))
    d["controls"] = d["controls"] or []
    if d["plugin"]["id"] != pid:
        problems.append(f"plugin id {d['plugin']['id']!r} does not match the file name")
    for s in d["attacks"] + d["controls"]:
        it = s["interaction"]
        if it.get("mode") not in MODES:
            problems.append(f"{s['id']}: unknown mode {it.get('mode')!r}")
        texts = it.get("messages") or [it.get("prompt") or it.get("opening") or {}]
        if any(not isinstance(t, dict) or set(t) != LANGUAGES for t in texts):
            problems.append(f"{s['id']}: every message needs exactly {sorted(LANGUAGES)}")
    for s in d["controls"]:
        if s["interaction"].get("mode") == "adaptive_multi_turn":
            problems.append(f"{s['id']}: a control cannot be adaptive, the attacker only steers attacks")
    if problems:
        sys.exit(f"{where}: " + "; ".join(problems))
    return d


def weigh(chosen: list[str], given: dict[str, float] | None) -> dict[str, float]:
    if given is None:
        even = round(1 / len(chosen), 6)
        weights = {r: even for r in chosen}
        weights[chosen[-1]] = round(1 - even * (len(chosen) - 1), 6)
    else:
        total = sum(given.values())
        weights = {r: round(w / total, 6) for r, w in given.items()}
        weights[chosen[-1]] = round(1 - sum(list(weights.values())[:-1]), 6)
    return weights


def build(family: str, chosen: list[str], weights: dict[str, float], name: str) -> dict:
    principles, plugins, strategies = [], [], []
    for pid in chosen:
        d = load(family, pid)
        pr, pl = d["principle"], d["plugin"]
        principles.append({"id": pr["id"], "weight": weights[pid], "rubric": pr["rubric"]})
        plugins.append({"id": pl["id"], "name": pl["name"], "description": pl["description"], "principle": pr["id"]})
        strategies += [strategy(s, pid) for s in d["attacks"]]
        strategies += [strategy(s, None) for s in d["controls"]]

    seen: set[str] = set()
    dupes = sorted({s["id"] for s in strategies if s["id"] in seen or seen.add(s["id"])})
    if dupes:
        sys.exit(f"{family}: strategy ids used more than once: {dupes}")

    return {"schema_version": 2, "name": name,
            "contract": {"version": "v1",
                         "verdict": {"positive": ["YES", " YES", "Yes"], "negative": ["NO", " NO", "No"]},
                         "principles": principles},
            "plugins": plugins, "strategies": strategies}


def render(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def full(family: str) -> str:
    chosen = available(family)
    return render(build(family, chosen, weigh(chosen, None), family))


def check() -> None:
    stale = []
    for family in families():
        path = ROOT / family / f"{family}.json"
        if not path.exists() or path.read_text(encoding="utf-8") != full(family):
            stale.append(str(path.relative_to(ROOT.parent)))
    if stale:
        sys.exit("out of date with their sources, run `uv run build.py`:\n  " + "\n  ".join(stale))
    print(f"{len(families())} families up to date")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build catalogue documents from catalogues/<family>/risks/*.yaml")
    ap.add_argument("family", nargs="?", help="the family to build; default every family")
    ap.add_argument("--risks", help="comma separated risk ids to include; default every risk")
    ap.add_argument("--weights", help="comma separated id=severity; sets the risk set and its weights")
    ap.add_argument("--name", help="catalogue name in the document; default the family")
    ap.add_argument("--out", type=pathlib.Path, help="output path; default catalogues/<family>/<family>.json")
    ap.add_argument("--list", action="store_true", help="print the risks of the family and exit")
    ap.add_argument("--check", action="store_true", help="verify every committed JSON matches its sources")
    args = ap.parse_args()

    if args.check:
        if args.family or args.risks or args.weights or args.name or args.out or args.list:
            sys.exit("--check takes no other argument")
        check(); return

    if args.family is None:
        if args.risks or args.weights or args.name or args.out or args.list:
            sys.exit("--risks, --weights, --name, --out and --list need a family")
        for family in families():
            path = ROOT / family / f"{family}.json"
            path.write_text(full(family), encoding="utf-8")
            print(path.relative_to(ROOT.parent))
        return

    if args.family not in families():
        sys.exit(f"unknown family {args.family!r}. available: {families()}")
    have = available(args.family)
    if args.list:
        print("\n".join(have)); return

    if args.risks is not None and args.weights is not None:
        sys.exit("--weights already names the risks, so use it or --risks, not both")
    given = parse_weights(args.weights) if args.weights is not None else None
    if given:
        chosen = list(given)
    elif args.risks is not None:
        chosen = parse_ids(args.risks)
    else:
        chosen = have
    unknown = [r for r in chosen if r not in have]
    if unknown:
        sys.exit(f"unknown risks: {unknown}. available: {have}")

    weights = weigh(chosen, given)
    doc = build(args.family, chosen, weights, args.name or args.family)
    out = args.out or ROOT / args.family / f"{args.family}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(doc), encoding="utf-8")
    attacks = sum(s["plugin"] is not None for s in doc["strategies"])
    print(f"{out}: {len(doc['plugins'])} risks, {attacks} attacks, {len(doc['strategies']) - attacks} controls")
    print("weights: " + ", ".join(f"{r}={weights[r]}" for r in chosen))


if __name__ == "__main__":
    main()
