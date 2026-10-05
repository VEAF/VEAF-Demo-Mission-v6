"""Outils communs aux générateurs de lots (tools/gen_*.py) de la mission de démo.

Chaque générateur écrit un fichier de lot dans tools/batches/ ; tools/mcp.py l'exécute sur le
catalogue d'actions de veaf-mission-mcp (code VMCT de develop, voir paths.py).
Les lots ne sont pas idempotents (une action « add » rejouée crée un second groupe) : ils servent à
construire la mission une fois, et à relire après coup ce qui a été posé et pourquoi.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = str(ROOT).replace("\\", "/")
NM = 1852

BLUE = dict(coalition="blue", country_id=2, country_name="USA")
RED = dict(coalition="red", country_id=0, country_name="Russia")

# Aérodromes de la démo (list_airfields, Caucasus).
AIRFIELDS = {
    "Kutaisi": (-284582.8, 685029.7),
    "Senaki-Kolkhi": (-281903.1, 648379.2),
    "Kobuleti": (-317604.9, 636704.2),
    "Batumi": (-356437.1, 618210.9),
    "Sukhumi-Babushara": (-221381.7, 565908.8),
    "Gudauta": (-195650.6, 515898.8),
    "Sochi-Adler": (-165163.3, 460901.6),
}

# Lieux géocodés le 2026-10-05 (geocode, OSM) : centre de la ville, à décaler pour poser une zone.
PLACES = {
    "Khoni": (-269098.9, 677147.1),
    "Abasha": (-284390.1, 660543.8),
    "Zugdidi": (-253719.1, 629600.7),
    "Poti": (-296043.7, 617584.1),
    "Gali": (-241346.0, 617136.8),
    "Ochamchire": (-234333.1, 594446.8),
    "Tkvarcheli": (-217565.1, 610142.3),
}

# Bullseye commun aux deux camps : Zugdidi, sur la ligne de front de l'Inguri, nommable par tous.
BULLSEYE = PLACES["Zugdidi"]


def xy(p):
    return {"x": round(p[0], 1), "y": round(p[1], 1)}


def nm(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) / NM


def off(p, brg, m):
    """Point à `m` mètres de `p`, au relèvement `brg` (degrés, x = nord, y = est)."""
    r = math.radians(brg)
    return (p[0] + m * math.cos(r), p[1] + m * math.sin(r))


def bearing(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 360


def bullseye(p):
    """« BULLSEYE 123/45 » : cap = atan2(Δy, Δx), distance en nm."""
    return f"BULLSEYE {bearing(BULLSEYE, p):03.0f}/{nm(BULLSEYE, p):.0f}"


class Batch:
    def __init__(self):
        self.items = []

    def act(self, action, **params):
        self.items.append({"name": action, "params": {"mission_path": M, **params}})

    def save(self, name):
        path = ROOT / "tools/batches" / name
        path.write_text(json.dumps(self.items, indent=1, ensure_ascii=False), encoding="utf-8")
        print(len(self.items), "actions ->", path.name)


def cmd_unit(alias_cmd, carrier_type, tag, extra=""):
    """Faux porteur de zone : `#command="<alias ...>"` + suffixe unique (+ balises de tirage).

    Le porteur est du type que l'alias génère, pour que l'éditeur montre le bon cercle de portée.
    """
    name = f'#command="{alias_cmd}"'
    if extra:
        name += " " + extra
    return {"type": carrier_type, "name": f"{name} {tag}"}


def interp_unit(alias_cmd, carrier_type, tag):
    """Batterie permanente : `#veafInterpreter["<commande>"]` + suffixe unique."""
    return {"type": carrier_type, "name": f'#veafInterpreter["{alias_cmd}"] {tag}'}
