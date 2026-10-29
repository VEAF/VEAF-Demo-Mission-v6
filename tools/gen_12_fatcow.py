"""Lot 12 : un slot CH-47F à Kutaisi, pour la Fat Cow de CTLD (VMCT FIX-FATCOW-CTLD-FARPS, ticket 02).

La Fat Cow est un CH-47F qui charge des réservoirs et des munitions dans une zone logistique CTLD, se pose et
ouvre une FARP dont le stock est ce qu'il transporte (CTLD 2.0.0-rc15, vendu par VMCT #1204).
Le CH-47F n'avait qu'un template de slot dynamique, qui ne marche qu'en multijoueur : ce slot `Client`, moteur
chaud, rend l'étape jouable en solo, comme les autres slots classiques de Kutaisi (lot 01).
Kutaisi est une zone logistique CTLD (étape « Aérodromes »), un cercle de 250 m autour du parking 43 : le CH-47F
y est garé, et l'AH-64D du lot 01 passe au parking 42, à 120 m. La recette se fait alors sans piloter : le CH-47F
charge et ouvre sa FARP sur place, l'AH-64D s'y ravitaille sans décoller (David, 2026-10-29). Garé au parking 49
choisi par l'action, le CH-47F était à 1,6 km du centre du cercle et CTLD refusait le chargement.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, Batch  # noqa: E402

b = Batch()
b.act("add_air_group", **BLUE, name="Kutaisi CH-47F", unit_type="CH-47Fbl1", count=1, start="parking-hot",
      airfield="Kutaisi", parking=["43"], skill="Client", task="Transport")
b.act("remove_group", group_name="Kutaisi AH-64D")
b.act("add_air_group", **BLUE, name="Kutaisi AH-64D", unit_type="AH-64D_BLK_II", count=1, start="parking-hot",
      airfield="Kutaisi", parking=["42"], skill="Client", task="CAS")
b.save("12-fatcow.json")
