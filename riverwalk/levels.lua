-- The game's levels in play order. Each name is a file in level/ (level/<name>.lua and its .map).
-- The story runs across all of them: a magpie steals Mia's ball in the park (1), a cat sits on it on the plaza
-- downtown (2), Mia throws it by the river and it lands on a ferry (3), it rolls all the way down Soder Hill (4),
-- and on the way home in the dark a fox takes it (5).
-- par: the PAR TIME medal's time in seconds (the autopilot's clear time times about 1.6, rounded up). Autopilot
-- clear times (levels/v2): 44.2, 51.5, 65.3, 73.3 (the scroll sets the pace), 81.3 s.
return {
  { name = "citypark",  number = 1, title = "CITY PARK",  par = 71 },      -- (was 60: 6 screens)
  { name = "downtown",  number = 2, title = "DOWNTOWN",   par = 83 },      -- (was 55: 6 screens)
  { name = "riverwalk", number = 3, title = "RIVER WALK", par = 105 },     -- (was 60: 10 screens)
  { name = "soder",     number = 4, title = "SODER HILL", par = 118 },
  { name = "night",     number = 5, title = "NIGHT HARBOUR", par = 135 },
}
