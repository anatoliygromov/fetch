"""tools/layout_qa_menus.py FRAMES_DIR: layout checks for the title and the menus (pilot 2) on the frames
tools/title_frames.py writes (<shot>.png, 320 x 240, and <shot>.txt: the bodies placed, name x0 y0 x1 y1 inclusive).
  title: PRESS START centred on the menu's centre line (title.lua T.CX)
  main menu: every row centred on that line, even pitch, the paw cursor on the selected row's centre line, 4 px
             before its label
  options: the panel, the ribbon and the title centred on the screen; labels share one left edge, even pitch; the
           meter and the switch share one right edge and sit on their rows' centre lines; the cursor on the selected
           row's centre line; equal room above and below the rows inside the panel
  controls: the panel, ribbon and title centred; glyphs centred in one column, labels share one left edge, keys one
            right edge, each row's glyph, label and keys on one centre line, even pitch; the handheld on the rows'
            middle line and inside the panel
  strip (every menu screen): centred on the screen, bodies' bottom at y 235 (the margin), glyphs and labels on one
         centre line, the same place on every screen
  nothing overlaps (text, glyphs, controls); pieces: every edge pixel is the outline (64,11,6) or the shadow (36,8,5)
Prints PASS / FAIL lines, then ALL PASS or SOME FAIL."""
import sys, os, glob, re
import numpy as np
from PIL import Image
D = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CX = float(re.search(r'T\.CX = ([\d.]+)', open(f'{ROOT}/riverwalk/title.lua').read()).group(1))
ok = True
def check(cond, msg):
    global ok; print(('PASS ' if cond else 'FAIL ') + msg); ok &= bool(cond)
def load(shot):
    out = []
    for l in open(f'{D}/{shot}.txt'):
        p = l.split()
        if len(p) == 5: out.append(dict(name=p[0], x0=int(p[1]), y0=int(p[2]), x1=int(p[3]), y1=int(p[4])))
    return out
def cx(b): return (b['x0'] + b['x1']) / 2
def cy(b): return (b['y0'] + b['y1']) / 2
def many(bs, *n): return [b for b in bs if b['name'] in n]
def overlaps(bs):
    r = []
    for i, a in enumerate(bs):
        for b in bs[i + 1:]:
            if not (a['x1'] < b['x0'] or b['x1'] < a['x0'] or a['y1'] < b['y0'] or b['y1'] < a['y0']): r.append((a['name'], b['name']))
    return r
def pitch_even(ys): d = np.diff(sorted(ys)); return len(set(d.tolist())) <= 1, d.tolist()
strips = {}
def strip(shot, bs):
    s = many(bs, 'glyph', 'strip')
    s = [b for b in s if b['y0'] >= 200]
    x0, x1 = min(b['x0'] for b in s), max(b['x1'] for b in s)
    check(abs((x0 + x1) / 2 - 159.5) <= 0.5, f'{shot}: strip centred on the screen ({x0}-{x1})')
    check(max(b['y1'] for b in s) == 235, f'{shot}: strip bodies end at the margin (y {max(b["y1"] for b in s)})')
    check(len({cy(b) for b in s}) == 1, f'{shot}: strip glyphs and labels on one centre line {sorted({cy(b) for b in s})}')
    strips[shot] = (min(b['y0'] for b in s), max(b['y1'] for b in s))
    return s

for f in sorted(glob.glob(f'{D}/*.txt')):
    shot = os.path.basename(f)[:-4]; bs = load(shot)
    if shot.startswith('title_press'):
        p = many(bs, 'press')[0]; check(abs(cx(p) - CX) <= 0.5, f'{shot}: PRESS START centred on x {CX} ({cx(p)})')
    elif shot.startswith('menu_'):
        labels = many(bs, 'label'); cur = many(bs, 'cursor')[0]
        check(all(abs(cx(b) - CX) <= 0.5 for b in labels), f'{shot}: rows centred on x {CX} {[cx(b) for b in labels]}')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        sel = int(shot.split('_')[1]) - 1; lb = sorted(labels, key=lambda b: b['y0'])[sel]
        check(abs(cy(cur) - cy(lb)) <= 1, f'{shot}: cursor on the selected row\'s centre line (bob 1 px) ({cy(cur)} vs {cy(lb)})')
        check(lb['x0'] - cur['x1'] - 1 == 4, f'{shot}: cursor 4 px before its label ({lb["x0"] - cur["x1"] - 1})')
        s = strip(shot, bs)
        check(not overlaps(labels + [cur] + s), f'{shot}: nothing overlaps {overlaps(labels + [cur] + s)}')
    elif shot.startswith('options'):
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        labels = sorted(many(bs, 'label'), key=lambda b: b['y0'])
        check(len({b['x0'] for b in labels}) == 1, f'{shot}: labels share one left edge')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        ctl = many(bs, 'meter', 'toggle')
        check(len({b['x1'] for b in ctl}) == 1, f'{shot}: meter and switch share one right edge {[b["x1"] for b in ctl]}')
        for b, l in zip(sorted(ctl, key=lambda b: b['y0']), labels[:2]): check(abs(cy(b) - cy(l)) <= 0.5, f'{shot}: {b["name"]} on its row\'s centre line ({cy(b)} vs {cy(l)})')
        cur = many(bs, 'cursor')[0]; sel = 1 if 'hard' in shot else int(shot.split('_')[1]) - 1
        check(abs(cy(cur) - cy(labels[sel])) <= 1, f'{shot}: cursor on the selected row\'s centre line (bob 1 px)')
        top, bot = labels[0]['y0'] - P['y0'], P['y1'] - labels[-1]['y1']
        check(abs(top - bot) <= 1, f'{shot}: rows centred in the panel (above {top}, below {bot})')
        s = strip(shot, bs)
        items = labels + ctl + [cur, T] + s
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot.startswith('controls'):
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; Hh = many(bs, 'handheld')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        labels = sorted(many(bs, 'label'), key=lambda b: b['y0'])
        check(len({b['x0'] for b in labels}) == 1, f'{shot}: labels share one left edge')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        gl = [b for b in many(bs, 'glyph') if b['y0'] < 200]; ks = many(bs, 'key')
        rows = {}
        for b in gl: rows.setdefault(b['y0'], []).append(b)
        cxs = {(min(b['x0'] for b in r) + max(b['x1'] for b in r)) / 2 for r in rows.values()}
        check(max(cxs) - min(cxs) <= 1, f'{shot}: glyphs centred in one column {sorted(cxs)}')
        kr = {}
        for b in ks: kr.setdefault(b['y0'], []).append(b)
        check(len({max(b['x1'] for b in r) for r in kr.values()}) == 1, f'{shot}: keys share one right edge')
        check(all(abs(cy(l) - cy(rows[y][0])) <= 0.5 and abs(cy(l) - cy(kr[y][0])) <= 0.5 for l, y in zip(labels, sorted(rows))), f'{shot}: each row on one centre line')
        mid = (labels[0]['y0'] + labels[-1]['y1']) / 2
        check(abs(cy(Hh) - mid) <= 1, f'{shot}: handheld on the rows\' middle line ({cy(Hh)} vs {mid})')
        check(Hh['x0'] - P['x0'] >= 18 and Hh['y0'] - P['y0'] >= 8 and P['y1'] - Hh['y1'] >= 8, f'{shot}: handheld inside the panel, clear of its frame')
        top, bot = labels[0]['y0'] - P['y0'], P['y1'] - labels[-1]['y1']
        check(abs(top - bot) <= 1, f'{shot}: rows centred in the panel (above {top}, below {bot})')
        s = strip(shot, bs)
        items = labels + gl + ks + [Hh, T] + s
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot.startswith('select'):
        s = strip(shot, bs)
        if 'slide' in shot: continue                                       # (two cards mid-slide: the strip only)
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; N = many(bs, 'name')[0]; Pic = many(bs, 'picture')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T), ('name', N), ('picture', Pic)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        check(Pic['x0'] - P['x0'] >= 8 and P['x1'] - Pic['x1'] >= 8 and Pic['y0'] > P['y0'] and P['y1'] > N['y1'], f'{shot}: picture and name inside the panel')
        ar = sorted(many(bs, 'arrow'), key=lambda b: b['x0'])
        check(len(ar) == 2 and abs((ar[0]['x0'] + ar[1]['x1']) / 2 - 159.5) <= 1 and cy(ar[0]) == cy(ar[1]), f'{shot}: arrows either side, symmetric (1 px nudge), one centre line')
        check(all(abs(cy(a) - cy(Pic)) <= 1 for a in ar), f'{shot}: arrows on the picture\'s middle line ({[cy(a) for a in ar]} vs {cy(Pic)})')
        check(ar[0]['x1'] < P['x0'] and ar[1]['x0'] > P['x1'] and ar[0]['x0'] >= 4 and ar[1]['x1'] <= 315, f'{shot}: arrows outside the card, on the screen')
        md = sorted(many(bs, 'medal'), key=lambda b: b['x0'])
        check(len(md) == 3 and md[0]['x0'] == Pic['x0'] + 4, f'{shot}: three medals from the picture\'s left edge ({md[0]["x0"]} vs {Pic["x0"] + 4})')
        e, d = pitch_even([b['x0'] for b in md]); check(e, f'{shot}: medals evenly spaced {d}')
        row = md + many(bs, 'clock', 'time', 'score')
        check(max(cy(b) for b in row) - min(cy(b) for b in row) <= 0.5, f'{shot}: medals, clock, time and points on one centre line {sorted({cy(b) for b in row})}')
        sc = many(bs, 'score')
        if sc: check(sc[0]['x1'] == Pic['x1'] - 4, f'{shot}: points end at the picture\'s right edge ({sc[0]["x1"]} vs {Pic["x1"] - 4})')
        lk = many(bs, 'lock')
        if lk: check(abs(cx(lk[0]) - cx(Pic)) <= 0.5 and abs(cy(lk[0]) - cy(Pic)) <= 0.5, f'{shot}: padlock centred on the picture')
        dots = many(bs, 'dot')
        check(abs((min(b['x0'] for b in dots) + max(b['x1'] for b in dots)) / 2 - 159.5) <= 0.5 and min(b['y0'] for b in dots) > P['y1'] and max(b['y1'] for b in dots) < s[0]['y0'] - 2, f'{shot}: dots centred between the card and the strip')
        items = [T, N] + row + many(bs, 'lock', 'hard') + s + dots
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot.startswith('intro'):
        P = many(bs, 'panel'); 
        if not P: continue                                                  # (the drop-in's first frame: before the strip)
        P = P[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; N = many(bs, 'name')[0]; L = sorted(many(bs, 'story'), key=lambda b: b['y0'])
        for n, b in [('panel', P), ('ribbon', R), ('title', T), ('name', N)] + [('story line', b) for b in L]: check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        e, d = pitch_even([b['y0'] for b in L]); check(e, f'{shot}: even story pitch {d}')
        check(N['y0'] > R['y1'] + 2 and L[0]['y0'] > N['y1'] + 2, f'{shot}: ribbon, name and story apart')
        check(all(b['x0'] - P['x0'] >= 12 and P['x1'] - b['x1'] >= 12 for b in L + [N]), f'{shot}: text clear of the frame (12 px)')
        check(P['y1'] - L[-1]['y1'] >= 9, f'{shot}: room under the story ({P["y1"] - L[-1]["y1"]})')
        if 'drop' not in shot:
            s = strip(shot, bs)
            check(P['y1'] < s[0]['y0'], f'{shot}: the card above the strip')
    elif shot.startswith('talk') and 'rise' not in shot:
        P = many(bs, 'talkpanel')[0]; Fr = many(bs, 'portrait')[0]; L = sorted(many(bs, 'talk'), key=lambda b: b['y0'])
        check(P['x0'] >= 4 and Fr['x1'] <= 315 and P['y1'] <= 235 and Fr['y1'] <= 235, f'{shot}: panel and portrait inside the margins')
        check(Fr['x0'] == P['x1'] - 7 or Fr['x1'] == P['x0'] + 7, f'{shot}: the portrait frame on the panel\'s side, 8 px over it')
        check(Fr['y1'] == P['y1'] or Fr['y0'] == P['y0'] or Fr['y1'] >= P['y1'], f'{shot}: panel and portrait share the bottom line')
        vis0, vis1 = (P['x0'], Fr['x0'] - 1) if Fr['x0'] > P['x0'] else (Fr['x1'] + 1, P['x1'])
        check(all(abs(cx(b) - (vis0 + vis1) / 2) <= 1 for b in L), f'{shot}: each row centred in the panel\'s open part {[cx(b) for b in L]} vs {(vis0 + vis1) / 2}')
        check(abs((L[0]['y0'] + L[-1]['y1']) / 2 - cy(P)) <= 1, f'{shot}: the rows centred top to bottom')
        e, d = pitch_even([b['y0'] for b in L]); check(e, f'{shot}: even row pitch {d}')
        check(all(b['x0'] - vis0 >= 10 and vis1 - b['x1'] >= 10 for b in L), f'{shot}: rows clear of the frame (10 px)')
        hud = many(bs, 'lives', 'head', 'health', 'bones', 'score', 'clock', 'time', 'bone')
        check(not overlaps([P, Fr] + hud) or not [h for h in hud if not (h['x1'] < min(P['x0'], Fr['x0']) or h['x0'] > max(P['x1'], Fr['x1']) or h['y1'] < min(P['y0'], Fr['y0']) or h['y0'] > max(P['y1'], Fr['y1']))], f'{shot}: clear of the HUD')
    elif (shot.startswith('hint') or shot.startswith('nudge')) and 'rise' not in shot and 'none' not in shot:
        Bs = many(bs, 'bubble'); Pp = many(bs, 'pepper')[-1]; tl = many(bs, 'tail')
        check(len(Bs) == 1 and len(tl) == 1, f'{shot}: one bubble with its tail')
        B = Bs[0]; t_ = tl[0]
        g = many(bs, 'glyph'); pc = many(bs, 'pic'); h = sorted(many(bs, 'hint'), key=lambda b: b['y0'])
        check(B['x0'] >= 4 and B['x1'] <= 315 and B['y0'] >= 4 and B['y1'] <= 235, f'{shot}: the bubble inside the margins')
        check(not overlaps([B, Pp]) and not overlaps([t_, Pp]), f'{shot}: never over Pepper')
        inside = [b for b in g + pc + h]
        check(all(b['x0'] - B['x0'] >= 6 and B['x1'] - b['x1'] >= 5 and b['y0'] - B['y0'] >= 5 and B['y1'] - b['y1'] >= 5 for b in inside), f'{shot}: glyph, picture and words inside with room')
        blk = (h[0]['y0'] + h[-1]['y1']) / 2
        check(all(abs(cy(b) - cy(B)) <= 1 for b in g + pc) and abs(blk - cy(B)) <= 1, f'{shot}: glyph, picture and words on the bubble\'s centre line')
        check(len(h) <= 2, f'{shot}: at most two rows')
        gx = sorted(g + pc + h, key=lambda b: b['x0'])
        check(not overlaps(g + pc + h[:1]) and not overlaps(g + pc + h[-1:]), f'{shot}: glyph, picture and words apart')
        side = ('below' if t_['y0'] >= B['y1'] - 2 else 'above' if t_['y1'] <= B['y0'] + 2 else 'right' if t_['x0'] >= B['x1'] - 2 else 'left')
        toward = {'below': Pp['y0'] > B['y1'], 'above': Pp['y1'] < B['y0'], 'right': Pp['x0'] > B['x1'], 'left': Pp['x1'] < B['x0']}[side]
        check(toward, f'{shot}: the tail ({side}) points toward Pepper')
        gap = {'below': Pp['y0'] - B['y1'], 'above': B['y0'] - Pp['y1'], 'right': Pp['x0'] - B['x1'], 'left': B['x0'] - Pp['x1']}[side]
        check(3 <= gap <= 8, f'{shot}: near her ({gap} px, the nudge\'s bounce up to 3)')
    elif shot.startswith('pause') and 'controls' not in shot:
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; Sb = many(bs, 'subtitle')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T), ('subtitle', Sb)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        top = [b for b in (many(bs, 'question') or many(bs, 'bone', 'bones')) if b['x0'] > P['x0'] and b['x1'] < P['x1'] and b['y0'] > P['y0'] and b['y1'] < P['y1']]
        check(abs((min(b['x0'] for b in top) + max(b['x1'] for b in top)) / 2 - 159.5) <= 0.5 and len({cy(b) for b in top}) == 1, f'{shot}: the bones (or the question) centred on one line')
        labels = sorted(many(bs, 'label'), key=lambda b: b['y0'])
        check(len({b['x0'] for b in labels}) == 1, f'{shot}: rows share one left edge')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        cur = many(bs, 'cursor')[0]; sel = int(re.findall(r'_(\d)', shot)[0]) - 1 if re.findall(r'_(\d)', shot) else 0
        check(abs(cy(cur) - cy(labels[sel])) <= 1, f'{shot}: the paw on the selected row\'s centre line')
        check(labels[0]['x0'] - cur['x1'] - 1 == 4, f'{shot}: the paw 4 px before the rows ({labels[0]["x0"] - cur["x1"] - 1})')
        mt = many(bs, 'meter')
        if mt: check(abs(cy(mt[0]) - cy(labels[1])) <= 0.5 and P['x1'] - mt[0]['x1'] >= 14, f'{shot}: the meter on SOUND\'s centre line, clear of the frame')
        check(all(b['x0'] > P['x0'] + 10 for b in labels + [cur]) and P['y1'] - max(b['y1'] for b in labels) >= 9 or 'confirm' in shot, f'{shot}: rows inside the panel with room')
        check(not many(bs, 'button', 'tab', 'row'), f'{shot}: no coins or tabs off the frame, no row boxes')
        s = strip(shot, bs)
        items = labels + [cur, T, Sb] + top + mt + s
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot == 'pause_controls':
        check(many(bs, 'handheld') and many(bs, 'panel'), f'{shot}: the controls page over the level'); strip(shot, bs)
    elif shot.startswith('tally'):
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        ic, lb, vl = many(bs, 'ticon'), many(bs, 'tlabel'), many(bs, 'tvalue')
        rows = {}
        for b in ic + lb + vl: rows.setdefault(round(cy(b)), []).append(b)
        check(all(max(cy(b) for b in r) - min(cy(b) for b in r) <= 0.5 for r in rows.values()), f'{shot}: each line\'s picture, label and value on one centre line')
        if 'stamp' not in shot and 'start' not in shot and 'bones' not in shot:
            check(len({b['x1'] for b in vl}) == 1, f'{shot}: values share one right edge {sorted({b["x1"] for b in vl})}')
        md = sorted(many(bs, 'medal'), key=lambda b: b['y0']); ml = sorted(many(bs, 'mlabel'), key=lambda b: b['y0'])
        if len(md) == 3 and 'medals' not in shot:
            e, d = pitch_even([b['y0'] for b in md]); check(e, f'{shot}: medals evenly spaced {d}')
            check(all(abs(cy(a) - cy(b)) <= 0.5 for a, b in zip(md, ml)), f'{shot}: each medal\'s name on its centre line')
        inside = ic + lb + vl + md + ml + many(bs, 'note', 'secrets', 'rule')
        check(all(b['x0'] - P['x0'] >= 10 and P['x1'] - b['x1'] >= 8 and b['y1'] <= P['y1'] - 7 for b in inside), f'{shot}: everything inside the panel with room')
        items = ic + lb + vl + md + ml + many(bs, 'note', 'secrets', 'hard') + [T]
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
        st = many(bs, 'stamp')
        if st: check(st[0]['x1'] <= 315 and not overlaps(st + many(bs, 'note', 'secrets', 'medal', 'tvalue')), f'{shot}: the stamp on screen, over nothing written')
        if 'end' in shot or 'medals_' in shot or shot.endswith('medals') is False and ('_g_' in shot or '_h_' in shot): strip(shot, bs)
    elif shot.split('_')[0] in ('story', 'over', 'ending', 'bonus', 'toast'):
        kind = shot.split('_')[0]
        if kind == 'toast': continue                                        # (over the level select: a moment's toast)
        Ps = many(bs, 'panel', 'storypanel')
        cen = ['ribbon', 'title', 'name', 'big', 'end'] + (['score'] if kind == 'ending' else [])
        for b in many(bs, *cen): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {b["name"]} centred ({cx(b)})')
        names = {'story': ['story', 'portrait'], 'over': ['label', 'cursor'], 'ending': ['story', 'label', 'best', 'thanks'],
                 'bonus': ['story', 'subtitle', 'goal', 'tlabel', 'tvalue', 'try', 'life', 'gicon'] + (['head'] if 'result' in shot else [])}[kind]
        txt = many(bs, *names)
        if Ps and shot.split('_')[0] != 'toast':
            P = Ps[0]
            inside = [b for b in txt if b['name'] != 'portrait']
            check(all(b['x0'] >= P['x0'] + 8 and b['x1'] <= P['x1'] - 8 and b['y0'] >= P['y0'] + 6 and b['y1'] <= P['y1'] - 6 for b in inside), f'{shot}: the words inside the panel with room')
            check(all(b['x0'] >= 4 and b['x1'] <= 315 and b['y0'] >= 0 and b['y1'] <= 235 for b in Ps + txt), f'{shot}: on the screen')
        st = [b for b in many(bs, 'glyph', 'strip') if b['y0'] >= 200]
        if st: strip(shot, bs)
        items = [b for b in txt if b['name'] != 'portrait'] + many(bs, *[c for c in cen if c != 'ribbon']) + st
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
# (ui/panel-hud) the cards over a level (intro, pause and its controls page, GAME OVER, tally, story, the bonus round's
# intro and result) draw no HUD row under them: no HUD piece outside the card's panel; and every card's panel and ribbon
# (the ending's too) keep the 4 px margin to the screen's top
HUDP = {'health', 'clock', 'time', 'bone', 'bones', 'score', 'head', 'lives', 'hard', 'ball', 'catches', 'points', 'hudlife'}
for f in sorted(glob.glob(f'{D}/*.txt')):
    shot = os.path.basename(f)[:-4]; bs = load(shot)
    over_level = shot.split('_')[0] in ('intro', 'pause', 'over', 'tally', 'story') or shot in ('bonus_intro', 'bonus_result_life', 'bonus_result_try')
    if not (over_level or shot.startswith('ending')): continue
    Ps = many(bs, 'panel', 'storypanel')
    if over_level:
        def inside(b): return any(b['x0'] >= P['x0'] and b['x1'] <= P['x1'] and b['y0'] >= P['y0'] and b['y1'] <= P['y1'] for P in Ps)
        row = [b['name'] for b in bs if b['name'] in HUDP and not inside(b)]
        check(not row, f'{shot}: no HUD row under the card {row[:4]}')
    top = [b for b in Ps + many(bs, 'ribbon')]
    check(top and min(b['y0'] for b in top) >= 4, f'{shot}: the card 4 px or more from the screen\'s top ({min(b["y0"] for b in top) if top else "-"})')
check(len(set(strips.values())) == 1, f'strip: the same place on every screen {sorted(set(strips.values()))}')
# pieces
INK = (64, 11, 6); SH = (36, 8, 5)
for n in ['g_a', 'g_b', 'g_x', 'g_y', 'g_l', 'g_r', 'g_start', 'g_dpad', 'g_lr', 'g_down', 'k_space', 'k_esc', 'k_shift', 'k_enter', 'k_x', 'k_z', 'k_q',
          'k_left', 'k_right', 'k_up', 'k_down', 'tog_on', 'tog_off', 'handheld', 'ribbon_menu',
          'arrow_l', 'arrow_r', 'lock', 'lock_big', 'dot_on', 'dot_off', 'frame_s', 'bubble', 'ball', 'stamp',
          'medal_nohit_on', 'medal_nohit_off', 'medal_bones_on', 'medal_bones_off', 'medal_par_on', 'medal_par_off']:
    a = np.array(Image.open(f'{ROOT}/riverwalk/art/ui/{n}.png').convert('RGBA')); op = a[..., 3] > 0
    p = np.pad(op, 1); edge = op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    cols = {tuple(c) for c in a[edge][:, :3]}
    check(cols <= {INK, SH}, f'piece {n}: edge pixels only outline / shadow' + ('' if cols <= {INK, SH} else f' (also {sorted(cols - {INK, SH})[:3]})'))
    check(set(np.unique(a[..., 3]).tolist()) <= {0, 255}, f'piece {n}: alpha 0 or 255')
print('ALL PASS' if ok else 'SOME FAIL')
