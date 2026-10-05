"""Lot 04 : bullseye, date, briefing (français puis anglais)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BULLSEYE, Batch, xy  # noqa: E402

b = Batch()
for side in ("blue", "red"):
    b.act("set_bullseye", coalition=side, position=xy(BULLSEYE))
b.act("set_mission_date", date="2024-06-15", start_time="09:00")

SITUATION = """MISSION DE DÉMO VEAF — VISITE GUIDÉE

Cette mission montre chaque fonctionnalité des outils VEAF (VEAF Mission Creation Tools v6), avec un exemple par fonctionnalité.
Ouvrez le menu F10 > Autre > VEAF > VISITE GUIDÉE : un chapitre, puis une étape ; chaque étape dit où aller, quoi faire et ce qu'on doit voir, et pose un repère sur votre carte F10.

Le front suit l'Inguri, entre la Géorgie (bleue) et l'Abkhazie (rouge). Bullseye commun : Zugdidi.
Base mère : Kutaisi (slots classiques moteur chaud). Slots dynamiques sur Kutaisi, Senaki, Kobuleti et Batumi en multijoueur. Porte-avions Stennis et Roosevelt au large de Batumi.
La sécurité VEAF est désactivée : toutes les commandes sont ouvertes à tous.

Guide détaillé : https://github.com/VEAF/VEAF-Demo-Mission-v6

— — —

VEAF DEMO MISSION — GUIDED TOUR

This mission shows every feature of the VEAF tools (VEAF Mission Creation Tools v6), one example per feature.
Open F10 > Other > VEAF > GUIDED TOUR: a chapter, then a step; each step tells where to go, what to do and what you should see, and places a mark on your F10 map.

The front follows the Inguri river, between Georgia (blue) and Abkhazia (red). Shared bullseye: Zugdidi.
Home base: Kutaisi (classic hot-start slots). Dynamic slots on Kutaisi, Senaki, Kobuleti and Batumi in multiplayer. Stennis and Roosevelt carriers off Batumi.
VEAF security is disabled: every command is open to everyone.

Detailed guide: https://github.com/VEAF/VEAF-Demo-Mission-v6"""

BLUE_TASK = """Suivre la visite guidée (F10 > Autre > VEAF > VISITE GUIDÉE), dans l'ordre ou non.

Soutien : Texaco 1 (KC-135 perche) 292.0 AM, TACAN 52Y, FL200 — Arco 1 (KC-135 MPRS panier) 291.0 AM, TACAN 51Y, FL180 — Overlord 1 (E-3A) 286.0 AM — Reaper 1 (JTAC laser 1511) 35.55 FM.
Porte-avions : Stennis 274.0 AM, TACAN 74X, ICLS 4 — Roosevelt 271.0 AM, TACAN 71X, ICLS 1. FARP Khoni 127.5 AM.

— — —

Follow the guided tour (F10 > Other > VEAF > GUIDED TOUR), in order or not.

Support: Texaco 1 (KC-135 boom) 292.0 AM, TACAN 52Y, FL200 — Arco 1 (KC-135 MPRS drogue) 291.0 AM, TACAN 51Y, FL180 — Overlord 1 (E-3A) 286.0 AM — Reaper 1 (JTAC laser 1511) 35.55 FM.
Carriers: Stennis 274.0 AM, TACAN 74X, ICLS 4 — Roosevelt 271.0 AM, TACAN 71X, ICLS 1. FARP Khoni 127.5 AM."""

RED_TASK = "Le camp rouge n'est pas jouable dans cette mission. / The red side is not playable in this mission."

b.act("set_briefing", sortie="VEAF - Mission de démo / Demo mission", situation=SITUATION, blue_task=BLUE_TASK, red_task=RED_TASK)
b.save("04-identite.json")
