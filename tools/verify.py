"""Contrôle des .miz construits : un verdict OK / ÉCHEC par contrôle, lu dans le .miz (lecteur de VMCT),
jamais par recherche de texte dans les sources.

    python tools/verify.py                  # tous les .miz de missions/ et de la racine
    python tools/verify.py chemin.miz ...   # ceux-là

Se termine en erreur si un contrôle échoue. Adapté de l'outil de l'Open Training Caucase v6.
"""
import collections
import math
import sys
import zipfile
from pathlib import Path

import yaml

from paths import VMCT  # noqa: F401  (met le code VMCT sur sys.path)
from mission_tools.miz_tools import read_miz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
STEPS = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))["steps"]
AIRDROMES = {v: k for k, v in yaml.safe_load(
    (VMCT / "src/python/veaf-tools/veaf_libs/data/airdromes.yaml").read_text(encoding="utf-8"))["theatres"]["Caucasus"].items()}
DYN_BASES = {"Kutaisi", "Senaki-Kolkhi", "Kobuleti", "Batumi"}
# Support : tâches attendues sur le premier point (ids DCS).
SUPPORT = {"Texaco 1": {"Tanker", "Orbit", "ActivateBeacon"}, "Arco 1": {"Tanker", "Orbit", "ActivateBeacon"},
           "Overlord 1": {"AWACS", "Orbit", "EPLRS"}, "Overlord 1 escort": {"Escort"}}
# Porteurs #veafInterpreter : type attendu = le lanceur que l'alias génère.
INTERP = {"-sa11": "SA-11 Buk LN 9A310M1", "-sa15": "Tor 9A331", "-ewr": "55G6 EWR",
          "-nasams": "NASAMS_LN_C", "-hawk": "Hawk ln"}

failures = []


def verdict(ok, label, detail=""):
    print(f"  [{'OK' if ok else 'ÉCHEC'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def seq(v):
    return list(v.values()) if isinstance(v, dict) else list(v or [])


def groups(m):
    for side, co in m["coalition"].items():
        for c in seq(co.get("country")):
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in seq((c.get(cat) or {}).get("group")):
                    yield side, c.get("name"), cat, g


def task_ids(point):
    out = set()
    for t in seq(((point.get("task") or {}).get("params") or {}).get("tasks")):
        out.add(t["id"] if t["id"] != "WrappedAction" else t["params"]["action"]["id"])
    return out


def check(path):
    print(f"\n===== {Path(path).name}")
    miz = read_miz(Path(path))
    m = miz.mission_content
    gnames, unames, gid, uid = (collections.Counter() for _ in range(4))
    by_name, problems = {}, []
    for side, _country, cat, g in groups(m):
        gnames[g["name"]] += 1
        gid[g["groupId"]] += 1
        by_name[g["name"]] = (side, cat, g)
        for u in seq(g["units"]):
            unames[u["name"]] += 1
            uid[u["unitId"]] += 1
            by_name.setdefault(u["name"], (side, cat, g))
            if cat in ("plane", "helicopter") and not g.get("dynSpawnTemplate") and not g["name"].startswith("veafSpawn-"):
                pt0 = seq(g["route"]["points"])[0]
                if (u.get("alt") or 0) <= 0 and "TakeOff" not in (pt0.get("type") or ""):
                    problems.append(f"altitude <= 0 : {g['name']}")
                if not (u.get("payload") or {}).get("fuel"):
                    problems.append(f"sans carburant : {g['name']}")
            if cat == "static" and not u.get("category"):
                problems.append(f"statique sans category : {g['name']} {u['type']}")
    dup = lambda c: [k for k, v in c.items() if v > 1]  # noqa: E731
    verdict(not dup(gnames) and not dup(unames), "noms de groupes et d'unités uniques", f"{dup(gnames)[:3]} {dup(unames)[:3]}")
    verdict(not dup(gid) and not dup(uid), "identifiants de groupes et d'unités uniques")
    verdict(not problems, "structure des avions et des statiques", "; ".join(problems[:5]))

    dyn = {AIRDROMES.get(int(k), k) for k, a in (miz.warehouses_content.get("airports") or {}).items()
           if isinstance(a, dict) and a.get("dynamicSpawn")}
    verdict(dyn == DYN_BASES, "slots dynamiques sur les quatre bases bleues seulement", str(sorted(dyn)))

    for name, expected in SUPPORT.items():
        g = by_name.get(name, (None, None, None))[2]
        got = task_ids(seq(g["route"]["points"])[0]) if g else set()
        verdict(expected <= got, f"tâches de {name}", f"attendu {sorted(expected)}, trouvé {sorted(got)}")

    g = by_name.get("combatZone_Convoi-colonne", (None, None, None))[2]
    pts = seq(g["route"]["points"]) if g else []
    verdict(len(pts) >= 2, "le convoi a une route", f"{len(pts)} points")

    bad = []
    for alias, typ in INTERP.items():
        carriers = [(n, by_name[n][2]) for n in unames if f'#veafInterpreter["{alias},' in n]
        for n, gg in carriers:
            utypes = {u["type"] for u in seq(gg["units"]) if u["name"] == n}
            if utypes != {typ}:
                bad.append(f"{n}: {utypes}")
        if not carriers:
            bad.append(f"{alias} absent")
    verdict(not bad, "porteurs #veafInterpreter du type du lanceur", "; ".join(bad))

    verdict(not m.get("requiredModules"), "requiredModules vide", str(m.get("requiredModules")))

    assets = CFG["modules"]["ASSETS"]["assets"]
    missing = [a["name"] for a in assets if a["name"] not in gnames] + \
              [a["name"] + " escort" for a in assets if a["name"] + " escort" in ("Overlord 1 escort",) and a["name"] + " escort" not in gnames]
    verdict(not missing, "chaque moyen de modules.ASSETS a son groupe", str(missing))

    zones = {z["name"] for z in seq(m["triggers"]["zones"])}
    lost = []
    for s in STEPS:
        a = s.get("anchor") or {}
        if "zone" in a and a["zone"] not in zones:
            lost.append(a["zone"])
        if "group" in a and a["group"] not in by_name:
            lost.append(a["group"])
        if "airbase" in a and a["airbase"] not in AIRDROMES.values():
            lost.append(a["airbase"])
    verdict(not lost, "chaque lieu de la visite existe dans la mission", str(lost))

    with zipfile.ZipFile(path) as z:
        files = z.namelist()
        cfg = next((n for n in files if n.endswith("veaf-config.lua")), None)
        txt = z.read(cfg).decode("utf-8") if cfg else ""
        tour = any(n.endswith("guided-tour.lua") for n in files)
    verdict(tour, "guided-tour.lua embarqué")
    if Path(path).parent.name == "missions":
        level = next((ln.strip() for ln in txt.splitlines() if "veaf.ForcedLogLevel" in ln), "")
        verdict("debug" not in level and "trace" not in level, "niveau de log de serveur (pas debug)", level)
    verdict("veaf.SecurityDisabled = true" in txt, "sécurité désactivée dans veaf-config.lua")
    counts = {"AddZone": txt.count("veafCombatZone.AddZone"), "operations": txt.count("VeafCombatOperation:new"),
              "VeafQRA": txt.count("VeafQRA:new"), "CAP": txt.count("addCapMission("),
              "sanctuaires": txt.count("veafSanctuary.addZoneFromTriggerZone(")}
    verdict(counts["AddZone"] >= 12 and counts["operations"] == 1 and counts["VeafQRA"] == 1 and counts["CAP"] == 3 and counts["sanctuaires"] == 1,
            "zones, opération, QRA, CAP et sanctuaire dans veaf-config.lua", str(counts))

    pics = {k: seq(m.get(k)) for k in ("pictureFileNameB", "pictureFileNameN", "pictureFileNameR")}
    verdict(bool(pics["pictureFileNameB"]) and pics["pictureFileNameB"] == pics["pictureFileNameN"] and not pics["pictureFileNameR"],
            "images de briefing en B et N, R vide", f"B {len(pics['pictureFileNameB'])}, N {len(pics['pictureFileNameN'])}, R {len(pics['pictureFileNameR'])}")
    w = m["weather"]
    return (w.get("clouds", {}).get("preset"), w.get("season", {}).get("temperature"),
            (w.get("wind", {}).get("atGround") or {}).get("speed"), m.get("start_time"))


def check_sources():
    """Ce qui se voit dans les sources et casse la mission au chargement."""
    print("\n===== sources")
    # Une action `lua` de modules.RADIO.user_menus est écrite comme une référence nue dans
    # veaf-config.lua, chargé AVANT mission-script.lua : la config s'arrête sur `nil` (retours-vmct n° 8).
    def lua_actions(nodes):
        for n in nodes or []:
            if n.get("action") == "lua":
                yield n.get("function")
            yield from lua_actions(n.get("items"))
    tree = ((CFG["modules"].get("RADIO") or {}).get("user_menus") or {}).get("tree")
    found = list(lua_actions(tree))
    verdict(not found, "aucune action `lua` dans modules.RADIO.user_menus", str(found))
    # Le lecteur YAML de CTLD lit `clé: valeur  # commentaire` comme la valeur « valeur  # commentaire » :
    # sur jtacLaserCodeMax, l'init de CTLD plante et veaf-config.lua s'arrête avec elle (retours-vmct n° 12).
    import re
    inline = [f"{i}: {ln.strip()}" for i, ln in enumerate((ROOT / "ctld-config.yaml").read_text(encoding="utf-8").splitlines(), 1)
              if re.match(r"^\s*[\w.-]+:\s+[^\s#'\"][^#]*\s#", ln)]
    verdict(not inline, "ctld-config.yaml sans commentaire en fin de ligne", "; ".join(inline[:3]))


if __name__ == "__main__":
    check_sources()
    paths = sys.argv[1:] or sorted(str(p) for p in list((ROOT / "missions").glob("*.miz")) + list(ROOT.glob("*.miz")))
    variants = [p for p in paths if Path(p).parent.name == "missions"]
    expected = len(yaml.safe_load((ROOT / "src/versions.yaml").read_text(encoding="utf-8"))["versions"])
    if not sys.argv[1:]:
        verdict(len(variants) == expected, "toutes les variantes météo sont construites",
                f"{len(variants)} dans missions/, {expected} attendues (lancer `veaf-tools build`)")
    weathers = {Path(p).name: check(p) for p in paths}
    if len(weathers) > 1:
        print("\n===== variantes météo (clouds.preset, température, vent au sol, heure de départ)")
        for n, w in weathers.items():
            print(f"  {n}: {w}")
        verdict(len(set(weathers.values())) == len(weathers), "chaque variante diffère dans les champs que DCS lit")
    print(f"\n{len(failures)} contrôle(s) en échec" + (" : " + ", ".join(sorted(set(failures))) if failures else ""))
    sys.exit(1 if failures else 0)
