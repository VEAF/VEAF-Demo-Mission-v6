"""Textes de la mission DCS elle-même (src/mission/), en français et en anglais.

src/mission/ est commun aux deux builds et porte le français : gen_04 (briefing), gen_05 (dessins F10)
et gen_map (cartes) y écrivent la version `fr`. tools/localize_miz.py réécrit la version `en` dans les
.miz anglais après le build. Les textes de mission.yaml, eux, sont dans i18n/en.yaml (tools/gen_i18n.py).
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/VEAF/VEAF-Demo-Mission-v6"

BRIEFING = {
    "fr": {
        "sortie": "VEAF - Mission de démo",
        "situation": f"""MISSION DE DÉMO VEAF — VISITE GUIDÉE

Cette mission montre chaque fonctionnalité des outils VEAF (VEAF Mission Creation Tools v6), avec un exemple par fonctionnalité.
Ouvrez le menu F10 > Autre > Visite guidée : un chapitre, puis une étape ; chaque étape dit où aller, quoi faire et ce qu'on doit voir, et pose un repère sur votre carte F10.

Le front suit l'Inguri, entre la Géorgie (bleue) et l'Abkhazie (rouge). Bullseye commun : Zugdidi.
Base mère : Kutaisi (slots classiques moteur chaud). Slots dynamiques sur Kutaisi, Senaki, Kobuleti et Batumi en multijoueur. Porte-avions Stennis et Roosevelt au large de Batumi.
La sécurité VEAF est désactivée : toutes les commandes sont ouvertes à tous.

Guide détaillé : {REPO}""",
        "blue": """Suivre la visite guidée (F10 > Autre > Visite guidée), dans l'ordre ou non.

Soutien : Texaco 1 (KC-135 perche) 292.0 AM, TACAN 52Y, FL200 — Arco 1 (KC-135 MPRS panier) 291.0 AM, TACAN 51Y, FL180 — Overlord 1 (E-3A) 286.0 AM — Reaper 1 (JTAC laser 1511) 35.55 FM.
Porte-avions : Stennis 274.0 AM, TACAN 74X, ICLS 4 — Roosevelt 271.0 AM, TACAN 71X, ICLS 1. FARP Khoni 127.5 AM.""",
        "red": "Le camp rouge n'est pas jouable dans cette mission.",
    },
    "en": {
        "sortie": "VEAF - Demo mission",
        "situation": f"""VEAF DEMO MISSION — GUIDED TOUR

This mission shows every feature of the VEAF tools (VEAF Mission Creation Tools v6), one example per feature.
Open F10 > Other > Guided tour: a chapter, then a step; each step tells where to go, what to do and what you should see, and places a mark on your F10 map.

The front follows the Inguri river, between Georgia (blue) and Abkhazia (red). Shared bullseye: Zugdidi.
Home base: Kutaisi (classic hot-start slots). Dynamic slots on Kutaisi, Senaki, Kobuleti and Batumi in multiplayer. Stennis and Roosevelt carriers off Batumi.
VEAF security is disabled: every command is open to everyone.

Detailed guide: {REPO}""",
        "blue": """Follow the guided tour (F10 > Other > Guided tour), in order or not.

Support: Texaco 1 (KC-135 boom) 292.0 AM, TACAN 52Y, FL200 — Arco 1 (KC-135 MPRS drogue) 291.0 AM, TACAN 51Y, FL180 — Overlord 1 (E-3A) 286.0 AM — Reaper 1 (JTAC laser 1511) 35.55 FM.
Carriers: Stennis 274.0 AM, TACAN 74X, ICLS 4 — Roosevelt 271.0 AM, TACAN 71X, ICLS 1. FARP Khoni 127.5 AM.""",
        "red": "The red side is not playable in this mission.",
    },
}

# Étiquettes fixes des dessins F10 et des cartes (les noms de zones de combat viennent de mission.yaml
# en français et d'i18n/en.yaml en anglais).
FIXED = {
    "fr": {"Op_Tkvarcheli": "Opération Tkvarcheli (3 tâches)", "QRA-Soukhoumi": "QRA Sukhumi",
           "Sanctuaire Gudauta": "Sanctuaire rouge de Gudauta", "Bac a sable": "Bac à sable (point ALPHA)",
           "Demo CSAR": "Pilote abattu (CSAR, menu Démo : commandes)", "Arene BVR": "Arène BVR (vagues aériennes)",
           "Embuscade": "Convoi sous le feu (départ : -convoy, dest EMBUSCADE, side blue)",
           "training_suffix": " (entraînement, 3 niveaux)"},
    "en": {"Op_Tkvarcheli": "Operation Tkvarcheli (3 tasks)", "QRA-Soukhoumi": "QRA Sukhumi",
           "Sanctuaire Gudauta": "Gudauta red sanctuary", "Bac a sable": "Sandbox (point ALPHA)",
           "Demo CSAR": "Downed pilot (CSAR, Demo: commands menu)", "Arene BVR": "BVR arena (air waves)",
           "Embuscade": "Convoy under fire (start: -convoy, dest EMBUSCADE, side blue)",
           "training_suffix": " (training, 3 levels)"},
}

MAP = {
    "fr": {"titles": {"carte": "Mission de démo VEAF — Caucase",
                      "01-kutaisi-khoni": "Kutaisi et Khoni : bac à sable, entraînement, FARP, CSAR, embuscade",
                      "02-front": "Front : Gali, Ochamchire, Tkvarcheli, convoi",
                      "03-mer": "Mer : arène BVR, porte-avions, Arco 1",
                      "04-abkhazie": "Soukhoumi et Gudauta : IADS, QRA, sanctuaire"},
           "legend": ["zone d'entraînement", "zone de combat", "ravitailleur / AWACS", "arène BVR", "étape de la visite (n°)"],
           "sanctuary": "Sanctuaire", "arena": "Arène BVR", "levels": " (3 niveaux)", "easy": " - facile",
           "operation": "Opération Tkvarcheli (3 tâches)", "sandbox": "Bac à sable (ALPHA)", "csar": "Pilote abattu (CSAR)",
           "ambush": "Convoi sous le feu (départ)"},
    "en": {"titles": {"carte": "VEAF demo mission — Caucasus",
                      "01-kutaisi-khoni": "Kutaisi and Khoni: sandbox, training, FARP, CSAR, ambush",
                      "02-front": "Front: Gali, Ochamchire, Tkvarcheli, convoy",
                      "03-mer": "Sea: BVR arena, carriers, Arco 1",
                      "04-abkhazie": "Sukhumi and Gudauta: IADS, QRA, sanctuary"},
           "legend": ["training zone", "combat zone", "tanker / AWACS", "BVR arena", "guided tour step (no.)"],
           "sanctuary": "Sanctuary", "arena": "BVR arena", "levels": " (3 levels)", "easy": " - easy",
           "operation": "Operation Tkvarcheli (3 tasks)", "sandbox": "Sandbox (ALPHA)", "csar": "Downed pilot (CSAR)",
           "ambush": "Convoy under fire (start)"},
}


def zone_names(lang):
    """friendly_name de chaque zone de combat dans la langue demandée."""
    cfg = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
    zones = cfg["modules"]["COMBATZONE"]["combat_zones"]
    if lang == "fr":
        return {z["zone_name"]: z["friendly_name"] for z in zones}
    en = yaml.safe_load((ROOT / "i18n/en.yaml").read_text(encoding="utf-8"))["combat_zones"]
    return {z["zone_name"]: en[z["zone_name"]]["friendly_name"] for z in zones}


def drawing_labels(lang, numbers):
    """Texte de chaque étiquette F10, par nom de dessin (le nom ne change pas d'une langue à l'autre).

    numbers : nom de zone -> numéro de l'étape de la visite qui y mène.
    """
    names, fixed = zone_names(lang), FIXED[lang]
    cfg = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
    out = {}

    def lab(zone, title):
        n = numbers.get(zone)
        out[f"Étiquette {zone}"] = f"{n}. {title}" if n else title

    for z in cfg["modules"]["COMBATZONE"]["combat_zones"]:
        zn = z["zone_name"]
        if z.get("type") == "operation" or zn.endswith(("_Medium", "_Hard")) or "_Tkvarcheli_" in zn:
            continue
        title = names[zn]
        if z.get("training"):
            title = title.rsplit(" - ", 1)[0] + fixed["training_suffix"]
        lab(zn, title)
    for zn in ("Op_Tkvarcheli", "QRA-Soukhoumi", "Sanctuaire Gudauta", "Bac a sable", "Demo CSAR", "Embuscade", "Arene BVR"):
        lab(zn, fixed[zn])
    for n in ("Texaco 1", "Arco 1", "Overlord 1"):
        out[f"Étiquette {n}"] = n
    return out
