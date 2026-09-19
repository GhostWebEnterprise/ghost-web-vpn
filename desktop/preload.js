const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("ghostVPN", {
  connect: (cfg) => ipcRenderer.invoke("vpn:connect", cfg),
  disconnect: () => ipcRenderer.invoke("vpn:disconnect"),
  status: () => ipcRenderer.invoke("vpn:status")
});
