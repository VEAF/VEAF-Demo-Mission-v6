"""Le lot 11 (briefing de la mission, tools/gen_11_briefing.py) : peut-on le lancer avec ce VMCT ?

Commun à tools/build_candidate.py et tools/release.py, qui le lancent après le build et localize_miz.py.
Le lot passe `language` à build_mission_briefing (VMCT FEAT-BRIEFING-PER-LANGUAGE) : sans ce paramètre,
l'action mettrait du français dans les .miz _EN, donc on ne le lance pas.
tools/mcp.py appelle le code du checkout VMCT (tools/paths.py), pas celui de veaf-tools.exe.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ["tools/mcp.py", "batch", "tools/batches/11-briefing.json"]


def supported():
    """Vrai si build_mission_briefing a `language` ; s'arrête si tools/mcp.py ne lit pas l'action."""
    schema = subprocess.run([sys.executable, "tools/mcp.py", "describe", "build_mission_briefing"], cwd=ROOT,
                            capture_output=True, text=True)
    if schema.returncode:
        sys.exit(f"tools/mcp.py ne lit pas build_mission_briefing (venv VMCT à jour ? poetry install) :\n"
                 f"{schema.stderr.strip().splitlines()[-1:]}")
    if '"language"' in schema.stdout:
        return True
    print("briefing sauté : build_mission_briefing n'a pas encore `language` (VMCT FEAT-BRIEFING-PER-LANGUAGE)")
    return False
