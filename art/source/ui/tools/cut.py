# key out the magenta background and cut every piece by connected alpha (pieces closer than `gap` px merge)
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
def key(im):
    a = np.array(im.convert('RGB')).astype(int)
    r,g,b = a[...,0],a[...,1],a[...,2]
    mag = (r > 150) & (b > 150) & (g < 110) & (abs(r-b) < 90)
    rgba = np.dstack([a, np.where(mag, 0, 255)]).astype(np.uint8)
    return rgba
def cut(rgba, gap=1):
    op = rgba[...,3] > 0
    grow = ndimage.binary_dilation(op, iterations=gap) if gap else op
    lab, n = ndimage.label(grow, structure=np.ones((3,3)))
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        m = (lab[sl] == i+1) & op[sl]
        ys, xs = np.nonzero(m)
        if len(ys) < 6: continue
        y0, x0 = sl[0].start + ys.min(), sl[1].start + xs.min()
        y1, x1 = sl[0].start + ys.max() + 1, sl[1].start + xs.max() + 1
        boxes.append((int(x0), int(y0), int(x1), int(y1)))
    # reading order: rows by y centre
    boxes.sort(key=lambda b: (round(((b[1]+b[3])/2)/12), b[0]))
    return boxes
if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    rgba = key(Image.open(src)); boxes = cut(rgba)
    Image.fromarray(rgba).save(out + "_keyed.png")
    json.dump(boxes, open(out + "_boxes.json", "w"))
    S = 4; im = Image.fromarray(rgba).resize((rgba.shape[1]*S, rgba.shape[0]*S), Image.NEAREST)
    bg = Image.new('RGBA', im.size, (40,44,60,255)); bg.alpha_composite(im); d = ImageDraw.Draw(bg)
    for i,(x0,y0,x1,y1) in enumerate(boxes):
        d.rectangle([x0*S-1,y0*S-1,x1*S,y1*S], outline=(0,255,120)); d.text((x0*S+1,y0*S+1), str(i), fill=(255,255,255))
    bg.save(out + "_index.png"); print(len(boxes), "pieces")
