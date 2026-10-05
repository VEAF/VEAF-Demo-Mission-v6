"""Lot 01 : soutien (ravitailleurs, AWACS + escorte, drone laser), deux porte-avions, FARP, slots joueurs.

Fréquences hors de la bande des tours du Caucase (250.0 à 270.0, une par MHz) : voir le prompt
new-open-training-mission §4.10.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, Batch, PLACES, off, xy  # noqa: E402

b = Batch()

# ── Ravitailleurs et AWACS ────────────────────────────────────────────────────────────────────
# nom, type, a, b (hippodrome), FL, kt, MHz, tâche, (canal TACAN Y, indicatif) ou None
SUPPORT = [
    # Perche (boom) : à l'est de Kutaisi, loin du front.
    ("Texaco 1", "KC-135", (-300000, 705000), (-300000, 750000), 200, 420, 292.0, "Refueling", (52, "TX1")),
    # Panier (drogue) : sur la mer, au sud des porte-avions.
    ("Arco 1", "KC135MPRS", (-345000, 575000), (-370000, 575000), 180, 420, 291.0, "Refueling", (51, "AR1")),
    # AWACS : au sud de Kutaisi.
    ("Overlord 1", "E-3A", (-320000, 680000), (-320000, 725000), 300, 360, 286.0, "AWACS", None),
]
for n, typ, a, bb, fl, kt, f, task, beacon in SUPPORT:
    b.act("add_air_group", **BLUE, name=n, unit_type=typ, count=1, start="air", position=xy(a),
          altitude_ft=fl * 100, speed_kt=kt, frequency_mhz=f, task=task, skill="High")
    b.act("edit_route", group_name=n, operation="add", position=xy(bb), altitude_ft=fl * 100, speed_kt=kt)
    b.act("edit_route", group_name=n, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
    if beacon:
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="activate_beacon",
              task_params={"channel": beacon[0], "mode": "Y", "callsign": beacon[1], "bearing": True, "aa": True})
    if task == "Refueling":
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="tanker", task_params={})
    else:
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="awacs", task_params={})
        b.act("edit_route", group_name=n, operation="add_task", index=1, task="eplrs", task_params={"value": True})
    b.act("edit_route", group_name=n, operation="add_task", index=1, task="orbit",
          task_params={"pattern": "Race-Track", "altitude_ft": fl * 100, "speed_kt": kt})

# Escorte de l'AWACS : démontre le `linked` de modules.ASSETS (relancée avec lui depuis le menu).
b.act("add_air_group", **BLUE, name="Overlord 1 escort", unit_type="F-15C", count=2, start="air",
      position=xy((-322000, 678000)), altitude_ft=30000, speed_kt=360, frequency_mhz=286.0,
      task="Escort", skill="High", payload="AIM-9*2,AIM-120*6,Fuel")
b.act("edit_route", group_name="Overlord 1 escort", operation="add_task", index=1, task="set_unlimited_fuel",
      task_params={"value": True})
b.act("edit_route", group_name="Overlord 1 escort", operation="add_task", index=1, task="escort",
      task_params={"group_name": "Overlord 1", "engagement_distance_nm": 30})

# Drone laser au-dessus du front (zone de Gali) : CTLD le prend comme JTAC.
b.act("add_air_group", **BLUE, name="Reaper 1", unit_type="MQ-9 Reaper", count=1, start="air",
      position=xy(off(PLACES["Gali"], 135, 4000)), altitude_ft=15000, speed_kt=160, frequency_mhz=118.8,
      task="AFAC", skill="High")

# ── Deux porte-avions : Stennis et Roosevelt (règle de David du 02/10/2026) ──────────────────────
b.act("add_carrier_group", **BLUE, name="CSG-74 Stennis", carrier_name="CVN-74 Stennis", carrier_type="Stennis",
      position=xy((-335000, 595000)), heading_deg=270, speed_kt=15, escorts=["TICONDEROG"],
      tower_mhz=274.0, tacan_channel=74, tacan_callsign="STN", icls_channel=4, link4_mhz=336.0,
      recovery_tanker=True, tanker_tacan_channel=75, tanker_tacan_callsign="T74", tanker_frequency_mhz=290.9,
      rescue_helicopter=True)
b.act("add_carrier_group", **BLUE, name="CSG-71 Roosevelt", carrier_name="CVN-71 Roosevelt", carrier_type="CVN_71",
      position=xy((-352000, 586000)), heading_deg=270, speed_kt=15, escorts=["TICONDEROG"],
      tower_mhz=271.0, tacan_channel=71, tacan_callsign="TDR", icls_channel=1, link4_mhz=337.0,
      recovery_tanker=True, tanker_tacan_channel=72, tanker_tacan_callsign="T71", tanker_frequency_mhz=290.8,
      rescue_helicopter=True)
for name, typ, n, start, ship in [
    ("Stennis F/A-18C", "FA-18C_hornet", 2, "deck-hot", "CVN-74 Stennis"),
    ("Roosevelt F-14B", "F-14B", 2, "deck-hot", "CVN-71 Roosevelt"),
]:
    b.act("add_air_group", **BLUE, name=name, unit_type=typ, count=n, start=start, carrier=ship, skill="Client",
          frequency_mhz=274.0 if "Stennis" in ship else 271.0, task="CAP")

# ── FARP de Khoni : hélicoptères (CTLD, CSAR), à côté des zones d'entraînement ─────────────────
FARP = off(PLACES["Khoni"], 225, 3500)
b.act("add_farp", **BLUE, name="FARP Khoni", position=xy(FARP), farp_type="FARP", frequency_mhz=127.5, modulation="AM")

# ── Slots joueurs classiques à Kutaisi, moteur chaud ───────────────────────────────────────────
# Les slots dynamiques ne marchent qu'en multijoueur : ces slots `Client` rendent la démo jouable en solo.
for name, typ, n, task in [
    ("Kutaisi A-10C II", "A-10C_2", 2, "CAS"),
    ("Kutaisi F-16C", "F-16C_50", 2, "CAP"),
    ("Kutaisi F/A-18C", "FA-18C_hornet", 2, "CAP"),
    ("Kutaisi UH-1H", "UH-1H", 2, "Transport"),
    ("Kutaisi Mi-8MTV2", "Mi-8MT", 2, "Transport"),
    ("Kutaisi AH-64D", "AH-64D_BLK_II", 1, "CAS"),
]:
    b.act("add_air_group", **BLUE, name=name, unit_type=typ, count=n, start="parking-hot", airfield="Kutaisi",
          skill="Client", task=task)

b.save("01-soutien.json")
