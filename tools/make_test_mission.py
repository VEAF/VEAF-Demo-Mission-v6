"""Mission de test locale : copie du build LOCAL_TEST, jamais dans les sources.

    .\\veaf-tools.exe mission build --profile LOCAL_TEST
    python tools/make_test_mission.py

Écrit missions-test/VEAF_Demo_TEST.miz (ignoré par git) :
  - un game master bleu et un rouge (rôle « instructor » de DCS) : on voit tout, on se place partout ;
  - le déclencheur du pont dcs-bridge (`veaf-tools dcs inject-bridge`), pour sonder la mission en
    cours depuis l'extérieur avec dcs-serve.
Les slots `Client` moteur chaud de Kutaisi (A-10C II, F-16C, F/A-18C, hélicoptères) sont déjà dans la
démo : les slots dynamiques ne marchent qu'en multijoueur.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from paths import VMCT  # noqa: F401
from mission_tools.miz_tools import read_miz, write_miz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
built = sorted(ROOT.glob("VEAF_Demo_Mission_Caucasus_ICAO_UGKO_*.miz"), key=lambda p: p.stat().st_mtime)
if not built:
    sys.exit("aucun build à la racine : lancer d'abord `veaf-tools mission build --profile LOCAL_TEST`")
out_dir = ROOT / "missions-test"
out_dir.mkdir(exist_ok=True)
out = out_dir / "VEAF_Demo_TEST.miz"
shutil.copyfile(built[-1], out)

miz = read_miz(out)
roles = miz.mission_content.setdefault("groundControl", {}).setdefault("roles", {})
roles.setdefault("instructor", {})
roles["instructor"].update({"blue": 1, "red": 1})
write_miz(miz, out)

subprocess.run([str(ROOT / "veaf-tools.exe"), "dcs", "inject-bridge", str(out)], check=True)
print(f"{out.relative_to(ROOT)} : copie de {built[-1].name}, game masters bleu et rouge, pont dcs-bridge")
