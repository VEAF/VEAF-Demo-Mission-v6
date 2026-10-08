"""Lot 09 : l'embuscade du convoi sous le feu (VMCT FEAT-CONVOY-UNDER-FIRE, #1099).

Une route à l'est de Kutaisi, relevée en jeu le 2026-10-08 (`land.findPathOnRoads`) : le joueur lance
`-convoy, dest EMBUSCADE` à son départ (zone « Embuscade »), et la route passe à 400 m de trois blindés
rouges. C'est là que VMCT les a mesurés : un convoi DCS livré à lui-même y meurt sans tirer.
Le point nommé EMBUSCADE, au bout de la route, est dans mission.yaml (NAMEDPOINTS).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import RED, Batch, xy  # noqa: E402

DEPART = (-283715.0, 705205.0)  # le point 16 de la route relevée, 2,8 km avant l'embuscade
EMBUSCADE = (-282289.0, 707791.0)  # 400 m au nord du point 32 de la route

b = Batch()
b.act("add_trigger_zone", name="Embuscade", position=xy(DEPART), radius=300)
b.act("add_group", **RED, category="vehicle", name="Embuscade-blindes", position=xy(EMBUSCADE), keep_position=True,
      units=[{"type": "BMP-2", "count": 2}, {"type": "BTR-80", "count": 1}])
b.save("09-embuscade.json")
