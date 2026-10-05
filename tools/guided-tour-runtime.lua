
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

--- Commande d'une étape. veafRadio (USAGE_ForGroup) passe { { n, lang }, unitName }.
function demoTour.show(parameters)
  local args, unitName = parameters[1], parameters[2]
  local step, lang = demoTour.steps[args[1]], args[2]
  local unit = unitName and Unit.getByName(unitName)
  if not (unit and unit:isExist()) then
    return
  end
  local groupId = unit:getGroup():getID()
  local text = step.text[lang] .. "\n\n" .. demoTour.whereText(step, lang, unit)
  trigger.action.outTextForGroup(groupId, text, demoTour.MESSAGE_DURATION)
  local point = demoTour.anchorPoint(step)
  if demoTour.marks[groupId] then
    trigger.action.removeMark(demoTour.marks[groupId])
    demoTour.marks[groupId] = nil
  end
  if point then
    demoTour.nextMarkId = demoTour.nextMarkId + 1
    trigger.action.markToGroup(demoTour.nextMarkId, string.format("%02d. %s", step.n, step.title[lang]), point, groupId, true)
    demoTour.marks[groupId] = demoTour.nextMarkId
  end
end

function demoTour.showSummary(parameters)
  local lang, unitName = parameters[1], parameters[2]
  local unit = unitName and Unit.getByName(unitName)
  if not (unit and unit:isExist()) then
    return
  end
  local lines = { TXT[lang].summaryText }
  for _, chapter in ipairs(demoTour.chapters) do
    table.insert(lines, chapter[lang])
    for _, step in ipairs(demoTour.steps) do
      if step.chapter == chapter.key then
        table.insert(lines, string.format("   %02d. %s", step.n, step.title[lang]))
      end
    end
  end
  trigger.action.outTextForGroup(unit:getGroup():getID(), table.concat(lines, "\n"), demoTour.MESSAGE_DURATION)
end

--- Les actions de la démo, appelées au clic (les fonctions vivent dans mission-script.lua).
local function call(name)
  return function()
    if demo and demo[name] then
      demo[name]()
    end
  end
end

function demoTour.buildMenus()
  -- La racine VEAF dépasse MENU_PAGE_SIZE (10) entrées et se pagine : `sortKey` place la visite et
  -- les actions de la démo en tête de la première page, devant les menus des modules.
  local actions = veafRadio.addMenu("Démo : actions")
  actions.sortKey = "!3"
  veafRadio.addCommandToSubmenu("Créer un pilote abattu près de Khoni", actions, call("spawnCsar"), nil, veafRadio.USAGE_ForAll)
  veafRadio.addCommandToSubmenu("Activer l'opération Tkvarcheli", actions, call("activateOperation"), nil, veafRadio.USAGE_ForAll)
  veafRadio.addCommandToSubmenu("Désactiver l'opération Tkvarcheli", actions, call("desactivateOperation"), nil, veafRadio.USAGE_ForAll)
  for i, lang in ipairs({ "fr", "en" }) do
    local root = veafRadio.addMenu(TXT[lang].root)
    root.sortKey = "!" .. i
    veafRadio.addCommandToSubmenu(TXT[lang].summary, root, demoTour.showSummary, lang, veafRadio.USAGE_ForGroup)
    for _, chapter in ipairs(demoTour.chapters) do
      local menu = veafRadio.addSubMenu(chapter[lang], root)
      for _, step in ipairs(demoTour.steps) do
        if step.chapter == chapter.key then
          local title = string.format("%02d. %s", step.n, step.title[lang])
          veafRadio.addCommandToSubmenu(title, menu, demoTour.show, { step.n, lang }, veafRadio.USAGE_ForGroup)
        end
      end
    end
  end
  veafRadio.refreshRadioMenu()
  veaf.loggers.get(veaf.Id):info("demoTour: %d étapes, menus fr et en", #demoTour.steps)
end

demoTour.buildMenus()
