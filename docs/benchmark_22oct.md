# FETCH! level design benchmark: ten 90s platformers

Research round 5, 22 Oct 2026. For the FETCH! level designer.

How to read this: section 1 compares the games in one table. Section 2 gives a short card per game. Sections 3 to 7 are the part to apply: principles, the difficulty curve for the 10 levels, ideas per level, assists, bonus rounds. Numbers come from the pages listed in Sources; where a number is my own estimate it says so.

---

## 1. The ten games at a glance

Per-level time = the published or submitted tool-assisted run (TAS) divided by the number of levels. It is a floor for "perfect play", not a normal player's time. Runs on the hardest setting are marked.

| Game | Levels | TAS total | Approx. TAS per level | Checkpoint | Health / safety net | Bonus round unlocked by | Main complaint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Lion King (Genesis, 1994) | 10 | 14:02.73 (hardest) | 84 s | Yes, in level | Health bar + roar meter, bugs heal | Finding hidden bugs | Uneven, unfair difficulty; level 2 monkey puzzle |
| Aladdin (Genesis, 1993) | 10 | 9:30.42 (hardest) | 57 s | Blue vases | Lamp-smoke health, hearts | Genie and Abu tokens | Off-screen hits, weak sword feel, random escape |
| Sonic the Hedgehog 2 (1992) | 11 zones, 20 acts | 17:40.08 real (11:24 in-game) | 34 s in-game per act (12 s to 2:06) | Star posts | Rings (hit with 1+ ring = survive) | 50 rings at a star post | Too easy and short (1992 press) |
| Super Mario World (1990) | 96 exits, 7 worlds | 1:20:22 (all 96 exits, extra goals) | about 50 s per exit | Midway Gate | Power-ups, Yoshi, lives | Keys, secret exits, 100 bonus stars | Too close to earlier Marios |
| Donkey Kong Country (1994) | 40 | 41:18.37 (101%, with bonus rooms) | 62 s incl. bonuses | Star Barrel, near middle | Second Kong = one extra hit | Hidden bonus rooms, 3 animal tokens | Looks over depth |
| Yoshi's Island (1995) | 48 + 6 extra | (no full time found); extra level 2-E at 100% in 1:09.72 | about 70 s for a short extra level | Middle Rings | Baby Mario countdown, 10 to 30 s | 100 points in all 8 levels of a world | Baby Mario's crying |
| Rayman (PS1, 1995) | 6 worlds, 17 main levels + final | 1:02:37.67 | about 3.5 min per level (each has sub-areas) | Photographer | 3 health, 5 lives, Tings | Magician challenge | Hard wall, distant checkpoints, cages gate the ending |
| Castle of Illusion (Genesis, 1990) | 6 worlds, several stages each | 18:23.45 (hard) | about 3 min per world | Not documented in sources | Health refills, tries | None to speak of | Slow pace, easy mode cuts the game short |
| Kirby's Adventure (NES, 1993) | 41 in 7 worlds | 34:22.22 | about 50 s | Auto-save after each level | Health bar, food heals, flying | Minigames, arenas, museums in hubs | Short and easy (retrospective) |
| DuckTales (NES, 1989) | 5, any order | 6:43.49 (hardest, rejected run) | about 80 s per destination | Leave via Launchpad | Hearts, hidden health refill | Hidden treasures, money endings | Short; final revisit a letdown |

What the table says for FETCH!

- The target of 60 to 170 s perfect play per level sits right in the band. Lion King averages 84 s, Aladdin 57 s, DKC 62 s, Kirby 50 s. Only Rayman and Castle of Illusion run 3 minutes or more, and both split a "level" into sub-stages.
- The best-loved games gave a cheap, visible way to absorb one mistake (rings, a second Kong, Yoshi, a countdown). The Lion King and Rayman, the two called unfair, had the thinnest safety nets (sparse healing, three health points, distant checkpoints).
- The games remembered as kind (Kirby, Yoshi's Island, DuckTales, Castle of Illusion) were also called short or easy. The ones remembered as cruel (Lion King, Rayman) were called unfair, not long.

---

## 2. Game cards

### 2.1 The Lion King (Westwood / Virgin, 1994)

**Structure.** 10 levels: The Pridelands, Can't Wait to be King, The Elephant Graveyard, The Stampede, Simba's Exile, Hakuna Matata, Simba's Destiny, Be Prepared, Simba's Return, Pride Rock (Giant Bomb). Two bonus games, Bug Toss and Bug Hunt. Genesis TAS on the hardest setting: 14:02.73; SNES TAS: 12:51.20 (TASVideos).

**Manner per level.** Platforming (Pridelands), an ostrich ride and the monkey puzzle (level 2), a sparse, dark graveyard with hyenas (3), an into-the-screen chase from wildebeest (4), ledges and falling rocks (5), swings and a waterfall cut from the film (6), leopard fights (7), geysers and a rideable rock (8), and the final boss (10) (TASVideos notes, Nintendo World Report, Wikipedia). Two levels come from scenes cut from the film.

**Teaching.** Level 1 teaches run, jump and fight. From level 2 on, Kotaku's writer argues "the game expects more than it has taught": the ostrich jumps kill instantly and the bright palette hides obstacles.

**Difficulty curve.** Not a curve. GamePro (SNES) called it "too daunting for beginning players and too annoying for experienced ones" with "highly uneven difficulty". Sega-16 notes adult Simba's slash makes the later game easier than the cub stages, against the usual pattern. Nintendo World Report: difficulty "pretty uneven", level 2 "more than a little cheap".

**The rental problem (cite this one).** Wikipedia: in 2014 director Louis Castle said difficulty, especially in level 2, was raised under Disney pressure so renters could not finish within a Blockbuster rental, and he has since apologised. Now I Know quotes him from a 2014 play-through with Double Fine: "The monkey puzzle was meant to be [relatively easy]", "Disney had a rule across all its products that [consumers] couldn't get past a certain percentage of the game", and "The reason we had to do it was the rental market". TheGamer: the puzzle has dozens of monkeys, most off-screen, with "no good way to get a lay of the land", and a deadly platforming section follows it.

**Checkpoints and lives.** Checkpoints inside levels; lives depend on the difficulty setting; continues come from Circle of Life icons (Wikipedia). Kotaku calls checkpoints sparse and says the Elephant Graveyard gives one health bug at the start and none after.

**Secrets and bonus.** Hidden bugs in certain levels open Timon or Pumbaa bonus games; every 10 bugs eaten gives lives or continues (Wikipedia). Kotaku says the Pumbaa catch game needs "superhuman" reflexes.

**Readability.** Stampede: unclear when Simba's hitbox touches obstacles (Kotaku). Dropped jump inputs and swings that fail to register. NWR: "The hit detection wasn't always precise."

**Modern fix.** The 2019 Disney Classic Games release added a rewind of about one minute, save anywhere, an invincibility and stage-select option, and a "Watch and Play" mode you can take over at any moment (GamePitt).

**Take for FETCH!** Copy the manners per level and the cut-scene feel. Do not copy the second-level spike, the puzzle with unseen parts, or the sparse healing.

### 2.2 Aladdin (Virgin, Genesis, 1993)

**Structure.** 10 levels: Agrabah Market, The Desert, Agrabah Rooftops, Sultan's Dungeon, Cave of Wonders, The Escape, Rug Ride, Inside the Lamp, Sultan's Palace, Jafar's Palace. TAS 9:30.42 on hardest (TASVideos). Rug Ride is "on rails".

**Manner.** Market and desert platforming, rooftops, a dungeon, a cave, an escape run, a carpet ride on rails, a surreal lamp interior, palace, boss.

**Checkpoints and lives.** Blue vases are checkpoints. Gems buy lives and "wishes" (continue from the current level) from a peddler in each level. Difficulty in the menu sets starting lives and apples (Wikipedia).

**Bonus.** Genie tokens unlock the Genie's Bonus Machine after a level (luck: gem, apples or a life; Jafar's face ends it). Abu tokens in three levels unlock an Abu bonus catch level (Wikipedia). Indie Gamer Chick: "I liked the Abu mini-games."

**Criticism.** "Unavoidable projectiles come from off-screen", enemy placement causing "seemingly unavoidable damage", the hand-drawn animation "cost the game weighty combat and accurate collision detection", the Cave of Wonders escape "is pure random chance if you live or die", and the Jafar fight is called one of the worst in 2D gaming (Indie Gamer Chick). The same reviewer says kids who tested it "enjoyed Aladdin more than me".

**Take for FETCH!** The ride level as a breather on rails is good. Every threat in the escape must be readable, never random.

### 2.3 Sonic the Hedgehog 2 (Sega, 1992)

**Structure.** 11 zones, 20 acts, most zones two acts plus a boss (Wikipedia). TAS per act (in-game): Emerald Hill 14 s and 33 s, Chemical Plant 13 s and 32 s, Metropolis three acts, Sky Chase 2:06 (an auto-scroll plane ride), Wing Fortress 1:30, Death Egg 40 s (TASVideos 5735S).

**Teaching and pacing.** Yasuhara planned short, middle and long goals; for typical players "short-distance goals were about 30 seconds each", and the player should feel "in control of his own fate" (Game Developer interview). Speed is interrupted on purpose: bumpers, water and fans, waits for "the right opening", single-screen boss arenas (Game Developer, "10 ways").

**Routes.** Intertwining paths linked by springs and ramps; changing "lanes" is common and teaches that extras lie off the main path (Game Developer, "10 ways").

**Safety nets.** Hit with at least one ring and you survive, rings scatter. 3 starting lives, 100 rings = a life. Star posts are checkpoints (Wikipedia). The spin dash was added so you never need to backtrack for momentum.

**Bonus.** Pass a star post with 50+ rings to warp to the half-pipe special stage; seven emeralds unlock Super Sonic (Wikipedia).

**Kids.** Yasuhara wanted a second character "so siblings could play together"; a second player can control Tails at any time (Wikipedia).

**Criticism.** Too easy: GamesMaster finished it in one sitting without a game over; "just more of Sonic". Tails got in the way of bosses and the special stage. Players single out the Chemical Plant water section (a short-contact platform over water, then drowning risk), Casino Night bumper traps, and Wing Fortress falls (CinemaBlend).

**Take for FETCH!** 30 s micro-goals, a ring-like "one free mistake", a drop-in second player, and high and low lanes. Avoid water where a miss means a long climb back under a timer.

### 2.4 Super Mario World (Nintendo, 1990)

**Structure.** 96 exits across seven worlds; keys and keyholes open new levels and Star Road shortcuts; the Special Zone changes the map and sprites when cleared (Wikipedia). All 96 exits TAS with extra goals: 1:20:22.46 (TASVideos 9827S).

**Teaching.** The four-step pattern (kishotenketsu) comes from later Mario directors, but the Reverse Design series shows it already in SMW: Donut Plains 3 runs six challenges, each a variation of the one before ("a linear expansion and then linear evolution with one twist"). Each level leans to platforming or action; long late levels "synthesize the lessons of various skill themes" (Game Design Forum). Hayashida's four steps: learn the mechanic, a "slightly more complicated scenario", then "something crazy happens that makes you think about it in a way you weren't expecting", then "demonstrate ... what sort of mastery you've gained" (Game Developer).

**Checkpoints.** The Midway Gate sits near the middle of a course and also makes small Mario big. Auto-scrolling, Star World and Special Zone courses have none; underwater courses lacked them until the GBA port (Mario Wiki).

**Secrets and bonus.** Secret exits are often in plain pockets high up; the only bonus stages are tic-tac-toe rooms after 100 bonus stars (Game Developer, "Touring SMW"). Forest Fortress hides a cape route worth nine 1-ups.

**Criticism.** The cape can skip whole stages and the design "doesn't support its tactical advantages"; Valley of Bowser 2 needs a revisit for its second exit; Forest Fortress puts "its hardest part at its start". The same writer prefers "conceivable first-time success" over death counts.

**Take for FETCH!** The midway checkpoint that also gives something back. Secret exits as optional spice. Never put a level's hardest beat right after a checkpoint with no warm-up.

### 2.5 Donkey Kong Country (Rare, 1994)

**Structure.** 40 levels on a world map, six starting lives, a boss per area (Wikipedia). 101% TAS with bonus rooms 41:18.37 (TASVideos).

**One idea per level.** "Many levels were designed around unique mechanics", and "It was always the plan to have as much diversity as possible" (Gary Richards). Mine cart levels where you must jump "at just the right moment". Sutherland: Mario's influence was "introducing new features at a steady rate to keep the player interested" (Episodic Content).

**Safety net with a body.** No health bar: Diddy is the health. "Both characters could absorb one hit"; rescue the lost partner from a DK barrel (Episodic Content).

**Checkpoints.** The Star Barrel, "typically at the midway point", in nearly every level (Mario Wiki).

**Darkness done two ways.** Torchlight Trouble: Squawks the parrot carries a flashlight that lights the path ahead; he even reappears after the checkpoint if you skipped him (Mario Wiki). Blackout Basement: lights switch off every few seconds; only the Kongs, bananas, barrels and faint platform edges stay visible, and enemies vanish (Mario Wiki).

**Secrets and bonus.** Hidden bonus rooms with bananas, letters, balloons and tokens; three tokens of one animal warp you to a token round with a 99 timer, every 100 mini tokens = a life (Mario Wiki). 101% gives a different ending.

**Difficulty tuning.** Nintendo told Rare to lower difficulty for a broad audience "reasoning that the secrets would challenge hardcore players"; GamePro said you could "breeze through" without bonus rooms (Wikipedia).

**Take for FETCH!** The buddy as a hit point, the flashlight buddy for the dark level, secrets as the hard mode, and a rideable set piece.

### 2.6 Yoshi's Island (Nintendo, 1995)

**Structure.** 48 levels in six worlds, eight each; every fourth level is a fort or castle with a boss (Wikipedia, Mario Wiki).

**Accessible by design.** Hino wanted a Yoshi game "more accessible than earlier Mario games"; no time limits for "gentle and relaxed pacing"; the flutter jump makes Yoshi easier to steer in the air (Wikipedia).

**Teaching.** Message blocks teach one idea each: make an egg, aim and throw it, push the Chomp Rock, red coins. World 1 holds 16 hint texts; the game 48 in all (Mario Wiki).

**Safety net.** When hit, Baby Mario floats in a bubble while a countdown runs (10 s base, up to 30 with stars). Catch him and nothing is lost. Below 10 it slowly climbs back to 10. Pits, spikes and lava still kill at once (Wikipedia, Mario Wiki).

**Checkpoints.** Middle Rings: add 10 to the countdown, turn on-screen enemies to stars; a few levels have several, "always a couple before boss fights" (Mario Wiki).

**Score and bonus.** Each level scores out of 100: 30 stars, 20 red coins, 5 flowers worth 10 each. Flowers add winning spots to the goal roulette, which opens a bonus game (cards, scratch, slots) for lives or items. 100 in all eight levels of a world unlocks its Extra level and bonus game. Extras are shorter, harder, mostly without Middle Rings, and you can quit them any time (Mario Wiki).

**Criticism.** Baby Mario's crying (Nintendo Power, GameFan); linear overworld (Edge); some easy bosses.

**Take for FETCH!** A per-level score out of 100 is the best model for medals. The countdown rescue is the gentlest failure state in the set.

### 2.7 Rayman (Ubisoft, 1995)

**Structure.** Six worlds; each level hides six cages; all Electoons in the first five worlds open the final Candy Chateau (Wikipedia). 17 main levels (Push Square). TAS 1:02:37.67 (TASVideos).

**Abilities over time.** Punch, hang, swing, hover and run arrive one by one; the run "doesn't arrive until over halfway through the game" (Push Square). TechRaptor: "Rayman makes you work for capabilities that are usually standard."

**Checkpoints and lives.** The Photographer is the checkpoint (Rayman PC wiki). Five lives, 100 Tings = a life, Tings reset on death (Wikipedia, TechRaptor).

**Criticism.** "Deadly falls, distant checkpoints, instant kill spikes, and pixel perfect jumps"; "a persistent impeding wall rather than a gradual difficulty curve"; trampolines placed "directly below sharp spikes" (Push Square). Players were "surprised and disappointed" when cages blocked the last world. Invisible spawn triggers can lead you into traps (TechRaptor). GameSpot faulted rare save points; Sega Saturn Magazine called it "plain irritating and damned difficult" (Wikipedia). The GBA port added one health point and players noticed.

**Camera.** The camera does not move during a jump and "gently snaps when he lands" (Keren, Game Developer).

**Take for FETCH!** The art and the hidden cages are lovely; gating the ending on them is the classic mistake. One extra heart changes how a game is remembered.

### 2.8 Castle of Illusion Starring Mickey Mouse (Sega, 1990)

**Structure.** Doors to illusion worlds: Enchanted Forest, Toyland, The Storm, Dessert Factory, The Library, The Castle; each ends with a boss (Wikipedia). Six levels with several stages each (VGMuseum). Designer Emiko Yamamoto, her first game (Retro Gamer). TAS on hard 18:23.45 (TASVideos).

**Manner and set pieces.** Rotating rooms; a toy tower where the exit is locked and the key is several floors up, after which "the stairs become a multi-storied slide" to run down (Indie Gamer Chick). The 2013 remake review describes a downhill escape from a giant apple in the forest, an upside-down section in Toyland, rising water and a chase by Mickey's shadow (Present Perfect Gaming; this is the remake, which rebuilt the original's set pieces).

**Difficulty.** Easy mode gives "truncated versions of the first three levels, with no boss fights" (Wikipedia). Indie Gamer Chick calls this a "fiasco": "the game ends after three levels" and the bosses are removed. Normal felt easy to her; her niece died twice. Praised: enemies spaced to prevent coasting, platforms measured so players can "brace before takeoff", set pieces that "carry the day". Criticised: slow, bosses "a bit too spongy", a "short game at only five levels long", "nearly perfect game for two hours".

**Reception.** Entertainment Weekly: "Perfect for younger players, but challenging enough to satisfy adults, too."

**Take for FETCH!** The best direct model for a gentle animal hero with a bounce attack. Its easy mode is the anti-pattern for assists: never cut content for the easy path.

### 2.9 Kirby's Adventure (HAL, 1993) with Kirby's Dream Land notes

**Structure.** 41 levels in seven worlds; each world hub has doors to 4 to 6 levels, a boss, minigames for lives, museums with free powers, arenas; the game saves after every level (Wikipedia). TAS 34:22.22 (TASVideos).

**Beginners first.** Sakurai: "we need to be kind to beginners" (Nintendo Life). Dream Land was "for beginners"; he wanted beginners "to enjoy simply inhaling and spitting out things" while experts used deeper abilities; Spring Breeze was meant to "show complete beginners how to play" (Nintendo interview). Minigames were added because the bigger moveset might make the game look hard (Wikipedia). Flying, extra lives and a generous attack range widen the audience (Nintendo Life).

**Two players.** Kirby Super Star's Helper lets "seasoned players and inexperienced players" play together (Nintendo interview).

**Criticism.** Short and easy (retrospectives); Nintendo Power said it was harder than its cute look; sprites small (Wikipedia).

**Take for FETCH!** The hub with doors and free mini-games, auto-save after each level, and the rule that the simple verb is enough to finish while depth is optional.

### 2.10 DuckTales (Capcom, NES, 1989): the licensed kid game done right

**Structure.** Five destinations played "in any order": African Mines, Amazon, Himalayas, Transylvania, the Moon; some need revisits (Wikipedia). TAS on hardest 6:43.49 (TASVideos, rejected run).

**The pogo.** Disney rules said characters could not kill, so "Disney game designs had to be more creative than simple point and shoot games"; that is "how ... Scrooge's pogo jump" came about (GoNintendo, producer Darlene Lacey). The same constraint as Pepper's no-attack rule.

**Safety nets.** Launchpad lets you leave a level and pick another while keeping your treasure; a hidden health refill on Select costs $3 million; three endings by money (Take on the NES Library, Wikipedia).

**Criticism.** EGM: made "with younger players in mind", "beaten after the first day of play"; Mean Machines called it "very tough"; the Himalayas spike with many deadly falls; the final Transylvania revisit "the biggest letdown" (Wikipedia, Take on the NES Library).

**Take for FETCH!** Pick-your-order inside a chapter, an "exit and try another" button, and a constraint (no killing) turned into a signature verb.

---

## 3. Cross-cutting findings

### 3.1 How new mechanics are taught

| Step | What it looks like | Best example |
| --- | --- | --- |
| 1. Introduce | One new thing in a safe spot, failure costs nothing | Yoshi's Island message blocks, one idea each; Kirby's Spring Breeze |
| 2. Develop | Same thing, a little harder, still alone | SMW Donut Plains 3, each challenge a variation of the last |
| 3. Twist | Same thing in a surprising context | Hayashida's "something crazy happens"; DKC Stop-and-Go Station |
| 4. Conclude | Show mastery, usually just before the goal | Hayashida's fourth panel |

Where it broke: Lion King level 2 skipped steps 1 and 2 (Kotaku); Rayman withheld basic verbs instead of teaching them (Push Square).

### 3.2 Level manners and who did them well

| Manner | Done well | Lesson | Done badly | Lesson |
| --- | --- | --- | --- | --- |
| Chase / escape | Castle of Illusion apple run (remake); Lion King Stampede as spectacle | Short, scripted, readable | Aladdin's Escape ("pure random chance"); Stampede hitbox unclear | No random hazards, clear hit areas |
| Ride on rails | Aladdin Rug Ride; DKC mine carts; Sonic 2 Sky Chase | A breather that feels fast | DKC carts can be punishing | Few inputs, fixed patterns |
| Vertical climb | Castle of Illusion tower then slide down | Reward the climb with a fast descent | Same tower called "repetitive" | Keep climbs short and varied |
| Darkness | DKC Torchlight Trouble (buddy with a light) | Light follows the player; restore it after a checkpoint | Blackout Basement hides enemies | Keep hazards visible or audible |
| Water | Sonic 2 Aquatic Ruin acts are short | Short water sections | Chemical Plant water, Rayman spikes under trampolines | No long climbs back under a timer |
| Puzzle | Yoshi's Island hint-led rooms | Show the whole puzzle | Lion King monkeys, mostly off-screen | Fit the puzzle on screen |
| Boss | Castle of Illusion bosses easy once patterns are read | Patterns, short phases | Aladdin's Jafar; spongy bosses | Few hits, clear tells |

### 3.3 Checkpoints and safety nets

| Game | Checkpoint | Gift at checkpoint | Free mistake |
| --- | --- | --- | --- |
| SMW | Midway Gate, mid-level | Small Mario becomes big | Power-up / Yoshi |
| Sonic 2 | Star posts, several | Special stage at 50 rings | Any ring |
| DKC | Star Barrel, mid-level | None | Second Kong |
| Yoshi's Island | Middle Rings, 1 or more; 2 before bosses | +10 countdown, enemies to stars | Countdown rescue |
| Aladdin | Blue vases | None | Health smoke |
| Rayman | Photographer | None | Criticised as "distant" |
| Lion King | Yes | None | Bugs heal; sparse later |

### 3.4 Camera and readability

- SMW: platform snapping (camera only moves vertically when you land) and dual forward focus (camera keeps its target until you cross a threshold when turning back) (Keren).
- Sonic: narrow horizontal window keeps Sonic centred to see ahead; taller vertical window ignores small jumps (Keren).
- Rayman: no camera move during the jump, gentle snap on landing (Keren).
- DKC: one of the first with smoothed (lerp) camera; designers tuned the camera per region, wide forward view in runner sections (Keren).
- Readability failures: Aladdin off-screen projectiles; Lion King's bright palette hiding obstacles; Rayman's invisible triggers.

---

## 4. Fifteen principles for FETCH!

Each principle: the rule, the evidence, how to apply it.

1. **One idea per level, in four beats.** Introduce the level's new thing where failure is free, develop it alone, twist it, then let the player show mastery right before Mia. Evidence: Hayashida's kishotenketsu; DKC "designed around unique mechanics"; SMW Donut Plains 3. Apply: write each level's beat sheet as 4 rows (intro, develop, twist, finale) before placing tiles.

2. **Teach before you test.** The first use of any verb or threat happens on flat ground with no pit, ideally with a sign or Mia's gesture. Evidence: Yoshi's Island hint blocks, one idea each; Lion King's level 2 "expects more than it has taught". Apply: a new threat's first appearance must be survivable by doing nothing.

3. **Never spike for time; never pad.** Do not put the hardest beat in level 2 and do not lengthen a section to slow players. Evidence: Castle's rental confession and apology; GamePro "highly uneven difficulty". Apply: check the curve in section 5; any level that measures harder than the next one gets reworked.

4. **A puzzle must fit on one screen, and it must not sit over a death zone.** Evidence: the monkey puzzle, "most off-screen", followed by deadly platforming (TheGamer). Apply: at 320x240, keep each puzzle's start, rule and goal visible together, or use a camera pan that shows it first.

5. **Lamp every 30 to 40 s of perfect play, and make the lamp a gift.** Evidence: Yasuhara's 30 s short goals; SMW Midway Gate turns small Mario big; Yoshi's Middle Ring adds 10 to the countdown; Rayman and GameSpot criticism of distant checkpoints. Apply: a lit lamp refills one heart. A 120 s level gets 3 lamps; the finale gets 4.

6. **Give the player one free mistake with a body.** Evidence: Sonic's rings, DKC's second Kong, Yoshi's countdown rescue. Apply: when Pepper is hit while carrying the ball, the ball bounces out (like the goose already does) and she can pick it back up before losing a heart. Losing the ball is the warning; losing a heart is the second hit.

7. **Telegraph everything, on screen, before it matters.** Evidence: Aladdin's off-screen projectiles and "unavoidable damage"; Lion King's Stampede hitbox and bright palette; Rayman's invisible triggers. Apply: every hazard shows a 0.5 to 1 s tell (sound plus pose plus shadow, as the gull already does) and is inside the camera window when the tell starts. No hit comes from off-screen.

8. **Camera: look ahead, snap on landing, tune per region.** Evidence: SMW platform snapping and dual forward focus; Rayman's landing snap; DKC per-region tuning (Keren). Apply: horizontal look-ahead toward travel; vertical moves only on landing or on a held look up/down; a per-zone camera setting for chases (wide forward view) and climbs (more view above).

9. **Change the manner, keep the verbs.** Evidence: Lion King and Aladdin give each level a new manner with the same few moves; DKC "as much diversity as possible". Apply: each FETCH! level gets one headline manner (chase, ride, vertical, dark), but no level adds a control. New things are world objects (springs, escalators, lifts), not buttons.

10. **Peaks then rest, inside a level and across the game.** Evidence: Sonic 2 alternates 12 s acts with 2 minute set pieces; Castle of Illusion follows the stair climb with a fast slide; Aladdin's Rug Ride follows the Escape. Apply: after every hard beat, a short reward run (bones in an arc, downhill, a ride). Across the game, a tense level is followed by a playful one.

11. **Secrets reward play, never gate the ending.** Evidence: Rayman's cages blocking the last world drew disappointment; DKC lowered difficulty and left the challenge to secrets; SMW's secret exits and Star Road are optional. Apply: golden bones and full bone sets unlock bonus rounds, medals and cosmetics only. Home in the storm opens for everyone.

12. **Two lanes: low and safe, high and skilled.** Evidence: Sonic's lane changes; SMW high secret pockets and cape routes; DKC secrets as hard content. Apply: most screens have a ground route a 6-year-old can do and a high route using the held jump and ledge scramble that is faster or holds more bones. Falling from the high lane lands on the low lane, not in a pit.

13. **Assists never remove content.** Evidence: Castle of Illusion's easy mode cut to three levels with no bosses, called a "fiasco"; Super Guide in NSMB Wii played the level for you but marked it and let you take over; the 2019 Lion King rerelease added rewind and a take-over "Watch and Play". Apply: the easy path plays all 10 levels with the same set pieces; assists change safety, not the map.

14. **Raise difficulty on fair axes only.** Fair: timing windows, threat density, combining two known things, longer gaps between lamps (within principle 5). Unfair: hidden information, fewer heals, randomness, new rules without teaching. Evidence: Lion King's Elephant Graveyard (one heal, then none); Aladdin's random escape; Rayman "impeding wall". Apply: use the curve table in section 5 and change one fair axis at a time.

15. **Bonus rounds are short, clear and cannot cost a life.** Evidence: DKC token rounds (99 timer, 100 tokens = life); Yoshi's goal roulette; Sonic 2 special stage at a checkpoint; Lion King's Pumbaa round needing "superhuman" reflexes; Aladdin's luck machine ended by a Jafar picture. Apply: see section 7.

---

## 5. Recommended difficulty curve for the 10 levels

Order as planned in the brief. One suggestion: River Walk had water, gulls and traffic as level 3 in v2; as level 1 it must be stripped to the basics (or swap with City Park, which already teaches sneak and bark gently).

Perfect-play targets follow the brief (60 to 170 s). Lamp spacing is in seconds of perfect play. "Threat density" = active threats per screen (320 px) on the main path. Timing windows are the time Pepper has to act once a threat's tell starts. These numbers are my design targets, not measured from the benchmarks; tune them in playtests with the autopilot and real children.

| # | Level | New thing (one) | Manner | Perfect play | Lamps | Threats per screen | Timing window | Safety nets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | River Walk | Run, hop, held jump, carry and give | Gentle walk, tutorial | 60 to 70 s | 2 (every 25 s) | 0 to 0.5, nothing harmful early | 1.2 s+ | No pits; water just returns Pepper to the bank; hearts full at every lamp |
| 2 | City Park | Sneak (hold B) and bark | Stealth-lite, geese | 70 to 85 s | 2 to 3 (every 30 s) | 0.5 | 1.0 s | Geese hit = ball pops out first |
| 3 | Downtown | Bounce props, ledge scramble | Bouncy town, trams | 80 to 95 s | 3 | 0.75 | 0.9 s | Low lane under every high lane |
| 4 | Rooftops | Magpie steals the ball (bark to drop) | Vertical climb | 90 to 110 s | 3 (every 35 s) | 0.75 | 0.9 s | Falls drop to a lower roof, rarely to death |
| 5 | Metro | Crouch and belly crawl; moving floors | Escalators, train ride set piece | 100 to 120 s | 3 to 4 | 1.0 | 0.8 s | Train ride needs few inputs |
| 6 | Soder Hill | Auto-scroll chase (ball rolls downhill) | Chase | 70 to 90 s (shorter on purpose) | 2 inside the chase | 1.0, all from ahead | 0.8 s, fixed pattern | Lamps inside the chase; after 3 fails offer a slower scroll |
| 7 | Building site | Combine: lifts, cranes, scramble, crawl | Vertical combination | 120 to 140 s | 4 | 1.25 | 0.7 s | Two lanes everywhere |
| 8 | Funfair | Twist: rides as platforms (Ferris wheel, bumper floor) | Playful, rest after 7 | 100 to 120 s | 3 | 1.0 | 0.8 s | Rides carry Pepper, few deaths |
| 9 | Night Harbour | Sniff in the dark | Darkness, slow and quiet | 120 to 150 s | 4 | 0.75 (fewer, scarier) | 0.9 s (dark costs reaction time) | Platform edges and threats always lit or audible |
| 10 | Home in the storm | Nothing new: storm gusts twist known moves | Finale, combination | 150 to 170 s | 4 to 5 (every 35 s) | 1.25 | 0.7 s | Lamp before the last stretch; a calm last screen with Mia |

Shape of the curve: rising sawtooth. Peaks at 4 (first vertical), 7 (combination), 10 (finale). Dips at 6 (short chase, exciting but simple inputs), 8 (playful), 9 (slow pace, lower density, but new sense). That follows principle 10.

What changes level by level (summary):

- **New skills:** one per level for 1 to 6, none from 7 on (7 combines, 8 twists, 9 adds a sense not a move, 10 concludes).
- **Threat density:** 0 to 1.25 per screen, rising by about 0.25 per chapter, with dips after peaks.
- **Lamp spacing:** 25 s in level 1 to 35 s at the end; never more than 40 s.
- **Timing windows:** 1.2 s down to 0.7 s; never below 0.6 s on normal.
- **Safety nets:** stay constant (ball-pop first hit, lamp heals, low lanes). Only Hard mode removes them.

---

## 6. Ideas per level, from the benchmarks

**1. River Walk (tutorial).** Borrow: Kirby's Spring Breeze idea, a first level that shows beginners how to play; Yoshi's one-idea hint signs (use Mia pointing or a picture sign, no reading needed for 6-year-olds). Lion King's Pridelands taught run, jump and fight in one level. Do: run, hop, held jump, pick up, carry, give, light a lamp, find a bone in a visible high spot. Avoid: the v2 River Walk's boats and gulls this early; move them to a later reprise.

**2. City Park (sneak and bark).** Borrow: DKC's single-mechanic level; Hayashida's four beats with geese: one sleeping goose to sneak past, then two with a gap, then a goose that wakes on a timer (twist), then bark to clear a gaggle guarding Mia (mastery). Avoid: geese that charge from off-screen (Aladdin).

**3. Downtown (bounce and carry).** Borrow: Sonic 2 Casino Night's playful springs, Sonic's high and low lanes. Bouncy awnings make a high lane over the tram street. Avoid: Casino Night's bumper trap, where bounces keep throwing the player back in; any spring chain must have a way out.

**4. Rooftops (vertical, magpie).** Borrow: Castle of Illusion's tower: climb to the gull nest, then a fast slide down the drainpipe or a sloped roof as the reward. The magpie stealing the ball is the twist: bark when it lands to make it drop. Camera: vertical snap on landing, look up allowed (Rayman, SMW). Avoid: Rayman-style deaths from falls; a missed jump drops one roof.

**5. Metro (crawl, moving floors, train).** Borrow: Aladdin's Rug Ride and Sonic 2's Sky Chase as a ride on rails: Pepper rides a train car roof or a carriage window view with only hop and crouch needed. DKC mine carts for the "jump at just the right moment" thrill, but with a slower, fixed pattern. Escalators as moving floors teach the next level's scroll feel. Avoid: random timing on trains; doors that close with no tell.

**6. Soder Hill (auto-scroll chase).** Borrow: Lion King's Stampede for drama, Castle of Illusion's apple escape for tone (it's the ball rolling, the chase is joyful, not scary). Keep it short (the benchmarks' chases are among the shortest sections). Obstacles come only from ahead, each with a shadow or sound. Lamps inside the chase (SMW had no Midway Gate in auto-scroll levels; for kids that is too harsh). Avoid: the Stampede's unclear hitboxes and Aladdin's random escape.

**7. Building site (combination).** Borrow: SMW's long late levels that "synthesize" skill themes; DKC's dexterity sequences (barrels become crane hooks and lifts). Everything taught in 1 to 6 appears, no new verb. Two lanes everywhere. Avoid: Wing Fortress (many places to fall, dead ends); keep the route clear with signs or Mia's whistle direction.

**8. Funfair (twist, rest).** Borrow: Casino Night's pinball-like fun; DKC's token round could live here as a reward. Ferris wheel cabins as moving platforms, a bouncy castle, a carousel. Lower density after the building site. Avoid: luck-based games in the level itself (Aladdin's machine is a bonus, not a gate).

**9. Night Harbour (sniff in the dark).** Borrow: DKC Torchlight Trouble: light follows the player; sniff reveals a scent trail and the next safe platform. Blackout Basement's rule that platform edges and collectibles stay visible. Lion King's Elephant Graveyard mood, without its "one heal then none". Avoid: hiding hazards completely in the dark; if the fox is in darkness, it must be heard (paws, growl) before it can reach Pepper. Restore the light state at each lamp, as Squawks reappears after the checkpoint.

**10. Home in the storm (finale).** Borrow: Hayashida's fourth beat across the whole game: every verb in one level, with storm gusts as the twist (wind pushes jumps, as Sonic's fans cancel speed). A courtyard, then the stairwell to Mia's door. No boss fight (Pepper never hurts anyone, like DuckTales' no-kill rule): the "boss" is a set piece, for example the magpie on the roof in the storm, solved with bark timing. End on a calm screen. Avoid: Lion King's "brutal" last level, Aladdin's disliked final boss, and DuckTales' disappointing revisit; the finale must feel new.

---

## 7. Assists, medals and a hard mode

The rule: kids never lose content, retro fans can opt into the full challenge, and nobody is shamed.

| Feature | For | Precedent | FETCH! version |
| --- | --- | --- | --- |
| Ball-pop first hit | Kids | Sonic rings, DKC Diddy | First hit knocks the ball out; second costs a heart |
| Lamp heals one heart | Kids | Midway Gate, Middle Ring | Already a checkpoint; add the heal |
| "Show me" after repeated failure | Kids, parents | NSMB Wii Super Guide (after 8 fails), Lion King rerelease "Watch and Play" | After 5 lives lost in the same lamp section, offer a ghost Pepper run by the existing autopilot; the player can take over at any time; the level counts as cleared but its medal stays empty |
| Puppy mode (menu) | Kids 6 to 7 | Aladdin difficulty sets lives; Kirby's generous design | Infinite lives, pits return Pepper to the edge with a heart lost; full game, same levels |
| Drop-in second player | Parents playing with kids | Sonic 2 Tails, Kirby Super Star Helper | Player 2 controls a second, hard-to-hurt helper (for example Mia's cat or a bird) that can bark or nudge the ball; it cannot die |
| Leave and pick another | Kids | DuckTales Launchpad | Within a chapter, levels can be played in any order (3 per chapter); bones kept |
| Rewind (optional, PC/phone) | Everyone | 2019 Lion King/Aladdin collection | Short rewind of a few seconds; off for medals |
| Score out of 100 | Retro fans | Yoshi's Island | Bones (30), golden bones (5 x 10 = 50), no-hit (10), par time (10) |
| Par medals | Speedrunners | TAS and speedrun culture | Already in v2 (par times); show the par after the first clear |
| High lanes | Skilled players | Sonic lanes, SMW cape routes | Faster, more bones, never required |
| Hard mode | Retro fans | Lion King and DuckTales difficulty settings | 2 hearts, no ball-pop, lamps do not heal, timing windows 20% shorter; same maps |
| Extra levels | Completionists | Yoshi's Island Extra levels | 100 points in all levels of a chapter opens a short, hard extra stage per chapter; never needed for the ending |

---

## 8. Bonus round design lessons

| Benchmark | How unlocked | Reward | What worked | What did not |
| --- | --- | --- | --- | --- |
| Lion King Bug Toss / Bug Hunt | Hidden bugs | Lives, continues, meter upgrades | Character change (Timon, Pumbaa) is charming | Catch game needs "superhuman" reflexes |
| Aladdin Genie machine / Abu level | Tokens | Gems, apples, lives | Abu catch level liked | Luck, ended by Jafar's face |
| Sonic 2 special stage | 50 rings at a star post | Emeralds, Super Sonic | Tied to playing well, at a checkpoint | Blocky, Tails hits bombs |
| DKC token rounds | 3 same animal tokens | 100 tokens = life | Simple, 99 timer, play as the buddy | Leftover tokens lost |
| Yoshi's Island goal roulette | Flowers add winning spots | Lives, items | Visible chance that you can improve | Pure luck once spun |
| SMW tic-tac-toe | 100 bonus stars | Lives | Simple | Shallow |

For **Fetch Frenzy** (golden bone opens a 30 s catch round):

1. Short and fixed length: 30 s is right (DKC's 99-tick rounds are similar in spirit).
2. It cannot cost a life or hearts, and ends with something every time (a minimum reward).
3. Skill, not luck. Ramp from easy to fast inside the 30 s; the first 10 s should be catchable by a 6-year-old (avoid the Pumbaa problem).
4. Change the view or the character a little for novelty (Lion King's Timon and Pumbaa, DKC's animal buddy): for example Mia throws from above, or Pepper catches in a park at sunset.
5. Clear reward tiers shown before the round starts (for example 10 balls = a heart refill, 20 = an extra life, 30 = a gold collar piece toward cosmetics), like DKC's visible 100-token rule.
6. Bonus rounds are optional and never block progress (principle 11).
7. Place the golden bone off the main path but in sight (DKC tokens "in hard-to-reach places"; SMW secret pockets "high in the sky"), so kids see what they can aim for.

---

## 9. Gaps and limits

- Normal-player times per level were not available from the pages I could open; only TAS times and a few reviewer remarks (Castle of Illusion "two hours", Rayman "11 hours" for an inexperienced player, DuckTales "after the first day").
- Yoshi's Island has no full-game TAS total in the pages opened; only one extra level (1:09.72 at 100%).
- Castle of Illusion's original level gimmicks are partly sourced from a review of the 2013 remake, which rebuilt the original set pieces. Sega Retro and Hardcore Gaming 101 were unreachable (bot block and site maintenance). Sonic Retro's physics guide camera page was also blocked.
- The Lion King's in-game difficulty names were not confirmed by a page I opened.
- Earthworm Jim was left out to keep the set at ten.
- Numbers in section 5 (density, windows, lamp spacing) are design targets derived from the evidence, not measurements.

---

## Sources (pages opened)

The Lion King
- [The Lion King (video game), Wikipedia](https://en.wikipedia.org/wiki/The_Lion_King_(video_game))
- [Lion King Remaster: Should The Monkey Level Stay This Hard?, TheGamer](https://www.thegamer.com/lion-king-remaster-monkey-level-controversy/)
- [How the hell did we ever beat The Lion King as kids, Kotaku](https://kotaku.com/how-the-hell-did-we-ever-beat-the-lion-king-as-kids-w-1843525096)
- [Why Was This Video Game So Hard to Beat?, Now I Know](https://nowiknow.beehiiv.com/p/why-was-this-video-game-so-hard-to-beat)
- [Genesis The Lion King in 14:02.73, TASVideos](https://tasvideos.org/1927S)
- [SNES The Lion King in 12:51.20, TASVideos](https://tasvideos.org/7506S)
- [The Lion King, Giant Bomb](https://www.giantbomb.com/games/3030-9186/)
- [Reset Button 2: The Lion King (SNES), Nintendo World Report](https://www.nintendoworldreport.com/feature/23109/reset-button-2-the-lion-king-snes)
- [Disney's The Lion King review, Sega-16](https://www.sega-16.com/2006/07/disneys-the-lion-king)
- [Disney Classic Games: Aladdin and The Lion King review, GamePitt](https://www.gamepitt.co.uk/disney-classic-games-aladdin-and-the-lion-king-ps4-review/)

Aladdin
- [Disney's Aladdin (Virgin Games video game), Wikipedia](https://en.wikipedia.org/wiki/Disney%27s_Aladdin_(Virgin_Games_video_game))
- [Genesis Disney's Aladdin in 09:30.42, TASVideos](https://tasvideos.org/6773S)
- [Disney's Aladdin (Sega Genesis) reviews, Indie Gamer Chick](https://indiegamerchick.com/tag/aladdin-genesis/)

Sonic the Hedgehog 2
- [Sonic the Hedgehog 2, Wikipedia](https://en.wikipedia.org/wiki/Sonic_the_Hedgehog_2)
- [Game Design Psychology: The Full Hirokazu Yasuhara Interview, Game Developer](https://www.gamedeveloper.com/design/game-design-psychology-the-full-hirokazu-yasuhara-interview)
- [10 ways in which Sonic the Hedgehog wasn't about speed, Game Developer](https://www.gamedeveloper.com/design/10-ways-in-which-sonic-the-hedgehog-wasn-t-about-speed)
- [Genesis Sonic the Hedgehog 2 in 17:40.08, TASVideos](https://tasvideos.org/5735S)
- [The Top 3 Most Annoying Zones in Sonic the Hedgehog 2, CinemaBlend](https://cinemablend.com/games/Top-3-Most-Annoying-Zones-Sonic-Hedgehog-2-121317.html)

Super Mario World and Nintendo method
- [Super Mario World, Wikipedia](https://en.wikipedia.org/wiki/Super_Mario_World)
- [The secret to Mario level design (Hayashida), Game Developer](https://www.gamedeveloper.com/design/the-secret-to-i-mario-i-level-design)
- [Midway Gate, Super Mario Wiki](https://www.mariowiki.com/Midway_Gate)
- [Touring Super Mario World in 2014, Game Developer](https://www.gamedeveloper.com/design/touring-super-mario-world-in-2014)
- [Reverse Design: Super Mario World, introduction, The Game Design Forum (archive)](https://www.quaddicted.com/files/webarchive/thegamedesignforum.com_20160521/features/RD_SMW_1.html)
- [Reverse Design: Super Mario World, part 1, The Game Design Forum (archive)](https://www.quaddicted.com/files/webarchive/thegamedesignforum.com_20160521/features/RD_SMW_2.html)
- [SNES Super Mario World "all 96 exits" in 1:20:22.46, TASVideos](https://tasvideos.org/9827S)
- [Super Guide, Super Mario Wiki](https://www.mariowiki.com/Super_Guide)

Donkey Kong Country
- [Donkey Kong Country, Wikipedia](https://en.wikipedia.org/wiki/Donkey_Kong_Country)
- [Kings of the Jungle: The Making of Donkey Kong Country, Chapter 2, Episodic Content](https://episodiccontentmag.com/2016/02/19/dkcountry1_chapter2)
- [Star Barrel, Super Mario Wiki](https://www.mariowiki.com/Star_Barrel)
- [Torchlight Trouble, Super Mario Wiki](https://www.mariowiki.com/Torchlight_Trouble)
- [Blackout Basement, Super Mario Wiki](https://www.mariowiki.com/Blackout_Basement)
- [Animal Token, Super Mario Wiki](https://www.mariowiki.com/Animal_Token)
- [Donkey Kong Country submissions list, TASVideos](https://tasvideos.org/Subs-List?GameId=132)

Yoshi's Island
- [Yoshi's Island, Wikipedia](https://en.wikipedia.org/wiki/Yoshi%27s_Island)
- [Super Mario World 2: Yoshi's Island, Super Mario Wiki](https://www.mariowiki.com/Super_Mario_World_2:_Yoshi%27s_Island)
- [Middle Ring, Super Mario Wiki](https://www.mariowiki.com/Middle_Ring)
- [List of Yoshi's Island Message Block hints, Super Mario Wiki](https://www.mariowiki.com/List_of_Super_Mario_World_2:_Yoshi%27s_Island_Message_Block_hints)
- [Yoshi's Island 48-level TAS submission, TASVideos](https://tasvideos.org/3312S)
- [Yoshi's Island "2-E 100%" in 01:09.72, TASVideos](https://tasvideos.org/5033S)

Rayman
- [Rayman (video game), Wikipedia](https://en.wikipedia.org/wiki/Rayman_(video_game))
- [The Difficulty of Rayman, TechRaptor](https://techraptor.net/content/the-difficulty-of-rayman)
- [Rayman review, Push Square](https://www.pushsquare.com/reviews/psone/rayman)
- [The Photographer, Rayman PC wiki](https://raymanpc.com/wiki/en/Photographer)
- [PSX Rayman in 1:02:37.67, TASVideos](https://tasvideos.org/5449S)

Castle of Illusion
- [Castle of Illusion Starring Mickey Mouse, Wikipedia](https://en.wikipedia.org/wiki/Castle_of_Illusion_Starring_Mickey_Mouse)
- [Castle of Illusion (Sega Genesis review), Indie Gamer Chick](https://indiegamerchick.com/2023/09/10/castle-of-illusion-starring-mickey-mouse-sega-genesis-review/)
- [Castle of Illusion review, VGMuseum](https://www.vgmuseum.com/reviews/genesis/castleillusion)
- [Castle of Illusion (2013 remake) review, Present Perfect Gaming](https://presentperfectgaming.com/castle-of-illusion-starring-mickey-mouse/)
- [Ultimate Guide: Castle of Illusion, Retro Gamer via PressReader](https://www.pressreader.com/uk/retro-gamer/20180125/281702615125691)
- [Genesis Castle of Illusion in 18:23.45, TASVideos](https://tasvideos.org/1421S)

Kirby
- [Kirby's Adventure, Wikipedia](https://en.wikipedia.org/wiki/Kirby%27s_Adventure)
- [Kirby's Dream Land is all about being kind to beginners, says Sakurai, Nintendo Life](https://www.nintendolife.com/news/2023/09/random-kirbys-dream-land-is-all-about-being-kind-to-beginners-says-sakurai)
- [Nintendo Classic Mini SNES developer interview, Volume 6: Kirby Super Star, Nintendo](https://www.nintendo.com/en-gb/News/2017/October/Nintendo-Classic-Mini-SNES-developer-interview-Volume-6-Kirby-Super-Star-1298937.html)
- [Kirby's Adventure submissions list, TASVideos](https://tasvideos.org/Subs-List?GameId=41)

DuckTales
- [DuckTales (video game), Wikipedia](https://en.wikipedia.org/wiki/DuckTales_(video_game))
- [DuckTales review, Take on the NES Library](https://takeontheneslibrary.com/tag/huey/)
- [DuckTales NES producer on how Scrooge's pogo came to be, GoNintendo](https://www.gonintendo.com/stories/376337-ducktales-nes-producer-reveal-how-scrooge-s-pogo-attack-came-to-b)
- [NES DuckTales in 06:43.49, TASVideos](https://tasvideos.org/6497S)

Camera
- [Scroll Back: The Theory and Practice of Cameras in Side-Scrollers (Itay Keren), Game Developer](https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers)
