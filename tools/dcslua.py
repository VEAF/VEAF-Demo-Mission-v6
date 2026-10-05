"""Lecture d'une table Lua au format des fichiers DCS (`mission`, `warehouses`, `options`…).

Lecture seule : les écritures dans src/mission/ passent par les actions MCP. Couvre ce que DCS
écrit : `nom = { ... }`, clés `[n]`, `["texte"]` ou nues, chaînes entre guillemets avec échappements,
nombres, true/false/nil, commentaires `--`.
"""
import re

_TOKEN = re.compile(r"""
    \s+|--\[\[.*?\]\]|--[^\n]*|
    (?P<str>"(?:\\.|[^"\\])*")|
    (?P<num>-?(?:0x[0-9a-fA-F]+|\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?))|
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)|
    (?P<sym>[{}\[\]=,;])
""", re.X | re.S)

_ESC = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "\n": "\n"}


def _tokens(text):
    pos = 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise ValueError(f"caractère inattendu à {pos}: {text[pos:pos + 30]!r}")
        pos = m.end()
        kind = m.lastgroup
        if kind:
            yield kind, m.group(kind)


def _unescape(s):
    body = s[1:-1]
    return re.sub(r"\\(\d{1,3}|.)", lambda m: chr(int(m.group(1))) if m.group(1).isdigit() else _ESC.get(m.group(1), m.group(1)), body, flags=re.S)


class _Parser:
    def __init__(self, text):
        self.toks = list(_tokens(text))
        self.i = 0

    def peek(self, k=0):
        return self.toks[self.i + k] if self.i + k < len(self.toks) else (None, None)

    def take(self):
        t = self.toks[self.i]
        self.i += 1
        return t

    def value(self):
        kind, v = self.take()
        if kind == "str":
            return _unescape(v)
        if kind == "num":
            return int(v, 16) if v.lower().startswith(("0x", "-0x")) else (float(v) if any(c in v for c in ".eE") else int(v))
        if kind == "name":
            return {"true": True, "false": False, "nil": None}[v]
        if v == "{":
            return self.table()
        raise ValueError(f"valeur attendue, trouvé {v!r}")

    def table(self):
        out, n = {}, 1
        while True:
            kind, v = self.peek()
            if v == "}":
                self.take()
                break
            if v == "[":
                self.take()
                key = self.value()
                self.take()  # ]
                self.take()  # =
                out[key] = self.value()
            elif kind == "name" and self.peek(1)[1] == "=":
                self.take()
                self.take()
                out[v] = self.value()
            else:
                out[n] = self.value()
                n += 1
            if self.peek()[1] in (",", ";"):
                self.take()
        return out


def load(path):
    """Lit un fichier `nom = { ... }` et rend la table (dict ; un tableau Lua a des clés 1..n)."""
    text = open(path, encoding="utf-8").read()
    p = _Parser(text)
    p.take()  # nom
    p.take()  # =
    return p.value()


def seq(t):
    """Les éléments d'un tableau Lua (clés 1..n), dans l'ordre."""
    if not isinstance(t, dict):
        return []
    return [t[k] for k in sorted(k for k in t if isinstance(k, int))]


def groups(mission):
    """Itère (coalition, pays, catégorie, groupe) sur tous les groupes de la mission."""
    for side, coal in mission["coalition"].items():
        for country in seq(coal.get("country", {})):
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in seq(country.get(cat, {}).get("group", {})):
                    yield side, country["name"], cat, g


def positions(mission):
    """Nom de groupe -> (x, y) de sa première unité ; nom de zone -> (x, y, rayon)."""
    grp = {}
    for _, _, _, g in groups(mission):
        u = seq(g.get("units", {}))
        if u:
            grp[g["name"]] = (u[0]["x"], u[0]["y"])
            for unit in u:
                grp.setdefault(unit.get("name"), (unit["x"], unit["y"]))
    zones = {z["name"]: (z["x"], z["y"], z.get("radius", 0)) for z in seq(mission["triggers"]["zones"])}
    return grp, zones
