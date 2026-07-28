"""Generate or verify the committed RS-02 Lenia CPU fixtures."""

from __future__ import annotations

import argparse
from pathlib import Path

from abiogenesis.lenia.config import load_config
from abiogenesis.lenia.fixtures import check_fixtures, write_fixtures

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPOSITORY_ROOT / "configs" / "lenia" / "lenia-single-channel-cpu-v1.json"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "tests" / "fixtures" / "lenia"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.check:
        check_fixtures(args.output, config)
        print(f"Lenia fixtures are byte-identical: {args.output}")
    else:
        manifest = write_fixtures(args.output, config)
        print(f"Wrote {len(manifest['files'])} Lenia fixtures and manifest: {args.output}")


if __name__ == "__main__":
    main()
