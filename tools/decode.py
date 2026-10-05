import json,re,sys
import numpy as np
from PIL import Image
src=sys.argv[1]
txt=json.load(open(src))[0]['text']
body=txt.split('BEGIN\n',1)[1].split('\nEND',1)[0]
A='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
def fnv(s):
    h=0x811c9dc5
    for ch in s.encode(): h^=ch; h=(h*16777619)&0xffffffff
    return h
for line in body.split('\n'):
    name,W,H,P,b,hx=line.split('|'); W=int(W);H=int(H); P=P.split(',')
    ok = fnv(b)==int(hx,16)
    L2=len(P)>52; cl=2 if L2 else 1
    img=np.zeros((H,W,4),np.uint8)
    rows=b.split('/'); assert len(rows)==H
    for y,r in enumerate(rows):
        x=0;i=0
        while i<len(r):
            c=r[i:i+cl]; i+=cl
            m=re.match(r'\d+',r[i:]); n=1
            if m: n=int(m.group()); i+=len(m.group())
            if c[0]!='.':
                v = A.index(c[0])*52+A.index(c[1]) if L2 else A.index(c)
                k=P[v]; img[y,x:x+n]=[int(k[j:j+2],16) for j in (0,2,4,6)]
            x+=n
        assert x==W,(name,y,x)
    Image.fromarray(img,'RGBA').save(f'sheets/{name}.png')
    print(name,W,H,len(P),'hash ok' if ok else 'HASH MISMATCH')
