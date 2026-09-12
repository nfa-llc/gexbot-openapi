"""Read, check and bump the published specification version.

The version appears in four places, and they must always agree:

* ``latest/gexbot.spec3.yaml`` -- ``info.version``, the source of truth
* ``latest/gexbot.spec3.json`` -- the generated twin of the YAML
* ``README.md`` -- "The specification version is ``x.y.z``."
* ``AGENTS.md`` -- "Spec version: x.y.z."

Usage::

    python scripts/spec-version.py --check
    python scripts/spec-version.py --bump patch
    python scripts/spec-version.py --bump minor
    python scripts/spec-version.py --set 2.6.0
    python scripts/spec-version.py --sync

``--check`` verifies that the four places agree and that the JSON twin matches
a fresh conversion of the YAML. It exits 1 on any mismatch and writes nothing.
A write mode edits the YAML version line in place, so the hand-written
formatting and the byte order mark survive. It then regenerates the twin and
rewrites both prose lines.

``--sync`` repairs the JSON twin and the two prose lines from the version the
YAML already states. Use it after a hand edit to the YAML. A version that does
not rise above the current one is refused unless ``--allow-downgrade`` is given.

Every mode prints ``version=x.y.z``. When ``GITHUB_OUTPUT`` is set, it appends
the same line there for a later workflow step to read.

Requires PyYAML.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SPEC_YAML = os.path.join(ROOT, "latest", "gexbot.spec3.yaml")
SPEC_JSON = os.path.join(ROOT, "latest", "gexbot.spec3.json")
README = os.path.join(ROOT, "README.md")
AGENTS = os.path.join(ROOT, "AGENTS.md")

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
# The only top-level "version" key sits two spaces deep under "info:". The
# anchor keeps it away from paths such as "/futures/conversion:".
YAML_VERSION = re.compile(r"^(  version: )(\S+)[ \t]*$", re.MULTILINE)
README_VERSION = re.compile(r"(The specification version is `)(\d+\.\d+\.\d+)(`\.)")
AGENTS_VERSION = re.compile(r"(- Spec version: )(\d+\.\d+\.\d+)(\.)")
BOM = "﻿"


class StrictLoader(yaml.SafeLoader):
    """A loader that refuses a duplicated mapping key.

    ``yaml.safe_load`` keeps the last of a duplicated pair and says nothing, so
    a second key silently discards the first. js-yaml, which Swagger UI, Redoc
    and swagger-cli all use, rejects the same document.
    """


def _no_duplicate_keys(loader, node, deep: bool = False) -> dict:
    seen: set = set()
    for key_node, _value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            mark = key_node.start_mark
            raise SystemExit(f"error: duplicated key {key!r} at line {mark.line + 1} of {mark.name}")
        seen.add(key)
    return loader.construct_mapping(node, deep=deep)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)


def load_spec(text: str) -> dict:
    """Parse the published YAML strictly, and insist it is a mapping."""
    document = yaml.load(text, Loader=StrictLoader)
    if not isinstance(document, dict) or not isinstance(document.get("info"), dict):
        raise SystemExit("error: latest/gexbot.spec3.yaml did not parse as an OpenAPI document")
    return document


def read_text(path: str) -> tuple[str, bool]:
    """Return the file text and whether it carried a byte order mark."""
    if not os.path.exists(path):
        raise SystemExit(f"error: {os.path.relpath(path, ROOT)} does not exist")
    with io.open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    if text.startswith(BOM):
        return text[len(BOM):], True
    return text, False


def write_text(path: str, text: str, bom: bool) -> None:
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write((BOM if bom else "") + text)


def json_twin(spec: dict) -> str:
    """Render the JSON twin exactly as the committed file is rendered."""
    return json.dumps(spec, indent=2) + "\n"


def sole_match(pattern: re.Pattern[str], text: str, label: str) -> re.Match[str]:
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise SystemExit(f"error: expected exactly one version in {label}, found {len(matches)}")
    return matches[0]


def next_version(current: str, part: str) -> str:
    found = SEMVER.match(current)
    if not found:
        raise SystemExit(f"error: {current!r} is not a three-part semantic version")
    major, minor, patch = (int(value) for value in found.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def emit(version: str) -> None:
    print(f"version={version}")
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with io.open(output, "a", encoding="utf-8") as handle:
            handle.write(f"version={version}\n")


def check() -> int:
    yaml_text, _bom = read_text(SPEC_YAML)
    spec = load_spec(yaml_text)
    version = spec["info"]["version"]

    problems: list[str] = []
    if not SEMVER.match(str(version)):
        problems.append(f"info.version {version!r} is not a three-part semantic version")

    line_version = sole_match(YAML_VERSION, yaml_text, "latest/gexbot.spec3.yaml").group(2)
    if line_version != version:
        problems.append(f"the YAML version line says {line_version!r} but the parsed value is {version!r}")

    json_text, _json_bom = read_text(SPEC_JSON)
    if json_text != json_twin(spec):
        problems.append(
            "latest/gexbot.spec3.json is not a current conversion of the YAML; "
            "run scripts/spec-version.py --sync"
        )
    else:
        twin_version = json.loads(json_text)["info"]["version"]
        if twin_version != version:
            problems.append(f"the JSON twin says {twin_version!r}")

    readme_text, _r_bom = read_text(README)
    readme_version = sole_match(README_VERSION, readme_text, "README.md").group(2)
    if readme_version != version:
        problems.append(f"README.md says {readme_version!r}")

    agents_text, _a_bom = read_text(AGENTS)
    agents_version = sole_match(AGENTS_VERSION, agents_text, "AGENTS.md").group(2)
    if agents_version != version:
        problems.append(f"AGENTS.md says {agents_version!r}")

    if problems:
        print(f"the specification version is inconsistent ({len(problems)} problem(s)):")
        for problem in problems:
            print("  " + problem)
        return 1
    print(f"the specification version is consistent in every file: {version}")
    emit(version)
    return 0


def apply(version: str) -> int:
    yaml_text, yaml_bom = read_text(SPEC_YAML)
    found = sole_match(YAML_VERSION, yaml_text, "latest/gexbot.spec3.yaml")
    previous = found.group(2)
    yaml_text = yaml_text[: found.start()] + found.group(1) + version + yaml_text[found.end():]
    write_text(SPEC_YAML, yaml_text, yaml_bom)

    spec = load_spec(yaml_text)
    if spec["info"]["version"] != version:
        raise SystemExit(f"error: the YAML still parses as version {spec['info']['version']!r}")
    write_text(SPEC_JSON, json_twin(spec), False)

    for path, pattern, label in ((README, README_VERSION, "README.md"), (AGENTS, AGENTS_VERSION, "AGENTS.md")):
        text, bom = read_text(path)
        match = sole_match(pattern, text, label)
        write_text(path, text[: match.start()] + match.group(1) + version + match.group(3) + text[match.end():], bom)

    if previous == version:
        print(f"synchronised the four files at version {version}")
    else:
        print(f"raised the specification version from {previous} to {version} in four files")
    emit(version)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="verify every file agrees; write nothing")
    group.add_argument("--bump", choices=("major", "minor", "patch"), help="raise this part of the version")
    group.add_argument("--set", dest="explicit", metavar="X.Y.Z", help="set this exact version")
    group.add_argument(
        "--sync",
        action="store_true",
        help="rewrite the JSON twin and both prose lines from the version the YAML already states",
    )
    parser.add_argument(
        "--allow-downgrade",
        action="store_true",
        help="permit a target version that does not rise above the current one",
    )
    args = parser.parse_args()

    if args.check:
        return check()

    current = str(load_spec(read_text(SPEC_YAML)[0])["info"]["version"])
    if args.sync:
        # Repair only. The version itself does not move.
        return apply(current)
    if args.explicit:
        if not SEMVER.match(args.explicit):
            raise SystemExit(f"error: {args.explicit!r} is not a three-part semantic version")
        target = args.explicit
    else:
        target = next_version(current, args.bump)

    def ordinal(value: str) -> tuple:
        found = SEMVER.match(value)
        if not found:
            raise SystemExit(f"error: {value!r} is not a three-part semantic version")
        return tuple(int(part) for part in found.groups())

    if not args.allow_downgrade and ordinal(target) <= ordinal(current):
        raise SystemExit(
            f"error: {target} does not rise above the current version {current}. "
            "Pass --allow-downgrade to force it."
        )
    return apply(target)


if __name__ == "__main__":
    sys.exit(main())
