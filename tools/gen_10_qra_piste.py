"""Lot 10 : la QRA de Soukhoumi décolle de la piste (VMCT FIX-CAMPAIGN-MISSION-1-FINDINGS, #1111, ticket 04).

`create_qra` pose maintenant ses intercepteurs au départ piste de l'aérodrome de leur camp le plus proche, et le
module QRA les fait monter à leur patrouille ; le départ en vol n'est plus que sur demande.
Le lot 03 avait posé la QRA avant ce changement, en vol à 15 000 ft au-dessus de Soukhoumi.
`create_qra` rejoué créerait une seconde zone et une seconde QRA dans mission.yaml : on reprend seulement ses quatre
groupes, retirés puis reposés comme `create_qra` les pose aujourd'hui (même nom, même type, même emport, activation
différée), au départ piste de Sukhumi-Babushara.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import RED, Batch  # noqa: E402

QRA = "QRA Sukhumi"
VARIANTS = {"MiG-29S": ("MiG-29S", "R-77*4,R-73*2"), "Su-27": ("Su-27", "R-73*4,R-27ER*6"),
            "Su-30": ("Su-30", "R-73*2,R-77*6,ECM"), "MiG-31": ("MiG-31", "R-40R*2,R-33*4")}

b = Batch()
for k in VARIANTS:
    b.act("remove_group", group_name=f"{QRA} - {k}")
for k, (t, p) in VARIANTS.items():
    b.act("add_air_group", **RED, name=f"{QRA} - {k}", unit_type=t, count=2, start="runway",
          airfield="Sukhumi-Babushara", task="Intercept", skill="High", late_activation=True, payload=p,
          speed_kt=350)
b.save("10-qra-piste.json")
