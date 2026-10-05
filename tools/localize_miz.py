"""Après le build : met en anglais ce qui vit dans la mission DCS des .miz anglais.

    .\\veaf-tools.exe build
    python tools/localize_miz.py            # tous les .miz de missions/ et de la racine
    python tools/localize_miz.py a.miz ...  # ceux-là

src/mission/ est commun aux deux builds (FR et EN, `build_variants` de mission.yaml) et porte le
français. Un .miz est anglais quand son veaf-config.lua dit `veaf.config.language = "en"` (profil EN) ;
ce script y réécrit le briefing, le texte des étiquettes F10 et les images de carte du briefing, depuis
tools/i18n_texts.py et docs/**/*.en.jpg (tools/gen_map.py). Les .miz français ne sont pas touchés.
Idempotent : relancé sur un .miz déjà traduit, il réécrit les mêmes textes.

Aucune action MCP ne sait localiser un .miz construit (docs/retours-vmct.md) : la table de mission est
relue avec le lecteur de VMCT et réécrite membre par membre (rewrite_miz_members).
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402,F401
from mission_tools.miz_tools import read_member, read_miz, rewrite_miz_members  # noqa: E402
import luadata  # noqa: E402  (fourni avec le code de VMCT)

from i18n_texts import BRIEFING, drawing_labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STEPS = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))["steps"]
NUM = {}
for i, s in enumerate(STEPS, 1):
    if s.get("anchor", {}).get("zone"):
        NUM.setdefault(s["anchor"]["zone"], i)
MAPS = {"demo-carte.jpg": ROOT / "docs/carte.en.jpg"}
MAPS.update({f"demo-{p.name[:-len('.en.jpg')]}.jpg": p for p in (ROOT / "docs/cartes").glob("*.en.jpg")})


def language(path):
    cfg = read_member(path, "l10n/DEFAULT/veaf-config.lua").decode("utf-8")
    return "en" if 'veaf.config.language = "en"' in cfg else "fr"


def localize(path):
    miz = read_miz(path)
    m = miz.mission_content
    b = BRIEFING["en"]
    m["sortie"], m["descriptionText"] = b["sortie"], b["situation"]
    m["descriptionBlueTask"], m["descriptionRedTask"] = b["blue"], b["red"]
    labels = drawing_labels("en", NUM)
    done, missing = 0, []
    layers = m.get("drawings", {}).get("layers", {})
    for layer in (layers.values() if isinstance(layers, dict) else layers):
        objects = layer.get("objects", {})
        for o in (objects.values() if isinstance(objects, dict) else objects):
            if "text" in o:
                if o["name"] in labels:
                    o["text"] = labels[o["name"]]
                    done += 1
                else:
                    missing.append(o["name"])
    files = {"mission": ("mission = \n" + luadata.serialize(m, indent="  ", indent_level=0,
                                                              always_provide_keyname=True, sort=True)).encode("utf-8")}
    import zipfile
    with zipfile.ZipFile(path) as z:
        maps_in_miz = [n for n in z.namelist() if n.startswith("l10n/DEFAULT/demo-") and n.endswith(".jpg")]
    no_en = []
    for arc in maps_in_miz:
        src = MAPS.get(arc.rsplit("/", 1)[1])
        if src:
            files[arc] = src.read_bytes()
        else:
            no_en.append(arc)   # la carte française resterait dans le .miz anglais
    rewrite_miz_members(path, files)
    # rewrite_miz_members peut avaler une erreur d'écriture (docs/retours-vmct.md) : on relit
    written = read_member(path, "mission").decode("utf-8")
    ok = not missing and not no_en and f'sortie = "{b["sortie"]}"' in written
    print(f"{path.name}: briefing, {done} étiquette(s) F10, {len(files) - 1} carte(s) en anglais"
          + (f" — étiquettes sans traduction : {missing}" if missing else "")
          + (f" — cartes sans version anglaise : {no_en}" if no_en else "")
          + ("" if f'sortie = "{b["sortie"]}"' in written else " — ÉCRITURE NON RELUE"))
    return ok


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] or sorted(list((ROOT / "missions").glob("*.miz")) + list(ROOT.glob("*.miz")))
    ok = True
    for p in paths:
        if language(p) == "en":
            ok = localize(p) and ok
    sys.exit(0 if ok else 1)
