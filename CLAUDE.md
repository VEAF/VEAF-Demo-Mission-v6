# Mission de démo VEAF v6 — consignes du dépôt

La mission de démonstration des VEAF Mission Creation Tools (VMCT) v6, sur le Caucase.
Elle a deux usages : faire découvrir chaque fonctionnalité aux joueurs (visite guidée en jeu + README), et vérifier avant chaque release des outils que les fonctionnalités existantes marchent toujours (`docs/recette.md`).

## La règle du dépôt

**Chaque nouvelle fonctionnalité VMCT ajoute son exemple à la démo**, dans la même PR que la fonctionnalité ou juste après :

1. poser l'exemple dans la mission — actions du serveur MCP `veaf-mission-mcp` sur le dossier (monde durable : `src/mission/` + `mission.yaml`), via un lot `tools/gen_0N_*.py` exécuté par `tools/mcp.py batch` ;
2. ajouter son étape dans `tour/steps.yaml`, avec son contrôle de recette (`check`) — c'est la **source unique** de la visite, du README et de la recette ;
3. `python tools/gen_tour.py`, puis `python tools/gen_map.py` si un lieu a bougé, puis `python tools/gen_05_dessins.py` + `python tools/mcp.py batch tools/batches/05-dessins.json` pour les dessins F10 ;
4. `.\veaf-tools.exe mission validate`, `.\veaf-tools.exe build`, `python tools/verify.py` (tout au vert).

Ne jamais modifier à la main `README.md`, `README.en.md`, `docs/recette.md`, `src/scripts/guided-tour.lua` : ils sont générés.

## Avant chaque release des outils

Construire la démo avec la version candidate, puis dérouler `docs/recette.md` en jeu (mission de test : `.\veaf-tools.exe mission build --profile LOCAL_TEST` puis `python tools/make_test_mission.py`).

## Outils

- `tools/mcp.py` appelle les actions MCP **dans le processus**, sur le checkout VMCT de `develop` (chemin : `tools/paths.py`, variable `VMCT_PY`). Les lots ne sont pas idempotents : une action `add` rejouée crée un second groupe.
- `tools/dcslua.py` lit les tables Lua de `src/mission/` (lecture seule).
- Une modification de `src/mission/` qu'aucune action MCP ne sait faire passe par `load_folder_mission` / `save_folder_mission` de VMCT (exemple : `tools/fix_convoy_on_road.py`), jamais par remplacement de texte, et se note dans `docs/retours-vmct.md`.
- `veaf-tools.exe` lancé par un script : rediriger sa sortie vers un fichier, jamais vers `/dev/null` — l'auto-pause finale lit alors l'entrée standard et le build réussi sort en code 1 (`docs/retours-vmct.md`, n° 1).

## Conventions

- Mission en français (`mission.language: fr`), visite et README en français **et** en anglais.
- Sécurité VEAF désactivée (décision du 2026-10-05) : la démo ouvre toutes les commandes à tous.
- Rouge non jouable : pas de slots rouges, pas de QRA bleue.
- Fréquences VEAF hors de la bande des tours du Caucase (250.0 à 270.0).
- Markdown : une phrase par ligne.
