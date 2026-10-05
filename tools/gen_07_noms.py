"""Lot 07 : noms neutres (anglais technique) pour tout ce que la carte F10 montre aux joueurs.

La mission se construit en deux langues (profils FR et EN de mission.yaml) mais src/mission/ est
commun aux deux : un nom de groupe ou de zone de combat y apparaît tel quel dans les deux builds (les
groupes générés s'appellent `<zone> [r] <groupe>#<id>`, lisibles puisque hide_names_from_spawned_groups
est à false). Ils deviennent donc des identifiants anglais, que les textes traduits n'ont pas à porter.

Les trigger zones que les joueurs ne voient jamais (Bac a sable, Sanctuaire Gudauta, Arene BVR…) gardent
leur nom : ce sont des identifiants de configuration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import Batch  # noqa: E402

b = Batch()

# zones de combat renommées : (ancien, nouveau) — les groupes qu'elles capturent suivent leur préfixe
ZONES = [("combatZone_Convoi", "combatZone_Convoy"), ("combatZone_Ochamchire_Navires", "combatZone_Ochamchire_Ships"),
         ("combatZone_Tkvarcheli_PC", "combatZone_Tkvarcheli_HQ")]
for old, new in ZONES:
    b.act("edit_zone", zone_name=old, new_name=new)

GROUPS = [(f"combatZone_Khoni_Easy-cible-{i:02d}", f"combatZone_Khoni_Easy-target-{i:02d}") for i in range(1, 9)] + [
    ("combatZone_Khoni_Medium-blindes", "combatZone_Khoni_Medium-armor"),
    ("combatZone_Khoni_Hard-bataillon", "combatZone_Khoni_Hard-battalion"),
    ("combatZone_Gali-blindes-a", "combatZone_Gali-armor-a"),
    ("combatZone_Gali-blindes-b", "combatZone_Gali-armor-b"),
    ("combatZone_Gali-artillerie", "combatZone_Gali-artillery"),
    ("combatZone_Gali-dca", "combatZone_Gali-sam"),
    ("combatZone_Gali-guetteurs", "combatZone_Gali-spotters"),
    ("combatZone_Ochamchire_Port-camions", "combatZone_Ochamchire_Port-trucks"),
    ("combatZone_Ochamchire_Port-dca", "combatZone_Ochamchire_Port-aaa"),
    ("combatZone_Tkvarcheli_PC-garde", "combatZone_Tkvarcheli_HQ-guard"),
    ("combatZone_Tkvarcheli_PC-pc", "combatZone_Tkvarcheli_HQ-hq"),
    ("combatZone_Tkvarcheli_PC-bunker", "combatZone_Tkvarcheli_HQ-bunker"),
    ("combatZone_Tkvarcheli_Depot-munitions", "combatZone_Tkvarcheli_Depot-ammo"),
    ("combatZone_Tkvarcheli_Depot-carburant-1", "combatZone_Tkvarcheli_Depot-fuel-1"),
    ("combatZone_Tkvarcheli_Depot-carburant-2", "combatZone_Tkvarcheli_Depot-fuel-2"),
    ("combatZone_Convoi-colonne", "combatZone_Convoy-column"),
    ("combatZone_Ochamchire_Navires-escorte", "combatZone_Ochamchire_Ships-escort"),
    ("combatZone_Ochamchire_Navires-cargo-1", "combatZone_Ochamchire_Ships-cargo-1"),
    ("combatZone_Ochamchire_Navires-cargo-2", "combatZone_Ochamchire_Ships-cargo-2"),
    ("QRA Soukhoumi - MiG-29S", "QRA Sukhumi - MiG-29S"),
    ("QRA Soukhoumi - Su-27", "QRA Sukhumi - Su-27"),
    ("QRA Soukhoumi - Su-30", "QRA Sukhumi - Su-30"),
    ("QRA Soukhoumi - MiG-31", "QRA Sukhumi - MiG-31"),
    ("OnDemand-CAP Su-27 mer FL300", "OnDemand-CAP Su-27 sea FL300"),
    ("OnDemand-CAP MiG-31 Sotchi FL350", "OnDemand-CAP MiG-31 Sochi FL350"),
    ("Vague MiG-29S", "Wave MiG-29S"),
    ("Vague Su-27", "Wave Su-27"),
    ("Vague Su-30", "Wave Su-30"),
]
for old, new in GROUPS:
    b.act("set_group_properties", group_name=old, new_name=new, acknowledge_conventions=True)
b.save("07-noms.json")

# même table pour les remplacements dans mission.yaml et les outils (tools/rename_refs.py)
RENAMES = ZONES + GROUPS


def unit_batch():
    """Second passage : les unités (et l'objet d'un statique, que la zone capture par son nom) suivent
    le nouveau nom de leur groupe. set_group_properties ne renomme que le groupe."""
    import dcslua
    from lib import ROOT
    old_by_new = {new: old for old, new in GROUPS}
    u = Batch()
    mis = dcslua.load(ROOT / "src/mission/mission")
    for _, _, _, g in dcslua.groups(mis):
        old = old_by_new.get(g["name"])
        if not old:
            continue
        for unit in dcslua.seq(g["units"]):
            if unit["name"].startswith(old):
                u.act("set_unit_properties", group_name=g["name"], unit_name=unit["name"],
                      new_name=g["name"] + unit["name"][len(old):])
    u.save("07b-noms-unites.json")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "units":
    unit_batch()
