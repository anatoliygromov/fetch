-- Night Harbour's palette (8 Nov 2026): ONE table, so it can be swapped. Read by riverwalk/levelart/night.lua (the
-- code-drawn parts) and by tools/build_night_kit.py (the built PNG parts: it parses the `name = "rrggbb"` lines, so
-- keep one entry per line). Sampled from the picked concept (art/gen/concepts/nh_home_concept_b.png): per-material
-- ramps, light to dark; the darks lifted to navy, never pure black, never grey.
return {
  -- sky: deep navy at the top, a violet-blue glow at the horizon (flat steps, no dither)
  sky0 = "061340", sky1 = "0a1a4c", sky2 = "0e2256", sky3 = "132a60", sky4 = "19326a", sky5 = "213a72",
  star = "d8dcf0", moon = "e6e4cc", moonD = "b9b9a6", moonHalo = "1d2c66",
  -- far town (the old town on the far shore): violet-blue silhouettes, lit windows, the spire
  far1 = "2a3466", far2 = "232c5c", far3 = "1d2552", farRoof = "2f3a6e", farWin = "d9a548", farWinD = "8a6a3e",
  -- the bay (water.png recoloured whole-pixel, darkest first) and the reflections in it
  w0 = "071039", w1 = "0a1748", w2 = "0d1f56", w3 = "122a63", w4 = "1a3570", w5 = "28457e", w6 = "3a5890",
  refl1 = "f2b14a", refl2 = "b97a3c", refl3 = "6e4a3a",
  -- mid: boat sheds on piles and moored boats (dark blue boards, white trim dimmed)
  tar1 = "41465e", tar2 = "353a50", tar3 = "292d42",
  shed1 = "24386a", shed2 = "1c2d5c", shed3 = "152350", shedRoof = "131c44", shedTrim = "4a5682", shedDoor = "101a42",
  hull1 = "56607e", hull2 = "434c6a", hull3 = "323a58", mast = "3e4766", tiny = "fdd657",
  -- granite (the quay: paving cap, coping, wall), grey-blue
  g1 = "6a6d86", g2 = "5f6279", g3 = "54586f", g4 = "4b4e66", g5 = "3f435b", g6 = "33374e", g7 = "2a2e43", g8 = "21243a",
  wet = "1a1d33",
  -- lamplight on the paving: flat stepped amber pools (hard edges)
  pool1 = "e89a4c", pool2 = "b7784e", pool3 = "7c5e58",
  -- wood (crates, jetty, planks, piles, steps), weathered
  wd1 = "9a7052", wd2 = "7e5a43", wd3 = "634636", wd4 = "4a3330", wd5 = "33242a",
  pile1 = "4a4048", pile2 = "3a3240", pile3 = "2a2434",
  -- the outline of everything Pepper uses (navy-black, not pure black)
  ink = "141631",
  -- Mia's house: Falu red boards, white trim, green door, brass lantern, warm windows
  red1 = "8c2a26", red2 = "771d1e", red3 = "5c1419", red4 = "430f1c",
  trim1 = "c2b4a8", trim2 = "988a88", trim3 = "6e6474",
  door1 = "2f5c3a", door2 = "244d30", door3 = "173a24",
  win1 = "fdd657", win2 = "f3b549", win3 = "c88a3e", winBar = "8a6046",
  brass1 = "e0873f", brass2 = "a74827", brass3 = "5a2a22", glass = "f6db77",
  roof1 = "3a2a40", roof2 = "2c2036", roof3 = "201830",
  -- the tarp over the beached boat, the nets
  tarp1 = "3c5c62", tarp2 = "2e4a52", tarp3 = "223a44", net1 = "4e5a76", net2 = "3a4462",
  -- the lamp posts at night (lamp_post.png recoloured whole-pixel): dark iron
  iron1 = "4a5272", iron2 = "363d5a", iron3 = "262b45", iron4 = "1a1e36",
  -- the moonlit rim on Pepper and the moonlit tops
  rim = "8ea4d8",
}
