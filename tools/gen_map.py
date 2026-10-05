"""Cartes de la démo : la carte générale et un zoom par secteur, sur fond OpenStreetMap.

    python tools/gen_map.py

Sorties : docs/carte.jpg (en tête du README), docs/cartes/*.jpg (zooms), et les mêmes images dans
src/mission/l10n/DEFAULT/ pour le briefing DCS : déclarées dans mapResource, listées dans
pictureFileNameB et pictureFileNameN, pictureFileNameR vide (limite connue
briefing-pictures-red-then-blue ; le rouge n'est pas jouable ici). Le script réécrit ces listes : la
mission liste toujours ce qui a été dessiné.

Tout vient des données : src/mission/ (positions), mission.yaml (QRA, sanctuaire, arène),
tour/steps.yaml (numéros des étapes, les mêmes que dans le menu F10 et le README).
Tuiles OSM en cache dans .veaf-backups/tiles/ ; User-Agent qui identifie l'outil, sans donnée
personnelle (politique d'usage d'OpenStreetMap) ; mention « © OpenStreetMap contributors ».
"""
import math
import shutil
import sys
import time
from pathlib import Path

import requests
import yaml
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402,F401  (met le code VMCT sur sys.path)
import dcslua  # noqa: E402
from veaf_libs.coordinates import xy_to_latlon  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TILE = 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = {"User-Agent": "veaf-demo-mission-map/1.0 (+https://github.com/VEAF/VEAF-Demo-Mission-v6)"}
CACHE = ROOT / ".veaf-backups/tiles"
L10N = ROOT / "src/mission/l10n/DEFAULT"
NM = 1852
FONT, FONTB = r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"
BLUE, RED, GREEN, ORANGE, TEAL, INK, HALO = "#1f5fbf", "#c2362b", "#2e7f38", "#d9822b", "#0b86a8", "#1b2629", "#ffffff"

MIS = dcslua.load(ROOT / "src/mission/mission")
GROUPS, ZONES = dcslua.positions(MIS)
CFG = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
STEPS = yaml.safe_load((ROOT / "tour/steps.yaml").read_text(encoding="utf-8"))["steps"]
BULL = (MIS["coalition"]["blue"]["bullseye"]["x"], MIS["coalition"]["blue"]["bullseye"]["y"])
BASES = {"Kutaisi": (-284582.8, 685029.7), "Senaki": (-281903.1, 648379.2), "Kobuleti": (-317604.9, 636704.2),
         "Batumi": (-356437.1, 618210.9)}
RED_BASES = {"Sukhumi": (-221381.7, 565908.8), "Gudauta": (-195650.6, 515898.8)}
# Côté où écrire le nom d'une zone sur les zooms (à droite par défaut) : relu sur les images, pour
# qu'aucune étiquette n'en chevauche une autre (port et convoi d'Ochamchire sont à 2 km l'un de l'autre).
LABEL_SIDE = {"combatZone_Ochamchire_Port": "above", "combatZone_Convoi": "below",
              "combatZone_Ochamchire_Navires": "below"}


def ll(x, y):
    r = xy_to_latlon("Caucasus", x, y)
    return (r[0], r[1]) if isinstance(r, (tuple, list)) else (r["lat"], r["lon"])


def merc01(lat, lon):
    return ((lon + 180) / 360,
            (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2)


def route(name):
    for _, _, _, g in dcslua.groups(MIS):
        if g["name"] == name:
            return [(p["x"], p["y"]) for p in dcslua.seq(g["route"]["points"])]
    raise KeyError(name)


def anchor(step):
    a = step.get("anchor") or {}
    if "zone" in a:
        return ZONES[a["zone"]][:2]
    if "group" in a:
        return GROUPS[a["group"]]
    if "airbase" in a:
        return {**BASES, **RED_BASES, "Senaki-Kolkhi": BASES["Senaki"]}[a["airbase"]]
    return None


class View:
    def __init__(self, title, pts, out_w=1600, margin_m=8000):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        corners = [ll(x, y) for x in (min(xs) - margin_m, max(xs) + margin_m) for y in (min(ys) - margin_m, max(ys) + margin_m)]
        us, vs = zip(*(merc01(*c) for c in corners))
        self.u0, self.u1, self.v0, self.v1 = min(us), max(us), min(vs), max(vs)
        # niveau de tuiles le plus proche de la résolution de sortie : les noms de lieux restent lisibles
        self.zoom = max(1, min(14, round(math.log2(out_w / ((self.u1 - self.u0) * TILE)))))
        self.out_w = out_w
        self.k = out_w / (self.u1 - self.u0)
        self.out_h = round((self.v1 - self.v0) * self.k)
        self.title = title

    def px(self, p):
        u, v = merc01(*ll(*p))
        return ((u - self.u0) * self.k, (v - self.v0) * self.k)

    def m_to_px(self, p):
        lat = ll(*p)[0]
        return self.k / (40075016.686 * math.cos(math.radians(lat)))


def tile(z, x, y):
    f = CACHE / f"{z}/{x}/{y}.png"
    if not f.is_file():
        f.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(TILE_URL.format(z=z, x=x, y=y), headers=UA, timeout=30)
        r.raise_for_status()
        f.write_bytes(r.content)
        time.sleep(0.2)
    return Image.open(f).convert("RGB")


def basemap(v):
    n = 2 ** v.zoom
    tx0, tx1 = int(v.u0 * n), int(v.u1 * n)
    ty0, ty1 = int(v.v0 * n), int(v.v1 * n)
    big = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            big.paste(tile(v.zoom, tx, ty), ((tx - tx0) * TILE, (ty - ty0) * TILE))
    left, top = (v.u0 * n - tx0) * TILE, (v.v0 * n - ty0) * TILE
    w, h = (v.u1 - v.u0) * n * TILE, (v.v1 - v.v0) * n * TILE
    img = big.crop((round(left), round(top), round(left + w), round(top + h))).resize((v.out_w, v.out_h), Image.LANCZOS)
    return Image.blend(img, Image.new("RGB", img.size, "white"), 0.35)


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def text(d, xy, s, fill, size=18, bold=True, anchor="la"):
    d.text(xy, s, fill=fill, font=font(size, bold), anchor=anchor, stroke_width=3, stroke_fill=HALO)


def circle(d, v, c, r_m, color, width=3, dash=None, fill=None):
    x, y = v.px(c)
    r = r_m * v.m_to_px(c)
    if dash:
        steps = max(24, int(2 * math.pi * r / (dash * 2)))
        for i in range(0, steps, 2):
            a0, a1 = 2 * math.pi * i / steps, 2 * math.pi * (i + 1) / steps
            d.line([(x + r * math.cos(a0), y + r * math.sin(a0)), (x + r * math.cos(a1), y + r * math.sin(a1))], fill=color, width=width)
    else:
        d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=width, fill=fill)


def badge(d, v, p, n, color):
    x, y = v.px(p)
    d.ellipse([x - 15, y - 15, x + 15, y + 15], fill=color, outline=HALO, width=3)
    d.text((x, y), f"{n}", fill="white", font=font(16, True), anchor="mm")


def draw(v, legend=True):
    img = basemap(v)
    d = ImageDraw.Draw(img, "RGBA")
    # zones de combat (rouge) et d'entraînement (vert), au rayon réel
    for z in CFG["modules"]["COMBATZONE"]["combat_zones"]:
        if z.get("type") == "operation":
            continue
        tz = ZONES[z["zone_name"]]
        col = GREEN if z.get("training") else RED
        circle(d, v, tz[:2], tz[2], col, 3)
        # sur les zooms, le nom à côté du cercle ; les tâches de l'opération sont nommées une fois
        if not legend and not z["zone_name"].endswith(("_Medium", "_Hard")) and "_Tkvarcheli_" not in z["zone_name"]:
            x, y = v.px(tz[:2])
            r = tz[2] * v.m_to_px(tz[:2])
            name = z["friendly_name"].replace(" - facile", " (3 niveaux)")
            side = LABEL_SIDE.get(z["zone_name"], "right")
            xy_, anch = {"right": ((x + r + 6, y), "lm"), "left": ((x - r - 6, y), "rm"),
                         "below": ((x, y + r + 4), "mt"), "above": ((x, y - r - 4), "mb")}[side]
            text(d, xy_, name, col, 16, anchor=anch)
    # zones de service : bac à sable (point nommé ALPHA) et pilote abattu à la demande
    for zn, label_ in (("Bac a sable", "Bac à sable (ALPHA)"), ("Demo CSAR", "Pilote abattu (CSAR)")):
        tz = ZONES[zn]
        circle(d, v, tz[:2], tz[2], "#6a3d9a", 3, dash=6)
        if not legend:
            x, y = v.px(tz[:2])
            text(d, (x + tz[2] * v.m_to_px(tz[:2]) + 6, y), label_, "#6a3d9a", 16, anchor="lm")
    if not legend:
        x, y = v.px(ZONES["Op_Tkvarcheli"][:2])
        text(d, (x + 30, y - 40), "Opération Tkvarcheli (3 tâches)", RED, 16, anchor="lm")
    # QRA, sanctuaire : cercles en tirets ; arène : orange
    for q in CFG["modules"]["QRA"]["definitions"]:
        tz = ZONES[q["trigger_zone"]]
        circle(d, v, tz[:2], tz[2], RED, 3, dash=10)
        x, y = v.px((tz[0] + tz[2], tz[1]))
        text(d, (x, y + 4), q["name"], RED, 16, anchor="mt")
    for s in CFG["modules"]["SANCTUARY"]["sanctuary_zones"]:
        tz = ZONES[s["trigger_zone"]]
        circle(d, v, tz[:2], tz[2], RED, 3, dash=6)
        x, y = v.px((tz[0] - tz[2], tz[1]))
        text(d, (x, y - 4), "Sanctuaire", RED, 16, anchor="mb")
    for a in CFG["modules"]["AIRWAVES"]["airwave_zones"]:
        tz = ZONES[a["trigger_zone_name"]]
        circle(d, v, tz[:2], tz[2], ORANGE, 4, dash=12)
        x, y = v.px((tz[0] + tz[2], tz[1]))
        text(d, (x, y + 4), "Arène BVR", ORANGE, 16, anchor="mt")
    # portée du SA-11 permanent (50 km, list_unit_types)
    sa11 = next(p for n, p in GROUPS.items() if n.startswith('#veafInterpreter["-sa11'))
    circle(d, v, sa11, 50000, "#c2362b80", 2, dash=5)
    x, y = v.px((sa11[0] + 50000, sa11[1]))
    text(d, (x, y + 4), "SA-11 (50 km)", RED, 14, bold=False, anchor="mt")
    # hippodromes de soutien
    for n in ("Texaco 1", "Arco 1", "Overlord 1"):
        r = route(n)
        d.line([v.px(r[0]), v.px(r[1])], fill=TEAL, width=6)
        text(d, (v.px(r[1])[0] + 8, v.px(r[1])[1]), n, TEAL, 16)
    # convoi
    r = route("combatZone_Convoi-colonne")
    d.line([v.px(p) for p in r], fill=RED, width=3)
    # bases, FARP, porte-avions, bullseye
    for n, p in BASES.items():
        x, y = v.px(p)
        d.rectangle([x - 8, y - 8, x + 8, y + 8], fill=BLUE, outline=HALO, width=2)
        text(d, (x + 12, y - 2), n, BLUE, 18, anchor="lm")
    for n, p in RED_BASES.items():
        x, y = v.px(p)
        d.rectangle([x - 7, y - 7, x + 7, y + 7], fill=RED, outline=HALO, width=2)
        text(d, (x + 12, y - 2), n, RED, 16, anchor="lm")
    for n in ("FARP Khoni", "CSG-74 Stennis", "CSG-71 Roosevelt"):
        x, y = v.px(GROUPS[n])
        d.polygon([(x, y - 10), (x + 9, y + 7), (x - 9, y + 7)], fill=BLUE, outline=HALO)
        text(d, (x + 12, y), n.replace("CSG-74 ", "").replace("CSG-71 ", ""), BLUE, 16, anchor="lm")
    x, y = v.px(BULL)
    for r in (6, 12):
        d.ellipse([x - r, y - r, x + r, y + r], outline=INK, width=2)
    text(d, (x, y - 16), "BULLSEYE", INK, 14, anchor="mb")
    # étapes numérotées (même numéro que le menu F10 et le README)
    for i, s in enumerate(STEPS, 1):
        p = anchor(s)
        if p and s["id"] not in ("generated", "weather"):
            badge(d, v, p, i, "#6a3d9a")
    # titre, échelle, légende, attribution
    d.rectangle([0, 0, v.out_w, 44], fill=(255, 255, 255, 220))
    text(d, (14, 8), v.title, INK, 24)
    centre = ((-290000, 600000))
    for nm_ in (5, 10, 20, 50):
        w = nm_ * NM * v.m_to_px(centre)
        if w > v.out_w / 8:
            break
    y0 = v.out_h - 40
    d.rectangle([14, y0, 14 + w, y0 + 8], fill=INK)
    text(d, (14, y0 - 4), f"{nm_} nm", INK, 15, anchor="lb")
    text(d, (v.out_w - 10, v.out_h - 8), "© OpenStreetMap contributors", INK, 13, bold=False, anchor="rb")
    if legend:
        items = [(GREEN, "zone d'entraînement"), (RED, "zone de combat"), (TEAL, "ravitailleur / AWACS"),
                 (ORANGE, "arène BVR"), ("#6a3d9a", "étape de la visite (n°)")]
        lx, ly = v.out_w - 260, 56
        d.rectangle([lx - 10, ly - 8, v.out_w - 10, ly + 24 * len(items) + 4], fill=(255, 255, 255, 220))
        for i, (c, t) in enumerate(items):
            d.rectangle([lx, ly + 24 * i + 4, lx + 18, ly + 24 * i + 18], fill=c)
            text(d, (lx + 26, ly + 24 * i), t, INK, 15, bold=False)
    return img


def pts_of(*names):
    out = []
    for n in names:
        if n in ZONES:
            x, y, r = ZONES[n]
            out += [(x - r, y - r), (x + r, y + r)]
        elif n in GROUPS:
            out.append(GROUPS[n])
        else:
            out.append({**BASES, **RED_BASES}[n])
    return out


def main():
    all_pts = [p for s in STEPS if (p := anchor(s))] + list(BASES.values()) + list(RED_BASES.values()) + \
              [GROUPS["CSG-71 Roosevelt"]] + route("Arco 1") + route("Texaco 1") + \
              pts_of("QRA-Soukhoumi", "Sanctuaire Gudauta", "Arene BVR")
    views = [
        ("carte", "Mission de démo VEAF — Caucase", all_pts, 10000),
        ("01-kutaisi-khoni", "Kutaisi et Khoni : bac à sable, entraînement, FARP, CSAR",
         pts_of("Bac a sable", "combatZone_Khoni_Easy", "FARP Khoni", "Demo CSAR", "Kutaisi", "Senaki"), 6000),
        ("02-front", "Front : Gali, Ochamchire, Tkvarcheli, convoi",
         pts_of("combatZone_Gali", "combatZone_Ochamchire_SAM", "combatZone_Ochamchire_Navires", "Op_Tkvarcheli",
                "combatZone_Convoi"), 6000),
        ("03-mer", "Mer : arène BVR, porte-avions, Arco 1",
         pts_of("Arene BVR", "CSG-74 Stennis", "CSG-71 Roosevelt", "Batumi") + route("Arco 1"), 8000),
        ("04-abkhazie", "Soukhoumi et Gudauta : IADS, QRA, sanctuaire",
         pts_of("QRA-Soukhoumi", "Sanctuaire Gudauta"), 6000),
    ]
    (ROOT / "docs/cartes").mkdir(parents=True, exist_ok=True)
    written = []
    for key, title, pts, margin in views:
        v = View(title, pts, margin_m=margin)
        img = draw(v, legend=(key == "carte"))
        out = ROOT / ("docs/carte.jpg" if key == "carte" else f"docs/cartes/{key}.jpg")
        img.save(out, quality=85)
        shutil.copyfile(out, L10N / f"demo-{key}.jpg")
        written.append(f"demo-{key}.jpg")
        print(f"{out.relative_to(ROOT)} ({v.out_w}x{v.out_h}, tuiles z{v.zoom})")
    declare(written)


def declare(files):
    """Déclare les images dans mapResource et dans pictureFileNameB/N (R vide), en retirant les anciennes."""
    from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission
    import luadata
    keys = [f"ResKey_ImageBriefing_{Path(f).stem}" for f in files]
    mis = load_folder_mission(ROOT)
    mis.mission_content["pictureFileNameB"] = list(keys)
    mis.mission_content["pictureFileNameN"] = list(keys)
    mis.mission_content["pictureFileNameR"] = []
    save_folder_mission(mis, ROOT)
    path = L10N / "mapResource"
    resources = {k: v for k, v in dict(mis.map_resource_content or {}).items() if not k.startswith("ResKey_ImageBriefing_demo-")}
    for f in L10N.glob("demo-*.jpg"):
        if f.name not in files:
            f.unlink()
    resources.update({k: f for k, f in zip(keys, files)})
    bk = ROOT / ".veaf-backups/l10n-DEFAULT"
    bk.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, bk / f"mapResource.{time.strftime('%Y%m%d-%H%M%S')}")
    path.write_text("mapResource = \n" + luadata.serialize(resources, indent="  ", indent_level=0,
                                                            always_provide_keyname=True, sort=True),
                    encoding="utf-8", newline="\n")
    print("briefing :", len(keys), "images en B et N, R vide")


if __name__ == "__main__":
    main()
