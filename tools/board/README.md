# The Art Review board

`board.html` is the page published at https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk (version 2, 25 Oct), with
the `db` and `user` capabilities. Its images live in the artifact's files (`img/...`), not here.

To add a family card: read the artifact (Artifact tool, action read, then path index.html), add one entry to
`ITEMS` and publish with the same url, passing the new images as `files`:

    {"id": "fam_rw_street", "title": "River Walk street furniture", "section": "family", "group": "River Walk",
     "layer": "play", "tier": "B", "note": "what changed and what to look for",
     "images": [{"src": "img/fam/rw_street_frame.png", "label": "in game, 1x and 3x, colour and greyscale"}],
     "members": [{"id": "rw_lamp_v2", "title": "lamp", "slot": "lamp_post.png", "img": "img/fam/rw_lamp_v2_5x.png",
                  "note": "", "findings": []}]}

Each member's decision is saved in the db collection `decisions` under its id (status approve|fix|redraw; the button
says Reject for redraw). Read them with ArtifactData list before acting. `tools/pipeline.py done NAME board` takes
`--board "approve ..."` copied from there.
