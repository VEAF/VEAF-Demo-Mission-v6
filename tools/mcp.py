"""Call veaf-mission-mcp actions in-process on the VMCT develop checkout.

python mcp.py describe <action>
python mcp.py list
python mcp.py run <action> '<json params>' [--full]
python mcp.py batch file.json [--full]
"""
import json, sys, subprocess

from paths import VMCT  # noqa: E402  (met aussi le code VMCT sur sys.path)

br = subprocess.run(["git", "-C", VMCT, "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
if br != "develop":
    sys.exit(f"VMCT checkout is on '{br}', not develop: refusing")
from veaf_mission_mcp.actions import register_default_actions
from veaf_mission_mcp.catalog import ActionCatalog
cat = ActionCatalog(); register_default_actions(cat)
full = "--full" in sys.argv
args = [a for a in sys.argv[1:] if a != "--full"]
def show(name, res):
    if not full and isinstance(res, dict):
        res = {k: v for k, v in res.items() if k not in ("route", "units", "groups")}
    txt = json.dumps(res, ensure_ascii=False, default=str, indent=None if not full else 1)
    print(f"{name}: {txt if full else txt[:1500]}")
cmd = args[0]
if cmd == "list":
    for s in cat.list_catalog(): print(s.name, "-", s.description[:110])
elif cmd == "describe":
    print(json.dumps(cat.describe_action(args[1]).model_dump(), ensure_ascii=False, indent=1))
elif cmd == "run":
    show(args[1], cat.run_action(args[1], json.loads(args[2]) if len(args) > 2 else {}))
elif cmd == "batch":
    for i, it in enumerate(json.load(open(args[1], encoding="utf-8")), 1):
        try:
            show(f"[{i}] {it['name']}", cat.run_action(it["name"], it.get("params", {})))
        except Exception as e:
            print(f"[{i}] {it['name']} FAILED: {e!r}"); sys.exit(1)
