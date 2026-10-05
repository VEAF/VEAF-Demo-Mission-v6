"""Lot 03 : QRA, CAP à la demande, mission scénarisée, AIRWAVES, sanctuaire, défenses permanentes.

Portées vérifiées (list_unit_types, threat_range_m) :
- SA-11 de l'IADS de Gudauta, 50 km : à 4,5 km au nord-est de l'aérodrome, à plus de 80 km des zones
  d'Ochamchire et de l'arène AIRWAVES.
- QRA de Soukhoumi, cercle de 40 km : couvre Ochamchire (35 km), pas Gali (55 km) ni Tkvarcheli (44 km).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import AIRFIELDS, BLUE, NM, PLACES, RED, Batch, bullseye, interp_unit, off, xy  # noqa: E402

b = Batch()

# ── QRA de Soukhoumi : réponse graduée, variantes tirées au sort ──────────────────────────────
SUK = AIRFIELDS["Sukhumi-Babushara"]
QRA = "QRA Soukhoumi"
VARIANTS = {"MiG-29S": ("MiG-29S", "R-77*4,R-73*2"), "Su-27": ("Su-27", "R-73*4,R-27ER*6"),
            "Su-30": ("Su-30", "R-73*2,R-77*6,ECM"), "MiG-31": ("MiG-31", "R-40R*2,R-33*4")}
b.act("create_qra", name=QRA, **RED, trigger_zone="QRA-Soukhoumi", position=xy(SUK), radius=40000,
      groups=[{"name": f"{QRA} - {k}", "units": [{"type": t, "count": 2}], "position": xy(SUK),
               "altitude_ft": 15000, "speed_kt": 350, "payload": p} for k, (t, p) in VARIANTS.items()],
      enemy_coalitions=["BLUE"],
      qra={"groups_by_enemy_count": [
          {"enemy_count": 1, "groups": [f"{QRA} - MiG-29S", f"{QRA} - Su-27"], "random_pick": 1},
          {"enemy_count": 3, "groups": [f"{QRA} - Su-30", f"{QRA} - MiG-31", f"{QRA} - MiG-29S"], "random_pick": 2}],
          "airport_link": "Sukhumi-Babushara", "delay_before_rearming": 300, "delay_before_activating": 60,
          "react_on_helicopters": False})


# ── CAP rouges à la demande ───────────────────────────────────────────────────────────────────
def cap(title, typ, payload, a, brg, fl, kt, what):
    bb = off(a, brg, 30 * NM)
    mid = ((a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2)
    b.act("create_cap_mission", mission_name=title, units=[{"type": typ, "count": 2}], **RED, position=xy(a),
          route=[{"x": bb[0], "y": bb[1], "altitude_ft": fl * 100}], altitude_ft=fl * 100, speed_kt=kt,
          payload=payload,
          cap={"menu_name": title, "briefing": f"{what} Hippodrome au FL{fl}, centré sur {bullseye(mid)}.",
               "default": False, "activated": True})


cap("CAP MiG-29S Gudauta FL250", "MiG-29S", "R-77*4,R-73*2", (-185000, 520000), 120, 250, 420,
    "Paire de MiG-29S armés Fox 3 (R-77) au-dessus de Gudauta.")
cap("CAP Su-27 mer FL300", "Su-27", "R-73*4,R-27ER*6", (-250000, 520000), 135, 300, 420,
    "Paire de Su-27 armés Fox 1 (R-27ER, guidage radar semi-actif), sur la mer au large de Soukhoumi.")
cap("CAP MiG-31 Sotchi FL350", "MiG-31", "R-40R*2,R-33*4", (-160000, 470000), 110, 350, 480,
    "Paire de MiG-31 : intercepteur haut et rapide, R-33 longue portée.")

# ── Mission scénarisée : raid de Su-24M escortés vers Senaki ──────────────────────────────────
SEN = AIRFIELDS["Senaki-Kolkhi"]
R0 = (-200000, 530000)
b.act("add_air_group", **RED, name="Raid Senaki - Su-24M", unit_type="Su-24M", count=2, start="air",
      position=xy(R0), altitude_ft=15000, speed_kt=420, task="Ground Attack", skill="High",
      payload="FAB-500*4,R-60M*2", late_activation=True)
b.act("edit_route", group_name="Raid Senaki - Su-24M", operation="add", position=xy(off(SEN, 300, 30000)),
      altitude_ft=8000, speed_kt=450)
b.act("edit_route", group_name="Raid Senaki - Su-24M", operation="add", position=xy(SEN), altitude_ft=3000, speed_kt=480)
b.act("edit_route", group_name="Raid Senaki - Su-24M", operation="add_task", index=3, task="bombing",
      task_params={"position": xy(SEN), "expend": "All", "attack_qty": 1})
b.act("edit_route", group_name="Raid Senaki - Su-24M", operation="add", position=xy(R0), altitude_ft=15000, speed_kt=450)
b.act("add_air_group", **RED, name="Raid Senaki - MiG-29S", unit_type="MiG-29S", count=2, start="air",
      position=xy(off(R0, 180, 2000)), altitude_ft=18000, speed_kt=420, task="Escort", skill="High",
      payload="R-77*4,R-73*2", late_activation=True)
b.act("edit_route", group_name="Raid Senaki - MiG-29S", operation="add_task", index=1, task="escort",
      task_params={"group_name": "Raid Senaki - Su-24M", "engagement_distance_nm": 20})

# ── AIRWAVES : arène BVR au large de Poti ─────────────────────────────────────────────────────
ARENA = (-295000, 560000)
b.act("add_trigger_zone", name="Arene BVR", position=xy(ARENA), radius=25000)
for n, typ, cnt, p in [("Vague MiG-29S", "MiG-29S", 1, "R-77*4,R-73*2"),
                       ("Vague Su-27", "Su-27", 2, "R-73*4,R-27ER*6"),
                       ("Vague Su-30", "Su-30", 2, "R-73*2,R-77*6,ECM")]:
    b.act("add_air_group", **RED, name=n, unit_type=typ, count=cnt, start="air", position=xy(off(ARENA, 0, 20000)),
          altitude_ft=25000, speed_kt=420, heading_deg=180, task="CAP", skill="High", payload=p, late_activation=True)

# ── Sanctuaire rouge de Gudauta : un intrus bleu est averti, puis abattu ───────────────────────
b.act("add_trigger_zone", name="Sanctuaire Gudauta", position=xy(AIRFIELDS["Gudauta"]), radius=15000)

# ── Défenses permanentes (#veafInterpreter) ────────────────────────────────────────────────────
# À moins de 6 km de Gudauta : le catalogue de terrain dégagé du Caucase couvre l'endroit (add_group
# pose alors le groupe sur un sol mesuré dégagé). A 85 km du port d'Ochamchire, hors de portée des zones.
IADS = off(AIRFIELDS["Gudauta"], 60, 4500)
for name, alias, carrier, pos, side in [
    ("IADS Gudauta - SA-11", "-sa11, country russia", "SA-11 Buk LN 9A310M1", IADS, RED),
    ("IADS Gudauta - SA-15", "-sa15, country russia", "Tor 9A331", off(IADS, 90, 1500), RED),
    ("IADS Gudauta - EWR", "-ewr, country russia", "55G6 EWR", off(IADS, 30, 3000), RED),
    ("Defense Kutaisi - NASAMS", "-nasams, country usa", "NASAMS_LN_C", off(AIRFIELDS["Kutaisi"], 90, 2500), BLUE),
    ("Defense Senaki - Hawk", "-hawk, country usa", "Hawk ln", off(AIRFIELDS["Senaki-Kolkhi"], 0, 2500), BLUE),
]:
    b.act("add_group", **side, category="vehicle", name=name, position=xy(pos),
          units=[interp_unit(alias, carrier, name.split(" - ")[0].replace(" ", "-"))])

# ── Zones de service : bac à sable des marqueurs, pilote abattu (CSAR) ─────────────────────────
b.act("add_trigger_zone", name="Bac a sable", position=xy((-298000, 688000)), radius=3000)
b.act("add_trigger_zone", name="Demo CSAR", position=xy(off(PLACES["Khoni"], 20, 9000)), radius=1500)

b.save("03-air.json")
