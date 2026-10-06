"""Écrit la fin de mission.yaml (profils FR et EN, leurs profils de test, `build_variants`) et src/versions.en.yaml.

    python tools/gen_i18n.py

mission.yaml porte les textes français (configuration de base) ; i18n/en.yaml porte leur version
anglaise. Ce script copie les blocs de mission.yaml qui contiennent du texte lisible par un joueur,
y remplace chaque texte par sa traduction, et écrit le profil EN. Un profil REMPLACE une liste au lieu
de la fusionner (doc/MISSION_YAML_REFERENCE, `profiles:`) : le profil EN recopie donc les listes en
entier, et c'est pour ne jamais les maintenir à la main qu'il est généré.

Il refuse de tourner si un texte français n'a pas sa traduction : un ajout dans mission.yaml sans son
entrée dans i18n/en.yaml casse le générateur, pas la mission anglaise en silence.

Tout ce qui suit le repère « ── Profils de build » dans mission.yaml est réécrit.
"""
import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MARK = "# ── Profils de build"
base = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
EN = yaml.safe_load((ROOT / "i18n/en.yaml").read_text(encoding="utf-8"))
missing = []


def tr(table, key, field=None):
    entry = EN.get(table, {}).get(key)
    if entry is None or (field and field not in entry):
        missing.append(f"{table}.{key}" + (f".{field}" if field else ""))
        return None
    return entry[field] if field else entry


mods = base["modules"]
en_modules = {}

def tr_tree(nodes):
    """L'arbre user_menus anglais, construit depuis le français : mêmes actions et mêmes cibles, seuls les
    textes (`menu`, `command`, `text`) changent — une entrée française sans traduction est signalée."""
    out = []
    for n in nodes:
        n = copy.deepcopy(n)
        for field in ("menu", "command", "text"):
            if field in n:
                n[field] = tr("user_menus", n[field])
        if "items" in n:
            n["items"] = tr_tree(n["items"])
        out.append(n)
    return out


en_modules["RADIO"] = {"user_menus": {**copy.deepcopy(mods["RADIO"]["user_menus"]),
                                      "tree": tr_tree(mods["RADIO"]["user_menus"]["tree"])}}

shortcuts = copy.deepcopy(mods["SHORTCUTS"]["shortcuts"])
for s in shortcuts:
    s["description"] = tr("shortcuts", s["name"])
en_modules["SHORTCUTS"] = {"shortcuts": shortcuts}

zones = copy.deepcopy(mods["COMBATZONE"]["combat_zones"])
for z in zones:
    for field in ("friendly_name", "briefing", "radio_group_name"):
        if field in z:
            z[field] = tr("combat_zones", z["zone_name"], field)
en_modules["COMBATZONE"] = {"combat_zones": zones}

waves = copy.deepcopy(mods["AIRWAVES"]["airwave_zones"])
for w in waves:
    w["description"] = tr("airwaves", w["name"], "description")
en_modules["AIRWAVES"] = {"airwave_zones": waves}

assets = copy.deepcopy(mods["ASSETS"]["assets"])
for a in assets:
    for field in ("description", "information"):
        if field in a:
            a[field] = tr("assets", a["name"], field)
en_modules["ASSETS"] = {"assets": assets}

sanct = copy.deepcopy(mods["SANCTUARY"]["sanctuary_zones"])
for s in sanct:
    s["name"] = tr("sanctuary", s["name"])
en_modules["SANCTUARY"] = {"sanctuary_zones": sanct}

caps = copy.deepcopy(base["cap_missions"])
for c in caps:
    for field in ("menu_name", "briefing"):
        c[field] = tr("cap_missions", c["group_name"], field)

cms = copy.deepcopy(base["combat_missions"])
for m in cms:
    for field in ("friendly_name", "briefing"):
        m[field] = tr("combat_missions", m["name"], field)
    names = tr("combat_missions", m["name"], "elements") or {}
    for e in m["elements"]:
        if e["name"] not in names:
            missing.append(f"combat_missions.{m['name']}.elements.{e['name']}")
        e["name"] = names.get(e["name"], e["name"])

# Variantes météo : même météo, noms anglais (ils finissent dans le nom des .miz _EN). Le build lit le
# fichier que le profil désigne (pipeline.weather.file), versions.yaml reste la seule source à éditer.
VERSIONS_EN = "src/versions.en.yaml"
versions = yaml.safe_load((ROOT / "src/versions.yaml").read_text(encoding="utf-8"))
for v in versions["versions"]:
    v["name"] = tr("weather_variants", v["name"])

if missing:
    sys.exit("traductions manquantes dans i18n/en.yaml :\n  " + "\n  ".join(missing))

(ROOT / VERSIONS_EN).write_text(
    "# Généré par tools/gen_i18n.py depuis src/versions.yaml et i18n/en.yaml : ne pas modifier à la main.\n"
    "# Variantes météo du build anglais (profil EN) : même météo, noms anglais.\n"
    + yaml.safe_dump(versions, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")

EN_PROFILE = {"mission": {"language": "en"}, "modules": en_modules, "cap_missions": caps, "combat_missions": cms,
              "pipeline": {"weather": {"file": VERSIONS_EN}}}
TEST = {"global_log_level": "debug", "pipeline": {"weather": False}}
profiles = {
    "FR": {"mission": {"language": "fr"}},
    "EN": EN_PROFILE,
    # Test local : logs détaillés, une seule météo (pas de variantes), build plus rapide.
    "LOCAL_TEST": copy.deepcopy(TEST),
    "LOCAL_TEST_EN": {**copy.deepcopy(EN_PROFILE), **copy.deepcopy(TEST)},
}

header = f"""{MARK} (générés par tools/gen_i18n.py — ne pas modifier à la main) ────
# Deux langues, construites ensemble par `veaf-tools build` (build_variants) : un .miz _FR et un _EN
# par variante météo. FR = la configuration ci-dessus ; EN = les mêmes blocs, textes d'i18n/en.yaml.
# Les textes de la mission DCS (briefing, dessins F10, cartes) sont traduits après le build par
# tools/localize_miz.py. Test local : --profile LOCAL_TEST (FR) ou LOCAL_TEST_EN.
"""
body = yaml.safe_dump({"build_variants": ["FR", "EN"], "profiles": profiles}, allow_unicode=True, sort_keys=False,
                      width=1000, default_flow_style=False)
text = (ROOT / "mission.yaml").read_text(encoding="utf-8")
i = text.index(MARK)
(ROOT / "mission.yaml").write_text(text[:i] + header + body, encoding="utf-8")
print(f"mission.yaml : build_variants FR, EN ; profils FR, EN, LOCAL_TEST, LOCAL_TEST_EN ; {VERSIONS_EN}")
