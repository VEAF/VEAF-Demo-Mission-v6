"""Reporte les renommages du lot 07 (tools/gen_07_noms.py) dans les fichiers qui citent zones et groupes.

Remplacement de chaînes exactes, du plus long au plus court, avec le décompte par fichier. À lancer
une fois après le lot 07 : relancé, il ne trouve plus rien à remplacer et ne le signale pas.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_07_noms import RENAMES  # noqa: E402
from lib import ROOT  # noqa: E402

EXTRA = [
    ("QRA Soukhoumi", "QRA Sukhumi"),                 # nom de la QRA (identifiant, cité par user_menus)
    ("CAP Su-27 mer FL300", "CAP Su-27 sea FL300"),   # group_name de cap_missions (sans le préfixe OnDemand-)
    ("CAP MiG-31 Sotchi FL350", "CAP MiG-31 Sochi FL350"),
]
FILES = ["mission.yaml", "tour/steps.yaml", "tools/gen_map.py", "tools/verify.py", "tools/fix_convoy_on_road.py",
         "tools/gen_05_dessins.py"]
pairs = sorted(RENAMES + EXTRA, key=lambda p: -len(p[0]))
for f in FILES:
    p = ROOT / f
    t = p.read_text(encoding="utf-8")
    n_total = 0
    for old, new in pairs:
        # un nom de zone est aussi le préfixe des groupes : on ne remplace qu'un nom entier
        pat = re.compile(re.escape(old) + r"(?![\w-])")
        t, n = pat.subn(new, t)
        n_total += n
    p.write_text(t, encoding="utf-8")
    print(f"{f}: {n_total} remplacement(s)")
