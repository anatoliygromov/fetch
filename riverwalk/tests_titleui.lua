-- love riverwalk --titleshots: the title and menu screens drawn straight to a 320 x 240 canvas for their QA cards
-- (ui/hud-v8 pilot 2): the title idle and with PRESS START, the main menu with each row selected, OPTIONS with each
-- row selected, the controls page, each with the gamepad and the keyboard glyphs; and the title loop at 8 fps for the
-- GIF (gif_000.png ...). Saves t_<name>.png and t_<name>.txt (the bodies hud.lua placed, for tools/layout_qa8.py)
-- in the save folder, prints "TITLESHOTS <folder>" and quits. tools/title_frames.py collects them.
local U = require("hud")
local I = require("input")
local Title = require("title")
return function(api)
  local F = api.flow
  local lg = love.graphics
  local canvas = lg.newCanvas(320, 240)
  local function shot(name, f)
    U.log = {}
    lg.setCanvas(canvas); lg.clear(0, 0, 0, 1); lg.origin(); f(); lg.setCanvas()
    canvas:newImageData():encode("png", "t_" .. name .. ".png")
    local out = {}
    for _, b in ipairs(U.log) do out[#out + 1] = table.concat(b, " ") end
    love.filesystem.write("t_" .. name .. ".txt", table.concat(out, "\n") .. "\n"); U.log = nil
  end
  local done = false
  local old = love.update
  love.update = function(dt)
    if done then return end
    done = true
    F.menu.moved, F.opts.moved = -1, -1
    shot("title_idle", function() Title.draw(0.9, nil, false) end)          -- PRESS START in its off phase
    shot("title_press", function() Title.draw(1.3, nil, false) end)         -- PRESS START on
    Title.TAGLINE = "lower"                                                  -- the second tagline version
    shot("title_lower_idle", function() Title.draw(0.9, nil, false) end)
    shot("title_lower_press", function() Title.draw(1.3, nil, false) end)
    Title.TAGLINE = "caps"
    for _, m in ipairs({ "bands", "steps6", "gradient" }) do Title.LOGO = m; shot("title_logo_" .. m, function() Title.draw(0.9, nil, false) end) end
    Title.LOGO = "gradient"; Title.TAGLINE = "lower"
    shot("title_gradient_lower", function() Title.draw(1.3, nil, false) end)
    Title.LOGO = "clean"; shot("title_clean_lower", function() Title.draw(1.3, nil, false) end)
    Title.TAGLINE = "caps"
    for _, dev in ipairs({ "pad", "key" }) do
      I.last = dev
      for i = 1, #F.menu.items do F.menu.sel, F.menu.from = i, i; shot(("menu_%d_%s"):format(i, dev), function() F.drawMenu(3.0) end) end
      for i = 1, #F.opts.items do F.opts.sel, F.opts.from = i, i; shot(("options_%d_%s"):format(i, dev), function() F.drawOptions(3.0) end) end
      shot("controls_" .. dev, function() F.drawControls(3.0) end)
    end
    F.hard = true; F.opts.sel = 2; I.last = "pad"; shot("options_hard_on", function() F.drawOptions(3.0) end); F.hard = false
    -- the title loop: 12 fps from 2.0 s for 9 s (blinks, about ten sparkles and two shine sweeps fall in it)
    for i = 0, 107 do shot(("gif_%03d"):format(i), function() Title.draw(2.0 + i / 12, nil, false) end) end
    print("TITLESHOTS " .. love.filesystem.getSaveDirectory()); io.stdout:flush()
    love.event.quit()
  end
end
