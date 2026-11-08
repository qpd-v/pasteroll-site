#!/usr/bin/env python3
"""Build the static site, including the reviewed release changelog.

Release summaries live in site/releases.json. Internal commits are not
published as changelog entries.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

def main():
    keep = '--keep-on-error' in sys.argv[1:]
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_site.py')], cwd=ROOT)
    if result.returncode and keep:
        print('Site build failed; keeping the committed pages.', file=sys.stderr)
        return 0
    return result.returncode

if __name__ == '__main__':
    raise SystemExit(main())
