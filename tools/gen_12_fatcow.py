"""Lot 12 : un slot CH-47F à Kutaisi, pour la Fat Cow de CTLD (VMCT FIX-FATCOW-CTLD-FARPS, ticket 02).

La Fat Cow est un CH-47F qui charge des réservoirs et des munitions dans une zone logistique CTLD, se pose et
ouvre une FARP dont le stock est ce qu'il transporte (CTLD 2.0.0-rc15, vendu par VMCT #1204).
Le CH-47F n'avait qu'un template de slot dynamique, qui ne marche qu'en multijoueur : ce slot `Client`, moteur
chaud, rend l'étape jouable en solo, comme les autres slots classiques de Kutaisi (lot 01).
Kutaisi est une zone logistique CTLD (étape « Aérodromes »), mais son cercle de 250 m n'atteint pas le parking :
DCS pose le CH-47F sur une place hélicoptère (la 58, mesurée le 2026-10-29), à 1,6 km du centre, quelle que soit
la place demandée (43, au centre, essayée et refusée). Le joueur saute donc dans le cercle avant de charger ; la
recette sans pilotage passe par la mission de test Fat Cow (tools/make_test_mission.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, Batch  # noqa: E402

b = Batch()
b.act("add_air_group", **BLUE, name="Kutaisi CH-47F", unit_type="CH-47Fbl1", count=1, start="parking-hot",
      airfield="Kutaisi", skill="Client", task="Transport")
b.save("12-fatcow.json")
