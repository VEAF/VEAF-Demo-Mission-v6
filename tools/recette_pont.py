"""Recette automatique de la démo, dans la mission qui tourne, par le pont dcs-bridge.

    python tools/recette_pont.py --lang fr                  # tout : chemins de menu, puis sondes de chaque étape
    python tools/recette_pont.py --lang en --menus          # seulement les chemins de menu (ne change rien en jeu)
    python tools/recette_pont.py --lang fr training front   # les sondes de ces étapes (id de tour/steps.yaml)

À lancer sur une mission de test fraîchement chargée (`python tools/make_test_mission.py`,
missions-test/VEAF_Demo_TEST_FR.miz ou _EN.miz), avec dcs-serve lancé à côté : les sondes activent des
zones, font apparaître et détruisent des unités. `--lang` dit laquelle est chargée ; le script s'arrête
si la mission est dans une autre langue (un _EN construit en français passerait sinon pour vert).
La clé du pont : DCS_BRIDGE_API_KEY, sinon le dcs-serve.yaml du dossier courant (--config pour en
désigner un autre).

Deux contrôles :
  1. chemins de menu : chaque « VEAF > … » cité dans les consignes (`how`) de la visite, dans la langue
     du build, doit exister tel quel dans le menu VEAF de la mission, tel que le joueur le lit (titres,
     capitales des sous-menus de la racine, « + » des commandes protégées). Les menus hors VEAF (CTLD,
     SKYNET, Démo : commandes, Visite guidée) ne sont pas lisibles depuis le Lua de mission et restent
     à l'œil.
  2. sondes : le champ `probe` de chaque étape, une liste de { name, act?, check, wait?, timeout? }.
     `act` (Lua) est lancé une fois ; `check` (Lua) rend `ok, détail`, essayé après `wait` secondes,
     puis toutes les 5 s jusqu'à `timeout`. tools/recette-lib.lua est collé devant chaque morceau (R.*),
     avec R.expected = la langue demandée.

Une ligne de verdict par contrôle, puis le total ; code de sortie 1 s'il y a un échec.
Ce qui n'a pas de sonde (ce que seuls des yeux voient) reste dans docs/recette.md.
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402,F401  (met le code VMCT sur sys.path)
from veaf_libs.dcs_bridge_capture import DEFAULT_SERVE_URL, exec_over_bridge, resolve_api_key  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STEPS = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))["steps"]
LIB = (ROOT / "tools/recette-lib.lua").read_text(encoding="utf-8")
POLL = 5

# VEAF met en capitales, à l'affichage, les sous-menus posés directement sous sa racine
# (veafRadio.RadioMenuBuilder:_buildSubtree) : le joueur lit ASSISTANCE, pas Assistance
MENU_LUA = r"""
local out = { R.lang }
local root = veafRadio._builder._root
local function walk(node, prefix)
  for _, sm in ipairs(node.subMenus or {}) do
    local title = node == root and veafRadio.toUpperCase(sm.title) or sm.title
    table.insert(out, prefix .. title)
    walk(sm, prefix .. title .. " > ")
  end
  for _, c in ipairs(node.commands or {}) do
    table.insert(out, prefix .. (c.isSecured and "+" or "") .. c.title)
  end
end
walk(root, "")
return table.concat(out, "\n")
"""


class Bridge:
    def __init__(self, url, key, lang):
        self.url, self.key, self.lang = url, key, lang

    def raw(self, code, timeout=30.0):
        return exec_over_bridge(self.url, self.key, code, timeout)

    def with_lib(self, body):
        return f'local R = (function()\n{LIB}\nreturn R\nend)()\nR.expected = "{self.lang}"\n{body}'

    def run(self, body, check):
        """Exécute `body` derrière la bibliothèque ; rend (statut, détail), statut OK / KO / ERR."""
        if check:
            tail = 'return (a and "OK" or "KO") .. "\\t" .. tostring(b == nil and "" or b)'
        else:
            tail = 'return "OK\\t"'
        code = self.with_lib(f"local ok, a, b = pcall(function()\n{body}\nend)\n"
                             f'if not ok then return "ERR\\t" .. tostring(a) end\n{tail}\n')
        try:
            res = self.raw(code)
        except RuntimeError as e:
            return "ERR", f"pont : {e}"
        status, _, detail = res.partition("\t")
        if status not in ("OK", "KO", "ERR"):
            return "ERR", f"réponse inattendue : {res[:200]!r}"
        return status, detail


results = []


def verdict(status, step, label, detail=""):
    results.append(status == "OK")
    mark = {"OK": "OK", "KO": "ÉCHEC", "ERR": "ERREUR"}[status]
    print(f"  [{mark}] {step} : {label}" + (f" — {detail}" if detail else ""), flush=True)


def menu_paths(text):
    """Les chemins « VEAF > … » d'une consigne, backticks retirés."""
    text = text.replace("`", "")
    return [m.group(1) for m in re.finditer(r"VEAF > (.+)", text)]


def check_menus(bridge, steps):
    lines = bridge.raw(bridge.with_lib(MENU_LUA)).split("\n")
    lang, known = lines[0], sorted(set(lines[1:]), key=len, reverse=True)
    print(f"\n===== chemins de menu ({lang}, {len(known)} entrées dans le menu VEAF)")
    if lang != bridge.lang:
        sys.exit(f"la mission chargée est en {lang!r}, la recette demandée en {bridge.lang!r} : mauvaise mission ?")
    for step in steps:
        for line in step["how"][lang]:
            for rest in menu_paths(line):
                hit = next((p for p in known if rest.startswith(p)
                            and (len(rest) == len(p) or not rest[len(p)].isalnum())), None)
                if hit is None:
                    verdict("KO", step["id"], "chemin de menu introuvable", f"VEAF > {rest[:120]}")
                elif rest[len(hit):].startswith(" > "):
                    verdict("KO", step["id"], "chemin de menu introuvable",
                            f"VEAF > {hit} existe, pas la suite : {rest[len(hit):][:80]}")
                else:
                    verdict("OK", step["id"], f"VEAF > {hit}")


def run_probes(bridge, steps):
    for step in steps:
        probes = step.get("probe") or []
        if not probes:
            continue
        print(f"\n===== {step['id']} : {step['title']['fr']}")
        for p in probes:
            if p.get("act"):
                status, detail = bridge.run(p["act"], check=False)
                if status != "OK":
                    verdict(status, step["id"], p["name"] + " (action)", detail)
                    continue
            if p.get("wait"):
                time.sleep(p["wait"])
            deadline = time.monotonic() + (p.get("timeout") or 0)
            while True:
                status, detail = bridge.run(p["check"], check=True)
                if status != "KO" or time.monotonic() >= deadline:
                    break
                time.sleep(POLL)
            verdict(status, step["id"], p["name"], detail)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", nargs="*", help="id des étapes à sonder (toutes par défaut)")
    ap.add_argument("--lang", required=True, choices=["fr", "en"], help="langue de la mission chargée (_FR ou _EN)")
    ap.add_argument("--menus", action="store_true", help="seulement les chemins de menu")
    ap.add_argument("--url", default=DEFAULT_SERVE_URL)
    ap.add_argument("--config", help="dcs-serve.yaml à lire pour la clé")
    args = ap.parse_args()
    unknown = set(args.steps) - {s["id"] for s in STEPS}
    if unknown:
        sys.exit(f"étapes inconnues : {sorted(unknown)}")
    steps = [s for s in STEPS if not args.steps or s["id"] in args.steps]

    bridge = Bridge(args.url, resolve_api_key(os.environ.get("DCS_BRIDGE_API_KEY"), args.config), args.lang)
    sys.stdout.reconfigure(encoding="utf-8")
    check_menus(bridge, steps)
    if not args.menus:
        run_probes(bridge, steps)
    failed = results.count(False)
    print(f"\n{len(results)} contrôle(s), {failed} en échec")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
