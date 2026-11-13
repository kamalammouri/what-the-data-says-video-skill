// Read-only reader for YouTube Studio in the Chrome opened by browser.mjs (CDP 9222): opens a URL in the Studio tab, waits, prints the visible text.
//   node studio.mjs <url> [waitMs] [screenshot.png]      Never clicks Save / Publish / Delete: navigation and reading only.
import { createRequire } from 'node:module';
import path from 'node:path';
const { chromium } = createRequire(path.join(process.env.PLAYWRIGHT_DIR, 'package.json'))('playwright');
const [url, wait = '9000', shot] = process.argv.slice(2);
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222', { timeout: 5000 });
const ctx = browser.contexts()[0];
const page = ctx.pages().find(p => /studio\.youtube\.com/.test(p.url())) || await ctx.newPage();
if (url) await page.goto(url, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(Number(wait));
if (shot) await page.screenshot({ path: shot });
const text = await page.evaluate(() => (document.querySelector('ytcp-app, body')?.innerText || '').replace(/\n{2,}/g, '\n'));
console.log(page.url() + '\n' + text);
process.exit(0);
