import sys, os, json, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from cut import key
R3 = '/tmp/claude-0/ui/r3'; OUT = '/tmp/claude-0/ui/kit'; os.makedirs(OUT, exist_ok=True); os.makedirs(OUT+'/raw', exist_ok=True)
A = key(Image.open(R3+'/kitA_1x.png')); B = key(Image.open(R3+'/kitB_1x.png'))
bA = json.load(open(R3+'/kitA_boxes.json')); bB = json.load(open(R3+'/kitB_boxes.json'))
def crop(img, b): x0,y0,x1,y1 = b; return img[y0:y1, x0:x1].copy()
def defringe(p):
    a = p[...,3] > 0; r,g,b = [p[...,i].astype(int) for i in range(3)]
    mag = (r > 140) & (b > 140) & (g < 130) & (b > g + 50)
    edge = a & ~ndimage.binary_erosion(a, structure=np.ones((3,3)), border_value=0)
    p[..., 3][mag & edge] = 0
    # a second ring
    a = p[...,3] > 0; edge = a & ~ndimage.binary_erosion(a, structure=np.ones((3,3)), border_value=0)
    p[..., 3][mag & edge] = 0
    return trim(p)
def trim(p):
    ys, xs = np.nonzero(p[...,3] > 0)
    return p[ys.min():ys.max()+1, xs.min():xs.max()+1]
def split_rows(p):
    rows = (p[...,3] > 0).any(axis=1); parts=[]; y=0; n=len(rows)
    while y < n:
        if rows[y]:
            y0=y
            while y<n and rows[y]: y+=1
            parts.append(trim(p[y0:y]))
        else: y+=1
    return parts
def split_dips(p):
    c = (p[...,3] > 0).sum(axis=1); m = c.max(); cuts=[0]
    for y in range(1, len(c)-1):
        if c[y] < m-1 and c[y+1] < m-1 and y+1-cuts[-1] > 4: cuts.append(y+1)
    cuts.append(len(c)); return [trim(p[a:b]) for a,b in zip(cuts, cuts[1:])]
def split_cols(p):
    return [np.transpose(q,(1,0,2)) for q in split_rows(np.transpose(p,(1,0,2)))]
pieces = {}
nameA = {0:'panel_wide',1:'panel_menu',3:'ribbon',4:'cursor_paw',7:'icon_clock',8:'icon_bone',9:'icon_bone_gold',10:'icon_ball',
 11:'icon_lock',12:'icon_speaker',13:'heart_full',14:'heart_empty',15:'pepper_head',16:'medal_nohit_won',17:'medal_bones_won',
 18:'medal_par_won',19:'btn_a_bronze',20:'dpad',21:'volume_bar',22:'toggle_on',23:'toggle_off'}
for i,n in nameA.items(): pieces[n] = defringe(crop(A, bA[i]))
hb = split_rows(defringe(crop(A, bA[5]))); pieces['health_full'], pieces['health_empty'] = hb[0], hb[1]
rw = split_dips(defringe(crop(A, bA[6]))); pieces['row_normal'], pieces['row_selected'], pieces['row_disabled'] = rw[0], rw[1], rw[2]
for k, ch in enumerate('0123456789'): pieces['digit_'+ch] = defringe(crop(A, bA[24+k]))
pieces['digit_x'] = defringe(crop(A, bA[34])); pieces['digit_slash'] = defringe(crop(A, bA[35])); pieces['digit_colon'] = defringe(crop(A, bA[36]))
for k, ch in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'): pieces['letter_'+ch] = defringe(crop(A, bA[37+k]))
# from kit B
pieces['medal_nohit_dark'] = defringe(crop(B, bB[20]))
m17 = split_rows(defringe(crop(B, bB[17]))); m18 = split_rows(defringe(crop(B, bB[18])))
pieces['medal_bones_dark'] = m17[-1]; pieces['medal_par_dark'] = m18[-1]
pieces['btn_a'] = defringe(crop(B, bB[24])); pieces['btn_b'] = defringe(crop(B, bB[25]))
pieces['panel_menu_cream'] = defringe(crop(B, bB[7])); pieces['panel_wide_cream'] = defringe(crop(B, bB[3]))
for n,p in pieces.items(): Image.fromarray(p).save(f'{OUT}/raw/{n}.png')
json.dump({n: [int(p.shape[1]), int(p.shape[0])] for n,p in pieces.items()}, open(OUT+'/raw_sizes.json','w'), indent=0)
for n,p in pieces.items(): print(f'{n:18s} {p.shape[1]:3d} x {p.shape[0]:3d}  colours {len(np.unique(p[p[...,3]>0][:,:3].reshape(-1,3),axis=0))}')
