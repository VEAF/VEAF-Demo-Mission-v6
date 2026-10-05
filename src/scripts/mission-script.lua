-- mission-script.lua — le Lua propre à la mission de démo.
--
-- Chargé APRÈS veaf-config.lua (généré depuis mission.yaml), et avant les custom_scripts
-- (src/scripts/guided-tour.lua, la visite guidée, générée par tools/gen_tour.py).
--
-- Ne contient que ce que mission.yaml ne sait pas exprimer : la fonction appelée par l'action `lua` du
-- menu « Démo : commandes » (modules.RADIO.user_menus). Le build vérifie qu'elle existe.

demo = demo or {}

--- Crée un pilote bleu abattu dans la zone « Demo CSAR », au nord du FARP Khoni, pour l'étape CSAR.
function demo.spawnCsar()
  local en = veaf.config.language == "en"
  if not csar then
    trigger.action.outText(en and "CSAR is not loaded in this mission." or "CSAR n'est pas chargé dans cette mission.", 10)
    return
  end
  csar.spawnCsarAtZone("Demo CSAR", coalition.side.BLUE, en and "Demo pilot" or "Pilote de démonstration", true)
  trigger.action.outTextForCoalition(coalition.side.BLUE, en
    and "A downed pilot is waiting north of FARP Khoni: listen for the beacon and pick the pilot up by helicopter (F10 > Other > CSAR)."
    or "Un pilote abattu attend au nord du FARP Khoni : écoutez sa balise et allez le chercher en hélicoptère (menu F10 > Autre > CSAR).", 20)
end
