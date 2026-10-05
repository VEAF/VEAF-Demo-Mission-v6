-- Essai hors DCS de la visite guidée : bouchons minimaux de l'API DCS et de veafRadio, puis chaque
-- commande de chaque étape dans les deux langues. lua tools/test_tour.lua (Lua 5.1, comme DCS).
local shown, marks = {}, {}
local function pt(x, z) return { x = x, y = 0, z = z } end
veaf = { Id = "VEAF", loggers = { get = function() return { info = function() end } end } }
veafRadio = { USAGE_ForGroup = 1, menus = {} }
function veafRadio.addMenu(t) local m = { title = t, items = {} }; table.insert(veafRadio.menus, m); return m end
function veafRadio.addSubMenu(t, parent) local m = { title = t, items = {} }; table.insert(parent.items, m); return m end
function veafRadio.addCommandToSubmenu(t, menu, f, p, u) table.insert(menu.items, { title = t, f = f, p = p, u = u }) end
function veafRadio.refreshRadioMenu() end
trigger = { misc = { getZone = function(n) return { point = pt(-250000, 600000), radius = 1000 } end },
            action = { outTextForGroup = function(g, t, d) table.insert(shown, t) end,
                       markToGroup = function(id, t, p, g, ro) marks[id] = t end, removeMark = function(id) marks[id] = nil end } }
coalition = { side = { BLUE = 2 }, getMainRefPoint = function() return pt(-253719, 629600) end }
local unit = { isExist = function() return true end, getPoint = function() return pt(-284582, 685029) end,
               getGroup = function() return { getID = function() return 42 end } end }
Unit = { getByName = function() return unit end }
Group = { getByName = function() return { isExist = function() return true end, getUnit = function() return unit end } end }
StaticObject = { getByName = function() return nil end }
Airbase = { getByName = function() return { getPoint = function() return pt(-195650, 515898) end } end }
local called = {}
demo = { spawnCsar = function() called.csar = true end, activateOperation = function() called.on = true end,
         desactivateOperation = function() called.off = true end }
dofile("src/scripts/guided-tour.lua")
assert(#veafRadio.menus == 3, "trois menus racine attendus (actions, visite fr, visite en)")
local n = 0
local function walk(m)
  for _, it in ipairs(m.items) do
    if it.items then walk(it) else
      local before = #shown
      it.f({ it.p, "joueur" }); n = n + 1
      if it.u == veafRadio.USAGE_ForGroup then
        assert(#shown == before + 1 and #shown[#shown] > 50, "texte vide pour " .. it.title)
      end
    end
  end
end
for _, m in ipairs(veafRadio.menus) do walk(m) end
local live = 0
for _ in pairs(marks) do live = live + 1 end
print(string.format("%d commandes essayées, %d messages, %d repère(s) vivant(s) pour le groupe", n, #shown, live))
assert(called.csar and called.on and called.off, "actions de la démo non appelées")
print("actions de la démo : pilote abattu, activer et désactiver l'opération appelées")
