import os, sys, math, json
os.environ['PASS']='3'
sys.path.insert(0,'/workspace/h6/KPC-Links/.github/scripts')
import kpc_fers as K
print('CELL',K.CELL,'TIGHT_SHRINK',K.TIGHT_SHRINK)
lat0=37.5; lon0=-84.0
kx=111320*math.cos(math.radians(lat0)); ky=110574
def rect(x0,y0,x1,y1,ang=0):
    pts=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)]
    a=math.radians(ang); out=[]
    for x,y in pts:
        xr=x*math.cos(a)-y*math.sin(a); yr=x*math.sin(a)+y*math.cos(a)
        out.append([lon0+xr/kx, lat0+yr/ky])
    return [[out]]   # groups: list of records, each list of rings
res=[]
for w in [0,3,6,10,14,16,18,20,22,22.86,24,26,30,46,50]:
    for ang in [0,17,45]:
      for off in [0,1.3,2.6]:
        A=rect(-2000,-1000,0+off+w,1000,ang)   # park A ends at x=w+off
        B=rect(0+off,-1000,2000,1000,ang)       # park B starts at x=off: overlap width w
        G={'A':A,'B':B}
        box=[min(p[0] for p in A[0][0]+B[0][0]),min(p[1] for p in A[0][0]+B[0][0]),max(p[0] for p in A[0][0]+B[0][0]),max(p[1] for p in A[0][0]+B[0][0])]
        sp=K.area_spots(G,['A','B'],box)
        wm=max([s['wide_m'] for s in sp],default=None)
        res.append((w,ang,off,len(sp),wm))
for r in res: print(r)
json.dump(res,open('probe1.json','w'))
