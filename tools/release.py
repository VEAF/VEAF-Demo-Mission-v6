"""Publie les .miz de la démo dans une release GitHub du dépôt, construits avec une version publiée des VMCT.

    python tools/release.py published-v6.28.0           # installe cette version, construit, publie
    python tools/release.py published-v6.28.0 --dry-run # tout sauf la publication (dépôt modifié toléré)

Étapes, chacune arrête tout si elle échoue :
  1. dépôt propre et à jour avec origin/main (la release pointe sur un commit publié) ;
  2. veaf-tools-updater.exe --tag <tag> : installe les exe et les scripts publiés de cette version ;
     une version de développement (« 6.27.0+28c606b3 », posée par publish-local) est refusée ;
  3. build des deux langues, tools/localize_miz.py, tools/verify.py ;
  4. gh release create v<version> avec les dix .miz (5 météos × FR/EN).

Les noms des .miz ne portent pas de version : le README pointe sur releases/latest/download/<nom>.miz,
un lien qui suit toujours la dernière release (tools/gen_tour.py, MIZ).
Les sorties de l'updater et du build vont dans missions/*.log : vers /dev/null, l'auto-pause les ferait
sortir en erreur (docs/retours-vmct.md, n° 1).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "VEAF/VEAF-Demo-Mission-v6"
MISSIONS = ROOT / "missions"
EXPECTED = 10  # 5 variantes météo (src/versions.yaml) × 2 langues (build_variants)


def run(cmd, log=None):
    """Lance une commande, sortie dans `log` s'il est donné ; s'arrête si elle échoue."""
    print("»", " ".join(str(c) for c in cmd))
    if log is None:
        subprocess.run(cmd, cwd=ROOT, check=True)
        return
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    if r.returncode:
        sys.exit(f"échec (code {r.returncode}), voir {log}")


def out(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1 or not args[0].startswith("published-v"):
        sys.exit(__doc__)
    vmct_tag = args[0]

    out(["git", "fetch", "-q", "origin"])
    problems = []
    if out(["git", "status", "--porcelain"]):
        problems.append("le dépôt a des modifications non committées : committer et pousser d'abord")
    if out(["git", "rev-parse", "HEAD"]) != out(["git", "rev-parse", "origin/main"]):
        problems.append("HEAD n'est pas origin/main : pousser (ou rapatrier) d'abord")
    for p in problems:
        print(("--dry-run, on continue : " if dry else "") + p)
    if problems and not dry:
        sys.exit(1)

    MISSIONS.mkdir(exist_ok=True)
    run([str(ROOT / "veaf-tools-updater.exe"), "--tag", vmct_tag, "--force", "--no-pause"],
        log=MISSIONS / "updater.log")
    version = json.loads((ROOT / "published/veaf-version.json").read_text(encoding="utf-8"))["version"]
    if f"published-v{version}" != vmct_tag:
        sys.exit(f"l'updater a installé {version}, pas {vmct_tag} (voir missions/updater.log)")
    tag = f"v{version}"
    if subprocess.run(["gh", "release", "view", tag, "-R", REPO], capture_output=True).returncode == 0:
        sys.exit(f"la release {tag} existe déjà")

    for old in MISSIONS.glob("*.miz"):
        old.unlink()
    run([str(ROOT / "veaf-tools.exe"), "mission", "validate"], log=MISSIONS / "validate.log")
    run([str(ROOT / "veaf-tools.exe"), "build"], log=MISSIONS / "build.log")
    run([sys.executable, "tools/localize_miz.py"])
    run([sys.executable, "tools/verify.py"], log=MISSIONS / "verify.log")
    mizs = sorted(MISSIONS.glob("*.miz"))
    if len(mizs) != EXPECTED:
        sys.exit(f"{len(mizs)} .miz dans missions/, {EXPECTED} attendus")

    commit = out(["git", "rev-parse", "--short", "HEAD"])
    notes = (f"Mission de démo construite avec les [VEAF Mission Creation Tools {version}]"
             f"(https://github.com/VEAF/VEAF-Mission-Creation-Tools/releases/tag/{vmct_tag}), commit {commit}.\n\n"
             f"Demo mission built with the VEAF Mission Creation Tools {version}, commit {commit}.\n\n"
             "`_FR` : version française · `_EN` : English version. "
             "Guide : [README](https://github.com/VEAF/VEAF-Demo-Mission-v6#readme) · "
             "[English guide](https://github.com/VEAF/VEAF-Demo-Mission-v6/blob/main/README.en.md)")
    print(f"{len(mizs)} .miz vérifiés, release {tag} sur {commit}")
    if dry:
        print("--dry-run : rien n'est publié")
        return
    run(["gh", "release", "create", tag, "-R", REPO, "--target", out(["git", "rev-parse", "HEAD"]),
         "--title", f"Mission de démo VEAF — VMCT {version}", "--notes", notes, *map(str, mizs)])


if __name__ == "__main__":
    main()
