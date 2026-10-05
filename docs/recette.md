# Recette de la mission de démo

> Générée par `tools/gen_tour.py` depuis `tour/steps.yaml` : ne pas modifier à la main.

À dérouler avant chaque release des outils VEAF, sur la démo construite avec la version candidate.
Chaque ligne est un observable : on coche quand on l'a vu, on note ce qu'on a vu sinon.

## Avant DCS

- [ ] `veaf-tools mission validate` sans erreur.
- [ ] `veaf-tools build` sans erreur, missions `_FR` et `_EN` ; journal relu : presets injectés, waypoints injectés, liens des entrepôts, nombre de variantes météo, aucun avertissement nouveau.
- [ ] `python tools/localize_miz.py` : chaque `.miz` `_EN` localisé (briefing, étiquettes F10, cartes).
- [ ] `python tools/verify.py` : tous les contrôles des `.miz` au vert, dans les deux langues.

## En jeu

Version des outils : `______`  —  Date : `______`  —  Testeur : `______`

| # | Étape | Contrôle | OK | Constat |
|---|---|---|---|---|
| 01 | Bienvenue | Menu F10 > Autre > VEAF présent ; canal 1 de la radio d'un F-16C = un canal du plan VEAF ; points de navigation présents dans l'avion ; slots dynamiques sur Kutaisi, Senaki, Kobuleti, Batumi (multijoueur). | ☐ | |
| 02 | Bac à sable : les commandes de marqueur | `-sa8`, `-armor`, `-convoy, dest ALPHA`, `-point`, `-smoke`, `-farp`, `-boum`, `-menage` : chacune produit son effet au marqueur, sans erreur dans dcs.log. | ☐ | |
| 03 | Missions générées : CAS et transport | `_cas` : groupe ennemi créé, menu MISSION CAS peuplé, fumée sur cible. `_transport, from ALPHA` : menu MISSION DE TRANSPORT peuplé, zone de livraison fumée. | ☐ | |
| 04 | Entraînement de Khoni : trois niveaux | Chaque niveau fait apparaître plus que celui qu'il inclut ; le tirage #spawngroup donne 2 pièces de DCA sur 4 au moyen, différentes d'une activation à l'autre ; la zone se termine quand tout est détruit. | ☐ | |
| 05 | Front de Gali, et le drone JTAC | Un seul groupe blindé sur deux ; artillerie Msta présente ; Reaper 1 déclaré JTAC par CTLD sur le code 1511 et 35.55 FM, et il désigne un véhicule. | ☐ | |
| 06 | Défense aérienne intégrée (Skynet) | SA-11, SA-15 et EWR présents dès le départ (interpréteur) ; SA-6 d'Ochamchire actif au démarrage et inscrit dans le réseau Skynet ; radar éteint tant qu'aucun avion bleu n'est détecté ; menu SKYNET IADS COALITION: RED présent ; vue des guetteurs rouge affichable depuis le slot game master rouge. | ☐ | |
| 07 | Mission chaînée : le port d'Ochamchire | La zone 2 (navires) n'existe pas avant la fin de la zone 1 et apparaît 60 s après ; elle n'a pas de menu propre. | ☐ | |
| 08 | Opération Tkvarcheli : tâches et dépendances | L'opération active ses trois zones ; la tâche PC n'est listée comme objectif qu'après radar + dépôt ; les statiques détruits sont comptés (zone dépôt terminée) ; message de fin d'opération. | ☐ | |
| 09 | Convoi en mouvement | Le convoi roule (position qui change entre deux relevés), atteint Gali et repart vers Ochamchire. | ☐ | |
| 10 | QRA de Soukhoumi | Entrée d'un avion bleu dans le cercle : décollage d'une paire après 60 s ; avec trois intrus, deux paires ; aucune réaction à un hélicoptère ; menu Démo : commandes arrête et redémarre la QRA. | ☐ | |
| 11 | CAP à la demande et raid sur Senaki | Chaque CAP apparaît au niveau et à la taille demandés et engage (tir de missile sur une cible bleue) ; le raid apparaît avec son escorte et suit sa route vers Senaki ; `-airstart Raid-Senaki/Good/1` / `-airstop` fonctionnent. | ☐ | |
| 12 | Arène BVR (vagues aériennes) | Entrée d'un joueur bleu : vague 1 après 30 s ; vague suivante 60 s après la destruction de la précédente ; reset par le menu Démo : commandes. | ☐ | |
| 13 | Sanctuaire rouge de Gudauta | Joueur bleu dans le cercle : avertissement à 10 s, défense à 60 s, destruction à 120 s ; un missile tiré sur une unité rouge du sanctuaire est détruit. | ☐ | |
| 14 | Ravitailleurs, AWACS et escorte | Ravitaillement possible sur Texaco 1 (perche) et Arco 1 (panier), TACAN reçus ; réapparition d'Overlord 1 avec son escorte ; `_move tanker` déplace l'orbite de Texaco 1. | ☐ | |
| 15 | Hélicoptères : FARP, CTLD, CSAR | Ravitaillement et réarmement au FARP Khoni ; chargement CTLD de troupes et d'une caisse au FARP ; pilote abattu créé par le menu, balise ADF audible, récupérable et ramené. | ☐ | |
| 16 | Porte-avions Stennis et Roosevelt | Démarrage des opérations : virage face au vent et vitesse ; TACAN / ICLS / Link 4 reçus ; S-3B et Pedro présents pour chaque navire. | ☐ | |
| 17 | Météo, ATC et assistance cockpit | Message d'accueil à la prise de slot ; menu MÉTÉO ET ATC répond ; checklist F-16C proposée au seul F-16C ; chaque variante météo du build diffère (nuages, température, vent). | ☐ | |

## Hors étapes

- [ ] Aucune erreur Lua VEAF dans `dcs.log` sur une heure de mission.
- [ ] Les dessins F10 (cercles et étiquettes des étapes) sont visibles et lisibles sur la carte du camp bleu.
- [ ] Version anglaise (`_EN`) : menus VEAF, CTLD, visite, « Demo: commands », briefing, carte F10 et cartes du briefing en anglais ; dérouler au moins les étapes 01, 02, 04 et 10 en anglais.
- [ ] La visite guidée existe dans la langue du build, et chaque entrée pose son repère F10.
- [ ] Les chemins de menu cités par la visite correspondent aux menus réels.
