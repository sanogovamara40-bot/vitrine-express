#!/usr/bin/env bash
# Génère 2 vidéos verticales 9:16 pour TikTok à partir des photos du bar.
# Reproductible : bash generer-videos.sh
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p videos texts
FPLAY=/root/workspace-vitrine/fonts/playfair-700.ttf
FKARLA=/root/workspace-vitrine/fonts/karla-700.ttf

# Fichiers texte (sans apostrophe dans le nom pour éviter les soucis d'échappement ffmpeg)
printf 'LE NÔTRE' > texts/titre.txt
printf 'Le bon endroit,' > texts/ligne1.txt
printf 'à la tombée du jour.' > texts/ligne2.txt
printf 'Une carte généreuse, faite maison' > texts/carte.txt
printf 'Cocktails, bissap et bonne ambiance' > texts/cocktail.txt
printf 'Cocody, Abidjan' > texts/lieu.txt
printf 'Réservez sur WhatsApp' > texts/reserver.txt
printf 'Votre restaurant mérite un site' > texts/pub1.txt
printf 'Site pro en 24h - 25.000 FCFA' > texts/pub2.txt
printf 'Wave / Orange Money - pas de carte' > texts/pub3.txt
printf 'Écrivez-nous sur WhatsApp' > texts/pub4.txt

# --- Helper : un plan fixe de 5s avec zoom lent + texte ---
clip() {
  local img="$1"; shift
  local filters="$1"; shift
  ffmpeg -loglevel error -y -loop 1 -framerate 25 -t 5 -i "$img" -vf "$filters" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$@"
}

txt() { # textfile font size y box
  printf "drawtext=fontfile=%s:textfile=%s:fontsize=%s:fontcolor=white:box=1:boxcolor=black@0.35:boxborderw=18:shadowcolor=black@0.9:shadowx=2:shadowy=2:x=(w-text_w)/2:y=%s" "$1" "$2" "$3" "$4"
}

zoombase() {
  printf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(1+on*0.0005,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=25,setsar=1"
}

echo ">> Generation video 1/2 : Le Nôtre (ambiance)"
C1="$(zoombase),$(txt "$FKARLA" texts/titre.txt 40 'h*0.18'),$(txt "$FKARLA" texts/ligne1.txt 72 'h*0.38'),$(txt "$FKARLA" texts/ligne2.txt 72 'h*0.48')"
C2="$(zoombase),$(txt "$FKARLA" texts/carte.txt 60 'h*0.55')"
C3="$(zoombase),$(txt "$FKARLA" texts/cocktail.txt 60 'h*0.55')"
C4="$(zoombase),$(txt "$FKARLA" texts/lieu.txt 56 'h*0.40'),$(txt "$FKARLA" texts/reserver.txt 52 'h*0.62')"

ffmpeg -loglevel error -y \
  -loop 1 -framerate 25 -t 5 -i photos/salle.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/plat.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/cocktail.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/dessert.jpg \
  -filter_complex "
    [0:v]${C1}[v0];
    [1:v]${C2}[v1];
    [2:v]${C3}[v2];
    [3:v]${C4}[v3];
    [v0][v1]xfade=transition=fade:duration=0.6:offset=4.4[x1];
    [x1][v2]xfade=transition=fade:duration=0.6:offset=8.8[x2];
    [x2][v3]xfade=transition=fade:duration=0.6:offset=13.2[out]
  " -map '[out]' -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -movflags +faststart videos/tiktok-le-notre.mp4

echo ">> Generation video 2/2 : publicite VitrineExpress"
P1="$(zoombase),$(txt "$FKARLA" texts/pub1.txt 64 'h*0.42')"
P2="$(zoombase),$(txt "$FKARLA" texts/pub2.txt 60 'h*0.45')"
P3="$(zoombase),$(txt "$FKARLA" texts/pub3.txt 52 'h*0.45')"
P4="$(zoombase),$(txt "$FKARLA" texts/pub4.txt 64 'h*0.45'),$(txt "$FKARLA" texts/reserver.txt 44 'h*0.62')"

ffmpeg -loglevel error -y \
  -loop 1 -framerate 25 -t 5 -i photos/salle.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/plat.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/cocktail.jpg \
  -loop 1 -framerate 25 -t 5 -i photos/dessert.jpg \
  -filter_complex "
    [0:v]${P1}[v0];
    [1:v]${P2}[v1];
    [2:v]${P3}[v2];
    [3:v]${P4}[v3];
    [v0][v1]xfade=transition=fade:duration=0.6:offset=4.4[x1];
    [x1][v2]xfade=transition=fade:duration=0.6:offset=8.8[x2];
    [x2][v3]xfade=transition=fade:duration=0.6:offset=13.2[out]
  " -map '[out]' -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -movflags +faststart videos/tiktok-vitrineexpress-pub.mp4

echo ">> Termine"
ls -lh videos/
