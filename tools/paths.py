"""Où sont le dossier de mission et le code Python de VMCT, pour tous les scripts de tools/.

Le chemin du checkout VMCT était écrit en dur dans chaque script (`D:/dev/_VEAF/VMCT-develop`),
qui n'existe plus : il est maintenant lu ici, une seule fois, et se règle par la variable
d'environnement VMCT_PY quand le checkout est ailleurs.
"""
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
VMCT_PY = Path(os.environ.get("VMCT_PY", ROOT.parent / "VEAF-Mission-Creation-Tools" / "src" / "python" / "veaf-tools"))

VMCT = VMCT_PY.parent.parent.parent   # racine du checkout (scripts Lua, données)

if not VMCT_PY.is_dir():
    raise SystemExit(f"[tools] code VMCT introuvable : {VMCT_PY}\n"
                     f"        indiquez-le avec la variable d'environnement VMCT_PY")
if str(VMCT_PY) not in sys.path:
    sys.path.insert(0, str(VMCT_PY))
