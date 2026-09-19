const { app, BrowserWindow, ipcMain, session } = require("electron");
const path = require("path");

let win;
let connected = false;

function createWindow() {
  win = new BrowserWindow({
    width: 460,
    height: 720,
    minWidth: 400,
    minHeight: 620,
    title: "GhostWeb VPN",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  win.loadFile(path.join(__dirname, "index.html"));
}

ipcMain.handle("vpn:connect", async (_event, cfg) => {
  const scheme = cfg.scheme || "socks5";
  const proxyRules = `${scheme}://${cfg.host}:${cfg.port}`;
  await session.defaultSession.setProxy({ proxyRules, proxyBypassRules: cfg.bypass || "<-loopback>" });
  connected = true;
  return { connected, endpoint: proxyRules };
});

ipcMain.handle("vpn:disconnect", async () => {
  await session.defaultSession.setProxy({ mode: "direct" });
  connected = false;
  return { connected };
});

ipcMain.handle("vpn:status", async () => ({ connected }));

app.whenReady().then(createWindow);
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
