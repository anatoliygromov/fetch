-- joins.lua: the ground's kind map and the transition rule table (day/07nov-ground, 0 credits).
-- The owner, 7 Nov: "whenever we see two different types of ground connecting, they look cut, including the hills
-- etc". The joins audit (docs/review/07nov/ground_joins/README.md, 35 joins, 29 cut) traced every cut to one cause:
-- the ground was painted one column at a time, each from its own recipe, so every change of kind was a one-column
-- seam, patched case by case. Now:
--   1 a kind map: per world column the kind of ground Pepper stands on and its top (Jn.kinds)
--   2 a rule table: for each pair of kinds (A, B) the transition that is stamped where they meet (Jn.RULES); the
--     painters in scene.lua draw them from parts built by rule (and tools/make_ground_kit.py for the textured parts)
--     and mark each one they stamp (Jn.mark)
--   3 a check (Jn.check, run by the levels' --physics tests): every change in the map must have a rule and a
--     stamped transition within a few px of it, or the check fails and names the join.
-- Downtown can reuse it: give its kinds in Jn.kinds and its painters' marks; the rules for quay ends and stairs are
-- the same rows.
local Jn = { marks = {} }

-- the transitions, by "A>B" (A on the left). `what` says what is stamped, `by` which painter does it.
Jn.RULES = {
  -- (owner, 7 Nov: "the asphalt goes on") the road runs on in front of the steps (Sc.ROAD_RUNS_ON); with it off,
  -- the old kerb return with the quoined corner and the road's contact shadow (cornerColour / roadShade / dRoad)
  ["road>ramp"]   = { what = "the road runs on under the steps: the kerb face steps down with the treads, the gutter under each", by = "Sc.paintQuay roadOn" },
  ["ramp>road"]   = { what = "the same, mirrored", by = "Sc.paintQuay roadOn" },
  ["ramp>quay"]   = { what = "the steps' last tread lands on the quay paving (8 px slope tile)", by = "Sc.paintQuay stepTop" },
  ["quay>ramp"]   = { what = "the same, mirrored", by = "Sc.paintQuay stepTop" },
  ["quay>water"]  = { what = "quay-end cap: coping overhang and its shadow, wet arris, ripple, reflection", by = "Sc.paintQuay quay-end pass" },
  ["water>quay"]  = { what = "the same, mirrored", by = "Sc.paintQuay quay-end pass" },
  ["road>garden"] = { what = "lawn over the paving's edge, picket post", by = "Sc.paintGarden" },
  ["garden>road"] = { what = "the same, mirrored", by = "Sc.paintGarden" },
  ["garden>path"] = { what = "the door path's paving with grass over its edges", by = "Sc.paintGarden" },
  ["path>garden"] = { what = "the same, mirrored", by = "Sc.paintGarden" },
  ["path>pond"]   = { what = "near bank: a rounded shoulder, then a 2 px slope tile into the water, grass lip, wet foot", by = "Sc.nearBanks" },
  ["pond>path"]   = { what = "the same, mirrored", by = "Sc.nearBanks" },
}
-- a change of height inside one kind: the ramp's steps are its own slope tiles
Jn.SAME = { ramp = "8 px stone steps (Sc.STEP_RW)" }

function Jn.reset() Jn.marks = {} end
-- a painter says it stamped the transition `rule` at world column x
function Jn.mark(x, rule) Jn.marks[#Jn.marks + 1] = { x = x, rule = rule } end

-- the kind of ground in each column (x = 0 .. width - 1): { kind, top }
--   River Walk (def.ground "quay"): road (the promenade with the road in front), garden (its front garden),
--   path (the garden's door path), ramp (the steps), quay (the lower quays), water (the river between them)
--   City Park (def.art "park"): path, pond
function Jn.kinds(w, def, columnRuns)
  local K = {}
  local gardens = {}
  for _, p in ipairs(def.props or {}) do if p.garden then gardens[#gardens + 1] = p end end
  local function inGarden(x)
    for _, g in ipairs(gardens) do
      if x >= g.x0 and x < g.x1 then return (g.path0 and x >= g.path0 and x < g.path1) and "path" or "garden" end
    end
  end
  local function wet(x)
    for _, r in ipairs(w.water or {}) do if x >= r.x0 and x < r.x1 then return true end end
  end
  local foot = def.foot or 184
  for x = 0, w.width - 1 do
    local k, top
    if def.ground == "quay" then
      local merged = columnRuns(w, x, "all")
      for _, m in ipairs(merged) do if m[1] >= 150 then top = m[1]; break end end
      if top then
        if w:slopeAt(x) then k = "ramp"
        elseif merged[1][1] == 184 then k = inGarden(x) or "road"
        else k = "quay" end
      elseif wet(x) then k = "water" end
    elseif def.art == "park" then
      if wet(x) then k = "pond"
      else
        for _, m in ipairs(columnRuns(w, x, "first")) do if m[2] > foot then top = math.max(m[1], foot); break end end
        if top then k = "path" end
      end
    end
    K[x] = { kind = k, top = top }
  end
  return K
end

-- every change in the map: { x (the first column of B), a, b, dh }
function Jn.changes(K, width)
  local C = {}
  for x = 1, width - 1 do
    local A, B = K[x - 1], K[x]
    if A.kind and B.kind and A.kind ~= B.kind then
      C[#C + 1] = { x = x, a = A.kind, b = B.kind }
    elseif A.kind and A.kind == B.kind and A.top and B.top and A.top ~= B.top and not Jn.SAME[A.kind] then
      C[#C + 1] = { x = x, a = A.kind, b = B.kind, dh = B.top - A.top }
    end
  end
  return C
end

-- the check: every change has a rule and a stamped transition within `near` px. Returns ok, n, list of problems
function Jn.check(K, width, near)
  near = near or 10
  local bad = {}
  local C = Jn.changes(K, width)
  for _, c in ipairs(C) do
    local key = c.a .. ">" .. c.b
    local rule = Jn.RULES[key]
    if c.dh then bad[#bad + 1] = ("x %d: %s changes height by %d with no transition"):format(c.x, c.a, c.dh)
    elseif not rule then bad[#bad + 1] = ("x %d: no rule for %s"):format(c.x, key)
    else
      local found = false
      for _, m in ipairs(Jn.marks) do if m.rule == key and math.abs(m.x - c.x) <= near then found = true; break end end
      if not found then bad[#bad + 1] = ("x %d: %s has a rule but nothing was stamped"):format(c.x, key) end
    end
  end
  return #bad == 0, #C, bad
end

return Jn
