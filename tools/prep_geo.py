import json,math
R=6371.0; l0=math.radians(10); p1=math.radians(50)
X0,X1,Y0,Y1=-3800,3800,-2850,2700
def fwd(lon,lat):
    l=math.radians(lon);p=math.radians(lat);d=l-l0
    k=2/(1+math.sin(p1)*math.sin(p)+math.cos(p1)*math.cos(p)*math.cos(d))
    return R*k*math.cos(p)*math.sin(d), R*k*(math.cos(p1)*math.sin(p)-math.sin(p1)*math.cos(p)*math.cos(d))
M=400 # margin km
def clampring(ring):
    out=[]
    for lon,lat in ring:
        if lat<-10 or abs(lon-10)>120: x,y=(X0-M if lon<10 else X1+M), (Y0-M)
        else:
            x,y=fwd(lon,lat)
        x=min(max(x,X0-M),X1+M); y=min(max(y,Y0-M),Y1+M)
        out.append((x,y))
    return out
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
                pr=[fwd(lo,la) if la>-10 and abs(lo-10)<120 else (1e9,1e9) for lo,la in ring]
                if not any(X0-M<x<X1+M and Y0-M<y<Y1+M for x,y in pr): continue
                c=clampring(ring)
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
land=proc('natural-earth/ne_50m_land.geojson', 300, 4)
holes=proc('natural-earth/ne_50m_land.geojson', 1500, 4, True, True)
lakes=holes+proc('natural-earth/ne_50m_lakes.geojson', 1500, 4, True)
js=json.dumps({'land':land,'lakes':lakes},separators=(',',':'))
open('geo.json','w').write(js)
print(len(land), sum(len(r)//2 for r in land), len(lakes), len(js))
