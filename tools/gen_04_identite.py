"""Lot 04 : bullseye, date, briefing (en français ; l'anglais est posé par tools/localize_miz.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from i18n_texts import BRIEFING  # noqa: E402
from lib import BULLSEYE, Batch, xy  # noqa: E402

b = Batch()
for side in ("blue", "red"):
    b.act("set_bullseye", coalition=side, position=xy(BULLSEYE))
b.act("set_mission_date", date="2024-06-15", start_time="09:00")

# Briefing en français : la mission de src/mission/ est la base FR ; tools/localize_miz.py pose l'anglais.
B = BRIEFING["fr"]
b.act("set_briefing", sortie=B["sortie"], situation=B["situation"], blue_task=B["blue"], red_task=B["red"])
b.save("04-identite.json")
