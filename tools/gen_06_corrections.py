"""Lot 06 : corrections issues du premier passage en jeu (2026-10-05, mission de test + dcs-bridge).

- Khoni facile, cibles 03 et 04 : posées dans l'eau (land.getSurfaceType = 3, mesuré par le pont) ; VEAF les
  replaçait au hasard à chaque activation. Déplacées sur des points mesurés terre ferme, à plus de 150 m
  des autres cibles.
- Navires d'Ochamchire : le porteur `#command="-cargoships"` ne crée rien — l'alias seul, hors zone, ne crée
  rien non plus et ne dit rien (docs/retours-vmct.md). Remplacé par deux cargos natifs, espacés de 400 m.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import RED, Batch, off, xy  # noqa: E402

b = Batch()
b.act("set_group_properties", group_name="combatZone_Khoni_Easy-cible-03", move_to=xy((-265294.7, 665351.2)))
b.act("set_group_properties", group_name="combatZone_Khoni_Easy-cible-04", move_to=xy((-265600.9, 665520.8)))

N = (-238000, 585000)
b.act("remove_group", group_name="combatZone_Ochamchire_Navires-cargos")
for i, (typ, brg) in enumerate((("Dry-cargo ship-1", 270), ("Dry-cargo ship-2", 0)), 1):
    b.act("add_group", **RED, category="ship", name=f"cargo-{i}", for_combat_zone="combatZone_Ochamchire_Navires",
          position=xy(off(N, brg, 400)), units=[{"type": typ}], keep_position=True)
b.save("06-corrections.json")
