"""'Tu savais que ?' fact video (octopus), HyperFrames 1080x1920, timed from timing.json."""
import json, shutil, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent; P = ROOT / "fact1"
T = json.loads((P / "timing.json").read_text())
LEAD, TAIL = T["lead"], T["tail"]
SC = T["scenes"]  # [{id, vo_start, vo_end, words:[{w,s,e}] (absolute in vo)}]
YEL, CYA, RED, BLU, PNK = "#FFD23F", "#22D3EE", "#FF3B3B", "#3B82F6", "#FF6FAE"
# scene boundaries in the final timeline: audio placed at LEAD
START = [0.0] + [round(LEAD + s["vo_start"] - 0.12, 3) for s in SC[1:]]
END = START[1:] + [round(LEAD + SC[-1]["vo_end"] + TAIL, 3)]
DUR = [round(e - s, 3) for s, e in zip(START, END)]
TOTAL = END[-1]
def AT(i, word):  # local time of a word in scene i
    for w in SC[i]["words"]:
        if w["w"].lower().strip(".,!?…").startswith(word.lower()):
            return round(LEAD + w["s"] - START[i], 3)
    raise KeyError(word)

CSS = """
#root{position:absolute;inset:0;overflow:hidden}
.cam{position:absolute;inset:0;transform-origin:504px 700px}
.big{position:absolute;left:110px;width:790px;text-align:center;font:900 92px/1.0 Inter;color:#fff;-webkit-text-stroke:12px #000;paint-order:stroke fill;text-transform:uppercase}
.pill{position:absolute;left:504px;transform:translateX(-50%);padding:12px 28px;border-radius:16px;border:3px solid #fff;font:900 40px Inter;color:#111;white-space:nowrap}
svg.abs{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
"""
FONTS = "@font-face{font-family:'Orbitron';src:url('assets/fonts/Orbitron.ttf');font-weight:400 900}"

def heart(c, s=1.0):
    return f'<path transform="scale({s})" d="M0 30 C-60 -10 -40 -60 0 -30 C40 -60 60 -10 0 30Z" fill="{c}" stroke="#fff" stroke-width="5"/>'

def octo(body="#FF7A59", eye=True, tid="t"):
    tent = ""
    for k in range(8):
        x0 = -105 + k * 30
        cx = x0 + (-40 if k < 4 else 40)
        tent += f'<path class="{tid}" d="M{x0} 60 Q{cx} 170 {x0 + (-20 if k<4 else 20)} 250" stroke="{body}" stroke-width="26" fill="none" stroke-linecap="round"/>'
    eyes = ('<ellipse cx="-45" cy="10" rx="24" ry="28" fill="#fff"/><ellipse cx="45" cy="10" rx="24" ry="28" fill="#fff"/>'
            '<circle cx="-40" cy="16" r="12" fill="#111"/><circle cx="50" cy="16" r="12" fill="#111"/>') if eye else ""
    return tent + f'<ellipse cx="0" cy="-40" rx="135" ry="150" fill="{body}" stroke="#fff" stroke-width="6"/>' + eyes

class TL:
    def __init__(s): s.o = []
    def a(s, js): s.o.append(js)
    def pop(s, sel, t, d=0.4): s.a(f'tl.fromTo("{sel}",{{opacity:0,scale:0.4,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:{d},ease:"back.out(2)"}},{max(0,t):.3f});')
    def up(s, sel, t, d=0.35): s.a(f'tl.fromTo("{sel}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:{d},ease:"power3.out"}},{max(0,t):.3f});')
    def sway(s, sel, d):
        n = max(1, int(d / 0.9))
        s.a(f'tl.fromTo("{sel}",{{rotation:-4,transformOrigin:"50% 0%"}},{{rotation:4,duration:0.9,ease:"sine.inOut",yoyo:true,repeat:{n},stagger:0.08}},0);')

def scene(cid, dur, body, tl):
    return f"""<template><style>{FONTS}{CSS}</style>
<div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-layout-allow-overlap>
<div class="cam" id="{cid}-cam">{body}</div></div>
<script>const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#{cid}-cam",{{scale:1}},{{scale:1.05,duration:{dur},ease:"none"}},0);
{chr(10).join(tl.o)}
window.__timelines["{cid}"] = tl;</script></template>"""

def G(id_, x, y, inner, s=1.0):
    return f'<g transform="translate({x} {y}) scale({s})"><g id="{id_}">{inner}</g></g>'

out = []
# 1 hook
i = 0; t = TL(); d = DUR[i]
b = (f'<div class="big" id="h1" style="top:330px">La pieuvre a</div>'
     f'<div class="big" id="h2" style="top:430px;font-size:150px;color:{YEL}">3 cœurs</div>'
     f'<svg class="abs">{G("h-o", 504, 870, octo(tid="ht"), 0.9)}</svg>')
t.up("#h1", 0.1); t.a(f'tl.fromTo("#h2",{{opacity:0,scale:2}},{{opacity:1,scale:1,duration:0.35,ease:"power4.out"}},{max(0.3, AT(i,"TROIS")):.3f});')
t.a('tl.fromTo("#h-o",{opacity:0,y:200},{opacity:1,y:0,duration:0.5,ease:"back.out(1.5)"},0.15);'); t.sway(".ht", d)
out.append(("hook", b, t))
# 2 hearts
i = 1; t = TL(); d = DUR[i]
hs = "".join(G(f"hh{k}", x, y, heart(c, 1.2)) for k, (x, y, c) in enumerate([(-70, -60, CYA), (70, -60, CYA), (0, 40, RED)]))
b = (f'<div class="big" id="c1" style="top:300px;color:{YEL}">Oui, trois !</div>'
     f'<svg class="abs">{G("c-o", 504, 760, octo(eye=False, tid="ct") + hs, 1.15)}</svg>'
     f'<div class="pill" id="c-a" style="top:1010px;background:{CYA}">2 cœurs → les branchies</div>'
     f'<div class="pill" id="c-b" style="top:1010px;background:{RED};color:#fff">1 cœur → tout le corps</div>')
t.up("#c1", 0.05); t.a('tl.fromTo("#c-o",{opacity:0},{opacity:1,duration:0.3},0);'); t.sway(".ct", d)
for k in range(3): t.pop(f"#hh{k}", 0.3 + k * 0.2)
t.a(f'tl.to(["#hh0","#hh1","#hh2"],{{scale:1.2,transformOrigin:"50% 50%",duration:0.25,yoyo:true,repeat:{int(d/0.5)},ease:"sine.inOut"}},1.0);')
ta, tb = AT(i, "Deux"), AT(i, "un")
t.pop("#c-a", ta); t.a(f'tl.to("#c-a",{{opacity:0,duration:0.2}},{tb-0.2:.3f});'); t.pop("#c-b", tb)
out.append(("hearts", b, t))
# 3 blue blood
i = 2; t = TL(); d = DUR[i]
drop = '<path id="drop" d="M0 -170 C60 -80 120 -20 120 50 A120 120 0 0 1 -120 50 C-120 -20 -60 -80 0 -170Z" fill="#E11D48" stroke="#fff" stroke-width="6"/>'
b = (f'<div class="big" id="b1" style="top:300px">Son sang est</div>'
     f'<div class="big" id="b2" style="top:400px;font-size:150px;color:{BLU}">bleu</div>'
     f'<svg class="abs">{G("b-d", 504, 730, drop, 0.85)}</svg>'
     f'<div id="b-fe" style="position:absolute;left:170px;top:830px;width:220px;text-align:center;font:900 90px Orbitron;color:#fff;background:#B91C1C;border:4px solid #fff;border-radius:24px;opacity:0">Fe</div>'
     f'<div id="b-cu" style="position:absolute;left:690px;top:830px;width:220px;text-align:center;font:900 90px Orbitron;color:#fff;background:{BLU};border:4px solid #fff;border-radius:24px;opacity:0">Cu</div>'
     f'<div class="pill" id="b-l1" style="top:970px;left:280px;background:#fff">Toi : fer</div>'
     f'<div class="pill" id="b-l2" style="top:970px;left:760px;background:#fff">Pieuvre : cuivre</div>')
t.up("#b1", 0.05); t.pop("#b-d", 0.2)
tbl = AT(i, "BLEU")
t.a(f'tl.fromTo("#b2",{{opacity:0,scale:2}},{{opacity:1,scale:1,duration:0.35,ease:"power4.out"}},{tbl:.3f});')
t.a(f'tl.to("#drop",{{attr:{{fill:"{BLU}"}},duration:0.6}},{tbl:.3f});')
t.pop("#b-cu", AT(i, "cuivre")); t.pop("#b-l2", AT(i, "cuivre") + 0.15)
t.pop("#b-fe", AT(i, "fer")); t.pop("#b-l1", AT(i, "fer") + 0.15)
out.append(("blood", b, t))
# 4 swim -> heart stops
i = 3; t = TL(); d = DUR[i]
ecg = '<path id="ecg" d="M140 1000 L330 1000 L360 930 L390 1070 L420 1000 L560 1000 L590 930 L620 1070 L650 1000 L940 1000" stroke="#22C55E" stroke-width="10" fill="none" stroke-linejoin="round" stroke-dasharray="1400" stroke-dashoffset="1400"/>'
b = (f'<div class="big" id="s1" style="top:300px">Quand elle nage…</div>'
     f'<svg class="abs">{G("s-o", 504, 700, octo(tid="st"), 0.7)}{ecg}</svg>'
     f'<div class="big" id="s2" style="top:1060px;font-size:110px;color:{RED};opacity:0">STOP</div>')
t.up("#s1", 0.05)
t.a('tl.fromTo("#s-o",{opacity:0,y:200},{opacity:1,y:0,duration:1.2,ease:"power2.out"},0.1);'); t.sway(".st", d)
t.a('tl.to("#ecg",{attr:{"stroke-dashoffset":0},duration:1.4,ease:"none"},0.3);')
tst = AT(i, "s'arrête")
t.a(f'tl.to("#ecg",{{attr:{{d:"M140 1000 L940 1000",stroke:"{RED}"}},duration:0.25}},{tst:.3f});')
t.a(f'tl.fromTo("#s2",{{opacity:0,scale:1.8}},{{opacity:1,scale:1,duration:0.3,ease:"power4.out"}},{tst+0.1:.3f});')
out.append(("swim", b, t))
# 5 crawl
i = 4; t = TL(); d = DUR[i]
b = (f'<div class="big" id="r1" style="top:300px">Elle préfère</div>'
     f'<div class="big" id="r2" style="top:400px;font-size:140px;color:{YEL}">ramper</div>'
     f'<svg class="abs"><line x1="120" y1="1060" x2="960" y2="1060" stroke="#fff" stroke-width="6" opacity=".5"/>{G("r-o", 250, 820, octo(tid="rt"), 0.75)}</svg>'
     f'<div class="pill" id="r-t" style="top:1030px;background:#22C55E">Moins fatigant</div>')
t.up("#r1", 0.05); t.pop("#r2", AT(i, "ramper"))
t.a(f'tl.to("#r-o",{{x:560,duration:{d-0.3:.2f},ease:"none"}},0.1);')
t.a(f'tl.to("#r-o",{{y:-18,duration:0.3,yoyo:true,repeat:{int(d/0.3)},ease:"sine.inOut"}},0.1);'); t.sway(".rt", d)
t.pop("#r-t", AT(i, "fatigue"))
out.append(("crawl", b, t))
# 6 roast
i = 5; t = TL(); d = DUR[i]
broken = ('<g id="bk"><path id="bkl" d="M0 30 C-60 -10 -40 -60 0 -30 L-12 -5 L6 10 Z" fill="#E11D48" stroke="#fff" stroke-width="5"/>'
          '<path id="bkr" d="M0 -30 C40 -60 60 -10 0 30 L6 10 L-12 -5Z" fill="#E11D48" stroke="#fff" stroke-width="5"/></g>')
b = (f'<div class="big" id="o1" style="top:300px">Elle : 3 cœurs</div>'
     f'<svg class="abs">' + "".join(G(f"oh{k}", 330 + k * 210, 560, heart(CYA if k < 2 else RED, 1.4)) for k in range(3))
     + G("o-b", 504, 790, broken, 2.4) + '</svg>'
     f'<div class="big" id="o2" style="top:950px;font-size:64px;color:{PNK}">Toi : même pas un entier</div>')
t.up("#o1", 0.05)
for k in range(3): t.pop(f"#oh{k}", 0.2 + k * 0.15)
tt = AT(i, "toi"); t.pop("#o-b", tt)
t.a(f'tl.to("#bkl",{{x:-14,rotation:-12,transformOrigin:"0% 100%",duration:0.3}},{tt+0.6:.3f});')
t.a(f'tl.to("#bkr",{{x:14,rotation:12,transformOrigin:"100% 100%",duration:0.3}},{tt+0.6:.3f});')
t.up("#o2", tt + 0.3)
out.append(("roast", b, t))
# 7 CTA
i = 6; t = TL(); d = DUR[i]
bubble = ('<path d="M-200 -120 Q-200 -170 -150 -170 L150 -170 Q200 -170 200 -120 L200 40 Q200 90 150 90 L-60 90 L-140 160 L-120 90 L-150 90 Q-200 90 -200 40Z" fill="#fff" stroke="#111" stroke-width="6"/>'
          '<circle cx="-80" cy="-40" r="18" fill="#111"/><circle cx="0" cy="-40" r="18" fill="#111"/><circle cx="80" cy="-40" r="18" fill="#111"/>')
b = (f'<div class="big" id="k1" style="top:300px">Ton animal</div>'
     f'<div class="big" id="k2" style="top:400px;font-size:84px;color:{YEL}">en commentaire</div>'
     f'<svg class="abs">{G("k-b", 504, 760, bubble, 0.9)}</svg>'
     f'<div class="pill" id="k-t" style="top:990px;background:{YEL}">Je te sors un fait encore plus chelou</div>')
t.up("#k1", 0.05); t.pop("#k2", AT(i, "commentaire")); t.pop("#k-b", 0.3)
t.a(f'tl.to("#k-b",{{y:-20,duration:0.35,yoyo:true,repeat:{int(d/0.35)},ease:"sine.inOut"}},0.7);')
t.pop("#k-t", AT(i, "je"))
out.append(("cta", b, t))

names = [n for n, _, _ in out]
for k, (n, b, t) in enumerate(out):
    (P / "compositions" / f"{n}.html").write_text(scene(n, DUR[k], b, t))

# background + brand badge
(P / "compositions" / "bg.html").write_text(f"""<template><style>
#root{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 35%,#1b2a4a 0%,#0B0C11 65%)}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.08) 2px,transparent 2.6px);background-size:54px 54px}}
#badge{{position:absolute;left:50%;top:200px;transform:translateX(-50%);padding:8px 30px;border-radius:40px;background:{YEL};border:4px solid #000;font:900 40px Inter;color:#111;white-space:nowrap}}
</style><div id="root" data-composition-id="bg" data-width="1080" data-height="1920" data-layout-ignore><div class="dots" id="bgd"></div><div id="badge">TU SAVAIS QUE ?</div></div>
<script>const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#bgd",{{backgroundPosition:"0px 0px"}},{{backgroundPosition:"0px 216px",duration:{TOTAL},ease:"none"}},0);
tl.fromTo("#badge",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.4,ease:"back.out(2)"}},0);
window.__timelines["bg"] = tl;</script></template>""")

# captions (karaoke, 1-3 words)
groups, ctl, gid = [], [], 0
for s in SC:
    cur = []
    def flush():
        global gid
        if not cur: return
        g0 = LEAD + cur[0]["s"]; g1 = LEAD + cur[-1]["e"]
        txt = " ".join(w["w"] for w in cur).upper()
        size = int(max(52, min(86, 660 / (0.64 * max(8, len(txt))))))
        spans = "".join(f'<span id="c{gid}w{j}">{w["w"].upper()}</span> ' for j, w in enumerate(cur))
        groups.append(f'<div class="grp clip" id="c{gid}" data-start="{g0:.3f}" data-duration="{g1-g0:.3f}" data-track-index="0"><div class="in" id="c{gid}i" style="font-size:{size}px">{spans}</div></div>')
        ctl.append(f'tl.fromTo("#c{gid}i",{{opacity:0,scale:0.85}},{{opacity:1,scale:1,duration:0.1,ease:"back.out(2)"}},{g0:.3f});')
        for j, w in enumerate(cur):
            ctl.append(f'tl.set("#c{gid}w{j}",{{color:"{YEL}"}},{LEAD+w["s"]:.3f});')
            ctl.append(f'tl.set("#c{gid}w{j}",{{color:"#FFFFFF"}},{LEAD+w["e"]:.3f});')
        gid += 1; cur.clear()
    for w in s["words"]:
        if not any(ch.isalnum() for ch in w["w"]): continue
        cur.append(w)
        if len(cur) >= 3 or len(" ".join(x["w"] for x in cur)) >= 14 or w["w"][-1] in ".,!?…:": flush()
    flush()
(P / "compositions" / "captions.html").write_text(f"""<template><style>
#root{{position:absolute;inset:0}}
.grp{{position:absolute;left:120px;width:680px;top:1130px;height:120px;display:flex;align-items:center;justify-content:center}}
.grp .in{{font-family:Inter;font-weight:900;color:#fff;text-align:center;line-height:1.05;-webkit-text-stroke:10px #000;paint-order:stroke fill}}
</style><div id="root" data-composition-id="captions" data-width="1080" data-height="1920">{chr(10).join(groups)}</div>
<script>const tl = gsap.timeline({{ paused: true }});
{chr(10).join(ctl)}
window.__timelines["captions"] = tl;</script></template>""")

hosts = [f'<div id="bg" data-composition-id="bg" data-composition-src="compositions/bg.html" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-width="1080" data-height="1920"></div>']
for k, n in enumerate(names):
    hosts.append(f'<div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{START[k]}" data-duration="{DUR[k]}" data-track-index="1" data-width="1080" data-height="1920" style="z-index:2"></div>')
hosts.append(f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-width="1080" data-height="1920" style="z-index:3"></div>')
if (P / "assets/vo.mp3").exists():
    hosts.append(f'<audio id="vo" class="clip" src="assets/vo.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-volume="1"></audio>')
(P / "index.html").write_text(f"""<!doctype html><html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/vendor/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#0B0C11}}#root{{position:relative;width:1080px;height:1920px}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(hosts)}</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script></body></html>""")
print("total", TOTAL, DUR)
