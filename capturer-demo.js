// Capture de vraies portions de la démo « Le Nôtre » pour la vidéo TikTok.
const puppeteer = require('/tmp/opencode/shots/node_modules/puppeteer');
const path = require('path');

const OUT = '/root/workspace-vitrine/captures';
const URL = 'https://vitrine-express-seven.vercel.app/exemple-bar.html';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  // 540x960 en CSS avec scale 2 => images 1080x1920, exactement 9:16.
  await page.setViewport({ width: 540, height: 960, deviceScaleFactor: 2, isMobile: true });
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 90000 });
  await new Promise((r) => setTimeout(r, 1500));

  const shots = [
    ['hero', '.bar-hero'],
    ['menu', '#carte'],
    ['galerie', '#galerie'],
    ['horaires', '#infos .bar-info-card:nth-child(1)'],
    ['maps', '#infos .bar-info-card:nth-child(2)'],
    ['socials', '#infos .bar-info-card:nth-child(3)'],
    ['contact', '#contact'],
  ];

  for (const [name, selector] of shots) {
    const el = await page.$(selector);
    if (!el) { console.log('INTROUVABLE', selector); continue; }
    await el.screenshot({ path: path.join(OUT, name + '.png') });
    console.log('OK', name);
  }

  // Bulles WhatsApp en motion design, avec le contenu réel de la démo.
  const bubbles = [
    ['b1', 'La carte ?'],
    ['b2', 'Les prix ?'],
    ['b3', 'Où êtes-vous ?'],
    ['b4', 'Les horaires ?'],
  ];
  for (const [name, text] of bubbles) {
    await page.setContent(`
      <html><body style="margin:0;background:transparent;">
      <div style="font-family:Arial,sans-serif;font-size:52px;font-weight:700;color:#F8F5F0;
                  background:#351515;border:3px solid #A86A08;border-radius:36px;
                  padding:26px 42px;display:inline-block;box-shadow:0 12px 40px rgba(0,0,0,.45);">
        ${text}
      </div></body></html>`);
    await page.screenshot({ path: path.join(OUT, name + '.png'), omitBackground: true });
    console.log('OK', name);
  }

  await browser.close();
  console.log('TERMINE');
})().catch((e) => { console.error('ERREUR', e.message); process.exit(1); });
