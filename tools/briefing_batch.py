"""Le lot 11 (briefing de la mission, tools/gen_11_briefing.py) : le lancer sans salir src/mission/.

    python tools/briefing_batch.py   # après le build et tools/localize_miz.py

Commun à tools/build_candidate.py et tools/release.py, qui le lancent après le build et localize_miz.py.
Le lot passe `language` à build_mission_briefing (VMCT FEAT-BRIEFING-PER-LANGUAGE) : sans ce paramètre,
l'action mettrait du français dans les .miz _EN, donc on ne le lance pas.
tools/mcp.py appelle le code du checkout VMCT (tools/paths.py), pas celui de veaf-tools.exe.

L'appel en français (la langue de mission.yaml) écrit aussi dans le dossier de la mission : images du briefing
dans src/mission/l10n/DEFAULT/, pages de planchette dans src/mission/KNEEBOARD/IMAGES/, et il réécrit
mission, warehouses et mapResource (`_write_pictures` de VMCT, `folder_too`). Les .miz construits reçoivent
leurs pages directement : src/mission/ n'en a pas besoin, et le prochain build repartirait de ces fichiers.
`mission_kept` remet donc src/mission/ exactement comme avant le lot, modifications en cours comprises.
"""
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSION = ROOT / "src" / "mission"
BATCH = ["tools/mcp.py", "batch", "tools/batches/11-briefing.json"]


def supported():
    """Vrai si build_mission_briefing a `language` ; s'arrête si tools/mcp.py ne lit pas l'action."""
    schema = subprocess.run([sys.executable, "tools/mcp.py", "describe", "build_mission_briefing"], cwd=ROOT,
                            capture_output=True, text=True)
    if schema.returncode:
        sys.exit(f"tools/mcp.py ne lit pas build_mission_briefing (venv VMCT à jour ? poetry install) :\n"
                 f"{schema.stderr.strip().splitlines()[-1:]}")
    if '"language"' in schema.stdout:
        return True
    print("briefing sauté : build_mission_briefing n'a pas encore `language` (VMCT FEAT-BRIEFING-PER-LANGUAGE)")
    return False


@contextmanager
def mission_kept():
    """Remet src/mission/ tel qu'il était à l'entrée, même si le lot échoue : copie avant, recopie après."""
    with tempfile.TemporaryDirectory() as tmp:
        saved = Path(tmp) / "mission"
        shutil.copytree(MISSION, saved)
        try:
            yield
        finally:
            shutil.rmtree(MISSION)
            shutil.copytree(saved, MISSION)


def main():
    """Lance le lot sur les .miz déjà construits, src/mission/ intact."""
    if not supported():
        return
    with mission_kept():
        code = subprocess.run([sys.executable, *BATCH], cwd=ROOT).returncode
    sys.exit(code)


if __name__ == "__main__":
    main()
