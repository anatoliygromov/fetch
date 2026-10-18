-- Chiptune sound effects and a short music loop, synthesised at start-up
-- (square, triangle and noise channels, like a 90s sound chip).
local S = {}
local RATE = 22050
local sounds = {}
local music
local ok = love.audio ~= nil

local function render(dur, fn)
  local n = math.floor(dur * RATE)
  local sd = love.sound.newSoundData(n, RATE, 16, 1)
  for i = 0, n - 1 do
    local v = fn(i / RATE)
    sd:setSample(i, math.max(-1, math.min(1, v)))
  end
  return sd
end

local function square(phase, duty) return (phase % 1) < (duty or 0.5) and 1 or -1 end
local function tri(phase) return 1 - 4 * math.abs((phase % 1) - 0.5) end

-- frequency sweep with decaying volume
local function sweep(f0, f1, dur, vol, wave, duty)
  local ph = 0
  return render(dur, function(t)
    local f = f0 + (f1 - f0) * (t / dur)
    ph = ph + f / RATE
    local env = vol * (1 - t / dur)
    if wave == "tri" then return tri(ph) * env end
    return square(ph, duty) * env
  end)
end

-- a sequence of {frequency, seconds}
local function arp(notes, vol, duty)
  local total = 0
  for _, n in ipairs(notes) do total = total + n[2] end
  local ph = 0
  return render(total, function(t)
    local acc = 0
    for _, n in ipairs(notes) do
      if t < acc + n[2] then
        ph = ph + n[1] / RATE
        local local_t = (t - acc) / n[2]
        return square(ph, duty or 0.25) * vol * (1 - 0.6 * local_t)
      end
      acc = acc + n[2]
    end
    return 0
  end)
end

local function midi(n) return 440 * 2 ^ ((n - 69) / 12) end

local function buildMusic()
  -- 8 bars of a bouncy city tune at 150 bpm: lead, bass and a hi-hat
  local beat = 60 / 150
  local lead = {   -- {midi note or 0, eighths}
    { 76, 1 }, { 79, 1 }, { 81, 2 }, { 79, 1 }, { 76, 1 }, { 74, 2 },
    { 72, 1 }, { 74, 1 }, { 76, 2 }, { 74, 2 }, { 0, 2 },
    { 76, 1 }, { 79, 1 }, { 84, 2 }, { 83, 1 }, { 81, 1 }, { 79, 2 },
    { 77, 1 }, { 76, 1 }, { 74, 2 }, { 72, 4 },
    { 81, 1 }, { 79, 1 }, { 77, 2 }, { 76, 1 }, { 74, 1 }, { 72, 2 },
    { 74, 1 }, { 76, 1 }, { 77, 2 }, { 79, 2 }, { 0, 2 },
    { 76, 1 }, { 79, 1 }, { 81, 2 }, { 84, 1 }, { 83, 1 }, { 81, 2 },
    { 79, 1 }, { 76, 1 }, { 74, 2 }, { 72, 4 },
  }
  local bassRoots = { 48, 45, 41, 43, 48, 45, 41, 43 }   -- C Am F G
  local bars = 8
  local dur = bars * 4 * beat
  local events = {}
  local t = 0
  for _, n in ipairs(lead) do
    events[#events + 1] = { t = t, d = n[2] * beat / 2, f = n[1] > 0 and midi(n[1]) or 0 }
    t = t + n[2] * beat / 2
  end
  local leadPh, bassPh = 0, 0
  local seed = 1
  return render(dur, function(time)
    local v = 0
    -- lead (find active note)
    for i = 1, #events do
      local e = events[i]
      if time >= e.t and time < e.t + e.d then
        if e.f > 0 then
          leadPh = leadPh + e.f / RATE
          local k = (time - e.t) / e.d
          v = v + square(leadPh, 0.25) * 0.16 * (1 - 0.5 * k)
        end
        break
      end
    end
    -- bass: eighth-note root / octave pattern, triangle wave
    local bar = math.floor(time / (4 * beat)) % bars + 1
    local eighth = math.floor(time / (beat / 2))
    local note = bassRoots[bar] + ((eighth % 2 == 1) and 12 or 0)
    bassPh = bassPh + midi(note) / RATE
    local ke = (time % (beat / 2)) / (beat / 2)
    v = v + tri(bassPh) * 0.22 * (1 - 0.7 * ke)
    -- hi-hat on off-beats: short noise
    local kb = (time % beat) / beat
    if kb > 0.5 and kb < 0.56 then
      seed = (seed * 1103515245 + 12345) % 2147483648
      v = v + ((seed / 2147483648) * 2 - 1) * 0.06
    end
    return v
  end)
end

function S.load()
  if not ok then return end
  local function src(sd) return love.audio.newSource(sd, "static") end
  pcall(function()
    sounds.jump = src(sweep(330, 760, 0.13, 0.25, "sq", 0.25))
    local seed = 7
    sounds.bark = src(render(0.18, function(t)
      seed = (seed * 1103515245 + 12345) % 2147483648
      local noise = (seed / 2147483648) * 2 - 1
      local f = 230 - 400 * t
      local env = (t < 0.02) and t / 0.02 or (1 - (t - 0.02) / 0.16)
      return (noise * 0.35 + square(t * f, 0.4) * 0.3) * env
    end))
    sounds.bone = src(arp({ { 988, 0.05 }, { 1319, 0.09 } }, 0.22))
    sounds.superbone = src(arp({ { 784, 0.06 }, { 988, 0.06 }, { 1175, 0.06 }, { 1568, 0.16 } }, 0.22))
    sounds.heart = src(arp({ { 523, 0.07 }, { 659, 0.07 }, { 784, 0.07 }, { 1047, 0.14 } }, 0.2))
    sounds.key = src(arp({ { 1568, 0.05 }, { 1976, 0.05 }, { 2349, 0.05 }, { 3136, 0.12 } }, 0.18))
    sounds.hurt = src(sweep(520, 110, 0.32, 0.28, "sq", 0.5))
    sounds.push = src(sweep(90, 70, 0.08, 0.12, "tri"))
    sounds.honk = src(render(0.28, function(t)
      return (square(t * 330, 0.5) + square(t * 415, 0.5)) * 0.12 * (1 - t / 0.28)
    end))
    sounds.flap = src(render(0.12, function(t)
      seed = (seed * 1103515245 + 12345) % 2147483648
      return ((seed / 2147483648) * 2 - 1) * 0.18 * (1 - t / 0.12) * (math.sin(t * 160) > 0 and 1 or 0.2)
    end))
    sounds.spring = src(sweep(200, 1200, 0.25, 0.22, "sq", 0.5))
    sounds.hiss = src(render(0.4, function(t)                       -- a goose's hiss: noise, swelling then gone
      seed = (seed * 1103515245 + 12345) % 2147483648
      return ((seed / 2147483648) * 2 - 1) * 0.2 * math.sin(math.pi * t / 0.4)
    end))
    sounds.squawk = src(render(0.3, function(t)                     -- a gull: a falling squawk, twice
      local k = t < 0.14 and t or t - 0.14
      return square(t * (1500 - 2600 * k), 0.3) * 0.12 * math.max(0, 1 - k / 0.14)
    end))
    sounds.checkpoint = src(arp({ { 659, 0.06 }, { 784, 0.06 }, { 1047, 0.12 } }, 0.18))
    sounds.gate = src(sweep(110, 220, 0.6, 0.2, "tri"))
    sounds.tick = src(arp({ { 1760, 0.02 } }, 0.12))
    sounds.clear = src(arp({ { 523, 0.12 }, { 659, 0.12 }, { 784, 0.12 }, { 1047, 0.12 },
                             { 784, 0.12 }, { 1047, 0.4 } }, 0.22, 0.5))
    sounds.over = src(arp({ { 392, 0.2 }, { 370, 0.2 }, { 349, 0.2 }, { 330, 0.5 } }, 0.22, 0.5))
    sounds.select = src(arp({ { 880, 0.05 }, { 1320, 0.08 } }, 0.2))
    sounds.bell = src(render(0.5, function(t)
      return (square(t * 2093, 0.5) * 0.5 + square(t * 2637, 0.5) * 0.5) * 0.1 * math.exp(-t * 7) * (((t * 14) % 1) < 0.85 and 1 or 0.3)
    end))
    -- the tram's warning bell: two quick strikes of a bright bell (a square with a fifth over it, ringing out)
    sounds.ding = src(render(0.34, function(t)
      local k = t < 0.15 and t or t - 0.15
      return (square(t * 1568, 0.5) * 0.6 + square(t * 2349, 0.5) * 0.4) * 0.12 * math.exp(-k * 18)
    end))
    sounds.secret = src(arp({ { 784, 0.05 }, { 1047, 0.05 }, { 1319, 0.05 }, { 1568, 0.05 }, { 2093, 0.14 } }, 0.18))
    sounds.splash = src(render(0.45, function(t)
      seed = (seed * 1103515245 + 12345) % 2147483648
      local n = (seed / 2147483648) * 2 - 1
      return n * 0.3 * math.exp(-t * 6) * (0.6 + 0.4 * math.sin(t * 90))
    end))
    sounds.land = src(sweep(140, 80, 0.05, 0.12, "tri"))
    sounds.scramble = src(sweep(180, 360, 0.18, 0.12, "tri"))
    music = love.audio.newSource(buildMusic(), "static")
    music:setLooping(true)
    music:setVolume(0.55)
  end)
end

function S.play(name)
  local s = sounds[name]
  if s then pcall(function() s:stop() s:play() end) end
end

function S.music(on)
  if not music then return end
  pcall(function()
    if on then if not music:isPlaying() then music:play() end else music:stop() end
  end)
end

return S
