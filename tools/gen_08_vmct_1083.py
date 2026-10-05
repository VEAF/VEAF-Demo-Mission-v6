"""Lot 08 : retrait des contournements que VMCT #1083 (FIX-DEMO-MISSION-FINDINGS) rend inutiles.

- Navires d'Ochamchire : le porteur `#command="-cargoships"` revient (ticket 05 corrigé dans VMCT, à vérifier
  en jeu) à la place des deux cargos natifs du lot 06.
Les autres retraits sont dans mission.yaml (action `lua` du pilote CSAR, ticket 01), mission-script.lua et
la visite (activation de l'opération par son propre menu, ticket 06).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import RED, Batch, cmd_unit, xy  # noqa: E402

b = Batch()
N = (-238000, 585000)
for i in (1, 2):
    b.act("remove_group", group_name=f"combatZone_Ochamchire_Ships-cargo-{i}")
b.act("add_group", **RED, category="ship", name="cargoships", for_combat_zone="combatZone_Ochamchire_Ships",
      position=xy(N), units=[cmd_unit("-cargoships", "Dry-cargo ship-1", "OchN-1")], keep_position=True)
b.save("08-vmct-1083.json")
