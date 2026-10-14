import sys

from kettle.pipeline import run

if len(sys.argv) != 2:
    print("Usage: uv run python -m kettle YYYY-MM-DD")
    sys.exit(1)

run(sys.argv[1])
