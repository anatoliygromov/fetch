-- The game's levels in play order. Each name is a file in level/ (level/<name>.lua and its .map).
-- The story runs across all three: the girl throws the ball too far in the park (1), a cat sits on it on the
-- plaza downtown (2), it bounces onto a ferry and Pepper brings it back to the girl by the river (3).
-- par: the PAR TIME medal's time in seconds (the autopilot's clear time, 33 to 36 s, times about 1.6, rounded up)
return {
  { name = "citypark",  number = 1, title = "CITY PARK",  par = 60 },
  { name = "downtown",  number = 2, title = "DOWNTOWN",   par = 55 },
  { name = "riverwalk", number = 3, title = "RIVER WALK", par = 60 },
}
