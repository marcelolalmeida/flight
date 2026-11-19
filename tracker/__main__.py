from __future__ import annotations

import argparse

from .config import load_watches
from .notify import send_telegram
from .runner import run


def _load_env() -> None:
    """Load KEY=VALUE lines from flight-tracker/.env (gitignored) without overriding real env vars."""
    import os
    from .config import ROOT
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip().strip('"'))


def main() -> None:
    _load_env()
    p =argparse.ArgumentParser(prog="tracker")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--dry-run", action="store_true", help="don't notify or save")
    sub.add_parser("check-config")
    sub.add_parser("test-telegram")
    args = p.parse_args()

    if args.cmd == "run":
        run(dry_run=args.dry_run)
    elif args.cmd == "check-config":
        for w in load_watches():
            print(w)
    elif args.cmd == "test-telegram":
        print("sent" if send_telegram("✈️ Flight tracker test message") else "not configured")


if __name__ == "__main__":
    main()
