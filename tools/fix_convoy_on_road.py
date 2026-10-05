"""Met les points de route du convoi en « On Road » : le convoi suit la route entre Ochamchire et Gali.

Aucune action MCP ne le fait (edit_route ne propose pas « On Road », voir docs/retours-vmct.md) :
charge la mission du dossier avec le lecteur de VMCT, modifie la table, réécrit avec
save_folder_mission (qui sauvegarde avant d'écrire). Idempotent.
"""
from pathlib import Path

import paths  # noqa: F401
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NAME = "combatZone_Convoy-column"
mis = load_folder_mission(ROOT)
found = 0
for side in mis.mission_content["coalition"].values():
    countries = side.get("country") or {}
    for c in (countries.values() if isinstance(countries, dict) else countries):
        groups = ((c.get("vehicle") or {}).get("group")) or {}
        for g in (groups.values() if isinstance(groups, dict) else groups):
            if g["name"] == NAME:
                pts = g["route"]["points"]
                for p in (pts.values() if isinstance(pts, dict) else pts):
                    p["type"], p["action"] = "Turning Point", "On Road"
                    found += 1
assert found >= 2, f"{NAME} : {found} point(s)"
print(found, "points en On Road ;", save_folder_mission(mis, ROOT).get("backups"))
