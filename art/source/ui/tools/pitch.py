import sys, numpy as np
from PIL import Image
def profile(a, axis):
    g = np.abs(np.diff(a.astype(float), axis=axis)).sum(axis=2)
    return g.sum(axis=1-axis) if axis==1 else g.sum(axis=1)
def best_pitch(sig, lo=2.5, hi=20.0):
    sig = sig - np.convolve(sig, np.ones(31)/31, mode='same')
    sig = np.clip(sig, 0, None)
    n = len(sig); idx = np.arange(n)
    best=None
    for p in np.arange(lo, hi, 0.01):
        ph = np.exp(2j*np.pi*idx/p)
        s = abs((sig*ph).sum())/ (sig.sum()+1e-9)
        if best is None or s>best[0]: best=(s,p, np.angle((sig*ph).sum()))
    s,p,ang = best
    off = (ang/(2*np.pi))*p % p
    return p, off, s
if __name__=="__main__":
    a = np.array(Image.open(sys.argv[1]).convert('RGB'))
    px = best_pitch(np.abs(np.diff(a.astype(float),axis=1)).sum(axis=2).sum(axis=0))
    py = best_pitch(np.abs(np.diff(a.astype(float),axis=0)).sum(axis=2).sum(axis=1))
    print("x pitch %.3f off %.2f score %.3f | y pitch %.3f off %.2f score %.3f"%(px+py))
