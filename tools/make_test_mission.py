"""Missions de test locales, une par langue : copies d'un build de test, jamais dans les sources.

    python tools/make_test_mission.py          # FR et EN
    python tools/make_test_mission.py en       # une seule langue

Pour chaque langue, construit le profil LOCAL_TEST (FR) ou LOCAL_TEST_EN (logs détaillés, sans
variantes météo), localise le .miz anglais (tools/localize_miz.py), puis écrit
missions-test/VEAF_Demo_TEST_<FR|EN>.miz (ignoré par git) avec :
  - un game master bleu et un rouge (rôle « instructor » de DCS) : on voit tout, on se place partout ;
    posés par le build lui-même (`mission.ground_control` des profils LOCAL_TEST, tools/gen_i18n.py) ;
  - le déclencheur du pont dcs-bridge (`veaf-tools dcs inject-bridge`), pour sonder la mission en cours
    depuis l'extérieur avec dcs-serve.
Puis, à côté, missions-test/VEAF_Demo_TEST_FATCOW_<FR|EN>.miz : la même, avec le CH-47F et l'AH-64D de Kutaisi
au sol sur une route, pour la recette de l'étape Fat Cow sans piloter (fatcow_mission).
Les slots `Client` moteur chaud de Kutaisi sont déjà dans la démo : les slots dynamiques ne marchent
qu'en multijoueur. Le build garde sa sortie dans un fichier : vers /dev/null, son auto-pause le ferait
sortir en erreur (docs/retours-vmct.md, n° 1).
"""
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from paths import VMCT  # noqa: F401
from mission_tools.miz_tools import list_members, read_member, read_miz, rewrite_miz_members, write_miz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {"fr": "LOCAL_TEST", "en": "LOCAL_TEST_EN"}
# veaf-tools du dossier, ou un autre (VEAF_TOOLS) : celui du venv de VMCT pour essayer les outils de develop
TOOL = os.environ.get("VEAF_TOOLS", str(ROOT / "veaf-tools.exe"))
BRIEFING_PAGE = re.compile(r"KNEEBOARD/IMAGES/\d{2}-briefing-[a-z0-9-]+\.jpg")
# Route droite de 2,1 km au cap 172°, à 14 km de toute base et de toute FARP, au sud-ouest de Kutaisi (mesurée par
# le pont le 2026-10-29) : sur une route, pas d'arbre. Un champ plat choisi d'abord avait des arbres, que le pont ne
# voit pas : l'AH-64D y est apparu dedans. La sonde de l'étape fatcow pose ici une zone logistique CTLD de 3 km.
FATCOW_ROAD = (-290581.0, 672368.0, 24.3, 172.0)   # x, y, altitude, cap de la route
FATCOW_SLOTS = {"Kutaisi CH-47F": 0.0, "Kutaisi AH-64D": 60.0}   # groupe -> distance le long de la route (m)


def fatcow_mission(test_miz):
    """missions-test/VEAF_Demo_TEST_FATCOW_<LANG>.miz : la recette de l'étape Fat Cow sans piloter.

    À Kutaisi, DCS gare le CH-47F à 1,6 km du cercle logistique et l'aéroport réarme l'AH-64D : le test ne dirait
    rien de la FARP Fat Cow. Ici les deux slots démarrent au sol, moteur chaud, à 60 m l'un de
    l'autre sur une route droite, loin de tout ce qui réarme (David, 2026-10-29 : « une mission dédiée avec une giga zone log »).
    """
    mission = read_miz(test_miz)
    x0, y0, alt, course = FATCOW_ROAD
    ux, uy = math.cos(math.radians(course)), math.sin(math.radians(course))
    moved = []
    for country in mission.mission_content["coalition"]["blue"]["country"]:
        for group in (country.get("helicopter") or {}).get("group", []):
            along = FATCOW_SLOTS.get(group["name"])
            if along is None:
                continue
            x, y = x0 + ux * along, y0 + uy * along
            group["x"], group["y"] = x, y
            for unit in group["units"]:
                unit.update(x=x, y=y, alt=alt, heading=math.radians(course))
                unit.pop("parking", None)
                unit.pop("parking_id", None)
            point = group["route"]["points"][0]
            point.update(x=x, y=y, alt=alt, type="TakeOffGroundHot", action="From Ground Area Hot")
            point.pop("airdromeId", None)
            moved.append(group["name"])
    if sorted(moved) != sorted(FATCOW_SLOTS):
        sys.exit(f"{test_miz.name} : slots Fat Cow introuvables ({moved})")
    out = test_miz.with_name(test_miz.name.replace("_TEST_", "_TEST_FATCOW_"))
    shutil.copy2(test_miz, out)
    write_miz(mission, out)
    print(f"{out.relative_to(ROOT)} : {', '.join(moved)} au sol, sur une route loin de toute base")


def english_briefing_pages(test_miz):
    """Les pages de planchette du briefing (lot 11) en anglais, reprises d'un .miz _EN de missions/.

    src/mission/ porte les pages françaises : le build de test les met aussi dans le .miz anglais, et
    build_mission_briefing n'écrit que dans missions/. Mêmes noms dans les deux langues (tirés des zones).
    """
    source = next(iter(sorted((ROOT / "missions").glob("*_EN_*.miz"))), None)
    if source is None:
        return
    pages = {m: read_member(source, m) for m in list_members(source) if BRIEFING_PAGE.fullmatch(m)}
    pages = {m: data for m, data in pages.items() if m in set(list_members(test_miz))}
    if pages:
        rewrite_miz_members(test_miz, pages)
        print(f"{test_miz.name} : {len(pages)} pages de briefing anglaises reprises de {source.name}")


langs = [a.lower() for a in sys.argv[1:]] or ["fr", "en"]
out_dir = ROOT / "missions-test"
out_dir.mkdir(exist_ok=True)

for lang in langs:
    for old in ROOT.glob("VEAF_Demo_Mission_Caucasus_ICAO_UGKO_*.miz"):
        old.unlink()
    log = out_dir / f"build-{lang}.log"
    with open(log, "w", encoding="utf-8") as f:
        subprocess.run([TOOL, "mission", "build", "--profile", PROFILES[lang]], cwd=ROOT,
                       stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, check=True)
    built = sorted(ROOT.glob("VEAF_Demo_Mission_Caucasus_ICAO_UGKO_*.miz"), key=lambda p: p.stat().st_mtime)[-1]
    out = out_dir / f"VEAF_Demo_TEST_{lang.upper()}.miz"
    shutil.move(built, out)
    if lang == "en":
        subprocess.run([sys.executable, str(ROOT / "tools/localize_miz.py"), str(out)], check=True)
        english_briefing_pages(out)
    gm = read_miz(out).mission_content.get("groundControl", {}).get("roles", {}).get("instructor", {})
    if gm.get("blue") != 1 or gm.get("red") != 1:
        sys.exit(f"{out.name} : le build n'a pas posé les game masters de mission.ground_control ({gm})")
    with open(out_dir / f"bridge-{lang}.log", "w", encoding="utf-8") as f:
        subprocess.run([TOOL, "dcs", "inject-bridge", str(out)], check=True,
                       stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    print(f"{out.relative_to(ROOT)} : profil {PROFILES[lang]}, game masters bleu et rouge, pont dcs-bridge")
    fatcow_mission(out)
