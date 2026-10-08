"""Lot 05 : dessins F10, sur la couche Blue (le seul camp jouable), mêmes données que la carte.

Chaque lieu porte son contour au rayon réel ET son étiquette, numérotée comme l'étape de la visite.
Étiquettes sur fond blanc presque opaque : sans `fill_color`, l'action pose un fond noir à 50 % et le
texte devient illisible sur la carte F10 (retour en vol sur l'Open Training Caucase, 29/09/2026).

Ce lot REMPLACE les dessins précédents : il retire d'abord ceux qui sont dans la mission (lus dans la
mission, jamais déduits), un nom ne pouvant pas servir deux fois.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import dcslua  # noqa: E402
from i18n_texts import drawing_labels  # noqa: E402
from lib import ROOT, Batch, xy  # noqa: E402

b = Batch()
MIS = dcslua.load(ROOT / "src/mission/mission")
GROUPS, ZONES = dcslua.positions(MIS)
CFG = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
STEPS = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))["steps"]
NUM = {}   # zone -> numéro de la PREMIÈRE étape qui y mène (02 et 03 partagent le bac à sable)
for i, s in enumerate(STEPS, 1):
    if s.get("anchor", {}).get("zone"):
        NUM.setdefault(s["anchor"]["zone"], i)
# textes en français : la mission de src/mission/ est la base FR ; tools/localize_miz.py pose l'anglais
LABELS = drawing_labels("fr", NUM)

RED_C, GREEN_C, PURPLE_C, ORANGE_C, TEAL_C = "0xc2362bff", "0x2e7f38ff", "0x6a3d9aff", "0xd9822bff", "0x0b86a8ff"
RED_F, GREEN_F, PURPLE_F = "0xc2362b20", "0x2e7f3820", "0x6a3d9a20"
LABEL_BG = "0xffffffe6"

for layer in dcslua.seq(MIS["drawings"]["layers"]):
    for o in dcslua.seq(layer.get("objects", {})):
        b.act("edit_map_drawing", layer=layer["name"], name=o["name"], remove=True)


def zone(zone_name, color, fill):
    x, y, r = ZONES[zone_name]
    b.act("add_map_drawing", layer="Blue", shape="circle", name=f"Cercle {zone_name}", position=xy((x, y)),
          radius=r, color=color, fill_color=fill, thickness=4)
    # au nord du cercle (x = nord dans le repère DCS)
    b.act("add_map_drawing", layer="Blue", shape="textbox", name=f"Étiquette {zone_name}", position=xy((x + r, y)),
          text=LABELS[f"Étiquette {zone_name}"], color=color, fill_color=LABEL_BG, font_size=14)


for z in CFG["modules"]["COMBATZONE"]["combat_zones"]:
    if z.get("type") == "operation" or z["zone_name"].endswith(("_Medium", "_Hard")) or "_Tkvarcheli_" in z["zone_name"]:
        continue
    training = z.get("training")
    zone(z["zone_name"], GREEN_C if training else RED_C, GREEN_F if training else RED_F)
zone("Op_Tkvarcheli", RED_C, "0x00000000")
zone("QRA-Soukhoumi", RED_C, "0x00000000")
zone("Sanctuaire Gudauta", RED_C, RED_F)
zone("Bac a sable", PURPLE_C, PURPLE_F)
zone("Demo CSAR", PURPLE_C, PURPLE_F)
zone("Embuscade", PURPLE_C, PURPLE_F)
# l'arène AIRWAVES se dessine elle-même en jeu (draw_zone: true) ; on n'ajoute que son étiquette
x, y, r = ZONES["Arene BVR"]
b.act("add_map_drawing", layer="Blue", shape="textbox", name="Étiquette Arene BVR", position=xy((x + r, y)),
      text=LABELS["Étiquette Arene BVR"], color=ORANGE_C, fill_color=LABEL_BG, font_size=14)

# hippodromes de soutien
for n in ("Texaco 1", "Arco 1", "Overlord 1"):
    for _, _, _, g in dcslua.groups(MIS):
        if g["name"] == n:
            pts = [(p["x"], p["y"]) for p in dcslua.seq(g["route"]["points"])][:2]
            break
    else:
        raise SystemExit(f"groupe de soutien introuvable : {n}")
    b.act("add_map_drawing", layer="Blue", shape="line", name=f"Hippodrome {n}", points=[xy(p) for p in pts],
          color=TEAL_C, thickness=6)
    b.act("add_map_drawing", layer="Blue", shape="textbox", name=f"Étiquette {n}", position=xy(pts[1]),
          text=n, color=TEAL_C, fill_color=LABEL_BG, font_size=14)

b.save("05-dessins.json")
