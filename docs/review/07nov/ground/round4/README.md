# GROUND track, round 4 (7 Nov): no kennel, the dog lives at home

Owner, 7 Nov 12:45: "I don't think we need kennel really, let's assume the dog lives at home". Also: keep the stone
steps; the bench stands on the pavement as a public bench.

## What changed

- **Kennel out:** its 2 collision boxes (ridge and eaves) and its L.pieces entry are gone from
  riverwalk/level/riverwalk.lua. riverwalk/art/scene/kennel.png is deleted, along with its pipeline spec and status.
  setpieces.lua only loads the kennel art if the file is there. `tools/build_rw_kennel.py` stays, marked "not in the
  game", so the round 3 kennel can be rebuilt if he wants it again. Its asset_qa slot and measure_layers entry are
  removed.
- **Garden out:** the GARDEN prop is gone, so no lawn and no pickets. The start screen is the approved paving again,
  with the house's contact shadow. The bench stands on the pavement as an ordinary public bench. Sc.paintGarden stays
  in scene.lua for a level that wants one.
- **Pepper's start is unchanged** (x 62, y 184): she starts on the pavement at her own green front door. PEPPER
  UNCHANGED, the golden trace identical (3908 steps).
- **The gold bone: it stays where it was, x 16, on her doorstep.** The secret KENNEL is now DOORSTEP (same box, x 0-30,
  y 176-184). River Walk still has 3 secrets and the same gold bones.
  Why this spot: it needs no new mechanic. The first hint says RUN and points right, and the bone sits a few steps
  behind her start, at the door. So the lesson is "look around before you run", at home, which fits a dog who lives
  there. A 7 year old can find it on the first screen.
  The other spots I weighed:
  - Under the bench: that is the tutorial's CRAWL, so everyone takes it and it is no secret.
  - Behind a planter: there is no "behind" in a front-on view.
  - A higher ledge: the early ledges (the bench seat, the flower box, the bin, the kiosk awnings) already carry bones,
    and the second awning has its own gold and secret.
- **Tests (tests.lua):** the kennel rows are replaced. "doorstep: walking left from the start reaches the door",
  "doorstep: the gold bone is taken", "secret: DOORSTEP counted (2 of 3)", "doorstep: walks back right on the
  pavement". The screenshot tour shot is renamed 14_doorstep.
- Tiled re-exported (maps/riverwalk.tmx, riverwalk/level/tiled/riverwalk.lua).

## Frames

- `start_screen_before_after_1x.png`: the start screen at 1x, before | after, colour over greyscale.
- `start_screen_before_after_3x.png`: the same at 3x.
- `gold_bone_doorstep_3x.png`: the gold bone on the doorstep at 3x, colour over greyscale.

## Checks

PEPPER UNCHANGED (3908 steps identical); riverwalk --physics 56/56 (the 4 doorstep rows PASS); riverwalk --qa 7844 runs,
0 problems; check_flow 125/125; TILED CHECK PASSED; check_curve identical to the base (main 5f30120): River Walk kids 8.5,
parents 10.9, retro 5.6, Elsa 100 %, lost 0.0 %; T1-T4 PASS.
