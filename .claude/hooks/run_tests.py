"""PostToolUse hook: run the tests after Claude edits a Python file.

Claude Code sends details of the tool call as JSON on stdin. If the tests
fail, we reply with a JSON "block" decision, which makes Claude Code show the
reason (the failing test output) to Claude.
"""

import json
import subprocess
import sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "-x", "--no-header"],
    capture_output=True,
    text=True,
    check=False,
)
if result.returncode != 0:
    reason = "Tests are failing after this edit:\n\n" + result.stdout[-3000:]
    print(json.dumps({"decision": "block", "reason": reason}))
