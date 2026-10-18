-- The game's levels in play order. Each name is a file in level/ (level/<name>.lua and its .map).
-- The story runs across all of them: a magpie steals Mia's ball in the park (1), a cat sits on it on the plaza
-- downtown (2), Mia throws it by the river and it lands on a ferry (3).
-- par: the PAR TIME medal's time in seconds (the autopilot's clear time, 33 to 36 s, times about 1.6, rounded up)
return {
  { name = "citypark",  number = 1, title = "CITY PARK",  par = 60 },
  { name = "downtown",  number = 2, title = "DOWNTOWN",   par = 55 },
  { name = "riverwalk", number = 3, title = "RIVER WALK", par = 60 },
  { name = "night",     number = 5, title = "NIGHT HARBOUR", par = 135 },  -- autopilot 81.3 s
}
