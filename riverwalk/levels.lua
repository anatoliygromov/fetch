-- The game's levels in play order. Each name is a file in level/ (level/<name>.lua and its .map).
-- The story is one day (r6/levels, the owner's ten-level plan; the levels not built yet are left out, so the cards
-- count the levels as they are played): in the morning Mia throws the ball by the river and it lands on a ferry
-- (1 River Walk), late morning a magpie steals it in the park (2 City Park), at noon a cat sits on it on the plaza
-- (3 Downtown), early in the afternoon a gull takes it up to its nest (4 Rooftops), in the afternoon it rolls all
-- the way down Soder Hill (5), and on the way home in the dark a fox takes it (6 Night Harbour).
-- Still to come in the plan: Metro (after Rooftops), the building site and the funfair (after Soder Hill), home in
-- the storm (after Night Harbour). When one is added, the numbers on the cards (L.number, L.intro) move up.
-- par: the PAR TIME medal's time in seconds (the autopilot's clear time times about 1.6, rounded up). Autopilot
-- clear times (r6/levels): 66.3, 44.6, 51.4, 54.1, 73.3 (the scroll sets the pace), 81.3 s; the tall City Park
-- 39.1 s and the tall Downtown 56.2 s (r7/curve) give pars 63 and 90. (r7/curve made Rooftops 58.1 s and Night
-- Harbour 82.6 s; their pars were left as they were.) r9/rooftops: Rooftops 92.4 s on both roads gives par 148.
--
-- D2 (owner, 23 Oct): the tall City Park and the tall Downtown are levels 2 and 3. They carry the flat levels'
-- titles, numbers and story (the cards say CITY PARK and DOWNTOWN). `was` names the flat level a tall one replaces:
-- a save that opened the flat level opens the tall one too (flow.lua F.load).
-- The flat City Park and Downtown stay in level/ as fallbacks, not in the order. To switch back to a flat one,
-- put its line back in place of the tall one (the old lines are below, commented out); nothing else changes
-- (each level file has its own number, intro and outro; the flat Downtown has the cargo bikes too).
return {
  { name = "riverwalk",     number = 1, title = "RIVER WALK", par = 107 },
  { name = "citypark_tall", number = 2, title = "CITY PARK",  par = 63, was = "citypark" },
  { name = "downtown_tall", number = 3, title = "DOWNTOWN",   par = 90, was = "downtown" },
  -- { name = "citypark",  number = 2, title = "CITY PARK",  par = 72 },   -- (flat, autopilot 44.6 s)
  -- { name = "downtown",  number = 3, title = "DOWNTOWN",   par = 83 },   -- (flat, autopilot 51.4 s)
  { name = "rooftops",      number = 4, title = "ROOFTOPS",   par = 148 },
  { name = "soder",         number = 5, title = "SODER HILL", par = 118 },
  { name = "night",         number = 6, title = "NIGHT HARBOUR", par = 135 },
}
