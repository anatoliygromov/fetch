# A bark drops the ball (owner, 7 Nov)

The owner's words: "if the dog barks with the ball in mouth, the ball should drop".

Downtown (tall), the street at x 2150, a goose 76 px ahead. Pepper carries the ball and barks (Y / Z key).
Game frames, 1x scaled 3x (nearest), from branch `day/07nov-barkdrop`.

1. `1_bark_with_ball_3x.png`: the bark. The ball leaves her mouth on the bark clip's first frame, the bark ring
   goes out and the goose is shooed (SHOO! +200).
2. `2_ball_in_the_air_3x.png`: 0.33 s later. The ball falls on the usual drop arc (St:dropBall) and lands on the
   street 25 px in front of her (a running bark: about 40 px). Nothing is drawn in her mouth. X picks it up again.

The bark clip has no ball drawn in (only the pick-up clip does); a bark during the pick-up clip ends that clip at once,
so no second ball shows in her mouth. Code: `riverwalk/stage.lua` (bark rings). Test: `riverwalk/tests_downtown_tall.lua`,
step 5b of `--physics`.
