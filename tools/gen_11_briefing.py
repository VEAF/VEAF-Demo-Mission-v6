"""Lot 11 : le briefing de la mission, en français et en anglais (VMCT `build_mission_briefing`).

L'action lit tout dans la mission construite (date, météo, routes, presets, cibles de chaque zone) et écrit
le deck (docs/briefing.pptx, .pdf), les cartes du briefing DCS et les pages de la planchette
(`KNEEBOARD/IMAGES/0N-briefing-*.jpg`, étape `kneeboard-briefing` de la visite).
On ne lui passe que les mots du scénario : un appel par langue, chacun n'écrit que les .miz de sa langue.

Le paramètre `language` attend VMCT FEAT-BRIEFING-PER-LANGUAGE (VEAF/VEAF-Mission-Creation-Tools#1191) :
avant lui, l'action écrit le français dans tous les .miz, `_EN` compris, et ce lot ne doit pas être lancé.
À relancer après chaque build (`build_candidate.py` le fait), jamais avant : l'action lit le .miz construit.
Pas de portée pour les menaces : l'action n'en dessine qu'avec leur source, et nous n'en avons pas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import Batch  # noqa: E402

THREATS = {
    "fr": [
        {"name": "SA-6 d'Ochamchire", "group": "combatZone_Ochamchire_SAM-sa6", "family": "SA-6"},
        {"name": "SAM courte portée de Gali", "group": "combatZone_Gali-sam", "family": "SAM courte portée"},
        {"name": "SA-11 de Gudauta", "group": "IADS Gudauta - SA-11", "family": "SA-11"},
        {"name": "SA-15 de Gudauta", "group": "IADS Gudauta - SA-15", "family": "SA-15"},
    ],
    "en": [
        {"name": "Ochamchire SA-6", "group": "combatZone_Ochamchire_SAM-sa6", "family": "SA-6"},
        {"name": "Gali short-range SAM", "group": "combatZone_Gali-sam", "family": "short-range SAM"},
        {"name": "Gudauta SA-11", "group": "IADS Gudauta - SA-11", "family": "SA-11"},
        {"name": "Gudauta SA-15", "group": "IADS Gudauta - SA-15", "family": "SA-15"},
    ],
}

WORDS = {
    "fr": dict(
        title="Démo VEAF : opérations en Abkhazie",
        context=[
            "Les forces rouges tiennent la rive nord de l'Inguri et défendent Ochamchire et Tkvarcheli.",
            "Ce briefing est un exemple : chaque objectif s'active depuis F10 > Autre > VEAF > ZONES DE COMBAT.",
        ],
        mission_bullets=[
            "Détruire les blindés et l'artillerie du front de Gali",
            "Neutraliser la batterie SA-6 d'Ochamchire",
            "Détruire le radar d'alerte de Tkvarcheli",
        ],
        objectives=[
            {"zone": "combatZone_Gali", "title": "Front de Gali",
             "task": ["Détruire les blindés et la batterie d'artillerie Msta.",
                      "Le drone Reaper 1 (JTAC, code 1511, 35.55 FM) orbite au-dessus."]},
            {"zone": "combatZone_Ochamchire_SAM", "title": "SAM d'Ochamchire",
             "task": ["Neutraliser la batterie SA-6 : elle n'allume son radar que quand le réseau Skynet rouge le lui demande."]},
            {"zone": "combatZone_Tkvarcheli_Radar", "title": "Tkvarcheli - radar",
             "task": ["Détruire le radar d'alerte 1L13 et sa DCA."]},
        ],
        air_opposition=["QRA de Soukhoumi : un MiG-29S ou un Su-27 décolle quand un avion bleu entre dans sa zone ; à partir de trois, deux appareils parmi Su-30, MiG-31 et MiG-29S."],
    ),
    "en": dict(
        title="VEAF demo: operations in Abkhazia",
        context=[
            "Red forces hold the north bank of the Inguri and defend Ochamchire and Tkvarcheli.",
            "This briefing is an example: each objective is activated from F10 > Other > VEAF > COMBAT ZONES.",
        ],
        mission_bullets=[
            "Destroy the armour and artillery of the Gali front",
            "Neutralise the Ochamchire SA-6 battery",
            "Destroy the Tkvarcheli early-warning radar",
        ],
        objectives=[
            {"zone": "combatZone_Gali", "title": "Gali front",
             "task": ["Destroy the armour and the Msta artillery battery.",
                      "The Reaper 1 drone (JTAC, code 1511, 35.55 FM) orbits above."]},
            {"zone": "combatZone_Ochamchire_SAM", "title": "Ochamchire SAM",
             "task": ["Neutralise the SA-6 battery: it lights its radar only when the red Skynet network tells it to."]},
            {"zone": "combatZone_Tkvarcheli_Radar", "title": "Tkvarcheli - radar",
             "task": ["Destroy the 1L13 early-warning radar and its AAA."]},
        ],
        air_opposition=["Sukhumi QRA: a MiG-29S or a Su-27 takes off when a blue aircraft enters its zone; from three, two among Su-30, MiG-31 and MiG-29S."],
    ),
}

b = Batch()
for lang in ("fr", "en"):  # le français d'abord : la langue de la mission, celle qui écrit le dossier
    b.act("build_mission_briefing", language=lang, side="blue", basemap="osm", kneeboard=True,
          threats=THREATS[lang], **WORDS[lang])
b.save("11-briefing.json")
