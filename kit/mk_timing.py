import json, sys, subprocess, numpy as np, soundfile as sf
from pathlib import Path
P = Path(__file__).resolve().parent / "fact1"
S = ["Tu savais que la pieuvre a TROIS cœurs ?",
 "Oui, trois ! Deux qui pompent le sang dans ses branchies, et un pour tout le reste du corps.",
 "Et attends, c'est pas fini… son sang est BLEU. Parce qu'elle utilise du cuivre, là où toi, tu utilises du fer.",
 "Mais le plus fou… quand elle nage, son cœur principal s'arrête de battre.",
 "Du coup, elle préfère ramper, ça la fatigue moins.",
 "Bref, elle a trois cœurs… et toi t'arrives même pas à en garder un entier.",
 "Allez, dis en commentaire un animal, et je te sors un fait encore plus chelou."]
L = [len(s) for s in S]
if len(sys.argv) > 1:
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",sys.argv[1],"-ar","44100","-ac","1","-af","loudnorm=I=-16:TP=-1.5:LRA=11","/tmp/f.wav"],check=True)
    a, sr = sf.read("/tmp/f.wav"); fr = int(sr*0.01); n = len(a)//fr
    db = 20*np.log10(np.array([np.sqrt(np.mean(a[i*fr:(i+1)*fr]**2)) for i in range(n)])+1e-9); v = db > db.max()-38
    i0 = int(np.argmax(v)); i1 = n-int(np.argmax(v[::-1]))
    sil=[]; j=i0
    while j<i1:
        if not v[j]:
            s0=j
            while j<i1 and not v[j]: j+=1
            if j-s0>=18: sil.append((s0*0.01,j*0.01))
        else: j+=1
    t0, t1 = i0*0.01, i1*0.01
    exp = [t0 + (t1-t0)*sum(L[:k])/sum(L) for k in range(1,len(S))]
    bounds=[]; used=set()
    for e in exp:  # nearest unused pause
        c = min([p for p in sil if p not in used], key=lambda p: abs((p[0]+p[1])/2-e)); used.add(c); bounds.append(c)
    bounds.sort()
    import os
    if os.environ.get("BOUNDS"): bounds=[tuple(map(float,x.split(":"))) for x in os.environ["BOUNDS"].split(",")]
    spans=[(t0, bounds[0][0])]+[(bounds[k][1], bounds[k+1][0]) for k in range(len(bounds)-1)]+[(bounds[-1][1], t1)]
    print("pauses", [(round(x,2),round(y,2)) for x,y in sil]); print("spans", [(round(x,2),round(y,2)) for x,y in spans])
    sf.write("/tmp/fn.wav", a, sr)
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i","/tmp/fn.wav","-af","highpass=f=70,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120:makeup=2,alimiter=limit=0.89","-b:a","192k",str(P/"assets/vo.mp3")],check=True)
else:
    rate=14.0; t=0; spans=[]
    for l in L: spans.append((t, t+l/rate)); t+=l/rate+0.35
out=[]
for s,(a0,a1) in zip(S,spans):
    import os
    segs=[(s.split(),a0,a1)]
    for sp in os.environ.get("SPLITS","").split(","):
        if not sp: continue
        word,x,y=sp.split(":"); x=float(x); y=float(y)
        ws0,b0,b1=segs[-1]
        if word in ws0 and b0<x<b1:
            k=ws0.index(word)+1; segs[-1:]=[(ws0[:k],b0,x),(ws0[k:],y,b1)]
    W=[]
    for ws,b0,b1 in segs:
        tot=sum(len(w)+1 for w in ws); c=0
        for w in ws:
            st=b0+(b1-b0)*c/tot; c+=len(w)+1; W.append({"w":w,"s":round(st,3),"e":round(b0+(b1-b0)*c/tot,3)})
    out.append({"vo_start":round(a0,3),"vo_end":round(a1,3),"words":W})
json.dump({"lead":0.3,"tail":0.6,"scenes":out},open(P/"timing.json","w"),ensure_ascii=False)
