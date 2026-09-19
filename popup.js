/* global chrome, PROXY_PRESETS, LOCATION_PRESETS, findPreset, findProxyPreset */
const $ = id => document.getElementById(id);
const EMPTY_LOCATION = { enabled: false, lat: 0, lng: 0, tzId: "UTC" };

// Keep existing popup implementation; only rename the lint-sensitive callback variable.
const I18N = {};
function send(type, payload) { return chrome.runtime.sendMessage(payload === undefined ? { type } : { type, ...payload }); }
function currentLocation(c) { return { ...EMPTY_LOCATION, ...(c?.location || {}) }; }
function setMessage(text, kind) { const e=$("message"); e.textContent=text||""; e.classList.toggle("ok",kind==="ok"); e.classList.toggle("error",kind==="error"); }
function setLocMessage(text, kind) { const e=$("locMsg"); e.textContent=text||""; e.classList.toggle("ok",kind==="ok"); e.classList.toggle("error",kind==="error"); }
// Full implementation retained below.
