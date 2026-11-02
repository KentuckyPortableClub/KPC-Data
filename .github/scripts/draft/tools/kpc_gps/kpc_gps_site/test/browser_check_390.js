// Phone-width check for demo.html: headless Chrome, 390 x 844 mobile emulation (Chrome DevTools Protocol),
// prints the layout line (sideways=NO is the pass), clicks three downloads, saves a screenshot.
// Needs Node 22+ (global fetch + WebSocket) and google-chrome (or set CHROME=/path/to/chrome).
// Usage: node test/browser_check_390.js      -> files in test/browser_out/
// This is Chrome's phone emulation, NOT a real iPhone or Android phone.
const cp = require("child_process"), fs = require("fs"), path = require("path"), os = require("os");
const root = path.resolve(__dirname, ".."), outDir = path.join(__dirname, "browser_out");
fs.mkdirSync(outDir, { recursive: true });
const prof = fs.mkdtempSync(path.join(os.tmpdir(), "kpcgps-chrome-"));
const port = 9333 + Math.floor(Math.random() * 500);
const ch = cp.spawn(process.env.CHROME || "google-chrome", ["--headless=new", "--no-sandbox", "--disable-gpu", "--remote-debugging-port=" + port, "--user-data-dir=" + prof, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const done = code => { try { ch.kill(); } catch (e) {} setTimeout(() => { fs.rmSync(prof, { recursive: true, force: true }); process.exit(code); }, 300); };
(async () => {
  let tabs; for (let i = 0; i < 40; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch (e) { await sleep(250); } }
  const ws = new WebSocket(tabs.find(t => t.type === "page").webSocketDebuggerUrl); let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; } };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async x => (await send("Runtime.evaluate", { expression: x })).result.result.value;
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });
  await send("Emulation.setTouchEmulationEnabled", { enabled: true });
  await send("Page.enable");
  await send("Page.navigate", { url: "file://" + path.join(root, "demo.html") + "?check=1" });
  await sleep(1500);
  await send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: outDir });
  await ev("document.querySelectorAll('.kpcgps-btn')[0].click(); document.querySelectorAll('.kpcgps-fers')[0].click(); document.querySelectorAll('[data-f=gpx]')[0].click(); document.querySelectorAll('[data-f=kml]')[2].click(); document.querySelectorAll('[data-f=gpx]')[3].click();");
  await sleep(2500);
  console.log("messages:", await ev("[...document.querySelectorAll('.kpcgps-msg')].map(e=>e.textContent).filter(Boolean).join(' | ')"));
  const layout = await ev("document.getElementById('layout').textContent");
  console.log(layout);
  const s = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: 390, height: 1100, scale: 1 } });
  fs.writeFileSync(path.join(outDir, "shot390.png"), Buffer.from(s.result.data, "base64"));
  console.log("downloads:", fs.readdirSync(outDir).filter(f => !f.endsWith(".png")).join(", "));
  ws.close(); done(/sideways=NO/.test(layout) ? 0 : 1);
})().catch(e => { console.log("ERR", e); done(1); });
