"""Missions de test locales, une par langue : copies d'un build de test, jamais dans les sources.

    python tools/make_test_mission.py          # FR et EN
    python tools/make_test_mission.py en       # une seule langue

Pour chaque langue, construit le profil LOCAL_TEST (FR) ou LOCAL_TEST_EN (logs détaillés, sans
variantes météo), localise le .miz anglais (tools/localize_miz.py), puis écrit
missions-test/VEAF_Demo_TEST_<FR|EN>.miz (ignoré par git) avec :
  - un game master bleu et un rouge (rôle « instructor » de DCS) : on voit tout, on se place partout ;
  - le déclencheur du pont dcs-bridge (`veaf-tools dcs inject-bridge`), pour sonder la mission en cours
    depuis l'extérieur avec dcs-serve.
Les slots `Client` moteur chaud de Kutaisi sont déjà dans la démo : les slots dynamiques ne marchent
qu'en multijoueur. Le build garde sa sortie dans un fichier : vers /dev/null, son auto-pause le ferait
sortir en erreur (docs/retours-vmct.md, n° 1).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from paths import VMCT  # noqa: F401
from mission_tools.miz_tools import read_miz, write_miz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {"fr": "LOCAL_TEST", "en": "LOCAL_TEST_EN"}
# veaf-tools du dossier, ou un autre (VEAF_TOOLS) : celui du venv de VMCT pour essayer les outils de develop
TOOL = os.environ.get("VEAF_TOOLS", str(ROOT / "veaf-tools.exe"))
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
    miz = read_miz(out)
    roles = miz.mission_content.setdefault("groundControl", {}).setdefault("roles", {})
    roles.setdefault("instructor", {})
    roles["instructor"].update({"blue": 1, "red": 1})
    write_miz(miz, out)
    with open(out_dir / f"bridge-{lang}.log", "w", encoding="utf-8") as f:
        subprocess.run([TOOL, "dcs", "inject-bridge", str(out)], check=True,
                       stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    print(f"{out.relative_to(ROOT)} : profil {PROFILES[lang]}, game masters bleu et rouge, pont dcs-bridge")
