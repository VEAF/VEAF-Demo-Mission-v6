"""Génère la visite guidée et sa documentation depuis tour/steps.yaml (source unique).

    python tools/gen_tour.py

Écrit :
  - src/scripts/guided-tour.lua  les menus F10 « Visite guidée » (fr) et « Guided tour » (en) ;
  - README.md, README.en.md     le guide détaillé, une section par étape ;
  - docs/recette.md             la liste de contrôle avant release.

Les positions viennent de la mission (src/mission/mission) : bullseye et base la plus proche sont
calculés, jamais tapés. Dans le jeu, le message d'une étape recalcule la position au moment du
clic, parce que les ravitailleurs et les porte-avions bougent.
"""
import math
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import dcslua  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# Documentation de la dernière version publiée (« latest »), dans la langue du README
DOC = {"fr": "https://veaf.github.io/documentation/latest/", "en": "https://veaf.github.io/documentation/latest/en/"}
VMCT = "https://github.com/VEAF/VEAF-Mission-Creation-Tools"
REPO = "https://github.com/VEAF/VEAF-Demo-Mission-v6"
# .miz publiés en assets de release par tools/release.py ; ce lien suit toujours la dernière release
MIZ = REPO + "/releases/latest/download/VEAF_Demo_Mission_Caucasus_ICAO_UGKO_{lang}_{variant}.miz"
WEATHER = {
    "fr": [("matin-reel", "matin, météo réelle de Kutaisi"), ("matin-degage", "matin, ciel clair"),
           ("aube-epars", "aube, nuages épars"), ("soir-pluie", "soir, pluie"), ("nuit-degage", "nuit, ciel clair")],
    "en": [("matin-reel", "morning, real Kutaisi weather"), ("matin-degage", "morning, clear sky"),
           ("aube-epars", "dawn, scattered clouds"), ("soir-pluie", "evening, rain"), ("nuit-degage", "night, clear sky")],
}
# les .miz _EN portent les noms anglais des variantes (src/versions.en.yaml, tools/gen_i18n.py)
VARIANT_EN = yaml.safe_load((ROOT / "i18n/en.yaml").read_text(encoding="utf-8"))["weather_variants"]


def downloads(lang):
    """Tableau des .miz à télécharger : une ligne par météo, une colonne par langue."""
    head = "| Météo | Français | Anglais |" if lang == "fr" else "| Weather | French | English |"
    rows = [head, "|---|---|---|"]
    for variant, label in WEATHER[lang]:
        en = VARIANT_EN[variant]
        rows.append(f"| {label} | [{variant}_FR.miz]({MIZ.format(lang='FR', variant=variant)}) "
                    f"| [{en}_EN.miz]({MIZ.format(lang='EN', variant=en)}) |")
    return chr(10).join(rows)

data = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))
CHAPTERS, STEPS = data["chapters"], data["steps"]
mission = dcslua.load(ROOT / "src/mission/mission")
GROUPS, ZONES = dcslua.positions(mission)
BULL = (mission["coalition"]["blue"]["bullseye"]["x"], mission["coalition"]["blue"]["bullseye"]["y"])
BASES = {"Kutaisi": (-284582.8, 685029.7), "Senaki-Kolkhi": (-281903.1, 648379.2),
         "Kobuleti": (-317604.9, 636704.2), "Batumi": (-356437.1, 618210.9)}
AIRFIELDS = {**BASES, "Gudauta": (-195650.6, 515898.8), "Sukhumi-Babushara": (-221381.7, 565908.8)}

T = {
    "fr": dict(where="Où", how="À faire", see="Ce qu'on doit voir", modules="Fonctionnalités", doc="Documentation",
               nowhere="Partout (pas de lieu particulier)", base="de", start="au départ de la mission", steps="Étapes"),
    "en": dict(where="Where", how="What to do", see="What you should see", modules="Features", doc="Documentation",
               nowhere="Anywhere (no particular place)", base="from", start="at mission start", steps="Steps"),
}


def anchor_xy(a):
    if not a:
        return None
    if "zone" in a:
        z = ZONES[a["zone"]]
        return z[0], z[1]
    if "group" in a:
        return GROUPS[a["group"]]
    if "airbase" in a:
        return AIRFIELDS[a["airbase"]]
    raise KeyError(a)


def nm(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) / 1852


def bull(p):
    brg = math.degrees(math.atan2(p[1] - BULL[1], p[0] - BULL[0])) % 360
    return f"BULLSEYE {brg:03.0f}/{nm(BULL, p):.0f}"


def where(step, lang):
    p = anchor_xy(step.get("anchor"))
    if not p:
        return T[lang]["nowhere"]
    base = min(BASES, key=lambda b: nm(BASES[b], p))
    moving = "group" in step["anchor"] and step["anchor"]["group"] in ("Texaco 1", "CSG-74 Stennis")
    s = f"{bull(p)} — {nm(BASES[base], p):.0f} nm {T[lang]['base']} {base}"
    return s + (f" ({T[lang]['start']})" if moving else "")


# ── Lua ────────────────────────────────────────────────────────────────────────────────────────
def lua_str(s):
    level = "="
    while f"]{level}]" in s:
        level += "="
    return f"[{level}[{s}]{level}]"


def step_text(step, lang):
    """Texte affiché en jeu : celui du README, sans les backticks qui y marquent les commandes."""
    t = T[lang]
    lines = [step["title"][lang].upper(), "", step["what"][lang], "", t["how"] + " :"]
    lines += [f"- {h}" for h in step["how"][lang]]
    lines += ["", f"{t['see']} : {step['see'][lang]}"]
    return "\n".join(lines).replace("`", "")


def gen_lua():
    out = ["-- guided-tour.lua — GÉNÉRÉ par tools/gen_tour.py depuis tour/steps.yaml : ne pas modifier à la main.",
           "-- Menus F10 « Visite guidée » (fr) et « Guided tour » (en), au premier niveau : un sous-menu par chapitre, une commande",
           "-- par étape. Une commande affiche le texte de l'étape au seul groupe qui la demande, avec la position",
           "-- recalculée au moment du clic, et pose un repère F10 sur le lieu de l'étape.",
           "", "demoTour = demoTour or {}", "demoTour.chapters = {"]
    for key, c in CHAPTERS.items():
        out.append(f'  {{ key = "{key}", fr = {lua_str(c["fr"])}, en = {lua_str(c["en"])} }},')
    out.append("}")
    out.append("demoTour.steps = {")
    for i, s in enumerate(STEPS, 1):
        a = s.get("anchor") or {}
        kind, name = (next(iter(a.items())) if a else ("none", ""))
        out.append(f'  {{ n = {i}, id = "{s["id"]}", chapter = "{s["chapter"]}", anchorKind = "{kind}", anchorName = {lua_str(name)},')
        out.append(f'    title = {{ fr = {lua_str(s["title"]["fr"])}, en = {lua_str(s["title"]["en"])} }},')
        out.append(f'    text = {{ fr = {lua_str(step_text(s, "fr"))},')
        out.append(f'             en = {lua_str(step_text(s, "en"))} }} }},')
    out.append("}")
    out.append((ROOT / "tools/guided-tour-runtime.lua").read_text(encoding="utf-8"))
    (ROOT / "src/scripts/guided-tour.lua").write_text("\n".join(out), encoding="utf-8")



def sentences(s):
    """Une phrase par ligne dans le markdown (règle du dépôt) : coupe après . ! ? suivi d'une majuscule."""
    return re.sub(r'([.!?]) (?=[A-ZÀ-Ý«"`])', lambda m: m.group(1) + chr(10), s)


# ── README ─────────────────────────────────────────────────────────────────────────────────────
INTRO = {
    "fr": f"""🇬🇧 *This document is also available [in English](README.en.md).*

# Mission de démo VEAF (Caucase)

La mission de démonstration des [VEAF Mission Creation Tools](https://github.com/VEAF/VEAF-Mission-Creation-Tools) v6 : **chaque fonctionnalité y a son exemple**, et une **visite guidée** en jeu mène de l'une à l'autre.
Elle est mise à jour à chaque nouvelle fonctionnalité, et vérifiée avant chaque release des outils : si une fonctionnalité marche ici, elle marche.

### Les VMCT, c'est quoi ?

Les **VEAF Mission Creation Tools** (VMCT) sont la boîte à outils avec laquelle la [VEAF](https://www.veaf.org) construit ses missions DCS World.
Elles apportent les scripts qui tournent en jeu (unités créées depuis un marqueur de la carte F10, zones de combat, QRA, CAP à la demande, ravitailleurs et AWACS, opérations porte-avions, défense aérienne Skynet, CTLD et CSAR…) et l'outil en ligne de commande `veaf-tools`, qui construit une mission à partir d'un dossier : la mission DCS, un `mission.yaml` qui règle chaque module, les préréglages radio, les points de navigation, les variantes météo.
[Documentation]({DOC['fr']}) · [Dépôt]({VMCT})

![Carte de la démo](docs/carte.jpg)

## Démarrer

1. Téléchargez la mission dans la langue et la météo de votre choix (dernière [release]({REPO}/releases/latest)), et copiez-la dans `Saved Games\\DCS\\Missions` ; ou construisez-la (voir [Pour les créateurs de mission](#pour-les-créateurs-de-mission)).
2. Lancez-la en solo ou sur un serveur, et prenez un slot à **Kutaisi** (slots classiques, moteur chaud) ou sur un porte-avions.
3. Ouvrez le menu **F10 > Autre > Visite guidée** : un sous-menu par chapitre, une entrée par étape. Chaque entrée affiche ce qu'il faut faire, la position de l'étape par rapport à vous, et pose un repère sur votre carte F10.

La sécurité VEAF est **désactivée** dans cette mission : toutes les commandes sont ouvertes à tous, y compris celles qu'un serveur réserve aux pilotes habilités.
La mission existe en **deux versions complètes**, française (`_FR`) et anglaise (`_EN`) : menus VEAF et CTLD, visite guidée, menus de la démo, briefing, carte F10 et cartes du briefing sont dans la langue de la version.
Seuls CSAR et Skynet, qui n'ont pas de traduction, gardent des messages en anglais dans la version française, ainsi que quelques libellés VEAF pas encore traduits.

{downloads('fr')}

### Taper une commande dans un marqueur

Beaucoup de fonctionnalités se commandent depuis la carte F10 : bouton « Ajouter un repère » dans la barre du haut, clic sur la carte, tapez le texte de la commande (par exemple `-sa8`), puis cliquez ailleurs pour valider.
La commande s'exécute à l'emplacement du marqueur, et le marqueur disparaît.

## Le théâtre

Le front suit l'Inguri, entre la Géorgie (bleue) et l'Abkhazie (rouge). Le bullseye, commun aux deux camps, est sur **Zugdidi**.

| Base bleue | Slots | Remarque |
|---|---|---|
| Kutaisi | classiques (moteur chaud) + dynamiques | base mère, défendue par un NASAMS |
| Senaki-Kolkhi | dynamiques | défendue par un Hawk ; cible du raid scénarisé |
| Kobuleti | dynamiques | |
| Batumi | dynamiques | |
| Porte-avions Stennis, Roosevelt | F/A-18C, F-14B (pont, moteur chaud) | au large de Batumi |
| FARP Khoni | — | hélicoptères, CTLD, CSAR |

Tous les aérodromes russes et abkhazes sont rouges, sans slot. Les dynamiques ne marchent qu'en multijoueur.

| Moyen | Fréquence | TACAN | Altitude | Où |
|---|---|---|---|---|
| Texaco 1 (KC-135, perche) | 292.0 AM | 52Y | FL200 | est de Kutaisi |
| Arco 1 (KC-135 MPRS, panier) | 291.0 AM | 51Y | FL180 | au sud des porte-avions |
| Overlord 1 (E-3A) + escorte F-15C | 286.0 AM | — | FL300 | sud de Kutaisi |
| Reaper 1 (MQ-9, JTAC laser 1511) | 35.55 FM | — | 3 000 m sol | front de Gali |
| CVN-74 Stennis | 274.0 AM | 74X STN, ICLS 4, Link 4 336.0 | — | au large de Batumi |
| CVN-71 Roosevelt | 271.0 AM | 71X TDR, ICLS 1, Link 4 337.0 | — | au large de Batumi |
| FARP Khoni | 127.5 AM | — | — | sud-ouest de Khoni |
""",
    "en": f"""🇫🇷 *Ce document existe aussi [en français](README.md).*

# VEAF demo mission (Caucasus)

The demonstration mission of the [VEAF Mission Creation Tools](https://github.com/VEAF/VEAF-Mission-Creation-Tools) v6: **every feature has its example here**, and an in-game **guided tour** leads from one to the next.
It is updated with every new feature, and checked before every release of the tools: if a feature works here, it works.

### What are the VMCT?

The **VEAF Mission Creation Tools** (VMCT) are the toolkit the [VEAF](https://www.veaf.org) uses to build its DCS World missions.
They bring the in-game scripts (spawning units from F10 map markers, combat zones, QRA, CAP on demand, tankers and AWACS, carrier operations, Skynet air defence, CTLD and CSAR…) and the `veaf-tools` command line that builds a mission from a folder: the DCS mission, a `mission.yaml` that configures every module, radio presets, waypoints, weather variants.
[Documentation]({DOC['en']}) · [Repository]({VMCT})

![Demo map](docs/carte.en.jpg)

## Getting started

1. Download the mission in the language and weather of your choice (latest [release]({REPO}/releases/latest)), and copy it into `Saved Games\\DCS\\Missions`; or build it (see [For mission makers](#for-mission-makers)).
2. Run it solo or on a server, and take a slot at **Kutaisi** (classic slots, hot start) or on a carrier.
3. Open **F10 > Other > Guided tour**: one submenu per chapter, one entry per step. Each entry shows what to do, where the step is relative to you, and places a mark on your F10 map.

VEAF security is **disabled** in this mission: every command is open to everyone, including those a server keeps for qualified pilots.
The mission comes in **two complete versions**, English (`_EN`) and French (`_FR`): VEAF and CTLD menus, guided tour, demo menus, briefing, F10 map and briefing maps are all in the version's language.
This guide follows the English version.

{downloads('en')}

### Typing a command into a marker

Many features are driven from the F10 map: "Add mark" button in the top bar, click on the map, type the command text (for example `-sa8`), then click elsewhere to validate.
The command runs at the marker's position, and the marker disappears.

## The theatre

The front follows the Inguri river, between Georgia (blue) and Abkhazia (red). The bullseye, shared by both sides, is on **Zugdidi**.

| Blue base | Slots | Note |
|---|---|---|
| Kutaisi | classic (hot start) + dynamic | home base, defended by a NASAMS |
| Senaki-Kolkhi | dynamic | defended by a Hawk; target of the scripted raid |
| Kobuleti | dynamic | |
| Batumi | dynamic | |
| Carriers Stennis, Roosevelt | F/A-18C, F-14B (deck, hot start) | off Batumi |
| FARP Khoni | — | helicopters, CTLD, CSAR |

Every Russian and Abkhazian airfield is red, without slots. Dynamic slots only work in multiplayer.

| Asset | Frequency | TACAN | Altitude | Where |
|---|---|---|---|---|
| Texaco 1 (KC-135, boom) | 292.0 AM | 52Y | FL200 | east of Kutaisi |
| Arco 1 (KC-135 MPRS, drogue) | 291.0 AM | 51Y | FL180 | south of the carriers |
| Overlord 1 (E-3A) + F-15C escort | 286.0 AM | — | FL300 | south of Kutaisi |
| Reaper 1 (MQ-9, JTAC laser 1511) | 35.55 FM | — | 3,000 m AGL | Gali front |
| CVN-74 Stennis | 274.0 AM | 74X STN, ICLS 4, Link 4 336.0 | — | off Batumi |
| CVN-71 Roosevelt | 271.0 AM | 71X TDR, ICLS 1, Link 4 337.0 | — | off Batumi |
| FARP Khoni | 127.5 AM | — | — | south-west of Khoni |
""",
}

MAKERS = {
    "fr": """## Pour les créateurs de mission

### Construire

Depuis ce dossier, avec `veaf-tools.exe` (installé par `veaf-tools-updater.exe`, voir la [documentation](https://veaf.github.io/documentation/latest/)) :

```
.\\veaf-tools.exe mission validate
.\\veaf-tools.exe build
python tools/localize_miz.py
python tools/verify.py
```

`build` construit les deux langues (`build_variants` de `mission.yaml`) : dans `missions/`, une mission `_FR` et une `_EN` par variante météo de `src/versions.yaml`.
`localize_miz.py` met ensuite en anglais ce qui vit dans la mission DCS des versions `_EN` (briefing, étiquettes F10, cartes du briefing) : sans lui, `verify.py` refuse les `.miz` anglais.
Pour un test local (logs détaillés, une seule météo, game masters, pont dcs-bridge) : `python tools/make_test_mission.py`, qui produit `missions-test/VEAF_Demo_TEST_FR.miz` et `_EN.miz`.

### Les fichiers

| Fichier | Rôle |
|---|---|
| `mission.yaml` | la configuration de tous les modules VEAF, textes en français ; sa fin (profils FR et EN, `build_variants`) est **générée** |
| `i18n/en.yaml` | la version anglaise de chaque texte de `mission.yaml` |
| `src/mission/` | la mission DCS elle-même, éclatée, en français |
| `src/scripts/mission-script.lua` | le Lua propre à la mission (fonction du menu « Démo : commandes ») |
| `src/scripts/guided-tour.lua` | la visite guidée, **générée** ; elle suit la langue du build |
| `tour/steps.yaml` | **la source** de la visite, de ce README et de la recette, en français et en anglais |
| `tools/` | les générateurs : lots d'actions MCP (`gen_0*.py`), visite et docs (`gen_tour.py`), profil anglais (`gen_i18n.py`), cartes (`gen_map.py`), textes de la mission DCS dans les deux langues (`i18n_texts.py`), localisation des `.miz` anglais (`localize_miz.py`), vérification (`verify.py`) |
| `docs/recette.md` | la liste de contrôle avant release, **générée** |

### Ajouter une fonctionnalité

Chaque nouvelle fonctionnalité des outils VEAF ajoute son exemple à la démo, dans la même PR que la fonctionnalité ou juste après :

1. poser l'exemple dans la mission (actions MCP sur le dossier, ou `mission.yaml`) ;
2. ajouter son étape dans `tour/steps.yaml`, en français et en anglais, avec son contrôle de recette (`check`) ;
3. traduire tout nouveau texte de `mission.yaml` dans `i18n/en.yaml`, puis `python tools/gen_i18n.py` (il refuse de tourner s'il manque une traduction) ;
4. `python tools/gen_tour.py` (visite, README, recette) et `python tools/gen_map.py` (cartes) ;
5. construire, `python tools/localize_miz.py`, puis `python tools/verify.py`.

### Avant chaque release des outils

Construire la démo avec la version candidate et dérouler [la recette](docs/recette.md) : chaque ligne est un observable en jeu.
Une fois les outils publiés, `python tools/release.py published-v<version>` installe cette version, construit, localise, vérifie, et publie les dix `.miz` dans une release du dépôt.
""",
    "en": """## For mission makers

### Building

From this folder, with `veaf-tools.exe` (installed by `veaf-tools-updater.exe`, see the [documentation](https://veaf.github.io/documentation/latest/en/)):

```
.\\veaf-tools.exe mission validate
.\\veaf-tools.exe build
python tools/localize_miz.py
python tools/verify.py
```

`build` builds both languages (`build_variants` in `mission.yaml`): in `missions/`, one `_FR` and one `_EN` mission per weather variant of `src/versions.yaml`.
`localize_miz.py` then puts into English what lives in the DCS mission of the `_EN` versions (briefing, F10 labels, briefing maps): without it, `verify.py` rejects the English `.miz`.
For a local test (verbose logs, a single weather, game masters, dcs-bridge): `python tools/make_test_mission.py`, which writes `missions-test/VEAF_Demo_TEST_FR.miz` and `_EN.miz`.

### Files

| File | Role |
|---|---|
| `mission.yaml` | the configuration of every VEAF module, French texts; its end (FR and EN profiles, `build_variants`) is **generated** |
| `i18n/en.yaml` | the English version of every text in `mission.yaml` |
| `src/mission/` | the DCS mission itself, exploded, in French |
| `src/scripts/mission-script.lua` | the mission's own Lua (function behind the "Demo: commands" menu) |
| `src/scripts/guided-tour.lua` | the guided tour, **generated**; it follows the build's language |
| `tour/steps.yaml` | **the source** of the tour, this README and the release checklist, in French and English |
| `tools/` | generators: MCP action batches (`gen_0*.py`), tour and docs (`gen_tour.py`), English profile (`gen_i18n.py`), maps (`gen_map.py`), DCS mission texts in both languages (`i18n_texts.py`), English `.miz` localisation (`localize_miz.py`), checks (`verify.py`) |
| `docs/recette.md` | the pre-release checklist (French), **generated** |

### Adding a feature

Every new VEAF tools feature adds its example to the demo, in the same PR as the feature or right after:

1. place the example in the mission (MCP actions on the folder, or `mission.yaml`);
2. add its step in `tour/steps.yaml`, in French and English, with its release check (`check`);
3. translate every new `mission.yaml` text in `i18n/en.yaml`, then `python tools/gen_i18n.py` (it refuses to run if a translation is missing);
4. `python tools/gen_tour.py` (tour, README, checklist) and `python tools/gen_map.py` (maps);
5. build, `python tools/localize_miz.py`, then `python tools/verify.py`.

### Before every tools release

Build the demo with the release candidate and run [the checklist](docs/recette.md): each line is an in-game observable.
Once the tools are published, `python tools/release.py published-v<version>` installs that version, builds, localises, checks, and publishes the ten `.miz` in a release of this repository.
""",
}


def anchor_slug(title):
    import re
    s = title.lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.U).strip().replace(" ", "-")
    return s


def gen_readme(lang):
    t = T[lang]
    out = [INTRO[lang], f"## {'La visite guidée' if lang == 'fr' else 'The guided tour'}", ""]
    out.append(f"| # | {t['steps']} | {t['where']} | {t['modules']} |")
    out.append("|---|---|---|---|")
    for i, s in enumerate(STEPS, 1):
        mods = ", ".join(f"`{m}`" for m in s["modules"])
        out.append(f"| {i:02d} | [{s['title'][lang]}](#{anchor_slug(f'{i:02d} ' + s['title'][lang])}) | {where(s, lang)} | {mods} |")
    out.append("")
    n = 0
    for key, c in CHAPTERS.items():
        out.append(f"### {c[lang]}")
        out.append("")
        for s in STEPS:
            if s["chapter"] != key:
                continue
            n = STEPS.index(s) + 1
            out.append(f"#### {n:02d} {s['title'][lang]}")
            out.append("")
            out.append(sentences(s["what"][lang]))
            out.append("")
            out.append(f"**{t['where']}** : {where(s, lang)}" if lang == "fr" else f"**{t['where']}**: {where(s, lang)}")
            out.append("")
            out.append(f"**{t['how']}**" + (" :" if lang == "fr" else ":"))
            out.append("")
            out += [f"- {h}" for h in s["how"][lang]]
            out.append("")
            out.append((f"**{t['see']}** : " if lang == "fr" else f"**{t['see']}**: ") + sentences(s["see"][lang]))
            out.append("")
            mods = ", ".join(f"`{m}`" for m in s["modules"])
            out.append((f"**{t['modules']}** : " if lang == "fr" else f"**{t['modules']}**: ") + mods
                       + f" — [{t['doc']}]({DOC[lang]}{s['doc']})")
            out.append("")
    out.append(MAKERS[lang])
    name = "README.md" if lang == "fr" else "README.en.md"
    (ROOT / name).write_text("\n".join(out), encoding="utf-8")


def gen_recette():
    out = ["# Recette de la mission de démo",
           "",
           "> Générée par `tools/gen_tour.py` depuis `tour/steps.yaml` : ne pas modifier à la main.",
           "",
           "À dérouler avant chaque release des outils VEAF, sur la démo construite avec la version candidate.",
           "Chaque ligne est un observable : on coche quand on l'a vu, on note ce qu'on a vu sinon.",
           "",
           "## Avant DCS",
           "",
           "- [ ] `python tools/build_candidate.py` sans erreur : validate, build des missions `_FR` et `_EN`, localisation, missions de test, `verify.py` au vert.",
           "- [ ] Journal du build relu (`missions/candidate-build.log`) : presets injectés, waypoints injectés, liens des entrepôts, nombre de variantes météo, aucun avertissement nouveau.",
           "",
           "## Par le pont",
           "",
           "Sur `missions-test/VEAF_Demo_TEST_FR.miz` fraîchement chargée : `python tools/recette_pont.py --lang fr` ; puis sur `_EN.miz` : `--lang en`.",
           "Il vérifie que chaque chemin « VEAF > … » cité par la visite existe dans le menu, puis lance les sondes de chaque étape :",
           ""]
    for i, s in enumerate(STEPS, 1):
        for pr in s.get("probe") or []:
            out.append(f"- {i:02d} {s['title']['fr']} : {pr['name']}")
    out += ["",
            "- [ ] FR : `0 en échec`.",
            "- [ ] EN : `0 en échec`.",
            "",
            "## En jeu",
            "",
            "Ce que les sondes ne voient pas : ce qui se lit, s'entend ou se pilote.",
            "",
            "Version des outils : `______`  —  Date : `______`  —  Testeur : `______`",
            "",
            "| # | Étape | Contrôle | OK | Constat |",
            "|---|---|---|---|---|"]
    for i, s in enumerate(STEPS, 1):
        out.append(f"| {i:02d} | {s['title']['fr']} | {s['check']} | ☐ | |")
    out += ["", "## Hors étapes", "",
            "- [ ] Aucune erreur Lua VEAF dans `dcs.log` sur une heure de mission.",
            "- [ ] Les dessins F10 (cercles et étiquettes des étapes) sont visibles et lisibles sur la carte du camp bleu.",
            "- [ ] Version anglaise (`_EN`) : menus VEAF, CTLD, visite, « Demo: commands », briefing, carte F10 et cartes du briefing en anglais ; dérouler au moins les étapes 01, 02, 04 et 10 en anglais.",
            "- [ ] La visite guidée existe dans la langue du build, et chaque entrée pose son repère F10.",
            "- [ ] Les chemins de menu hors VEAF cités par la visite (CTLD, SKYNET, Démo : commandes) correspondent aux menus réels.", ""]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/recette.md").write_text("\n".join(out), encoding="utf-8")


gen_lua()
gen_readme("fr")
gen_readme("en")
gen_recette()
print(f"{len(STEPS)} étapes -> guided-tour.lua, README.md, README.en.md, docs/recette.md")
