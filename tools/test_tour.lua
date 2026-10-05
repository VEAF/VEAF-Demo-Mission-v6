-- Essai hors DCS de la visite guidée : bouchons minimaux de l'API DCS, puis chaque commande de chaque
-- menu, et le contrôle que le menu français parle français et l'anglais anglais.
-- lua tools/test_tour.lua (Lua 5.1, comme DCS).
local shown, marks = {}, {}
local function pt(x, z) return { x = x, y = 0, z = z } end

-- missionCommands : un arbre de menus, par groupe ou commun
local menus = { common = {}, group = {} }
local function node(title, parent, list)
  local n = { title = title, items = {} }
  table.insert(parent and parent.items or list, n)
  return n
end
missionCommands = {
  addSubMenu = function(t, parent) return node(t, parent, menus.common) end,
  addCommand = function(t, parent, f, a) local n = node(t, parent, menus.common); n.f, n.a = f, a; return n end,
  addSubMenuForGroup = function(g, t, parent) menus.group[g] = menus.group[g] or {}; return node(t, parent, menus.group[g]) end,
  addCommandForGroup = function(g, t, parent, f, a) local n = node(t, parent, menus.group[g]); n.f, n.a = f, a; return n end,
  removeItemForGroup = function(g, path)
    for i, n in ipairs(menus.group[g] or {}) do if n == path then table.remove(menus.group[g], i) return end end
  end,
}
local handlers = {}
world = { event = { S_EVENT_BIRTH = 15, S_EVENT_PLAYER_ENTER_UNIT = 20 }, addEventHandler = function(h) table.insert(handlers, h) end }
env = { info = function() end, error = function(m) error(m) end }
trigger = { misc = { getZone = function() return { point = pt(-250000, 600000), radius = 1000 } end },
            action = { outTextForGroup = function(g, t) table.insert(shown, t) end,
                       markToGroup = function(id, t) marks[id] = t end, removeMark = function(id) marks[id] = nil end } }
coalition = { side = { RED = 1, BLUE = 2 }, getMainRefPoint = function() return pt(-253719, 629600) end }
local unit, group
unit = { isExist = function() return true end, getPoint = function() return pt(-284582, 685029) end,
         getPlayerName = function() return "joueur" end, getGroup = function() return group end }
group = { getID = function() return 42 end, getName = function() return "Kutaisi F-16C" end, isExist = function() return true end,
          getUnits = function() return { unit } end, getUnit = function() return unit end }
Group = { Category = { AIRPLANE = 0, HELICOPTER = 1 }, getByName = function() return group end }
coalition.getGroups = function(side, cat) return (side == 2 and cat == 0) and { group } or {} end
StaticObject = { getByName = function() return nil end }
Airbase = { getByName = function() return { getPoint = function() return pt(-195650, 515898) end } end }
local called = {}
demo = { spawnCsar = function() called.csar = true end, activateOperation = function() called.on = true end,
         desactivateOperation = function() called.off = true end }

dofile("src/scripts/guided-tour.lua")

-- le joueur reprend un slot : les menus sont reposés, pas empilés
handlers[1]:onEvent({ id = world.event.S_EVENT_BIRTH, initiator = unit })
assert(#menus.group[42] == 2, "deux menus de visite attendus pour le groupe, trouvé " .. #menus.group[42])
assert(#menus.common == 1 and menus.common[1].title == "Démo : actions", "menu « Démo : actions » attendu au premier niveau")

local FR, EN = "Où :", "Where:"
local n = 0
local function walk(m, expect)
  for _, it in ipairs(m.items) do
    if it.f then
      local before = #shown
      it.f(it.a); n = n + 1
      if it.a then
        local text = shown[#shown]
        assert(#shown == before + 1 and #text > 50, "texte vide pour " .. it.title)
        if it.a.n then
          assert(text:find(expect, 1, true), "« " .. it.title .. " » ne répond pas dans sa langue")
        end
      end
    else
      walk(it, expect)
    end
  end
end
walk(menus.group[42][1], FR)
walk(menus.group[42][2], EN)
walk(menus.common[1])
local live = 0
for _ in pairs(marks) do live = live + 1 end
assert(called.csar and called.on and called.off, "actions de la démo non appelées")
print(string.format("%d commandes essayées, %d messages, chaque menu dans sa langue, %d repère vivant", n, #shown, live))
