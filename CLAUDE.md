# Mission de démo VEAF v6 — consignes du dépôt

La mission de démonstration des VEAF Mission Creation Tools (VMCT) v6, sur le Caucase.
Elle a deux usages : faire découvrir chaque fonctionnalité aux joueurs (visite guidée en jeu + README), et vérifier avant chaque release des outils que les fonctionnalités existantes marchent toujours (`docs/recette.md`).

## La règle du dépôt

**Chaque nouvelle fonctionnalité VMCT ajoute son exemple à la démo**, dans la même PR que la fonctionnalité ou juste après :

1. poser l'exemple dans la mission — actions du serveur MCP `veaf-mission-mcp` sur le dossier (monde durable : `src/mission/` + `mission.yaml`), via un lot `tools/gen_0N_*.py` exécuté par `tools/mcp.py batch` ;
2. ajouter son étape dans `tour/steps.yaml`, **en français et en anglais**, avec son contrôle à l'œil (`check`) et ses sondes (`probe`, lancées par `tools/recette_pont.py`) — c'est la **source unique** de la visite, du README et de la recette ; le texte anglais cite les libellés du build anglais (`COMBAT ZONES`, `ASSETS`…) ;
3. traduire tout nouveau texte de `mission.yaml` dans `i18n/en.yaml`, puis `python tools/gen_i18n.py` ; un nouveau texte de la mission DCS (briefing, étiquette F10, carte) va dans `tools/i18n_texts.py` ;
4. `python tools/gen_tour.py`, puis `python tools/gen_map.py` si un lieu a bougé, puis `python tools/gen_05_dessins.py` + `python tools/mcp.py batch tools/batches/05-dessins.json` pour les dessins F10 ;
5. `.\veaf-tools.exe mission validate`, `.\veaf-tools.exe build`, `python tools/localize_miz.py`, `python tools/verify.py` (tout au vert) ; `lua tools/test_tour.lua fr` et `en`.

Ne jamais modifier à la main `README.md`, `README.en.md`, `docs/recette.md`, `src/scripts/guided-tour.lua`, `src/versions.en.yaml`, ni la fin de `mission.yaml` (profils et `build_variants`) : ils sont générés.

## Deux langues, deux missions complètes

Un build produit une mission `_FR` et une `_EN` par variante météo (`build_variants` de `mission.yaml`, profils `FR` et `EN`).
`mission.yaml` et `src/mission/` portent le français ; le profil `EN` (généré depuis `i18n/en.yaml`) traduit la configuration VEAF, et `tools/localize_miz.py` traduit après le build ce qui vit dans la mission DCS (briefing, étiquettes F10, cartes).
Les noms de groupes et de zones de combat visibles sur la carte F10 sont des identifiants anglais neutres, communs aux deux.
Les variantes météo s'éditent dans `src/versions.yaml` seulement : `tools/gen_i18n.py` en tire `src/versions.en.yaml` (même météo, noms anglais d'`i18n/en.yaml`), que le profil `EN` désigne, et les `.miz` anglais portent ces noms.

## Avant chaque release des outils

Le skill `maj-demo` (`.claude/skills/maj-demo/`) déroule tout le cycle : lire ce qui a changé dans VMCT, adapter la visite, `python tools/build_candidate.py` (démo construite avec le checkout VMCT, missions de test comprises), `python tools/recette_pont.py --lang fr` puis `--lang en` sur `missions-test/VEAF_Demo_TEST_FR.miz` puis `_EN.miz` chargées dans DCS, le reste de `docs/recette.md` à l'œil.
Une fois les outils publiés : `python tools/release.py published-vX.Y.Z` publie les `.miz` dans une release du dépôt.
La clé du pont : `DCS_BRIDGE_API_KEY`, ou un `dcs-serve.yaml` à la racine (ignoré par git).

## Outils

- `tools/mcp.py` appelle les actions MCP **dans le processus**, sur le checkout VMCT de `develop` (chemin : `tools/paths.py`, variable `VMCT_PY`). Les lots ne sont pas idempotents : une action `add` rejouée crée un second groupe.
- `tools/dcslua.py` lit les tables Lua de `src/mission/` (lecture seule).
- Une modification de `src/mission/` qu'aucune action MCP ne sait faire passe par `load_folder_mission` / `save_folder_mission` de VMCT (exemple : `tools/fix_convoy_on_road.py`), jamais par remplacement de texte, et se note dans `docs/retours-vmct.md`.
- `veaf-tools.exe` lancé par un script : rediriger sa sortie vers un fichier, jamais vers `/dev/null` — l'auto-pause finale lit alors l'entrée standard et le build réussi sort en code 1 (`docs/retours-vmct.md`, n° 1).

## Conventions

- Deux missions complètes, `_FR` et `_EN` ; README en français et en anglais.
- Sécurité VEAF désactivée (décision du 2026-10-05) : la démo ouvre toutes les commandes à tous.
- Rouge non jouable : pas de slots rouges, pas de QRA bleue.
- Fréquences VEAF hors de la bande des tours du Caucase (250.0 à 270.0).
- Markdown : une phrase par ligne.
