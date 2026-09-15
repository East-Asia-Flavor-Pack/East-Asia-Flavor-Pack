#!/usr/bin/env python3
"""Generate the EAFP Japanese culture compatibility patch.

The vanilla culture block owns every non-name field.  EAFP contributes only a
stable union of four character-name lists and two curated noble first-name
lists. The latter each contain exactly 300 historically attested names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


NAME_LISTS = (
    "male_common_first_names",
    "female_common_first_names",
    "noble_last_names",
    "common_last_names",
)
NOBLE_NAME_COUNT = 300
NOBLE_DATA = Path(__file__).parent / "data" / "japanese_noble_names.json"
OUTPUT_LANGUAGES = ("korean", "english", "simp_chinese")
GENERATED_LOC_PREFIX = "eafp_japanese_noble_names_l_"


def load_noble_names() -> dict:
    data = json.loads(NOBLE_DATA.read_text(encoding="utf-8"))
    for sex in ("male", "female"):
        rows = data[sex]
        names = [row["name"].casefold() for row in rows]
        if len(rows) != NOBLE_NAME_COUNT or len(set(names)) != NOBLE_NAME_COUNT:
            raise ValueError(f"{sex} noble names must contain exactly {NOBLE_NAME_COUNT} unique names")
        for row in rows:
            if not re.fullmatch(r"[A-Za-z]+", row["name"]):
                raise ValueError(f"invalid noble name: {row['name']}")
            if not all(row.get(key) for key in ("korean", "japanese", "simp_chinese", "person", "source")):
                raise ValueError(f"incomplete noble name record: {row['name']}")
            if row["source"] not in data["sources"]:
                raise ValueError(f"unknown name source: {row['source']}")
    return data


def read_localizations(root: Path) -> tuple[dict, set[str]]:
    """Read occupied keys globally, but restrict reuse candidates to person names."""
    catalogs = {}
    name_keys = set()
    for language in (*OUTPUT_LANGUAGES, "japanese"):
        entries = {}
        for path in sorted((root / language).rglob("*.yml")):
            # Previous generated output must not reserve its own keys on the next run.
            if path.name.startswith(GENERATED_LOC_PREFIX):
                continue
            values = dict(re.findall(
                r'^\s*([^\s:#]+):\d*\s*"((?:[^"\\]|\\.)*)"',
                path.read_text(encoding="utf-8-sig"), re.MULTILINE,
            ))
            entries.update(values)
            if language == "english" and (
                path.name == "names_l_english.yml"
                or path.name.endswith("_names_l_english.yml")
                and not any(part in path.name for part in ("ship", "hub", "state", "formation"))
            ):
                name_keys.update(values)
        catalogs[language] = entries
    return catalogs, name_keys


def romanized_name(value: str) -> str:
    # Vanilla English names can contain macrons even when their keys do not.
    plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", plain.casefold())


def resolve_noble_names(data: dict, vanilla: tuple, mod: tuple) -> dict:
    """Reuse matching name/kanji pairs; allocate bare or numbered keys otherwise."""
    vanilla_loc, vanilla_names = vanilla
    mod_loc, mod_names = mod
    effective = {language: vanilla_loc[language] | mod_loc[language]
                 for language in vanilla_loc}
    # Localization keys are case-sensitive (historical EAFP keys also use lowercase).
    occupied = {key for catalogs in (vanilla_loc, mod_loc)
                for entries in catalogs.values() for key in entries}

    def index(catalogs: dict, keys: set[str]) -> dict:
        result = {}
        for key in sorted(keys):
            value = catalogs["english"].get(key, "")
            if value and not any(character in value for character in "$[]#"):
                result.setdefault(romanized_name(value), []).append(key)
        return result

    vanilla_index = index(vanilla_loc, vanilla_names)
    mod_index = index(mod_loc, mod_names)
    generated = {}
    resolved = {"sources": data["sources"], "male": [], "female": []}
    for sex in ("male", "female"):
        for row in data[sex]:
            name = row["name"]
            reading = romanized_name(name)
            kanji = unicodedata.normalize("NFKC", row["japanese"])
            pair = (reading, kanji)
            key = None
            origin = "generated"
            for catalogs, candidates, source in (
                (vanilla_loc, vanilla_index, "vanilla"),
                (mod_loc, mod_index, "mod"),
            ):
                # Prefer the unnumbered key, then the lowest existing suffix.
                def priority(candidate):
                    suffix = re.fullmatch(re.escape(name) + r"_(\d+)", candidate, re.I)
                    return (0 if candidate == name else 1 if suffix else 2,
                            int(suffix[1]) if suffix else 0, candidate)

                for candidate in sorted(candidates.get(reading, []), key=priority):
                    if not all(candidate in effective[language] for language in OUTPUT_LANGUAGES):
                        continue
                    japanese = catalogs["japanese"].get(candidate)
                    chinese = catalogs["simp_chinese"].get(candidate)
                    same_kanji = (unicodedata.normalize("NFKC", japanese) == kanji
                                  if japanese is not None else
                                  chinese in (row["japanese"], row["simp_chinese"]))
                    if same_kanji:
                        key, origin = candidate, source
                        break
                if key is not None:
                    break
            if key is None:
                if pair in generated:
                    key = generated[pair]
                else:
                    key = name
                    suffix = 2
                    while key in occupied:
                        key = f"{name}_{suffix}"
                        suffix += 1
                    occupied.add(key)
                    generated[pair] = key
            resolved[sex].append(row | {"key": key, "origin": origin})
    return resolved


def noble_key(row: dict) -> str:
    return row["key"]


def noble_localization(data: dict, language: str) -> str:
    lines = [f"l_{language}:", " # Generated from tools/data/japanese_noble_names.json"]
    seen = set()
    for sex in ("male", "female"):
        for row in data[sex]:
            key = noble_key(row)
            if row["origin"] != "generated" or key in seen:
                continue
            seen.add(key)
            value = row["name"] if language == "english" else row[language]
            lines.append(f' {key}: "{value}"')
    return "\n".join(lines) + "\n"


def find_block(text: str, key: str) -> tuple[int, int, str]:
    match = re.search(rf"(?m)^\s*(?:REPLACE:)?{re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"could not find block {key!r}")

    brace = text.index("{", match.start())
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for index in range(brace, len(text)):
        char = text[index]
        if comment:
            if char == "\n":
                comment = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == "#":
            comment = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return match.start(), index + 1, text[match.start() : index + 1]
    raise ValueError(f"unterminated block {key!r}")


def read_names(block: str, key: str) -> list[str]:
    _, _, name_block = find_block(block, key)
    body = name_block[name_block.index("{") + 1 : name_block.rindex("}")]
    names: list[str] = []
    for line in body.splitlines():
        token = line.split("#", 1)[0].strip()
        if not token:
            continue
        if any(character.isspace() for character in token):
            raise ValueError(f"unexpected name token in {key}: {token!r}")
        names.append(token)
    return names


def stable_union(vanilla: list[str], eafp: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for name in vanilla + eafp:
        normalized = " ".join(name.split()).casefold()
        if normalized not in seen:
            seen.add(normalized)
            result.append(name)
    return result


def replace_name_list(block: str, key: str, names: list[str]) -> str:
    start, end, old = find_block(block, key)
    opening = old[: old.index("{") + 1]
    replacement = opening + "\n" + "\n".join(f"\t\t{name}" for name in names) + "\n\t}"
    return block[:start] + replacement + block[end:]


def build(vanilla_text: str, eafp_text: str, vanilla_hash: str, noble_data: dict) -> str:
    _, _, vanilla_block = find_block(vanilla_text, "japanese")
    _, _, eafp_block = find_block(eafp_text, "japanese")

    generated = vanilla_block
    counts: list[str] = []
    for key in NAME_LISTS:
        vanilla_names = read_names(vanilla_block, key)
        eafp_names = read_names(eafp_block, key)
        merged = stable_union(vanilla_names, eafp_names)
        generated = replace_name_list(generated, key, merged)
        counts.append(f"{key}={len(merged)}")

    # Keep the curated count fixed instead of unioning these lists with vanilla.
    for sex in ("male", "female"):
        key = f"{sex}_noble_first_names"
        if re.search(rf"\b{key}\s*=\s*\{{", generated):
            start, end, _ = find_block(generated, key)
            generated = generated[:start] + generated[end:]
    position, _, _ = find_block(generated, "noble_last_names")
    additions = []
    for sex in ("male", "female"):
        additions.extend([f"\n\t#추가 실존 다이묘·귀족 인명 {NOBLE_NAME_COUNT}개. 출처: tools/data/japanese_noble_names.json",
                          f"\t{sex}_noble_first_names = {{"])
        additions.extend(f"\t\t{noble_key(row)} # {row['person']}" for row in noble_data[sex])
        additions.append("\t}")
    generated = generated[:position] + "\n".join(additions) + "\n" + generated[position:]

    generated = re.sub(
        r"(?m)^\s*japanese\s*=\s*\{",
        "REPLACE:japanese = {",
        generated,
        count=1,
    )
    header = (
        "# Generated by tools/generate_japanese_culture_patch.py\n"
        "# Vanilla baseline: Victoria 3 1.13.11, common/cultures/00_cultures.txt\n"
        f"# Vanilla SHA-256: {vanilla_hash}\n"
        f"# Stable name union: {', '.join(counts)}\n"
        f"# Curated noble first names: male={NOBLE_NAME_COUNT}, female={NOBLE_NAME_COUNT}\n"
        "# Do not hand-edit non-name fields; regenerate after a vanilla update.\n"
    )
    return header + generated.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vanilla", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    vanilla_bytes = args.vanilla.read_bytes()
    vanilla_text = vanilla_bytes.decode("utf-8-sig")
    eafp_text = args.target.read_text(encoding="utf-8-sig")
    vanilla_hash = hashlib.sha256(vanilla_bytes).hexdigest()
    root = args.target.resolve().parents[2]
    vanilla_root = args.vanilla.resolve().parents[2]
    noble_data = resolve_noble_names(
        load_noble_names(), read_localizations(vanilla_root / "localization"),
        read_localizations(root / "localization"),
    )
    output = build(vanilla_text, eafp_text, vanilla_hash, noble_data)

    outputs = {args.target: output}
    for language in OUTPUT_LANGUAGES:
        path = root / "localization" / language / f"eafp_japanese_noble_names_l_{language}.yml"
        outputs[path] = noble_localization(noble_data, language)

    if args.check:
        for path, expected in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8-sig") != expected:
                raise SystemExit(f"Japanese culture/name output is stale: {path}")
        return 0

    # Victoria 3 reports a lexer warning for script files without a UTF-8 BOM.
    for path, expected in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8-sig", newline="\r\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
