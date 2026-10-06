-- Fonctions communes aux sondes de recette (champ `probe` de tour/steps.yaml).
-- tools/recette_pont.py colle ce fichier devant chaque sonde et l'exécute dans la mission en cours,
-- par le pont dcs-bridge. Une sonde `check` rend `ok, détail` ; `act` ne rend rien.

local R = {}
R.lang = (veaf and veaf.config and veaf.config.language == "en") and "en" or "fr"

-- texte selon la langue du build
function R.L(fr, en)
  return R.lang == "en" and en or fr
end

-- centre d'une trigger zone, posé au sol (vec3)
function R.at(zoneName, dx, dz)
  local z = trigger.misc.getZone(zoneName)
  assert(z, "trigger zone introuvable : " .. tostring(zoneName))
  local p = { x = z.point.x + (dx or 0), z = z.point.z + (dz or 0) }
  p.y = land.getHeight({ x = p.x, y = p.z })
  return p, z.radius
end

-- unités vivantes et actives (sol + navires, tous camps) et statiques à moins de `margin` m du cercle
function R.inZone(zoneName, margin)
  local center, radius = R.at(zoneName)
  local r2 = (radius + (margin or 0)) ^ 2
  local n, statics, types = 0, 0, {}
  for _, side in ipairs({ coalition.side.RED, coalition.side.BLUE, coalition.side.NEUTRAL }) do
    for _, cat in ipairs({ Group.Category.GROUND, Group.Category.SHIP }) do
      for _, g in ipairs(coalition.getGroups(side, cat)) do
        for _, u in ipairs(g:getUnits()) do
          local p = u:getPoint()
          if u:isActive() and (p.x - center.x) ^ 2 + (p.z - center.z) ^ 2 < r2 then
            n = n + 1
            types[u:getTypeName()] = (types[u:getTypeName()] or 0) + 1
          end
        end
      end
    end
    for _, s in ipairs(coalition.getStaticObjects(side)) do
      local p = s:getPoint()
      if s:isExist() and (p.x - center.x) ^ 2 + (p.z - center.z) ^ 2 < r2 then
        statics = statics + 1
      end
    end
  end
  return n, statics, types
end

-- « T-72Bx4, Ural-375x2 » : résumé lisible d'une table type -> nombre
function R.types(types)
  local t = {}
  for k, v in pairs(types or {}) do
    table.insert(t, k .. "x" .. v)
  end
  table.sort(t)
  return table.concat(t, ", ")
end

-- groupe existant et nombre d'unités vivantes (0 si absent)
function R.alive(groupName)
  local g = Group.getByName(groupName)
  if not g or not g:isExist() then
    return 0
  end
  local n = 0
  for _, u in ipairs(g:getUnits()) do
    if u:isExist() and u:getLife() > 0 then
      n = n + 1
    end
  end
  return n
end

-- groupes dont le nom contient `fragment` (motif simple), avec leurs unités vivantes
function R.groupsMatching(fragment, categories)
  local found = {}
  for _, side in ipairs({ coalition.side.RED, coalition.side.BLUE, coalition.side.NEUTRAL }) do
    for _, cat in ipairs(categories or { Group.Category.GROUND, Group.Category.SHIP, Group.Category.AIRPLANE, Group.Category.HELICOPTER }) do
      for _, g in ipairs(coalition.getGroups(side, cat)) do
        if g:getName():find(fragment, 1, true) then
          found[g:getName()] = g:getSize()
        end
      end
    end
  end
  return found
end

function R.count(t)
  local n = 0
  for _ in pairs(t or {}) do
    n = n + 1
  end
  return n
end

-- une commande du menu VEAF, par ses titres depuis la racine (sans le « + » des commandes protégées)
function R.menu(...)
  local node = veafRadio._builder._root
  local path = { ... }
  for i, title in ipairs(path) do
    local nextNode
    for _, sm in ipairs(node.subMenus or {}) do
      if sm.title == title then
        nextNode = sm
      end
    end
    if not nextNode and i == #path then
      for _, c in ipairs(node.commands or {}) do
        if c.title == title then
          return c
        end
      end
    end
    assert(nextNode, "menu introuvable : " .. table.concat(path, " > ", 1, i))
    node = nextNode
  end
  return node
end

-- clique une commande du menu VEAF avec les paramètres que DCS lui passerait
-- (veafRadio.RadioMenuBuilder:_placeCommandOnMenu) ; sécurité désactivée dans la démo, donc une
-- commande protégée passe aussi par là. Une commande posée par groupe reçoit en plus le nom de l'unité
-- du joueur : la mission de test n'a pas de joueur dans une unité, elle reçoit nil.
function R.click(...)
  local c = R.menu(...)
  local params = c.parameters
  if c.usage and c.usage ~= veafRadio.USAGE_ForAll then
    params = c.parameters == nil and nil or { c.parameters }
  end
  c.method(params)
end

-- pose un vrai marqueur F10 bleu portant `text` au centre d'une zone, décalé de dx, dz m, et envoie à
-- VEAF l'événement « marqueur modifié » que DCS envoie quand un joueur valide son texte : la commande
-- suit le même chemin qu'en jeu (veafMarkers, puis le module qui la reconnaît)
function R.marker(text, zoneName, dx, dz)
  local p = R.at(zoneName, dx, dz)
  R.mem.markId = (R.mem.markId or 900000) + 1
  trigger.action.markToCoalition(R.mem.markId, text, p, coalition.side.BLUE)
  local pos = veafMarkers.DCSbugfixed and { x = p.x, y = p.y, z = p.z } or { x = p.z, y = p.y, z = p.x }
  veafMarkers.eventHandler:onEvent({
    id = world.event.S_EVENT_MARK_CHANGE, idx = R.mem.markId, text = text, pos = pos,
    coalition = coalition.side.BLUE, time = timer.getTime(),
  })
end

-- détruit toutes les unités et statiques actives d'une zone (pour terminer une zone de combat)
function R.destroyZone(zoneName, margin)
  local center, radius = R.at(zoneName)
  local r2 = (radius + (margin or 0)) ^ 2
  local n = 0
  for _, side in ipairs({ coalition.side.RED, coalition.side.BLUE }) do
    for _, cat in ipairs({ Group.Category.GROUND, Group.Category.SHIP }) do
      for _, g in ipairs(coalition.getGroups(side, cat)) do
        for _, u in ipairs(g:getUnits()) do
          local p = u:getPoint()
          if u:isActive() and (p.x - center.x) ^ 2 + (p.z - center.z) ^ 2 < r2 then
            trigger.action.explosion(p, 2000)
            n = n + 1
          end
        end
      end
    end
    for _, s in ipairs(coalition.getStaticObjects(side)) do
      local p = s:getPoint()
      if s:isExist() and (p.x - center.x) ^ 2 + (p.z - center.z) ^ 2 < r2 then
        trigger.action.explosion(p, 2000)
        n = n + 1
      end
    end
  end
  return n
end

-- mémoire entre sondes (act puis check, ou deux étapes) : survit tant que la mission tourne
demoRecette = demoRecette or {}
R.mem = demoRecette
