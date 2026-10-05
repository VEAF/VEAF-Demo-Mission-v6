
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

--- La langue du build : mission.language de mission.yaml (profils FR / EN), écrite par le build dans
--- veaf.config.language. Une mission = une langue, menus et messages compris.
demoTour.lang = (veaf and veaf.config and veaf.config.language == "en") and "en" or "fr"

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

demoTour.groupMenus = {}   -- groupId -> { chemins de premier niveau posés pour ce groupe }

--- Pose (ou repose) les deux menus de la visite pour un groupe de joueurs.
function demoTour.addMenusForGroup(group)
  local groupId, groupName = group:getID(), group:getName()
  for _, path in ipairs(demoTour.groupMenus[groupId] or {}) do
    missionCommands.removeItemForGroup(groupId, path)
  end
  local paths = {}
  for _, lang in ipairs({ demoTour.lang }) do
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
  env.info(string.format("demoTour: %d étapes, langue %s, menus au premier niveau", #demoTour.steps, demoTour.lang))
end

demoTour.buildMenus()
