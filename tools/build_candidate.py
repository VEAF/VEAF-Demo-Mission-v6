"""Construit la démo avec la version candidate des VMCT : le checkout local (`develop` en général).

    python tools/build_candidate.py            # scripts du checkout, missions/ et missions-test/
    python tools/build_candidate.py --no-test  # sans les missions de test

C'est la recette d'avant release : on vérifie ce qui va sortir, pas ce qui est publié. Étapes :
  1. dans le checkout VMCT (tools/paths.py) : `veaf-build build --dev` régénère les scripts
     (build/veaf-scripts.lua, published.zip) avec la version « <pyproject>+<commit> » ;
  2. `veaf-build publish-local` les installe dans published/ de la démo. Il y dépose aussi des
     veaf-tools*.exe qui ne sont pas ceux du checkout : ceux de la démo sont sauvegardés avant et remis
     après ;
  3. le build passe par le veaf-tools du venv poetry de VMCT, donc par le code du checkout :
     `mission build` (missions/), tools/localize_miz.py, tools/verify.py, puis les missions de test
     (tools/make_test_mission.py, variable VEAF_TOOLS).

Ensuite : charger missions-test/VEAF_Demo_TEST_FR.miz et lancer tools/recette_pont.py.
published/ reste celui du checkout jusqu'au prochain `veaf-tools-updater.exe` (tools/release.py le fait).
Sorties de veaf-build et veaf-tools dans missions/candidate-*.log : vers /dev/null, l'auto-pause les
ferait sortir en erreur (docs/retours-vmct.md, n° 1).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "missions"
EXES = ("veaf-tools.exe", "veaf-tools-updater.exe")


def run(cmd, cwd, log, env=None):
    print("»", " ".join(str(c) for c in cmd))
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)
    if r.returncode:
        sys.exit(f"échec (code {r.returncode}), voir {log}")


def out(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def main():
    LOGS.mkdir(exist_ok=True)
    branch = out(["git", "branch", "--show-current"], VMCT)
    commit = out(["git", "rev-parse", "--short=8", "HEAD"], VMCT)
    dirty = bool(out(["git", "status", "--porcelain", "--untracked-files=no"], VMCT))
    base = tomllib.loads((VMCT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["poetry"]["version"]
    version = f"{base}+{commit}"
    print(f"VMCT {VMCT} : branche {branch}, {version}" + (" (modifications non committées)" if dirty else ""))

    venv = Path(out(["poetry", "env", "info", "-p"], VMCT))
    tool = venv / "Scripts" / "veaf-tools.cmd"
    if not tool.is_file():
        sys.exit(f"veaf-tools introuvable dans le venv de VMCT : {tool} (poetry install dans {VMCT})")

    with tempfile.TemporaryDirectory() as tmp:
        run(["poetry", "run", "veaf-build", "build", "--skip-python", "--dev", "--version", version,
             "--output", tmp], VMCT, LOGS / "candidate-vmct-build.log")
        saved = Path(tmp) / "exe"
        saved.mkdir()
        for exe in EXES:
            if (ROOT / exe).is_file():
                shutil.copy2(ROOT / exe, saved / exe)
        try:
            run(["poetry", "run", "veaf-build", "publish-local", str(ROOT), "--published-zip",
                 str(Path(tmp) / "published.zip")], VMCT, LOGS / "candidate-publish.log")
        finally:
            for exe in EXES:
                if (saved / exe).is_file():
                    shutil.copy2(saved / exe, ROOT / exe)
    installed = json.loads((ROOT / "published/veaf-version.json").read_text(encoding="utf-8"))["version"]
    if installed != version:
        sys.exit(f"published/ porte {installed}, pas {version} (voir missions/candidate-publish.log)")

    for old in LOGS.glob("*.miz"):
        old.unlink()
    run([str(tool), "mission", "validate"], ROOT, LOGS / "candidate-validate.log")
    run([str(tool), "mission", "build"], ROOT, LOGS / "candidate-build.log")
    subprocess.run([sys.executable, "tools/localize_miz.py"], cwd=ROOT, check=True)
    if "--no-test" not in sys.argv:
        subprocess.run([sys.executable, "tools/make_test_mission.py"], cwd=ROOT, check=True,
                       env={**os.environ, "VEAF_TOOLS": str(tool)})
    # après les missions de test : verify.py contrôle aussi missions-test/
    r = subprocess.run([sys.executable, "tools/verify.py"], cwd=ROOT)
    if r.returncode:
        sys.exit("verify.py en échec")
    print(f"démo construite avec VMCT {version}")


if __name__ == "__main__":
    main()
