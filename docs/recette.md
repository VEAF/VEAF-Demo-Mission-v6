# Recette de la mission de démo

> Générée par `tools/gen_tour.py` depuis `tour/steps.yaml` : ne pas modifier à la main.

À dérouler avant chaque release des outils VEAF, sur la démo construite avec la version candidate.
Chaque ligne est un observable : on coche quand on l'a vu, on note ce qu'on a vu sinon.

## Avant DCS

- [ ] `python tools/build_candidate.py` sans erreur : validate, build des missions `_FR` et `_EN`, localisation, missions de test, `verify.py` au vert.
- [ ] Journal du build relu (`missions/candidate-build.log`) : presets injectés, waypoints injectés, liens des entrepôts, nombre de variantes météo, aucun avertissement nouveau.

## Par le pont

Sur `missions-test/VEAF_Demo_TEST_FR.miz` fraîchement chargée : `python tools/recette_pont.py --lang fr` ; puis sur `_EN.miz` : `--lang en`.
Il vérifie que chaque chemin « VEAF > … » cité par la visite existe dans le menu, puis lance les sondes de chaque étape :

- 01 Bienvenue : Configuration VEAF chargée en entier (zones, missions, QRA, moyens, fonction du menu Démo)
- 01 Bienvenue : Mission, configuration VEAF et visite guidée dans la langue demandée (--lang)
- 01 Bienvenue : Menu VEAF > MISSIONS présent dès le démarrage
- 02 Bac à sable : les commandes de marqueur : `-sa8` : une batterie SA-8 au marqueur
- 02 Bac à sable : les commandes de marqueur : `_spawn unit, name T-80UD, hdg 270` : un char
- 02 Bac à sable : les commandes de marqueur : `-armor` : un groupe blindé
- 02 Bac à sable : les commandes de marqueur : `-point BRAVO` : un point nommé
- 02 Bac à sable : les commandes de marqueur : `-farp` : un FARP et son décor
- 02 Bac à sable : les commandes de marqueur : `-menage` : tout est détruit autour du marqueur
- 03 Missions générées : CAS et transport : `_cas` : un groupe ennemi et le menu MISSION CAS
- 03 Missions générées : CAS et transport : `_transport, from ALPHA` : mission créée, menu MISSION DE TRANSPORT peuplé
- 04 Entraînement de Khoni : trois niveaux : Khoni facile : huit camions
- 04 Entraînement de Khoni : trois niveaux : Khoni moyen : plus que le facile, dont 2 pièces de DCA sur 4
- 04 Entraînement de Khoni : trois niveaux : Khoni difficile : plus que le moyen
- 05 Front de Gali, et le drone JTAC : Gali : la zone apparaît, artillerie Msta comprise
- 05 Front de Gali, et le drone JTAC : Reaper 1 déclaré JTAC par CTLD, code 1511
- 06 Défense aérienne intégrée (Skynet) : Réseau rouge : SA-11, SA-15, SA-6 d'Ochamchire et EWR inscrits dans Skynet
- 07 Mission chaînée : le port d'Ochamchire : Port activé ; la zone des navires n'existe pas encore
- 07 Mission chaînée : le port d'Ochamchire : Port détruit : les navires apparaissent une minute après
- 08 Opération Tkvarcheli : tâches et dépendances : Opération activée depuis son menu : les trois tâches apparaissent
- 09 Convoi en mouvement : Convoi activé : il roule
- 10 Convoi sous le feu : `-convoy, dest EMBUSCADE, side blue` : le convoi est surveillé
- 10 Convoi sous le feu : Au contact, il réagit avant d'être détruit
- 10 Convoi sous le feu : En repli sans pilote bleu, ni appel ni fumigène
- 11 QRA de Soukhoumi : QRA de Soukhoumi prête
- 11 QRA de Soukhoumi : Ses quatre groupes décollent de la piste de Soukhoumi
- 12 Niveau d'opposition : Un niveau d'opposition est réglé
- 12 Niveau d'opposition : Opposition > Niveau > 4 joueur(s) en CAP : niveau 4, fixe
- 12 Niveau d'opposition : La QRA de Soukhoumi choisit son palier d'après le niveau
- 12 Niveau d'opposition : Taille auto : la CAP MiG-29S Good apparaît en scale 2
- 12 Niveau d'opposition : `_opposition air_to_air` : le niveau suit à nouveau les joueurs en CAP
- 13 CAP à la demande et raid sur Senaki : Menu MISSIONS : la CAP MiG-29S Good scale 1 apparaît en vol
- 13 CAP à la demande et raid sur Senaki : `-airstart Raid-Senaki/Good/1` : le raid apparaît avec son escorte
- 13 CAP à la demande et raid sur Senaki : `-airstop Raid-Senaki/Good/1` : le raid s'arrête
- 14 Arène BVR (vagues aériennes) : Arène BVR enregistrée avec ses trois vagues
- 15 Sanctuaire rouge de Gudauta : Sanctuaire rouge de Gudauta enregistré (15 km, protection contre les missiles)
- 16 Ravitailleurs, AWACS et escorte : Texaco 1, Arco 1, Overlord 1 et son escorte en vol
- 16 Ravitailleurs, AWACS et escorte : Menu MOYENS : Overlord 1 réapparaît avec son escorte
- 17 Escorte à la demande : Escorte de Texaco 1 par le modèle fox3
- 17 Escorte à la demande : Escorte refusée, sans modèle à ce nom
- 18 Hélicoptères : FARP, CTLD, CSAR : FARP Khoni présent
- 18 Hélicoptères : FARP, CTLD, CSAR : Pilote abattu créé par la fonction du menu Démo : commandes
- 19 Aérodromes : caisses et troupes CTLD : Kutaisi : zone logistique et zone de troupes bleues
- 20 Porte-avions Stennis et Roosevelt : Opérations aériennes du Stennis : il accélère face au vent
- 20 Porte-avions Stennis et Roosevelt : S-3B et Pedro du Stennis présents avec les opérations

- [ ] FR : `0 en échec`.
- [ ] EN : `0 en échec`.

## En jeu

Ce que les sondes ne voient pas : ce qui se lit, s'entend ou se pilote.

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
| 10 | Convoi sous le feu | Le convoi réagit avant d'être détruit : groupe « unarmed » détaché, compte rendu de contact sous son indicatif, marqueur F10 ; vainqueur, il repart seul, par la route, ses camions repris ; en repli avec un pilote bleu en vol, appel « TROOPS IN CONTACT », fumigènes rouge et vert, puis il tient la position ; en repli sans pilote bleu connecté (slot game master seul), ni appel ni fumigène. | ☐ | |
| 11 | QRA de Soukhoumi | Aucun joueur en CAP, entrée d'un avion bleu dans le cercle : après 60 s, une paire décolle de la piste de Soukhoumi (pas d'apparition en vol) et monte vers l'intrus ; avec deux paires, les quatre avions décollent sans se percuter ; avec trois intrus, deux paires ; aucune réaction à un hélicoptère ; menu Démo : commandes arrête et redémarre la QRA. | ☐ | |
| 12 | Niveau d'opposition | Opposition > Niveau actuel annonce le niveau ; Opposition > Niveau > 4 joueur(s) en CAP l'annonce à 4 « fixe » ; un avion bleu en vol avec des AIM-120 compte, un A-10 non ; un intrus seul dans le cercle de Soukhoumi fait alors décoller deux paires ; Taille auto active la CAP Good/2 ; `_opposition air_to_air` revient au nombre de joueurs en CAP. | ☐ | |
| 13 | CAP à la demande et raid sur Senaki | Chaque CAP apparaît au niveau et à la taille demandés et engage (tir de missile sur une cible bleue) ; le raid apparaît avec son escorte et suit sa route vers Senaki ; `-airstart Raid-Senaki/Good/1` / `-airstop` fonctionnent. | ☐ | |
| 14 | Arène BVR (vagues aériennes) | Entrée d'un joueur bleu : vague 1 après 30 s ; vague suivante 60 s après la destruction de la précédente ; reset par le menu Démo : commandes. | ☐ | |
| 15 | Sanctuaire rouge de Gudauta | Joueur bleu dans le cercle : avertissement à 10 s, défense à 60 s, destruction à 120 s ; un missile tiré sur une unité rouge du sanctuaire est détruit. | ☐ | |
| 16 | Ravitailleurs, AWACS et escorte | Ravitaillement possible sur Texaco 1 (perche) et Arco 1 (panier), TACAN reçus ; réapparition d'Overlord 1 avec son escorte ; `_move tanker` déplace l'orbite de Texaco 1. | ☐ | |
| 17 | Escorte à la demande | En A-10C ou F-16C en vol, +Escorte-moi (fox3) fait apparaître un F-15C qui suit l'avion ; `-escort introuvable` affiche « Aucun modèle d'escorte « introuvable » pour votre camp : pas d'escorte » ; en UH-1H, « Seul un avion peut être escorté ». | ☐ | |
| 18 | Hélicoptères : FARP, CTLD, CSAR | Ravitaillement et réarmement au FARP Khoni ; chargement CTLD de troupes et d'une caisse au FARP ; pilote abattu créé par le menu, balise ADF audible, récupérable et ramené. | ☐ | |
| 19 | Aérodromes : caisses et troupes CTLD | Cercle vert visible autour de Kutaisi pour le camp bleu ; en UH-1H posé dans le cercle, embarquement de troupes et caisse CTLD possibles ; troupes débarquées dans le cercle renvoyées à la base, hors du cercle déployées. | ☐ | |
| 20 | Porte-avions Stennis et Roosevelt | Démarrage des opérations : virage face au vent et vitesse ; TACAN / ICLS / Link 4 reçus ; S-3B et Pedro présents pour chaque navire. | ☐ | |
| 21 | Météo, ATC et assistance cockpit | Message d'accueil à la prise de slot ; menu MÉTÉO ET ATC répond ; checklist F-16C proposée au seul F-16C ; chaque variante météo du build diffère (nuages, température, vent). | ☐ | |

## Hors étapes

- [ ] Aucune erreur Lua VEAF dans `dcs.log` sur une heure de mission.
- [ ] Les dessins F10 (cercles et étiquettes des étapes) sont visibles et lisibles sur la carte du camp bleu.
- [ ] Version anglaise (`_EN`) : menus VEAF, CTLD, visite, « Demo: commands », briefing, carte F10 et cartes du briefing en anglais ; dérouler au moins les étapes 01, 02, 04 et 10 en anglais.
- [ ] La visite guidée existe dans la langue du build, et chaque entrée pose son repère F10.
- [ ] Les chemins de menu hors VEAF cités par la visite (CTLD, SKYNET, Démo : commandes) correspondent aux menus réels.
