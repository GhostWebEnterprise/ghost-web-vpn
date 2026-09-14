#!/usr/bin/env node
/**
 * Generates legacy (pre-API-26) launcher PNG icons for the Ghost Web VPN
 * Android app. Zero dependencies: renders the ghost glyph with per-pixel
 * supersampling and encodes PNGs with zlib from Node's standard library.
 *
 * Usage: node android/scripts/make-android-icons.mjs
 */
import { deflateSync } from "node:zlib";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "app", "src", "main", "res");

const DENSITIES = {
  "mipmap-mdpi": 48,
  "mipmap-hdpi": 72,
  "mipmap-xhdpi": 96,
  "mipmap-xxhdpi": 144,
  "mipmap-xxxhdpi": 192,
};

// Brand palette (matches res/values/colors.xml)
const BG = [13, 17, 23]; // #0D1117
const GHOST = [103, 232, 162]; // #67E8A2
const EYE = [13, 17, 23]; // #0D1117

/** Is this viewport point inside the ghost body? */
function insideGhost(x, y) {
  // Body: rounded-top arch from y=3 down, wavy skirt bottom to y=20, x=5..19
  if (y < 3 || y > 20 || x < 5 || x > 19) return false;
  if (y <= 10) {
    // Arch: circle of radius 7 centered at (12,10)
    const dx = x - 12;
    const dy = y - 10;
    return dx * dx + dy * dy <= 49;
  }
  // Skirt with a scalloped hem: 6 scallops across the 14-unit width,
  // alternating deep (y=20) and shallow (y=17.8) hems.
  const scallop = Math.floor((x - 5) / 2.3333);
  const hem = scallop % 2 === 0 ? 20 : 17.8;
  return y <= hem;
}

/** Eyes at (9.2,10.5) and (14.8,10.5), radius 1.2 (viewport units). */
function insideEye(x, y) {
  for (const cx of [9.2, 14.8]) {
    const dx = x - cx;
    const dy = y - 10.5;
    if (dx * dx + dy * dy <= 1.44) return true;
  }
  return false;
}

/** Render one PNG at the given square size using NxN supersampling. */
function render(size, samples = 4) {
  // Viewport is 24x24 units (icon drawn in the middle 20 of 108 -> scaled)
  const VIEW = 24;
  const px = new Uint8Array(size * size * 4);
  for (let py = 0; py < size; py++) {
    for (let x = 0; x < size; x++) {
      let ghostHits = 0;
      let eyeHits = 0;
      for (let sy = 0; sy < samples; sy++) {
        for (let sx = 0; sx < samples; sx++) {
          const vx = ((x + (sx + 0.5) / samples) / size) * VIEW;
          const vy = ((py + (sy + 0.5) / samples) / size) * VIEW;
          if (insideGhost(vx, vy)) {
            ghostHits++;
            if (insideEye(vx, vy)) eyeHits++;
          }
        }
      }
      const total = samples * samples;
      const idx = (py * size + x) * 4;
      let r = BG[0], g = BG[1], b = BG[2];
      if (ghostHits > 0) {
        const ghostAlpha = ghostHits / total;
        const eyeAlpha = eyeHits / total;
        const solidAlpha = Math.max(ghostAlpha - eyeAlpha, 0);
        // Blend: bg -> ghost color by solidAlpha, then ghost -> eye by eye portion
        r = Math.round(BG[0] + (GHOST[0] - BG[0]) * solidAlpha + (EYE[0] - GHOST[0]) * (eyeAlpha / Math.max(ghostAlpha, 1e-9)) * ghostAlpha);
        g = Math.round(BG[1] + (GHOST[1] - BG[1]) * solidAlpha + (EYE[1] - GHOST[1]) * (eyeAlpha / Math.max(ghostAlpha, 1e-9)) * ghostAlpha);
        b = Math.round(BG[2] + (GHOST[2] - BG[2]) * solidAlpha + (EYE[2] - GHOST[2]) * (eyeAlpha / Math.max(ghostAlpha, 1e-9)) * ghostAlpha);
      }
      px[idx] = r;
      px[idx + 1] = g;
      px[idx + 2] = b;
      px[idx + 3] = 255;
    }
  }
  return encodePng(px, size, size);
}

/** Minimal PNG encoder: 8-bit RGBA, no filtering, single IDAT. */
function encodePng(rgba, width, height) {
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (width * 4 + 1)] = 0; // filter: none
    Buffer.from(rgba.buffer, y * width * 4, width * 4).copy(raw, y * (width * 4 + 1) + 1);
  }
  const chunks = [];
  chunks.push(signature());
  chunks.push(chunk("IHDR", ihdr(width, height)));
  chunks.push(chunk("IDAT", deflateSync(raw, { level: 9 })));
  chunks.push(chunk("IEND", Buffer.alloc(0)));
  return Buffer.concat(chunks);
}

function signature() {
  return Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
}

function ihdr(width, height) {
  const buf = Buffer.alloc(13);
  buf.writeUInt32BE(width, 0);
  buf.writeUInt32BE(height, 4);
  buf[8] = 8; // bit depth
  buf[9] = 6; // color type RGBA
  buf[10] = 0; // compression
  buf[11] = 0; // filter
  buf[12] = 0; // interlace
  return buf;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeBuf = Buffer.from(type, "ascii");
  const crcInput = Buffer.concat([typeBuf, data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(crcInput) >>> 0, 0);
  return Buffer.concat([len, typeBuf, data, crc]);
}

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return c ^ 0xffffffff;
}

for (const [dir, size] of Object.entries(DENSITIES)) {
  const outDir = join(outRoot, dir);
  mkdirSync(outDir, { recursive: true });
  const png = render(size);
  writeFileSync(join(outDir, "ic_launcher.png"), png);
  console.log(`wrote ${join(dir, "ic_launcher.png")} (${size}x${size})`);
}
console.log("done");
