import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
NE=ROOT/'natural-earth'
R=6371.0; l0=math.radians(10); p1=math.radians(50)
X0,X1,Y0,Y1=-3800,3800,-2850,2700
def fwd(lon,lat):
    l=math.radians(lon);p=math.radians(lat);d=l-l0
    k=2/(1+math.sin(p1)*math.sin(p)+math.cos(p1)*math.cos(p)*math.cos(d))
    return R*k*math.cos(p)*math.sin(d), R*k*(math.cos(p1)*math.sin(p)-math.sin(p1)*math.cos(p)*math.cos(d))
M=400 # margin km
BOX=(X0-M,X1+M,Y0-M,Y1+M)
def clip(pts):
    # Sutherland-Hodgman: clip the projected ring to the box (domain + margin).
    # Points far outside are projected too (stereographic is finite everywhere except
    # the antipode), so edges crossing the domain keep their true direction.
    for ax,side in ((0,0),(0,1),(1,0),(1,1)):
        b=BOX[2*ax+side]; ins=(lambda q: q[ax]>=b) if side==0 else (lambda q: q[ax]<=b)
        out=[]
        for i in range(len(pts)):
            P,Q=pts[i-1],pts[i]
            if ins(Q):
                if not ins(P): out.append(cut(P,Q,ax,b))
                out.append(Q)
            elif ins(P): out.append(cut(P,Q,ax,b))
        pts=out
        if not pts: break
    return pts
def cut(P,Q,ax,b):
    t=(b-P[ax])/(Q[ax]-P[ax]); return (P[0]+t*(Q[0]-P[0]), P[1]+t*(Q[1]-P[1]))
def dp(pts,eps):
    if len(pts)<3: return pts
    keep=[False]*len(pts); keep[0]=keep[-1]=True
    st=[(0,len(pts)-1)]
    while st:
        a,b=st.pop(); ax,ay=pts[a]; bx,by=pts[b]; dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy) or 1e-9
        mi,md=-1,0
        for i in range(a+1,b):
            px,py=pts[i]; d=abs(dy*(px-ax)-dx*(py-ay))/L if L>1e-6 else math.hypot(px-ax,py-ay)
            if d>md: md,mi=d,i
        if md>eps: keep[mi]=True; st+= [(a,mi),(mi,b)]
    return [p for p,k in zip(pts,keep) if k]
def area(r): return 0.5*abs(sum(r[i][0]*r[i-1][1]-r[i-1][0]*r[i][1] for i in range(len(r))))
def proc(fn, minarea, eps, names=False, holes=False):
    g=json.load(open(fn)); res=[]
    for f in g['features']:
        geom=f['geometry']; polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for poly in polys:
            for ring in (poly[1:] if holes else poly[:1]):
                if max(la for lo,la in ring)<-30: continue  # Antarctica etc. (close to the antipode)
                c=clip([fwd(lo,la) for lo,la in ring])
                if len(c)<3: continue
                # dedupe
                d=[c[0]]
                for p in c[1:]:
                    if abs(p[0]-d[-1][0])>0.01 or abs(p[1]-d[-1][1])>0.01: d.append(p)
                if area(d)<minarea: continue
                s=dp(d,eps)
                if len(s)<4: continue
                if names: print(f['properties'].get('name'), round(area(d)))
                # delta encode ints (km)
                xs=[round(p[0]) for p in s]; ys=[round(p[1]) for p in s]
                enc=[xs[0],ys[0]]
                for i in range(1,len(xs)): enc+= [xs[i]-xs[i-1], ys[i]-ys[i-1]]
                res.append(enc)
    return res
land=proc(NE/'ne_50m_land.geojson', 300, 4)
holes=proc(NE/'ne_50m_land.geojson', 1500, 4, True, True)
lakes=holes+proc(NE/'ne_50m_lakes.geojson', 1500, 4, True)
js=json.dumps({'land':land,'lakes':lakes},separators=(',',':'))
open(ROOT/'data'/'geo.json','w').write(js)
print(len(land), sum(len(r)//2 for r in land), len(lakes), len(js))
