"""Génère la visite guidée et sa documentation depuis tour/steps.yaml (source unique).

    python tools/gen_tour.py

Écrit :
  - src/scripts/guided-tour.lua  le menu F10 « VISITE GUIDÉE » (fr) et « GUIDED TOUR » (en) ;
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
DOC = "https://veaf.github.io/documentation/dev/"
REPO = "https://github.com/VEAF/VEAF-Demo-Mission-v6"

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
           "-- Menu F10 « VISITE GUIDÉE » (fr) et « GUIDED TOUR » (en) : un sous-menu par chapitre, une commande",
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
    "fr": f"""Ce document est aussi disponible [en anglais](README.en.md).

# Mission de démo VEAF (Caucase)

La mission de démonstration des [VEAF Mission Creation Tools](https://github.com/VEAF/VEAF-Mission-Creation-Tools) v6 : **chaque fonctionnalité y a son exemple**, et une **visite guidée** en jeu mène de l'une à l'autre.
Elle est mise à jour à chaque nouvelle fonctionnalité, et vérifiée avant chaque release des outils : si une fonctionnalité marche ici, elle marche.

![Carte de la démo](docs/carte.jpg)

## Démarrer

1. Construisez la mission (voir [Pour les créateurs de mission](#pour-les-créateurs-de-mission)), ou prenez-la dans les [releases]({REPO}/releases) du dépôt quand elles sont publiées.
2. Lancez-la en solo ou sur un serveur, et prenez un slot à **Kutaisi** (slots classiques, moteur chaud) ou sur un porte-avions.
3. Ouvrez le menu **F10 > Autre > VEAF > VISITE GUIDÉE** : un sous-menu par chapitre, une entrée par étape. Chaque entrée affiche ce qu'il faut faire, la position de l'étape par rapport à vous, et pose un repère sur votre carte F10.

La sécurité VEAF est **désactivée** dans cette mission : toutes les commandes sont ouvertes à tous, y compris celles qu'un serveur réserve aux pilotes habilités.
La mission est en français (menus VEAF compris) ; la visite existe en anglais (**GUIDED TOUR**).

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
    "en": f"""This document is also available [in French](README.md).

# VEAF demo mission (Caucasus)

The demonstration mission of the [VEAF Mission Creation Tools](https://github.com/VEAF/VEAF-Mission-Creation-Tools) v6: **every feature has its example here**, and an in-game **guided tour** leads from one to the next.
It is updated with every new feature, and checked before every release of the tools: if a feature works here, it works.

![Demo map](docs/carte.jpg)

## Getting started

1. Build the mission (see [For mission makers](#for-mission-makers)), or take it from the repository [releases]({REPO}/releases) once they are published.
2. Run it solo or on a server, and take a slot at **Kutaisi** (classic slots, hot start) or on a carrier.
3. Open **F10 > Other > VEAF > GUIDED TOUR**: one submenu per chapter, one entry per step. Each entry shows what to do, where the step is relative to you, and places a mark on your F10 map.

VEAF security is **disabled** in this mission: every command is open to everyone, including those a server keeps for qualified pilots.
The mission runs in French (VEAF menus included); this guide gives the French menu names with their translation.

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

Depuis ce dossier, avec `veaf-tools.exe` (installé par `veaf-tools-updater.exe`, voir la [documentation](https://veaf.github.io/documentation/)) :

```
.\\veaf-tools.exe mission validate
.\\veaf-tools.exe build
```

Les missions construites arrivent dans `missions/`, une par variante météo de `src/versions.yaml`.
Pour un test local (logs détaillés, une seule météo) : `.\\veaf-tools.exe mission build --profile LOCAL_TEST`.

### Les fichiers

| Fichier | Rôle |
|---|---|
| `mission.yaml` | la configuration de tous les modules VEAF |
| `src/mission/` | la mission DCS elle-même, éclatée |
| `src/scripts/mission-script.lua` | le Lua propre à la mission (fonction du menu « Démo : commandes ») |
| `src/scripts/guided-tour.lua` | la visite guidée, **générée** |
| `tour/steps.yaml` | **la source** de la visite, de ce README et de la recette |
| `tools/` | les générateurs : lots d'actions MCP (`gen_0*.py`), visite et docs (`gen_tour.py`), carte (`gen_map.py`), vérification du `.miz` (`verify.py`) |
| `docs/recette.md` | la liste de contrôle avant release, **générée** |

### Ajouter une fonctionnalité

Chaque nouvelle fonctionnalité des outils VEAF ajoute son exemple à la démo, dans la même PR que la fonctionnalité ou juste après :

1. poser l'exemple dans la mission (actions MCP sur le dossier, ou `mission.yaml`) ;
2. ajouter son étape dans `tour/steps.yaml`, avec son contrôle de recette (`check`) ;
3. `python tools/gen_tour.py` (visite, README, recette) et `python tools/gen_map.py` (carte) ;
4. construire, puis `python tools/verify.py`.

### Avant chaque release des outils

Construire la démo avec la version candidate et dérouler [la recette](docs/recette.md) : chaque ligne est un observable en jeu.
""",
    "en": """## For mission makers

### Building

From this folder, with `veaf-tools.exe` (installed by `veaf-tools-updater.exe`, see the [documentation](https://veaf.github.io/documentation/)):

```
.\\veaf-tools.exe mission validate
.\\veaf-tools.exe build
```

Built missions land in `missions/`, one per weather variant of `src/versions.yaml`.
For a local test (verbose logs, a single weather): `.\\veaf-tools.exe mission build --profile LOCAL_TEST`.

### Files

| File | Role |
|---|---|
| `mission.yaml` | the configuration of every VEAF module |
| `src/mission/` | the DCS mission itself, exploded |
| `src/scripts/mission-script.lua` | the mission's own Lua (function behind the "Démo : commandes" menu) |
| `src/scripts/guided-tour.lua` | the guided tour, **generated** |
| `tour/steps.yaml` | **the source** of the tour, this README and the release checklist |
| `tools/` | generators: MCP action batches (`gen_0*.py`), tour and docs (`gen_tour.py`), map (`gen_map.py`), `.miz` check (`verify.py`) |
| `docs/recette.md` | the pre-release checklist (French), **generated** |

### Adding a feature

Every new VEAF tools feature adds its example to the demo, in the same PR as the feature or right after:

1. place the example in the mission (MCP actions on the folder, or `mission.yaml`);
2. add its step in `tour/steps.yaml`, with its release check (`check`);
3. `python tools/gen_tour.py` (tour, README, checklist) and `python tools/gen_map.py` (map);
4. build, then `python tools/verify.py`.

### Before every tools release

Build the demo with the release candidate and run [the checklist](docs/recette.md): each line is an in-game observable.
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
                       + f" — [{t['doc']}]({DOC}{s['doc']})")
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
           "- [ ] `veaf-tools mission validate` sans erreur.",
           "- [ ] `veaf-tools build` sans erreur ; journal relu : presets injectés, waypoints injectés, liens des entrepôts, nombre de variantes météo, aucun avertissement nouveau.",
           "- [ ] `python tools/verify.py` : tous les contrôles du `.miz` au vert.",
           "",
           "## En jeu",
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
            "- [ ] La visite guidée existe en français et en anglais, et chaque entrée pose son repère F10.",
            "- [ ] Les chemins de menu cités par la visite correspondent aux menus réels.", ""]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/recette.md").write_text("\n".join(out), encoding="utf-8")


gen_lua()
gen_readme("fr")
gen_readme("en")
gen_recette()
print(f"{len(STEPS)} étapes -> guided-tour.lua, README.md, README.en.md, docs/recette.md")
