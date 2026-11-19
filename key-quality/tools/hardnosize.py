import json,glob,os,sys,collections
old,new=sys.argv[1:3]; H=('PIN_FAR','SHARED','OTHER_PARK')
tot=collections.Counter(); rises=[]
for f in sorted(glob.glob(os.path.join(new,'factcheck-US-*.json'))):
    a=os.path.basename(f)[10:-5]; O=json.load(open(os.path.join(old,os.path.basename(f))))['parks']; N=json.load(open(f))['parks']
    def cnt(P): return sum(1 for p in P.values() if any(x[0] in H for x in p.get('flags') or []))
    o,n=cnt(O),cnt(N); tot['o']+=o; tot['n']+=n
    if n>o: rises.append(f'{a} {o}->{n}')
print(f"parks with a hard flag other than size (PIN_FAR / SHARED / OTHER_PARK): {tot['o']} -> {tot['n']}; states where it rises: {rises or 'none'}")
