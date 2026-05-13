"""
Parse flutter analyze output for errors and warnings.
"""
import subprocess
import re
import sys

# Run flutter analyze with no-fatal-infos
result = subprocess.run(
    ["flutter", "analyze", "--no-fatal-infos"],
    cwd=r"x:\BMJ\lush",
    capture_output=True,
    text=True,
    timeout=120
)

output = result.stdout + result.stderr

# Find the summary line
summary_match = re.search(r'(\d+) issues found', output)
if summary_match:
    total = int(summary_match.group(1))
    print(f"Total issues: {total}")
else:
    print("No summary found")
    total = 0

# Find errors
errors = re.findall(r'^  error - (.+)', output, re.MULTILINE)
warnings = re.findall(r'^  warning - (.+)', output, re.MULTILINE)
infos = re.findall(r'^  info - (.+)', output, re.MULTILINE)

print(f"\nErrors: {len(errors)}")
for e in errors:
    print(f"  ❌ {e}")

print(f"\nWarnings: {len(warnings)}")
for w in warnings:
    print(f"  ⚠️ {w}")

print(f"\nInfos: {len(infos)}")

if len(errors) == 0 and len(warnings) == 0:
    print("\n✅ No errors or warnings! Only info-level hints remain.")
    sys.exit(0)
else:
    sys.exit(1)
