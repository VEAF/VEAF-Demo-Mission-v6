"""Lot 02 : zones de combat — une mécanique par zone, pour que chaque étape de la visite en montre une.

- Khoni : entraînement en 3 niveaux imbriqués (`includes:`), `defense N`, tirage `#spawngroup`.
- Gali : vraie zone de front, faux porteurs `#command`, tirage d'un groupe blindé parmi deux.
- Ochamchire SAM : zone `active_at_start`, intégrée au réseau Skynet.
- Ochamchire port -> navires : `chained_zones` (la seconde n'apparaît qu'après la première).
- Tkvarcheli : opération (`type: operation`) en trois tâches, la troisième dépendant des deux autres.
- Convoi : groupe natif qui roule en boucle entre Ochamchire et Gali.

Les entrées `operation` et les clés de chaînage sont écrites dans mission.yaml par ce lot (via
create_combat_zone) ; l'opération elle-même est ajoutée à la main dans mission.yaml (aucune action
MCP ne la crée — voir « Retours pour VMCT »).

Noms d'avant le lot 07 : ce lot crée des groupes et des zones que tools/gen_07_noms.py renomme ensuite en
anglais neutre. Les lots se rejouent dans l'ordre (01 → 08), pas isolément.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, PLACES, RED, Batch, bullseye, cmd_unit, off, xy  # noqa: E402

b = Batch()


def zone(name, center, radius, groups, friendly, briefing, category="vehicle", side=RED, **cz):
    cz = {"friendly_name": friendly, "briefing": briefing, **cz}
    b.act("create_combat_zone", zone_name=name, position=xy(center), radius=radius,
          groups=groups, **side, category=category, combat_zone=cz)


def g(name, units, pos, **kw):
    return {"name": name, "units": units, "position": xy(pos), **kw}


# ── 1. Entraînement de Khoni : facile ⊂ moyen ⊂ difficile ────────────────────────────────────
# 11 km du FARP Khoni, 22 km de Kutaisi. Pas de SA-8 au niveau difficile : il porte à 10 km et
# atteindrait presque le FARP ; la défense la plus longue ici est un SA-13 / Igla (~5 km).
K = off(PLACES["Khoni"], 290, 12000)
EASY = ["Ural-375", "Ural-375", "KAMAZ Truck", "KAMAZ Truck", "GAZ-66", "ZIL-131 KUNG", "Ural-375 PBU", "ATZ-5"]
zone("combatZone_Khoni_Easy", K, 2500,
     [g(f"cible-{i + 1:02d}", [{"type": t}], off(K, 45 * i, 400 + 50 * i)) for i, t in enumerate(EASY)],
     "Khoni - facile", "Cibles inertes : huit camions à l'arrêt, sans arme ni défense. " + bullseye(K) + ".",
     training=True, radio_group_name="Entraînement Khoni")
MED_AAA = [("-zu23", "Ural-375 ZU-23"), ("-zu23", "Ural-375 ZU-23"), ("-shilka", "ZSU-23-4 Shilka"),
           ("-shilka", "ZSU-23-4 Shilka")]
zone("combatZone_Khoni_Medium", K, 2500,
     [g("blindes", [cmd_unit("-armor, defense 1, size 4", "T-72B", "KhoM-1")], off(K, 200, 1200))]
     + [g(f"aaa-{i + 1}", [cmd_unit(a, t, f"KhoM-a{i + 1}", '#spawngroup="aaa" #spawncount=2')], off(K, 90 * i + 45, 1000))
        for i, (a, t) in enumerate(MED_AAA)],
     "Khoni - moyen",
     "Les cibles du niveau facile, plus une compagnie blindée (`-armor, defense 1`) et deux pièces de DCA "
     "tirées au sort parmi quatre. " + bullseye(K) + ".",
     training=True, radio_group_name="Entraînement Khoni", includes=["combatZone_Khoni_Easy"])
HARD = [("-sa13_squad", "Strela-10M3"), ("-sa9_squad", "Strela-1 9P31"), ("-sa18s", "SA-18 Igla-S manpad"),
        ("-shilka", "ZSU-23-4 Shilka")]
zone("combatZone_Khoni_Hard", K, 2500,
     [g("bataillon", [cmd_unit("-armor, defense 3, size 6", "T-72B", "KhoH-1")], off(K, 20, 1500))]
     + [g(f"sr-{i + 1}", [cmd_unit(a, t, f"KhoH-s{i + 1}", '#spawngroup="sr" #spawncount=2')], off(K, 90 * i, 1800))
        for i, (a, t) in enumerate(HARD)],
     "Khoni - difficile",
     "Le niveau moyen, plus un bataillon blindé mieux défendu (`-armor, defense 3`) et deux systèmes courte "
     "portée tirés au sort parmi SA-13, SA-9, Igla et Shilka. " + bullseye(K) + ".",
     training=True, radio_group_name="Entraînement Khoni", includes=["combatZone_Khoni_Medium"])

# ── 2. Front de Gali ─────────────────────────────────────────────────────────────────────────
GA = off(PLACES["Gali"], 150, 3000)
zone("combatZone_Gali", GA, 3000,
     [g("blindes-a", [cmd_unit("-armor, defense 0, size 8", "T-72B", "Gali-1", '#spawngroup="blindes" #spawncount=1')],
        off(GA, 0, 1200)),
      g("blindes-b", [cmd_unit("-armor, defense 0, size 8, armor 4", "T-72B", "Gali-2", '#spawngroup="blindes" #spawncount=1')],
        off(GA, 180, 1200)),
      g("artillerie", [cmd_unit("-msta", "SAU Msta", "Gali-3")], off(GA, 270, 2000)),
      g("dca", [cmd_unit("-samSR", "Strela-10M3", "Gali-4")], off(GA, 90, 800)),
      g("guetteurs", [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "Gali-5")], off(GA, 315, 2200))],
     "Front de Gali",
     "Une brigade blindée tient la rive nord de l'Inguri, au sud-est de Gali. Détruire les blindés et la "
     "batterie d'artillerie Msta. Défense : une batterie sol-air courte portée tirée au sort et des MANPADS. "
     "Un drone Reaper 1 (JTAC) orbite au-dessus. " + bullseye(GA) + ".")

# ── 3. Batterie SA-6 d'Ochamchire, active au démarrage, dans le réseau Skynet ───────────────────
S = off(PLACES["Ochamchire"], 0, 9000)
zone("combatZone_Ochamchire_SAM", S, 1500,
     [g("sa6", [cmd_unit("-sa6", "Kub 2P25 ln", "OchS-1")], S),
      g("aaa", [cmd_unit("-shilka", "ZSU-23-4 Shilka", "OchS-2")], off(S, 120, 600))],
     "SAM d'Ochamchire",
     "Une batterie SA-6 au nord d'Ochamchire, active dès le début de la mission et reliée au réseau "
     "Skynet rouge : elle n'allume son radar que quand le réseau le lui demande. " + bullseye(S) + ".",
     active_at_start=True)

# ── 4. Port d'Ochamchire, puis ses navires (chaînage) ─────────────────────────────────────────
P = off(PLACES["Ochamchire"], 45, 1500)
zone("combatZone_Ochamchire_Port", P, 1200,
     [g("camions", [{"type": "Ural-375", "count": 3}, {"type": "KAMAZ Truck", "count": 2}], off(P, 0, 200)),
      g("dca", [cmd_unit("-zu23", "Ural-375 ZU-23", "OchP-1")], off(P, 180, 400))],
     "Port d'Ochamchire - 1 : dépôt",
     "Première étape d'une mission chaînée : détruire les camions du dépôt portuaire. Une fois le dépôt "
     "détruit, les navires en rade apparaissent (étape 2). " + bullseye(P) + ".",
     chained_zones=["combatZone_Ochamchire_Navires"], chained_delay=60)
N = (-238000, 585000)   # en rade, ~10 km au large (vérifié en lat/lon : en mer)
zone("combatZone_Ochamchire_Navires", N, 2500,
     [g("cargos", [cmd_unit("-cargoships", "Dry-cargo ship-1", "OchN-1")], N),
      g("escorte", [{"type": "ALBATROS"}], off(N, 90, 800))],
     "Port d'Ochamchire - 2 : navires",
     "Deuxième étape : des cargos et leur corvette d'escorte (SA-N-4 courte portée) en rade d'Ochamchire. "
     + bullseye(N) + ".",
     category="ship", radio_menu_disabled=True)

# ── 5. Opération Tkvarcheli : trois tâches, la troisième dépend des deux autres ───────────────
T = PLACES["Tkvarcheli"]
TR, TD, TP = off(T, 250, 4000), off(T, 200, 2500), off(T, 150, 1500)
zone("combatZone_Tkvarcheli_Radar", TR, 800,
     [g("ewr", [{"type": "1L13 EWR"}], TR), g("aaa", [cmd_unit("-shilka", "ZSU-23-4 Shilka", "TkvR-1")], off(TR, 90, 300))],
     "Tkvarcheli - radar", "Tâche 1 : un radar d'alerte 1L13 et sa DCA. " + bullseye(TR) + ".",
     radio_menu_disabled=True)
zone("combatZone_Tkvarcheli_Depot", TD, 800,
     [g("munitions", [{"type": ".Ammunition depot"}], TD),
      g("carburant-1", [{"type": "Fuel tank"}], off(TD, 90, 120)),
      g("carburant-2", [{"type": "Fuel tank"}], off(TD, 270, 120))],
     "Tkvarcheli - dépôt", "Tâche 2 : un dépôt de munitions et deux réservoirs (statiques). " + bullseye(TD) + ".",
     category="static", radio_menu_disabled=True)
zone("combatZone_Tkvarcheli_PC", TP, 800,
     [g("pc", [{"type": ".Command Center"}], TP), g("bunker", [{"type": "Bunker"}], off(TP, 0, 150))],
     "Tkvarcheli - PC", "Tâche 3, ouverte quand le radar et le dépôt sont détruits : le poste de commandement. "
     + bullseye(TP) + ".", category="static", radio_menu_disabled=True)
b.act("add_group", **RED, category="vehicle", name="garde", for_combat_zone="combatZone_Tkvarcheli_PC",
      position=xy(off(TP, 180, 200)), units=[{"type": "BTR-80", "count": 2}])
b.act("add_trigger_zone", name="Op_Tkvarcheli", position=xy(T), radius=6000)

# ── 6. Convoi en mouvement, en boucle entre Ochamchire et Gali ────────────────────────────────
C0 = off(PLACES["Ochamchire"], 80, 4000)
zone("combatZone_Convoi", C0, 2000,
     [g("colonne", [{"type": "Ural-375", "count": 3}, {"type": "KAMAZ Truck", "count": 2},
                    {"type": "ZSU-23-4 Shilka"}], C0,
        route=[xy(C0), xy(off(PLACES["Gali"], 270, 500))], patrol=True)],
     "Convoi d'Ochamchire",
     "Un convoi logistique (cinq camions et sa Shilka) fait la navette par la route entre Ochamchire et Gali. "
     "Départ : " + bullseye(C0) + ".")

b.save("02-zones.json")
