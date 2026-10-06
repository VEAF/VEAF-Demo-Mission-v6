---
name: maj-demo
description: Mettre la mission de démo VEAF v6 à jour pour une release des VMCT — lire ce qui a changé dans les outils, adapter la visite (nouvelles fonctionnalités, changements, retraits), construire avec la version candidate, dérouler la recette par le pont puis à l'œil, et publier les .miz une fois les outils sortis. À utiliser quand une release VMCT se prépare (« recette de la démo », « mets la démo à jour », « la 6.x sort ») ou vient de sortir (« publie la démo »).
---

# Mettre la démo à jour pour une release VMCT

La démo a deux rôles (voir `CLAUDE.md`) : montrer chaque fonctionnalité, et vérifier avant chaque release que rien n'a cassé.
Ce skill déroule les deux moments d'une release : **recette** sur la version candidate, puis **publication** une fois les outils sortis.
Il s'arrête aux points marqués 🛑 et attend la décision de David.

## Mode recette (avant la release VMCT)

### 1. Se synchroniser

- Démo : `git fetch` puis `git pull --ff-only` sur `main`.
- VMCT (chemin dans `tools/paths.py`) : le checkout doit être sur la candidate, en général `develop` à jour, ou la branche de release une fois créée.
  Ne pas changer sa branche sans le dire : d'autres sessions y travaillent peut-être.
  Une branche de release est souvent ouverte dans un worktree de la session de release, et `git switch` la refuse : `git switch --detach origin/release/X.Y.Z` le temps du build, puis revenir sur `develop`.
  Vérifier la version construite dans `published/veaf-version.json` (`X.Y.Z+<commit>`) : c'est elle qui dit ce qui a été testé.

### 2. Lire ce qui a changé

- Version de référence : celle de la dernière release de la démo, `gh release view -R VEAF/VEAF-Demo-Mission-v6 --json tagName` (tag `v<version VMCT>`).
  Pas de release encore : partir de la dernière release VMCT dont la démo a été recettée, et le dire.
- Lire dans `CHANGELOG.md` de VMCT toutes les entrées postérieures à cette version, `[Unreleased]` compris.
- Classer chaque entrée :

  | Nature | Dans la démo |
  |---|---|
  | nouvelle fonctionnalité visible en jeu ou dans `mission.yaml` | une étape nouvelle, ou une ligne dans une étape existante |
  | changement visible : libellé, menu, alias, valeur par défaut, comportement | corriger l'étape, `mission.yaml`, `i18n/en.yaml`, la sonde |
  | fonctionnalité retirée ou renommée | retirer ou renommer partout (`grep` dans `tour/`, `mission.yaml`, `i18n/`, `tools/`) |
  | correction d'un défaut que la démo contournait (`docs/retours-vmct.md`) | retirer le contournement, mettre à jour la ligne |
  | interne, outillage, doc seule | rien |

- Vérifier chaque classement dans le code de VMCT (le diff de la PR citée), pas seulement dans le texte du changelog.

🛑 Présenter le tableau des entrées retenues, avec la reco pour chacune (« étape nouvelle », « corriger l'étape X », « rien »).
David tranche ligne par ligne ; ce qu'il ne reprend pas est écarté.

### 3. Mettre la mission à jour

Pour chaque entrée retenue, suivre la règle du dépôt (`CLAUDE.md`, *La règle du dépôt*) :

1. poser l'exemple dans la mission : lot `tools/gen_0N_*.py` (numéro suivant) exécuté par `python tools/mcp.py batch`, ou `mission.yaml` ;
2. l'étape dans `tour/steps.yaml`, en français **et** en anglais, avec son `check` (ce que des yeux vérifient) et sa `probe` (ce que le pont vérifie, voir plus bas) ;
3. tout nouveau texte de `mission.yaml` traduit dans `i18n/en.yaml`, puis `python tools/gen_i18n.py` ;
4. `python tools/gen_tour.py`, `python tools/gen_map.py` si un lieu a bougé, les dessins F10 si besoin.

Committer tôt et souvent sur une branche si le lot est gros ; sinon directement sur `main`, après le feu vert de David.

### 4. Construire avec la candidate

```
python tools/build_candidate.py
```

Il construit les scripts du checkout VMCT, les installe dans `published/`, construit `missions/` et `missions-test/` avec le `veaf-tools` du venv de VMCT, localise et lance `verify.py`.
Un échec s'y lit dans `missions/candidate-*.log`.
`lua tools/test_tour.lua fr` et `en` doivent rester verts.

### 5. Recette par le pont

David charge `missions-test/VEAF_Demo_TEST_FR.miz` en solo (slot game master) ; `dcs-serve` tourne avec la clé de `dcs-serve.yaml` à la racine (ou `DCS_BRIDGE_API_KEY`).
Lancer `dcs-serve` en tâche de fond depuis la session est accepté (2026-10-05) ; charger la mission reste à David.

```
python tools/recette_pont.py --lang fr
```

- `--lang` dit quelle mission est chargée : le script s'arrête si la mission est dans une autre langue.
- D'abord les chemins de menu : chaque « VEAF > … » cité par la visite doit exister dans le menu de la mission, tel que le joueur le lit.
  Un échec veut dire que le texte de la visite ou le menu a changé : corriger le texte (`steps.yaml`), ou signaler le défaut VMCT.
- Puis les sondes de chaque étape, dans l'ordre.
  Elles activent des zones et détruisent des unités : une seule passe par mission chargée.
  Pour rejouer une étape, la nommer (`python tools/recette_pont.py --lang fr convoy`), sur une mission rechargée : une zone déjà active ou des opérations déjà lancées changent les titres du menu.
- Puis la même chose sur `_EN.miz`, avec `--lang en`.

Une sonde en échec : lire `dcs.log` (`Saved Games\DCS\Logs`, heures en UTC sur le poste de David) autour de l'heure du verdict, et trouver si c'est la sonde ou VMCT.
Mesurer la cause par le pont avant de l'écrire dans un ticket : le premier diagnostic du `-menage` (noms « [CH] ») était faux, la vraie cause était des noms d'unités en double.
**Ne pas affaiblir une sonde pour la faire passer** : si VMCT a changé exprès, la sonde suit le changement ; sinon c'est un défaut à remonter.

### 6. Recette à l'œil

Ce que les sondes ne voient pas : `docs/recette.md`, section *En jeu*, et *Hors étapes*.
David ne fouille pas les logs : lui poser une question à la fois, un observable visible sans rien ouvrir, sous forme de tableau des réponses possibles et de ce que chacune conclut.

### 7. Remonter ce qui ne va pas

- Chaque défaut VMCT trouvé : une ligne dans `docs/retours-vmct.md` (quoi, où, constat mesuré, contournement), et un lot dans le backlog VMCT (`.backlog/<LOT>/`, PRD et tickets) si David le demande.
- Mettre à jour la section d'état de `docs/retours-vmct.md` pour ce qui a été corrigé.

🛑 Rendre compte : ce qui a changé dans la démo, le verdict du pont (FR et EN), ce qui reste à l'œil, les défauts trouvés.
Lancer une revue de code du diff avant d'annoncer que c'est prêt, puis attendre le feu vert pour committer et pousser.

## Mode publication (après la release VMCT)

Quand le tag `published-vX.Y.Z` existe dans `VEAF/VEAF-Mission-Creation-Tools` :

```
python tools/release.py published-vX.Y.Z --dry-run
python tools/release.py published-vX.Y.Z
```

Il exige un dépôt propre égal à `origin/main`, installe exactement cette version (`veaf-tools-updater.exe --tag`), refuse une version de développement, construit, localise, vérifie, puis crée la release `vX.Y.Z` de la démo avec les dix `.miz`.
Les liens du README (`releases/latest/download/…`) suivent tout seuls.

🛑 Le `--dry-run` d'abord ; la publication est publique, elle attend le feu vert de David.

## Écrire une sonde

Champ `probe` d'une étape de `tour/steps.yaml`, une liste :

```yaml
probe:
  - name: "Khoni facile : des cibles apparaissent"     # en français, une ligne de docs/recette.md
    act: |                                              # optionnel, lancé une fois
      R.click(R.L("ZONES DE COMBAT", "COMBAT ZONES"), ...)
    check: |                                            # rend ok, détail
      local n = R.inZone("combatZone_Khoni_Easy")
      return n >= 8, n .. " unités"
    wait: 5          # secondes avant le premier essai (optionnel)
    timeout: 60      # réessaie toutes les 5 s jusque-là (optionnel)
```

- Les fonctions `R.*` sont dans `tools/recette-lib.lua` : langue du build (`R.lang`, `R.L(fr, en)`, `R.expected` = la langue de `--lang`), unités d'une zone, groupes, menu VEAF (`R.menu`, `R.click`), vrai marqueur F10 (`R.marker`), destruction d'une zone, mémoire entre sondes (`R.mem`).
- Une sonde doit pouvoir échouer : vérifier qu'elle teste ce que son nom promet, et qu'elle ne passe pas déjà avant l'action (relever l'état dans `act`, comparer dans `check`).
- Une sonde passe dans les deux langues : les titres de menu par `R.L`, les noms de zones et de groupes sont des identifiants communs.
- Elle mesure l'effet en jeu (unités apparues, groupe qui bouge, état d'un module), pas seulement qu'une fonction existe.
- Préférer cliquer le menu (`R.click`) à appeler la fonction VEAF directement : la sonde vérifie alors aussi que le menu mène au bon endroit.
- Un comportement lent (convoi, enchaînement de zones) : `wait` et `timeout`, jamais une attente dans le Lua.
