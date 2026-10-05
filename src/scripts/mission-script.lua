-- mission-script.lua — le Lua propre à la mission de démo.
--
-- Chargé APRÈS veaf-config.lua (généré depuis mission.yaml), et avant les custom_scripts
-- (src/scripts/guided-tour.lua, la visite guidée, générée par tools/gen_tour.py, qui pose aussi le
-- menu « DÉMO : ACTIONS » appelant les fonctions ci-dessous).
--
-- Ces fonctions ne sont PAS branchées sur une action `lua` de modules.RADIO.user_menus : le build
-- y écrit une référence nue (`demo.spawnCsar`) évaluée dans veaf-config.lua, avant que ce fichier
-- soit chargé, et toute la config s'arrête sur l'erreur (docs/retours-vmct.md, n° 8).

demo = demo or {}

--- Crée un pilote bleu abattu dans la zone « Demo CSAR », au nord du FARP Khoni, pour l'étape CSAR.
function demo.spawnCsar()
  if not csar then
    trigger.action.outText("CSAR n'est pas chargé dans cette mission.", 10)
    return
  end
  csar.spawnCsarAtZone("Demo CSAR", coalition.side.BLUE, "Pilote de démonstration", true)
  trigger.action.outTextForCoalition(coalition.side.BLUE,
    "Un pilote abattu attend au nord du FARP Khoni : écoutez sa balise et allez le chercher en hélicoptère (menu F10 > Autre > CSAR).", 20)
end

--- Active / désactive l'opération Tkvarcheli : VEAF ne pose pas ces commandes dans le menu d'une
--- opération (elles sont commentées dans veafCombatZone.lua), la démo les fournit.
function demo.activateOperation()
  veafCombatZone.ActivateZone("Op_Tkvarcheli")
end

function demo.desactivateOperation()
  veafCombatZone.DesactivateZone("Op_Tkvarcheli")
end
