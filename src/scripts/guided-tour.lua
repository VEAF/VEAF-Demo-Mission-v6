-- guided-tour.lua — GÉNÉRÉ par tools/gen_tour.py depuis tour/steps.yaml : ne pas modifier à la main.
-- Menus F10 « Visite guidée » (fr) et « Guided tour » (en), au premier niveau : un sous-menu par chapitre, une commande
-- par étape. Une commande affiche le texte de l'étape au seul groupe qui la demande, avec la position
-- recalculée au moment du clic, et pose un repère F10 sur le lieu de l'étape.

demoTour = demoTour or {}
demoTour.chapters = {
  { key = "start", fr = [=[1. Prise en main]=], en = [=[1. Getting started]=] },
  { key = "ground", fr = [=[2. Zones de combat]=], en = [=[2. Combat zones]=] },
  { key = "air", fr = [=[3. Menace aérienne]=], en = [=[3. Air threats]=] },
  { key = "support", fr = [=[4. Soutien et logistique]=], en = [=[4. Support and logistics]=] },
}
demoTour.steps = {
  { n = 1, id = "welcome", chapter = "start", anchorKind = "none", anchorName = [=[]=],
    title = { fr = [=[Bienvenue]=], en = [=[Welcome]=] },
    text = { fr = [=[BIENVENUE

Cette mission montre chaque fonctionnalité des outils VEAF, une par étape. Chaque étape donne le lieu, ce qu'il faut faire et ce qu'on doit voir. Un repère est posé sur votre carte F10 quand vous ouvrez une étape.

À faire :
- Les menus VEAF sont dans F10 > Autre > VEAF ; ce menu a plusieurs pages (« Page suivante » en bas). La visite guidée et les menus « Démo : actions » et « Démo : commandes » sont à part, directement dans F10 > Autre. La mission est en français : les menus aussi.
- Beaucoup de commandes se tapent dans un marqueur de la carte F10 : bouton « Ajouter un repère » de la barre du haut, clic sur la carte, tapez le texte, puis cliquez ailleurs pour valider.
- Slots : à Kutaisi, des slots classiques moteur chaud (A-10C II, F-16C, F/A-18C, UH-1H, Mi-8, AH-64D), et des slots dynamiques sur les quatre bases bleues en multijoueur ; sur les porte-avions, F/A-18C et F-14B.

Ce qu'on doit voir : Le menu VEAF, ses sous-menus, et dans chaque avion les préréglages radio et les points de navigation injectés par le build.]=],
             en = [=[WELCOME

This mission shows every feature of the VEAF tools, one per step. Each step gives the place, what to do and what you should see. A mark is placed on your F10 map when you open a step.

What to do :
- VEAF menus are under F10 > Other > VEAF; that menu has several pages ("Page suivante" = next page, at the bottom). The guided tour and the "Démo : actions" and "Démo : commandes" menus are separate, directly under F10 > Other. The mission runs in French, so the menus are in French too (translations are given here).
- Many commands are typed into an F10 map marker: "Add mark" button in the top bar, click on the map, type the text, then click elsewhere to validate.
- Slots: classic hot-start slots at Kutaisi (A-10C II, F-16C, F/A-18C, UH-1H, Mi-8, AH-64D), dynamic slots on the four blue bases in multiplayer; F/A-18C and F-14B on the carriers.

What you should see : The VEAF menu and its submenus, and in every aircraft the radio presets and waypoints injected by the build.]=] } },
  { n = 2, id = "sandbox", chapter = "start", anchorKind = "zone", anchorName = [=[Bac a sable]=],
    title = { fr = [=[Bac à sable : les commandes de marqueur]=], en = [=[Sandbox: marker commands]=] },
    text = { fr = [=[BAC À SABLE : LES COMMANDES DE MARQUEUR

Le bac à sable, au sud de Kutaisi (point nommé ALPHA), sert à essayer les commandes qu'on tape dans un marqueur F10 : faire apparaître des unités, un convoi, de la fumée, un FARP, et tout effacer.

À faire :
- -sa8 : une batterie SA-8 (alias livré ; liste complète dans la documentation des raccourcis).
- -armor : un groupe blindé tiré au sort ; -armor, size 4, defense 0 pour le régler.
- _spawn unit, name T-80UD, hdg 270 : un char isolé, cap 270.
- -convoy, dest ALPHA : un convoi qui rejoint le point nommé ALPHA par la route (posez le marqueur à quelques km).
- _name point BRAVO : crée votre propre point nommé, réutilisable dans -convoy, dest BRAVO.
- _spawn smoke, color red : une fumée rouge ; -farp : un FARP complet avec son décor.
- -boum : une explosion de 500 kg ; -menage : détruit tout dans un rayon de 2 km (deux raccourcis propres à cette mission).

Ce qu'on doit voir : Chaque commande répond par un message et fait apparaître ce qu'elle annonce à l'emplacement du marqueur ; le marqueur disparaît une fois la commande exécutée.]=],
             en = [=[SANDBOX: MARKER COMMANDS

The sandbox, south of Kutaisi (named point ALPHA), is where you try the commands typed into an F10 marker: spawn units, a convoy, smoke, a FARP, and wipe it all.

What to do :
- -sa8: an SA-8 battery (shipped alias; full list in the shortcuts documentation).
- -armor: a random armour group; -armor, size 4, defense 0 to tune it.
- _spawn unit, name T-80UD, hdg 270: a single tank, heading 270.
- -convoy, dest ALPHA: a convoy that drives by road to the named point ALPHA (place the marker a few km away).
- _name point BRAVO: creates your own named point, usable in -convoy, dest BRAVO.
- _spawn smoke, color red: red smoke; -farp: a complete FARP with its props.
- -boum: a 500 kg explosion; -menage: destroys everything within 2 km (two shortcuts defined by this mission).

What you should see : Each command answers with a message and spawns what it announces at the marker; the marker disappears once the command has run.]=] } },
  { n = 3, id = "generated", chapter = "start", anchorKind = "zone", anchorName = [=[Bac a sable]=],
    title = { fr = [=[Missions générées : CAS et transport]=], en = [=[Generated missions: CAS and transport]=] },
    text = { fr = [=[MISSIONS GÉNÉRÉES : CAS ET TRANSPORT

Deux commandes fabriquent une mission complète là où vous posez le marqueur : un appui aérien rapproché (CAS) ou un transport héliporté.

À faire :
- _cas (ou _cas, size 3, defense 2) dans un marqueur du bac à sable : un groupe ennemi apparaît dans la zone, à trouver et détruire.
- Menu F10 > Autre > VEAF > MISSION CAS : informations sur la cible, fumée, éclairage, passer l'objectif.
- _transport, from ALPHA dans un marqueur posé près du FARP Khoni (à plus de 15 km d'ALPHA) : des caisses à prendre à ALPHA et à livrer au marqueur.
- Menu F10 > Autre > VEAF > MISSION DE TRANSPORT : position de la zone de livraison, fumée.

Ce qu'on doit voir : Un menu propre à la mission générée, et un message quand l'objectif est atteint.]=],
             en = [=[GENERATED MISSIONS: CAS AND TRANSPORT

Two commands build a complete mission where you place the marker: a close air support (CAS) task or a helicopter transport task.

What to do :
- _cas (or _cas, size 3, defense 2) in a sandbox marker: an enemy group appears in the area, to find and destroy.
- F10 > Other > VEAF > MISSION CAS (CAS mission): target information, smoke, illumination, skip the target.
- _transport, from ALPHA in a marker near FARP Khoni (more than 15 km from ALPHA): cargo to pick up at ALPHA and deliver at the marker.
- F10 > Other > VEAF > MISSION DE TRANSPORT (transport mission): drop zone position, smoke.

What you should see : A menu specific to the generated mission, and a message when the objective is met.]=] } },
  { n = 4, id = "training", chapter = "ground", anchorKind = "zone", anchorName = [=[combatZone_Khoni_Easy]=],
    title = { fr = [=[Entraînement de Khoni : trois niveaux]=], en = [=[Khoni training range: three levels]=] },
    text = { fr = [=[ENTRAÎNEMENT DE KHONI : TROIS NIVEAUX

Une zone d'entraînement en trois niveaux posés sur le même cercle. Chaque niveau inclut le précédent : le moyen fait apparaître les cibles du facile en plus des siennes, le difficile celles du moyen.

À faire :
- Menu F10 > Autre > VEAF > ZONES DE COMBAT > Entraînement Khoni > Khoni - facile > Activer la zone.
- Détruisez les camions, puis désactivez et passez au niveau moyen, puis au difficile.
- Infos de la zone, fumée et fusée éclairante dans le même menu.

Ce qu'on doit voir : Facile : huit camions. Moyen : les camions, une compagnie blindée et deux pièces de DCA tirées parmi quatre (jamais les mêmes d'une fois sur l'autre). Difficile : en plus, un bataillon blindé et deux systèmes courte portée tirés au sort.]=],
             en = [=[KHONI TRAINING RANGE: THREE LEVELS

A training range in three levels on the same circle. Each level includes the one below: medium also spawns the easy targets, hard also spawns the medium ones.

What to do :
- F10 > Other > VEAF > ZONES DE COMBAT (combat zones) > Entraînement Khoni > Khoni - facile (easy) > Activer la zone (activate).
- Destroy the trucks, then deactivate and move on to medium (moyen), then hard (difficile).
- Zone info, smoke and illumination flare are in the same menu.

What you should see : Easy: eight trucks. Medium: the trucks, an armour company and two AAA pieces drawn among four (never the same twice). Hard: on top, an armour battalion and two short-range systems drawn at random.]=] } },
  { n = 5, id = "front", chapter = "ground", anchorKind = "zone", anchorName = [=[combatZone_Gali]=],
    title = { fr = [=[Front de Gali, et le drone JTAC]=], en = [=[Gali front, and the JTAC drone]=] },
    text = { fr = [=[FRONT DE GALI, ET LE DRONE JTAC

Une vraie zone de combat sur le front de l'Inguri. Son contenu est décrit par des unités-porteuses qui portent une commande (#command) : la zone fait apparaître à leur place un groupe blindé tiré au sort parmi deux, une batterie d'artillerie, une DCA et des MANPADS. Le drone Reaper 1 orbite au-dessus et désigne les blindés au laser.

À faire :
- Menu F10 > Autre > VEAF > ZONES DE COMBAT > Front de Gali > Activer la zone.
- Le JTAC : code laser 1511, radio 35.55 FM ; menu F10 > Autre > CTLD > JTAC pour la cible en cours.
- Le drone est relançable depuis F10 > Autre > VEAF > MOYENS > Reaper 1 (MQ-9, JTAC).

Ce qu'on doit voir : Un seul des deux groupes blindés apparaît ; le drone annonce sa cible et la désigne au code 1511.]=],
             en = [=[GALI FRONT, AND THE JTAC DRONE

A real combat zone on the Inguri front. Its content is described by carrier units holding a command (#command): the zone spawns in their place one armour group drawn among two, an artillery battery, air defence and MANPADS. The Reaper 1 drone orbits above and lases the armour.

What to do :
- F10 > Other > VEAF > ZONES DE COMBAT > Front de Gali > Activer la zone.
- The JTAC: laser code 1511, radio 35.55 FM; F10 > Other > CTLD > JTAC for the current target.
- The drone can be respawned from F10 > Other > VEAF > MOYENS (assets) > Reaper 1 (MQ-9, JTAC).

What you should see : Only one of the two armour groups appears; the drone announces its target and lases it on code 1511.]=] } },
  { n = 6, id = "iads", chapter = "ground", anchorKind = "zone", anchorName = [=[combatZone_Ochamchire_SAM]=],
    title = { fr = [=[Défense aérienne intégrée (Skynet)]=], en = [=[Integrated air defence (Skynet)]=] },
    text = { fr = [=[DÉFENSE AÉRIENNE INTÉGRÉE (SKYNET)

Le réseau de défense aérienne rouge : un radar d'alerte, un SA-11 et un SA-15 permanents près de Gudauta (posés par #veafInterpreter), plus le SA-6 d'Ochamchire, une zone de combat active dès le démarrage qui rejoint le réseau. Les batteries gardent leur radar éteint et ne l'allument que quand le réseau le leur demande. Les unités au sol rouges servent de guetteurs : elles voient les avions et relaient l'alerte.

À faire :
- Approchez Ochamchire par le sud-est, à basse altitude puis en montant : regardez quand votre RWR s'allume.
- L'état de l'IADS rouge (sites, radars allumés) : F10 > Autre > SKYNET IADS COALITION: RED.
- La vue des guetteurs est propre à chaque camp : F10 > Autre > VEAF > RÉSEAU DE GUETTEURS > Afficher la vue des guetteurs montre les guetteurs de VOTRE camp. Pour voir le réseau rouge, prenez le slot game master rouge de la mission de test (rouvrez la carte F10 après le clic).

Ce qu'on doit voir : Le SA-6 n'émet pas tant que le réseau ne vous a pas détecté, puis s'allume ; le menu SKYNET IADS COALITION: RED montre quel site émet.]=],
             en = [=[INTEGRATED AIR DEFENCE (SKYNET)

The red air defence network: an early-warning radar, a permanent SA-11 and SA-15 near Gudauta (placed by #veafInterpreter), plus the Ochamchire SA-6, a combat zone active from the start that joins the network. Batteries keep their radar off until the network tells them to light up. Red ground units act as spotters: they see aircraft and relay the alert.

What to do :
- Approach Ochamchire from the south-east, low then climbing: watch when your RWR lights up.
- Red IADS status (sites, radars on): F10 > Other > SKYNET IADS COALITION: RED.
- The spotter view belongs to each side: F10 > Other > VEAF > RÉSEAU DE GUETTEURS (spotter network) > Afficher la vue des guetteurs shows YOUR side's spotters. To see the red network, take the red game master slot of the test mission (reopen the F10 map after clicking).

What you should see : The SA-6 stays silent until the network has detected you, then lights up; the SKYNET IADS COALITION: RED menu shows which site is emitting.]=] } },
  { n = 7, id = "chained", chapter = "ground", anchorKind = "zone", anchorName = [=[combatZone_Ochamchire_Port]=],
    title = { fr = [=[Mission chaînée : le port d'Ochamchire]=], en = [=[Chained mission: Ochamchire port]=] },
    text = { fr = [=[MISSION CHAÎNÉE : LE PORT D'OCHAMCHIRE

Deux zones enchaînées : la seconde n'existe pas tant que la première n'est pas terminée. D'abord le dépôt du port, puis, une minute après sa destruction, les cargos et leur corvette en rade (lutte antinavire).

À faire :
- Menu F10 > Autre > VEAF > ZONES DE COMBAT > Port d'Ochamchire - 1 : dépôt > Activer la zone.
- Détruisez les camions et la ZU-23, puis attendez une minute.

Ce qu'on doit voir : La zone 1 se termine, et les navires apparaissent au large sans qu'aucun menu ne les ait activés. Attention : le cercle de la QRA de Soukhoumi couvre Ochamchire.]=],
             en = [=[CHAINED MISSION: OCHAMCHIRE PORT

Two chained zones: the second does not exist until the first is complete. First the port depot, then, one minute after it is destroyed, the cargo ships and their corvette at anchor (anti-ship).

What to do :
- F10 > Other > VEAF > ZONES DE COMBAT > Port d'Ochamchire - 1 : dépôt > Activer la zone.
- Destroy the trucks and the ZU-23, then wait one minute.

What you should see : Zone 1 completes, and the ships appear offshore without any menu activating them. Beware: the Sukhumi QRA circle covers Ochamchire.]=] } },
  { n = 8, id = "operation", chapter = "ground", anchorKind = "zone", anchorName = [=[Op_Tkvarcheli]=],
    title = { fr = [=[Opération Tkvarcheli : tâches et dépendances]=], en = [=[Operation Tkvarcheli: tasks and dependencies]=] },
    text = { fr = [=[OPÉRATION TKVARCHELI : TÂCHES ET DÉPENDANCES

Une opération regroupe plusieurs zones en tâches : le radar et le dépôt d'abord, puis le poste de commandement, qui n'est donné comme objectif qu'une fois les deux premiers détruits. Toutes les unités apparaissent à l'activation : la dépendance ordonne les objectifs, pas l'apparition.

À faire :
- Menu F10 > Autre > Démo : actions > Activer l'opération Tkvarcheli (VEAF ne pose pas de commande d'activation dans le menu d'une opération : la démo la fournit).
- Menu F10 > Autre > VEAF > ZONES DE COMBAT > Opération Tkvarcheli : la tâche en cours ; détruisez le radar 1L13 et le dépôt (statiques), puis le PC.

Ce qu'on doit voir : Les tâches passent de « en cours » à « terminée » ; quand les trois sont faites, le message « L'opération … est terminée ».]=],
             en = [=[OPERATION TKVARCHELI: TASKS AND DEPENDENCIES

An operation groups several zones as tasks: the radar and the depot first, then the command post, given as an objective only once the first two are destroyed. All units spawn on activation: the dependency orders the objectives, not the spawning.

What to do :
- F10 > Other > Démo : actions > Activer l'opération Tkvarcheli (activate; VEAF puts no activation command in an operation's menu, so the demo provides one).
- F10 > Other > VEAF > ZONES DE COMBAT > Opération Tkvarcheli: the current task; destroy the 1L13 radar and the depot (statics), then the command post.

What you should see : Tasks move from "in progress" to "done"; when all three are done, the message "Operation … is over".]=] } },
  { n = 9, id = "convoy", chapter = "ground", anchorKind = "zone", anchorName = [=[combatZone_Convoi]=],
    title = { fr = [=[Convoi en mouvement]=], en = [=[Moving convoy]=] },
    text = { fr = [=[CONVOI EN MOUVEMENT

Un convoi logistique, cinq camions et sa Shilka, qui fait la navette entre Ochamchire et Gali : une cible qui bouge.

À faire :
- Menu F10 > Autre > VEAF > ZONES DE COMBAT > Convoi d'Ochamchire > Activer la zone.
- Infos de la zone : la position du convoi au moment de la demande.

Ce qu'on doit voir : Le convoi roule vers Gali, puis revient, en boucle.]=],
             en = [=[MOVING CONVOY

A logistics convoy, five trucks and their Shilka, shuttling between Ochamchire and Gali: a moving target.

What to do :
- F10 > Other > VEAF > ZONES DE COMBAT > Convoi d'Ochamchire > Activer la zone.
- Zone info: the convoy position when you ask.

What you should see : The convoy drives to Gali, then comes back, in a loop.]=] } },
  { n = 10, id = "qra", chapter = "air", anchorKind = "zone", anchorName = [=[QRA-Soukhoumi]=],
    title = { fr = [=[QRA de Soukhoumi]=], en = [=[Sukhumi QRA]=] },
    text = { fr = [=[QRA DE SOUKHOUMI

Une alerte en vol (QRA) défend Soukhoumi dans un cercle de 40 km, qui couvre Ochamchire. Elle répond à la menace : un intrus fait décoller une paire tirée au sort entre MiG-29S et Su-27 ; trois intrus ou plus, deux paires parmi Su-30, MiG-31 et MiG-29S. Elle ne réagit pas aux hélicoptères.

À faire :
- Entrez dans le cercle (dessiné sur la carte F10) avec un avion : la QRA décolle 60 s plus tard.
- Menu F10 > Autre > Démo : commandes > Arrêter / Démarrer la QRA de Soukhoumi (menu déclaré en YAML).

Ce qu'on doit voir : Un message annonce le décollage ; les chasseurs viennent vers vous. Une fois la QRA détruite, elle se réarme 5 minutes après que le cercle s'est vidé d'intrus.]=],
             en = [=[SUKHUMI QRA

A quick reaction alert (QRA) defends Sukhumi within a 40 km circle that covers Ochamchire. It answers the threat: one intruder scrambles a pair drawn between MiG-29S and Su-27; three or more, two pairs among Su-30, MiG-31 and MiG-29S. It ignores helicopters.

What to do :
- Enter the circle (drawn on the F10 map) in an aircraft: the QRA scrambles 60 s later.
- F10 > Other > Démo : commandes > Arrêter / Démarrer la QRA de Soukhoumi (stop / start; a menu declared in YAML).

What you should see : A message announces the scramble; the fighters come at you. Once destroyed, the QRA rearms 5 minutes after the circle is clear of intruders.]=] } },
  { n = 11, id = "cap", chapter = "air", anchorKind = "airbase", anchorName = [=[Gudauta]=],
    title = { fr = [=[CAP à la demande et raid sur Senaki]=], en = [=[On-demand CAP and the Senaki raid]=] },
    text = { fr = [=[CAP À LA DEMANDE ET RAID SUR SENAKI

Des patrouilles rouges qu'on fait apparaître depuis le menu, de menaces différentes (MiG-29S Fox 3, Su-27 Fox 1, MiG-31), et une mission scénarisée : deux Su-24M escortés par deux MiG-29S partent bombarder Senaki.

À faire :
- Menu F10 > Autre > VEAF > MISSIONS > CAP MiG-29S Gudauta FL250 > niveau (Good, Excellent) > taille (scale 1, 2) > Activer la mission.
- Menu F10 > Autre > VEAF > MISSIONS > Raid sur Senaki > Good > scale 1 > Activer la mission, puis interceptez les bombardiers.
- Ou par marqueur : -airstart Raid-Senaki/Good/1, -airstop Raid-Senaki/Good/1 (nom, niveau, taille).

Ce qu'on doit voir : La patrouille apparaît en vol sur son hippodrome et engage ce qui entre à portée ; le raid vole vers Senaki et bombarde la base s'il n'est pas intercepté.]=],
             en = [=[ON-DEMAND CAP AND THE SENAKI RAID

Red patrols you spawn from the menu, each a different threat (MiG-29S Fox 3, Su-27 Fox 1, MiG-31), and a scripted mission: two Su-24M escorted by two MiG-29S head out to bomb Senaki.

What to do :
- F10 > Other > VEAF > MISSIONS > CAP MiG-29S Gudauta FL250 > level (Good, Excellent) > size (scale 1, 2) > Activer la mission (activate).
- F10 > Other > VEAF > MISSIONS > Raid sur Senaki > Good > scale 1 > Activer la mission, then intercept the bombers.
- Or by marker: -airstart Raid-Senaki/Good/1, -airstop Raid-Senaki/Good/1 (name, level, size).

What you should see : The patrol spawns airborne on its race-track and engages what comes in range; the raid flies to Senaki and bombs the base unless intercepted.]=] } },
  { n = 12, id = "airwaves", chapter = "air", anchorKind = "zone", anchorName = [=[Arene BVR]=],
    title = { fr = [=[Arène BVR (vagues aériennes)]=], en = [=[BVR arena (air waves)]=] },
    text = { fr = [=[ARÈNE BVR (VAGUES AÉRIENNES)

Une arène au large de Poti : dès qu'un avion bleu y entre, des vagues de chasseurs rouges arrivent l'une après l'autre, de plus en plus dures (MiG-29S seul, deux Su-27, deux Su-30).

À faire :
- Entrez dans le cercle de l'arène (dessiné sur la carte F10), entre 1 000 et 40 000 ft.
- Pour recommencer : F10 > Autre > Démo : commandes > Relancer l'arène BVR.

Ce qu'on doit voir : Message de début, puis une vague ; la suivante arrive une minute après la destruction de la précédente. Si vous mourez, l'arène se réinitialise.]=],
             en = [=[BVR ARENA (AIR WAVES)

An arena off Poti: as soon as a blue aircraft enters, waves of red fighters come one after another, harder each time (a single MiG-29S, two Su-27, two Su-30).

What to do :
- Enter the arena circle (drawn on the F10 map), between 1,000 and 40,000 ft.
- To start over: F10 > Other > Démo : commandes > Relancer l'arène BVR (reset).

What you should see : A start message, then a wave; the next comes one minute after the previous is destroyed. If you die, the arena resets.]=] } },
  { n = 13, id = "sanctuary", chapter = "air", anchorKind = "zone", anchorName = [=[Sanctuaire Gudauta]=],
    title = { fr = [=[Sanctuaire rouge de Gudauta]=], en = [=[Gudauta red sanctuary]=] },
    text = { fr = [=[SANCTUAIRE ROUGE DE GUDAUTA

Un sanctuaire protège une zone pour un camp : un pilote adverse qui y entre est averti, puis une défense apparaît, puis il est abattu. Celui-ci protège Gudauta (15 km) côté rouge ; il détruit aussi les missiles tirés sur les unités qui s'y trouvent.

À faire :
- Entrez dans le cercle de Gudauta avec un avion bleu et restez-y.

Ce qu'on doit voir : Avertissement après 10 s, défense déployée à 60 s, avion abattu à 120 s.]=],
             en = [=[GUDAUTA RED SANCTUARY

A sanctuary protects an area for one side: an enemy pilot who enters is warned, then defences spawn, then the aircraft is shot down. This one protects Gudauta (15 km) for red; it also destroys missiles fired at units inside it.

What to do :
- Fly into the Gudauta circle in a blue aircraft and stay.

What you should see : Warning after 10 s, defences deployed at 60 s, aircraft shot down at 120 s.]=] } },
  { n = 14, id = "assets", chapter = "support", anchorKind = "group", anchorName = [=[Texaco 1]=],
    title = { fr = [=[Ravitailleurs, AWACS et escorte]=], en = [=[Tankers, AWACS and escort]=] },
    text = { fr = [=[RAVITAILLEURS, AWACS ET ESCORTE

Deux ravitailleurs (Texaco 1 à perche, Arco 1 à panier) et un AWACS (Overlord 1) escorté par deux F-15C. Le menu MOYENS les relance et donne leurs informations ; une commande de marqueur déplace un ravitailleur.

À faire :
- Texaco 1 : TACAN 52Y, 292.0 AM, FL200 ; Arco 1 : TACAN 51Y, 291.0 AM, FL180 ; Overlord 1 : 286.0 AM.
- Menu F10 > Autre > VEAF > MOYENS > Overlord 1 (E-3A) > Réapparition de Overlord 1 (E-3A) : l'AWACS et son escorte réapparaissent ensemble.
- Marqueur _move tanker, name Texaco 1, alt 22000 posé où vous voulez l'hippodrome.

Ce qu'on doit voir : Les ravitailleurs répondent sur leur fréquence et leur TACAN ; après un _move tanker, Texaco 1 rejoint sa nouvelle orbite.]=],
             en = [=[TANKERS, AWACS AND ESCORT

Two tankers (Texaco 1 boom, Arco 1 drogue) and an AWACS (Overlord 1) escorted by two F-15C. The MOYENS (assets) menu respawns them and gives their details; a marker command moves a tanker.

What to do :
- Texaco 1: TACAN 52Y, 292.0 AM, FL200; Arco 1: TACAN 51Y, 291.0 AM, FL180; Overlord 1: 286.0 AM.
- F10 > Other > VEAF > MOYENS > Overlord 1 (E-3A) > Réapparition de Overlord 1 (E-3A) (respawn): the AWACS and its escort respawn together.
- Marker _move tanker, name Texaco 1, alt 22000 where you want the race-track.

What you should see : Tankers answer on their frequency and TACAN; after a _move tanker, Texaco 1 flies to its new orbit.]=] } },
  { n = 15, id = "helos", chapter = "support", anchorKind = "group", anchorName = [=[FARP Khoni]=],
    title = { fr = [=[Hélicoptères : FARP, CTLD, CSAR]=], en = [=[Helicopters: FARP, CTLD, CSAR]=] },
    text = { fr = [=[HÉLICOPTÈRES : FARP, CTLD, CSAR

Le FARP Khoni réarme et ravitaille les hélicoptères ; son dépôt de munitions est un point de chargement CTLD (troupes et caisses). Un pilote abattu peut être créé à la demande, à aller chercher en hélicoptère (CSAR).

À faire :
- Décollez de Kutaisi en UH-1H ou Mi-8 et posez-vous au FARP Khoni (127.5 AM).
- Menu F10 > Autre > CTLD : charger des troupes, demander une caisse, puis les déposer ailleurs.
- Menu F10 > Autre > Démo : actions > Créer un pilote abattu près de Khoni, puis menu CSAR pour sa balise et sa position.

Ce qu'on doit voir : Le FARP ravitaille et réarme ; CTLD charge les troupes ; le pilote abattu émet une balise et se laisse embarquer.]=],
             en = [=[HELICOPTERS: FARP, CTLD, CSAR

FARP Khoni rearms and refuels helicopters; its ammo dump is a CTLD loading point (troops and crates). A downed pilot can be created on demand, to be rescued by helicopter (CSAR).

What to do :
- Take off from Kutaisi in a UH-1H or Mi-8 and land at FARP Khoni (127.5 AM).
- F10 > Other > CTLD: load troops, request a crate, then drop them elsewhere.
- F10 > Other > Démo : actions > Créer un pilote abattu près de Khoni (create a downed pilot), then the CSAR menu for its beacon and position.

What you should see : The FARP refuels and rearms; CTLD loads the troops; the downed pilot transmits a beacon and boards.]=] } },
  { n = 16, id = "carrier", chapter = "support", anchorKind = "group", anchorName = [=[CSG-74 Stennis]=],
    title = { fr = [=[Porte-avions Stennis et Roosevelt]=], en = [=[Stennis and Roosevelt carriers]=] },
    text = { fr = [=[PORTE-AVIONS STENNIS ET ROOSEVELT

Deux porte-avions au large de Batumi, chacun avec son ravitailleur S-3B et son hélicoptère de sauvetage. Le menu OPS PORTE-AVIONS met le navire face au vent pour les opérations aériennes.

À faire :
- Stennis : TACAN 74X STN, ICLS 4, Link 4 336.0, tour 274.0 AM. Roosevelt : TACAN 71X TDR, ICLS 1, Link 4 337.0, tour 271.0 AM.
- Menu F10 > Autre > VEAF > OPS PORTE-AVIONS > OPS PORTE-AVIONS - BLEU > CSG-74 Stennis > Start carrier air operations for 45 minutes.
- Slots de pont : Stennis F/A-18C, Roosevelt F-14B.

Ce qu'on doit voir : Le porte-avions vire face au vent, accélère, et le menu donne le cap de récupération ; le S-3B ravitaille.]=],
             en = [=[STENNIS AND ROOSEVELT CARRIERS

Two carriers off Batumi, each with its S-3B tanker and rescue helicopter. The OPS PORTE-AVIONS (carrier ops) menu turns the ship into the wind for air operations.

What to do :
- Stennis: TACAN 74X STN, ICLS 4, Link 4 336.0, tower 274.0 AM. Roosevelt: TACAN 71X TDR, ICLS 1, Link 4 337.0, tower 271.0 AM.
- F10 > Other > VEAF > OPS PORTE-AVIONS > OPS PORTE-AVIONS - BLEU > CSG-74 Stennis > Start carrier air operations for 45 minutes.
- Deck slots: Stennis F/A-18C, Roosevelt F-14B.

What you should see : The carrier turns into the wind, speeds up, and the menu gives the recovery course; the S-3B refuels.]=] } },
  { n = 17, id = "weather", chapter = "support", anchorKind = "airbase", anchorName = [=[Kutaisi]=],
    title = { fr = [=[Météo, ATC et assistance cockpit]=], en = [=[Weather, ATC and cockpit assistance]=] },
    text = { fr = [=[MÉTÉO, ATC ET ASSISTANCE COCKPIT

Un message d'accueil à la prise de slot (base, piste en service, météo), un menu météo et ATC, et pour le F-16C une checklist de démarrage pas à pas. Sur un serveur VEAF, la météo suit la METAR réelle de Kutaisi (UGKO).

À faire :
- Prenez un slot à Kutaisi : lisez le message d'accueil.
- Menu F10 > Autre > VEAF > MÉTÉO ET ATC > météo au point le plus proche / ATC de la base la plus proche.
- En F-16C à Kutaisi : F10 > Autre > VEAF > Assistance > Démarrage à froid ; ensuite, à la racine du menu VEAF : ASSISTANCE : VALIDER L'ÉTAPE / PASSER L'ÉTAPE.

Ce qu'on doit voir : Le message d'accueil donne la piste en service ; la checklist coche les étapes déjà faites.]=],
             en = [=[WEATHER, ATC AND COCKPIT ASSISTANCE

A welcome message when you take a slot (base, runway in use, weather), a weather and ATC menu, and for the F-16C a step-by-step start-up checklist. On a VEAF server, the weather follows Kutaisi's real METAR (UGKO).

What to do :
- Take a slot at Kutaisi: read the welcome message.
- F10 > Other > VEAF > MÉTÉO ET ATC (weather and ATC) > weather at closest point / ATC of closest airbase.
- In the F-16C at Kutaisi: F10 > Other > VEAF > Assistance > Démarrage à froid (cold start); then, at the root of the VEAF menu: ASSISTANCE : VALIDER L'ÉTAPE / PASSER L'ÉTAPE (confirm / skip).

What you should see : The welcome message gives the runway in use; the checklist ticks the steps already done.]=] } },
}

-- ── Code de la visite (tools/guided-tour-runtime.lua, recopié tel quel par gen_tour.py) ───────────

demoTour.MESSAGE_DURATION = 60
demoTour.marks = {}        -- groupId -> id du repère F10 posé pour ce groupe
demoTour.nextMarkId = 7700000

local TXT = {
  fr = { where = "Où : %s, à %d nm de vous au %03d.", whereNoPlayer = "Où : %s.", nowhere = "Où : partout.",
         unknown = "Où : lieu introuvable (%s).", root = "Visite guidée", summary = "00. Sommaire",
         summaryText = "VISITE GUIDÉE\n\nChoisissez un chapitre, puis une étape : son texte s'affiche une minute et un repère est posé sur votre carte F10.\n\n" },
  en = { where = "Where: %s, %d nm from you, bearing %03d.", whereNoPlayer = "Where: %s.", nowhere = "Where: anywhere.",
         unknown = "Where: place not found (%s).", root = "Guided tour", summary = "00. Summary",
         summaryText = "GUIDED TOUR\n\nPick a chapter, then a step: its text shows for one minute and a mark is placed on your F10 map.\n\n" },
}

--- Position (vec3) du lieu d'une étape, lue au moment du clic : les navires et les avions bougent.
function demoTour.anchorPoint(step)
  local kind, name = step.anchorKind, step.anchorName
  if kind == "zone" then
    local zone = trigger.misc.getZone(name)
    return zone and zone.point
  elseif kind == "group" then
    local group = Group.getByName(name)
    if group and group:isExist() and group:getUnit(1) then
      return group:getUnit(1):getPoint()
    end
    local static = StaticObject.getByName(name)
    if static and static:isExist() then
      return static:getPoint()
    end
    -- un héliport (FARP) se trouve aussi comme Airbase
    local airbase = Airbase.getByName(name)
    if airbase then
      return airbase:getPoint()
    end
  elseif kind == "airbase" then
    local airbase = Airbase.getByName(name)
    return airbase and airbase:getPoint()
  end
  return nil
end

local function bearingAndRangeNm(from, to)
  local dx, dz = to.x - from.x, to.z - from.z
  local brg = math.floor(math.deg(math.atan2(dz, dx)) + 0.5) % 360
  return brg, math.floor(math.sqrt(dx * dx + dz * dz) / 1852 + 0.5)
end

local function bullseyeText(point)
  local bull = coalition.getMainRefPoint(coalition.side.BLUE)
  local brg, range = bearingAndRangeNm(bull, point)
  return string.format("BULLSEYE %03d/%d", brg, range)
end

function demoTour.whereText(step, lang, unit)
  local t = TXT[lang]
  if step.anchorKind == "none" then
    return t.nowhere
  end
  local point = demoTour.anchorPoint(step)
  if not point then
    return string.format(t.unknown, step.anchorName)
  end
  if unit and unit:isExist() then
    local brg, range = bearingAndRangeNm(unit:getPoint(), point)
    return string.format(t.where, bullseyeText(point), range, brg)
  end
  return string.format(t.whereNoPlayer, bullseyeText(point))
end

-- ── Menus : posés directement avec missionCommands, au premier niveau de F10 > Autre ─────────────
-- Hors de veafRadio, pour deux raisons : la visite doit se voir au premier niveau (à côté de VEAF et
-- CTLD), et chaque commande porte elle-même son groupe et sa langue — aucun paramètre n'est ajouté
-- ou réécrit entre le menu et la fonction.

local function firstAliveUnit(groupName)
  local group = Group.getByName(groupName)
  if group and group:isExist() then
    for _, unit in ipairs(group:getUnits()) do
      if unit:isExist() then
        return unit
      end
    end
  end
  return nil
end

--- Commande d'une étape : args = { group = <nom du groupe>, groupId = <id>, n = <étape>, lang = "fr" | "en" }.
function demoTour.show(args)
  local step, lang = demoTour.steps[args.n], args.lang
  local unit = firstAliveUnit(args.group)
  local text = step.text[lang] .. "\n\n" .. demoTour.whereText(step, lang, unit)
  trigger.action.outTextForGroup(args.groupId, text, demoTour.MESSAGE_DURATION)
  if demoTour.marks[args.groupId] then
    trigger.action.removeMark(demoTour.marks[args.groupId])
    demoTour.marks[args.groupId] = nil
  end
  local point = demoTour.anchorPoint(step)
  if point then
    demoTour.nextMarkId = demoTour.nextMarkId + 1
    trigger.action.markToGroup(demoTour.nextMarkId, string.format("%02d. %s", step.n, step.title[lang]), point, args.groupId, true)
    demoTour.marks[args.groupId] = demoTour.nextMarkId
  end
end

function demoTour.showSummary(args)
  local lang = args.lang
  local lines = { TXT[lang].summaryText }
  for _, chapter in ipairs(demoTour.chapters) do
    table.insert(lines, chapter[lang])
    for _, step in ipairs(demoTour.steps) do
      if step.chapter == chapter.key then
        table.insert(lines, string.format("   %02d. %s", step.n, step.title[lang]))
      end
    end
  end
  trigger.action.outTextForGroup(args.groupId, table.concat(lines, "\n"), demoTour.MESSAGE_DURATION)
end

--- Les actions de la démo, appelées au clic (les fonctions vivent dans mission-script.lua).
local function call(name)
  return function()
    if demo and demo[name] then
      demo[name]()
    end
  end
end

demoTour.groupMenus = {}   -- groupId -> { chemins de premier niveau posés pour ce groupe }

--- Pose (ou repose) les deux menus de la visite pour un groupe de joueurs.
function demoTour.addMenusForGroup(group)
  local groupId, groupName = group:getID(), group:getName()
  for _, path in ipairs(demoTour.groupMenus[groupId] or {}) do
    missionCommands.removeItemForGroup(groupId, path)
  end
  local paths = {}
  for _, lang in ipairs({ "fr", "en" }) do
    local root = missionCommands.addSubMenuForGroup(groupId, TXT[lang].root)
    table.insert(paths, root)
    missionCommands.addCommandForGroup(groupId, TXT[lang].summary, root, demoTour.showSummary,
      { group = groupName, groupId = groupId, lang = lang })
    for _, chapter in ipairs(demoTour.chapters) do
      local menu = missionCommands.addSubMenuForGroup(groupId, chapter[lang], root)
      for _, step in ipairs(demoTour.steps) do
        if step.chapter == chapter.key then
          missionCommands.addCommandForGroup(groupId, string.format("%02d. %s", step.n, step.title[lang]), menu,
            demoTour.show, { group = groupName, groupId = groupId, n = step.n, lang = lang })
        end
      end
    end
  end
  demoTour.groupMenus[groupId] = paths
end

local function isPlayerUnit(unit)
  return unit and unit.getPlayerName and unit:getPlayerName() ~= nil
end

demoTour.eventHandler = {}
function demoTour.eventHandler:onEvent(event)
  if (event.id == world.event.S_EVENT_BIRTH or event.id == world.event.S_EVENT_PLAYER_ENTER_UNIT)
    and isPlayerUnit(event.initiator) and event.initiator.getGroup then
    local ok, err = pcall(demoTour.addMenusForGroup, event.initiator:getGroup())
    if not ok then
      env.error("demoTour: " .. tostring(err))
    end
  end
end

function demoTour.buildMenus()
  -- Actions de la démo : un seul menu pour tous, au premier niveau.
  local actions = missionCommands.addSubMenu("Démo : actions")
  missionCommands.addCommand("Créer un pilote abattu près de Khoni", actions, call("spawnCsar"))
  missionCommands.addCommand("Activer l'opération Tkvarcheli", actions, call("activateOperation"))
  missionCommands.addCommand("Désactiver l'opération Tkvarcheli", actions, call("desactivateOperation"))
  -- Visite : par groupe de joueurs, à chaque arrivée dans un appareil (slots classiques et dynamiques).
  world.addEventHandler(demoTour.eventHandler)
  for _, side in ipairs({ coalition.side.BLUE, coalition.side.RED }) do
    for _, category in ipairs({ Group.Category.AIRPLANE, Group.Category.HELICOPTER }) do
      for _, group in ipairs(coalition.getGroups(side, category)) do
        local unit = group:getUnit(1)
        if isPlayerUnit(unit) then
          demoTour.addMenusForGroup(group)
        end
      end
    end
  end
  env.info(string.format("demoTour: %d étapes, menus fr et en au premier niveau", #demoTour.steps))
end

demoTour.buildMenus()
