#!/usr/bin/env python3
"""Vidéo TikTok 100 % motion design à partir des captures de la démo Le Nôtre.

7 plans, 7 mouvements différents, 6 transitions différentes, 14,1 s.
Aucune photo de plat réutilisée : uniquement les captures de la démo web.
"""
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(BASE, "captures")
PARTS = os.path.join(BASE, "videos", "parts-temp")
TX = os.path.join(BASE, "texts-motion")
FINAL = os.path.join(BASE, "videos", "tiktok-motion-abidjan.mp4")
os.makedirs(PARTS, exist_ok=True)
os.makedirs(TX, exist_ok=True)

F = os.path.join(BASE, "fonts", "karla-700.ttf")
FP = os.path.join(BASE, "fonts", "playfair-700.ttf")
W, H, FPS, D = 1080, 1920, 25, 2.4
BG = "0x351515"
OR = "0xA86A08"
BL = "0xF8F5F0"


def txt(name, value):
    p = os.path.join(TX, name + ".txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(value)
    return p


T_AVANT = txt("avant", "AVANT")
T_UNLIEN = txt("unlien", "1 LIEN")
T_TOUS = txt("tous", "TOUS DETAILS")
T_PRIX = txt("prix", "2 500 FCFA")
T_HOR = txt("hor", "7J/7")
T_MAPS = txt("maps", "GOOGLE MAPS")
T_WA = txt("wa", "RESERVATION WA")
T_OFFRE = txt("offre", "25 000 FCFA")
T_24H = txt("24h", "PRET EN 24H")
T_PAIEMENT = txt("paiement", "WAVE / ORANGE MONEY")
T_CTA = txt("cta", "COMMENTE ``RESTO``")


def draw(path, size, y, color=BL, alpha="1", font=F, box=None):
    s = "drawtext=fontfile=%s:textfile=%s:fontsize=%d:fontcolor=%s:x=(w-text_w)/2:y=%s:alpha='%s'" % (
        font, path, size, color, y, alpha)
    if box:
        s += ":box=1:boxcolor=%s:boxborderw=22" % box
    return s


def run(name, inputs, chain):
    out = os.path.join(PARTS, name + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    cmd += inputs
    cmd += ["-filter_complex", chain, "-map", "[v]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-t", str(D), out]
    subprocess.run(cmd, check=True)
    print("plan", name, "OK", flush=True)
    return out


def image_input(path):
    return ["-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", path]


def bg_input():
    return ["-f", "lavfi", "-i", "color=c=%s:s=%dx%d:r=%d:d=%s" % (BG, W, H, FPS, D)]


plans = []

# PLAN 1 — bulles WhatsApp qui arrivent en cascade (glissements opposés).
ins = bg_input()
for b in ["b1", "b2", "b3", "b4"]:
    ins += image_input(os.path.join(CAP, b + ".png"))
c = ""
base = "[0:v]"
positions = [
    (1, "-1150+1240*min((t-0.10)/0.45\\,1)", "330"),
    (2, "1150-1240*min((t-0.45)/0.45\\,1)", "640"),
    (3, "-1150+1240*min((t-0.80)/0.45\\,1)", "950"),
    (4, "1150-1240*min((t-1.15)/0.45\\,1)", "1260"),
]
for idx, xexpr, y in positions:
    c += "%s[%d:v]overlay=x='%s':y=%s:enable='gte(t\\,%.2f)'[o%d];" % (
        base, idx, xexpr, y, 0.10 + (idx - 1) * 0.35, idx)
    base = "[o%d]" % idx
c = c.rstrip(";")
c += ";" + base + draw(T_AVANT, 46, "150", color=OR,
                       alpha="min(t/0.3\\,1)*min((2.4-t)/0.4\\,1)") + "[v]"
plans.append(run("p1", ins, c))

# PLAN 2 — hero : zoom dynamique + parallaxe, texte glissant.
ins = image_input(os.path.join(CAP, "hero.png"))
c = ("[0:v]scale=1350:2048:force_original_aspect_ratio=increase,"
     "crop=1350:2048,"
     "zoompan=z='min(1.08+on*0.0009\\,1.24)':x='iw/2-(iw/zoom/2)+on*0.35':"
     "y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d,"
     "drawbox=x=0:y=0:w=iw:h=ih:color=%s@0.42:t=fill,"
     "%s[v]" % (W, H, FPS, BG,
                draw(T_UNLIEN, 128, "h*0.42+60*(1-min(t/0.5\\,1))", color=BL,
                     alpha="min(t/0.4\\,1)")))
plans.append(run("p2", ins, c))

# PLAN 3 — carte : glissement vertical (parallaxe) + badge prix qui pop.
ins = image_input(os.path.join(CAP, "menu.png"))
c = ("[0:v]crop=%d:%d:0:'min(t/2.2*1090\\,1090)',setsar=1," % (W, H) +
     draw(T_TOUS, 54, "120", color=OR, alpha="min(t/0.3\\,1)") + "," +
     draw(T_PRIX, 82, "h*0.72", color=BL, box=OR,
          alpha="min(t/0.35\\,1)") + "[v]")
plans.append(run("p3", ins, c))

# PLAN 4 — horaires : carte flottante qui glisse depuis la droite.
ins = bg_input() + image_input(os.path.join(CAP, "horaires.png"))
c = ("[0:v][1:v]overlay=x='1200-1240*min((t)/0.6\\,1)':"
     "y='h*0.38+18*sin(t*3)':enable='gte(t\\,0)':[o];"
     "[o]" + draw(T_HOR, 140, "h*0.68+50*(1-min(t/0.5\\,1))",
                  color=OR, alpha="min(t/0.4\\,1)") + "[v]")
plans.append(run("p4", ins, c))

# PLAN 5 — Google Maps : zoom arrière + badge.
ins = bg_input() + image_input(os.path.join(CAP, "maps.png"))
c = ("[1:v]scale=1600:600,"
     "zoompan=z='max(1.35-on*0.004\\,1.0)':x='iw/2-(iw/zoom/2)':"
     "y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d[m];" % (W, H, FPS) +
     "[0:v][m]overlay=x='(w-w*1)/2':y='h*0.34':[o];"
     "[o]" + draw(T_MAPS, 92, "h*0.62", color=OR,
                  alpha="min(t/0.4\\,1)") + "[v]")
plans.append(run("p5", ins, c))

# PLAN 6 — bouton WhatsApp : carte flottante + badge réservation.
ins = bg_input() + image_input(os.path.join(CAP, "contact.png"))
c = ("[0:v][1:v]overlay=x='(w-1080)/2':"
     "y='h*0.30+22*sin(t*2.6)':[o];"
     "[o]" + draw(T_WA, 76, "h*0.76", color=BL, box=OR,
                  alpha="min(t/0.4\\,1)") + "[v]")
plans.append(run("p6", ins, c))

# PLAN 7 — offre finale : texte qui grandit, puis CTA.
ins = bg_input()
c = ("[0:v]" +
     draw(T_OFFRE, 132, "h*0.28+70*(1-min(t/0.55\\,1))", color=OR, font=FP,
          alpha="min(t/0.3\\,1)") + "," +
     draw(T_24H, 72, "h*0.46", color=BL,
          alpha="min((t-0.45)/0.35\\,1)") + "," +
     draw(T_PAIEMENT, 58, "h*0.57", color=BL,
          alpha="min((t-0.8)/0.35\\,1)") + "," +
     draw(T_CTA, 64, "h*0.70+40*(1-min((t-1.15)/0.4\\,1))", color=OR, box=BL,
          alpha="min((t-1.15)/0.3\\,1)") + "[v]")
plans.append(run("p7", ins, c))

# ASSEMBLAGE — 6 transitions toutes différentes.
transitions = ["slideleft", "slideright", "wipeup", "circleopen", "dissolve", "wiperight"]
cmd = ["ffmpeg", "-y", "-loglevel", "error"]
for p in plans:
    cmd += ["-i", p]
offset = D - 0.45
chain = ""
base = "[0:v]"
for i in range(1, 7):
    chain += "%s[%d:v]xfade=transition=%s:duration=0.45:offset=%.2f[x%d];" % (
        base, i, transitions[i - 1], offset * i, i)
    base = "[x%d]" % i
chain = chain.rstrip(";")
chain += ";" + base + "format=yuv420p[out]"
cmd += ["-filter_complex", chain, "-map", "[out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-movflags", "+faststart", FINAL]
subprocess.run(cmd, check=True)
print("VIDEO FINALE:", FINAL, flush=True)
