#!/usr/bin/env python3
"""Générateur de 10 variantes TikTok — motion design optimisé.

Principes appliqués :
  - Accroche visible dès la 1re seconde (hook).
  - Texte animé : fondu + léger glissement vers le haut.
  - 4 mouvements caméra distincts (zoom in, zoom out, pan gauche, pan droite).
  - Fondus croisés 0,5 s entre les plans.
  - Zone sûre TikTok respectée (texte centré, hors bas de l'écran).
  - Aucune piste audio : le son tendance s'ajoute dans l'app TikTok.
"""
import os
import subprocess
import sys

DEBUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
FIN = int(sys.argv[2]) if len(sys.argv) > 2 else 10

BASE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(BASE, "photos")
TMP = os.path.join(BASE, "texts-variantes")
OUT = os.path.join(BASE, "videos", "variantes")
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

FONT = os.path.join(BASE, "fonts", "karla-700.ttf")
W, H, FPS, DUR = 1080, 1920, 25, 4.5
N = int(FPS * DUR)
PHOTO_FILES = ["salle.jpg", "plat.jpg", "cocktail.jpg", "dessert.jpg"]

# (expression z, expression x, expression y)
MOUVEMENTS = [
    ("min(1+on*0.0012\\,1.14)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("max(1.14-on*0.0012\\,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("1.12", "(iw-iw/zoom)*(1-on/%d)" % N, "ih/2-(ih/zoom/2)"),
    ("1.12", "(iw-iw/zoom)*(on/%d)" % N, "ih/2-(ih/zoom/2)"),
]

VARIANTES = [
    ["Votre maquis est invisible sur Google ?", "Le bon endroit, à la tombée du jour.", "Site pro en 24h — 25.000 FCFA", "Cocody, Abidjan 🇨🇮"],
    ["Combien de clients passent devant vous ?", "Une carte généreuse, faite maison", "Site pro en 24h — 25.000 FCFA", "Wave / Orange Money — pas de carte"],
    ["Un site web pour 25.000 FCFA ?", "Cocktails, bissap, bonne ambiance", "Réservez sur WhatsApp", "Cocody, Abidjan 🇨🇮"],
    ["Votre restaurant mérite mieux qu'une page Facebook", "Le bon endroit, à la tombée du jour.", "Site pro en 24h — 25.000 FCFA", "Écrivez-nous sur WhatsApp"],
    ["Les clients cherchent. Vous n'êtes pas là.", "Une carte généreuse, faite maison", "25.000 FCFA — Wave / Orange Money", "Cocody, Plateau 🇨🇮"],
    ["Cocody, Plateau : votre site en 24h", "Cocktails, bissap, bonne ambiance", "Le bon endroit, à la tombée du jour.", "Réservez sur WhatsApp"],
    ["Arrêtez de perdre des réservations", "Le bon endroit, à la tombée du jour.", "Site pro en 24h — 25.000 FCFA", "Wave / Orange Money"],
    ["Wave ou Orange Money. Pas de carte.", "Une carte généreuse, faite maison", "Site pro en 24h — 25.000 FCFA", "Cocody, Abidjan 🇨🇮"],
    ["Votre carte, vos horaires, votre WhatsApp", "Cocktails, bissap, bonne ambiance", "Le bon endroit, à la tombée du jour.", "Écrivez-nous sur WhatsApp"],
    ["Le Nôtre a son site. Et le vôtre ?", "Le bon endroit, à la tombée du jour.", "Site pro en 24h — 25.000 FCFA", "Cocody, Abidjan 🇨🇮"],
]


def texte_filtre(path, size=62):
    """Fondu entrée/sortie + glissement vers le haut, centré horizontalement."""
    alpha = "if(lt(t\\,0.4)\\,t/0.4\\,if(gt(t\\,4.05)\\,(4.5-t)/0.45\\,1))"
    y = "h*0.46+(1-min(t/0.4\\,1))*24"
    return (
        "drawtext=fontfile=%s:textfile=%s:fontsize=%d:fontcolor=white:"
        "box=1:boxcolor=black@0.42:boxborderw=20:"
        "shadowcolor=black@0.9:shadowx=3:shadowy=3:"
        "x=(w-text_w)/2:y=%s:alpha='%s'"
    ) % (FONT, path, size, y, alpha)


def clip_filtre(photo_idx, text_path, mouvement_idx, size=62):
    z, x, y = MOUVEMENTS[mouvement_idx % len(MOUVEMENTS)]
    zoom = (
        "scale=%d:%d:force_original_aspect_ratio=increase,"
        "crop=%d:%d,"
        "zoompan=z='%s':x='%s':y='%s':d=1:s=%dx%d:fps=%d,setsar=1"
    ) % (W, H, W, H, z, x, y, W, H, FPS)
    return zoom + "," + texte_filtre(text_path, size)


for i in range(DEBUT - 1, FIN):
    lignes = VARIANTES[i]
    num = i + 1
    print(">> Variante %02d/10" % num, flush=True)
    chemins = []
    for j, ligne in enumerate(lignes):
        p = os.path.join(TMP, "v%02d_%d.txt" % (num, j))
        with open(p, "w", encoding="utf-8") as f:
            f.write(ligne)
        chemins.append(p)

    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for photo in PHOTO_FILES:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(DUR),
                "-i", os.path.join(PHOTOS, photo)]

    chain = []
    for j in range(4):
        size = 58 if len(lignes[j]) > 38 else 64
        chain.append("[%d:v]%s[v%d]" % (
            j, clip_filtre(j, chemins[j], num + j, size), j))

    # Fondus croisés : chaque transition commence 0,5 s avant la fin du plan.
    offset = DUR - 0.5
    chain.append("[v0][v1]xfade=transition=fade:duration=0.5:offset=%.2f[x1]" % offset)
    chain.append("[x1][v2]xfade=transition=fade:duration=0.5:offset=%.2f[x2]" % (offset * 2))
    chain.append("[x2][v3]xfade=transition=fade:duration=0.5:offset=%.2f[out]" % (offset * 3))
    cmd += ["-filter_complex", ";".join(chain), "-map", "[out]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            os.path.join(OUT, "v%02d.mp4" % num)]
    subprocess.run(cmd, check=True)

print(">> Terminé : 10 variantes dans", OUT)
