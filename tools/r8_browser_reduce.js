// r8/art batch 1: the 1x reduction used for the animation sources, run in a browser tab at the SpriteCook origin
// (SpriteCook files cannot be uploaded from the cloud workspace, so the 1x stills that the animator starts from are
// made where the source pictures are). Same steps as tools/r8lib.py: binary alpha, crop, box filter to an exact
// height (area-weighted, premultiplied alpha), median-cut palette, no lone pixels, 1 px outline in the darkest colour.
// The results were uploaded to SpriteCook, downloaded again and saved in source_sheets/r8_*_1x.png, which is what
// tools/build_r8_people.py reads.
window.R8 = (() => {
  const lum = (r, g, b) => 0.299 * r + 0.587 * g + 0.114 * b;
  async function decode(b64) {
    const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const bm = await createImageBitmap(new Blob([bin], { type: 'image/png' }), { premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
    const c = new OffscreenCanvas(bm.width, bm.height), g = c.getContext('2d');
    g.drawImage(bm, 0, 0);
    const d = g.getImageData(0, 0, bm.width, bm.height);
    return { w: bm.width, h: bm.height, d: d.data };
  }
  function binarize(im) { for (let i = 3; i < im.d.length; i += 4) im.d[i] = im.d[i] >= 128 ? 255 : 0; return im; }
  function sub(im, x0, y0, x1, y1) {
    const w = x1 - x0, h = y1 - y0, d = new Uint8ClampedArray(w * h * 4);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) for (let k = 0; k < 4; k++) d[(y * w + x) * 4 + k] = im.d[((y + y0) * im.w + x + x0) * 4 + k];
    return { w, h, d };
  }
  function bbox(im) {
    let x0 = im.w, y0 = im.h, x1 = -1, y1 = -1;
    for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) if (im.d[(y * im.w + x) * 4 + 3] > 0) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    return [x0, y0, x1 + 1, y1 + 1];
  }
  const crop = im => sub(im, ...bbox(im));
  function splitColumns(im, n) {               // the n widest runs of non-empty columns, left to right
    const col = []; for (let x = 0; x < im.w; x++) { let f = false; for (let y = 0; y < im.h && !f; y++) f = im.d[(y * im.w + x) * 4 + 3] > 0; col.push(f); }
    const runs = []; let x = 0;
    while (x < im.w) { if (col[x]) { const s = x; while (x < im.w && col[x]) x++; runs.push([s, x]); } else x++; }
    runs.sort((a, b) => (b[1] - b[0]) - (a[1] - a[0]));
    return runs.slice(0, n).sort((a, b) => a[0] - b[0]).map(([s, e]) => crop(sub(im, s, 0, e, im.h)));
  }
  function boxResize(im, W, H) {               // area-weighted average, premultiplied
    const sx = im.w / W, sy = im.h / H, d = new Uint8ClampedArray(W * H * 4);
    for (let Y = 0; Y < H; Y++) for (let X = 0; X < W; X++) {
      const fx0 = X * sx, fx1 = (X + 1) * sx, fy0 = Y * sy, fy1 = (Y + 1) * sy;
      let r = 0, g = 0, b = 0, a = 0, wt = 0;
      for (let y = Math.floor(fy0); y < Math.ceil(fy1); y++) {
        const wy = Math.min(fy1, y + 1) - Math.max(fy0, y);
        for (let x = Math.floor(fx0); x < Math.ceil(fx1); x++) {
          const wx = Math.min(fx1, x + 1) - Math.max(fx0, x), w = wx * wy, p = (y * im.w + x) * 4, al = im.d[p + 3] / 255;
          r += im.d[p] * al * w; g += im.d[p + 1] * al * w; b += im.d[p + 2] * al * w; a += al * w; wt += w;
        }
      }
      const q = (Y * W + X) * 4;
      if (a > 0) { d[q] = r / a; d[q + 1] = g / a; d[q + 2] = b / a; }
      d[q + 3] = 255 * a / wt;
    }
    return { w: W, h: H, d };
  }
  const fitHeight = (im, H) => boxResize(im, Math.max(1, Math.round(im.w * H / im.h)), H);
  function medianCut(im, n) {                  // binary alpha at 0.5, colours to n by median cut, nearest mapping
    const px = [];
    for (let i = 0; i < im.d.length; i += 4) { if (im.d[i + 3] >= 128) { im.d[i + 3] = 255; px.push([im.d[i], im.d[i + 1], im.d[i + 2]]); } else im.d[i + 3] = 0; }
    let boxes = [px];
    while (boxes.length < n) {
      let bi = -1, best = -1, ch = 0;
      boxes.forEach((b, i) => { if (b.length < 2) return; for (let c = 0; c < 3; c++) { let lo = 255, hi = 0; for (const p of b) { lo = Math.min(lo, p[c]); hi = Math.max(hi, p[c]); } if (hi - lo > best) { best = hi - lo; bi = i; ch = c; } } });
      if (bi < 0 || best <= 0) break;
      const b = boxes[bi].slice().sort((p, q) => p[ch] - q[ch]), m = b.length >> 1;
      boxes.splice(bi, 1, b.slice(0, m), b.slice(m));
    }
    const pal = boxes.map(b => { const s = [0, 0, 0]; for (const p of b) for (let c = 0; c < 3; c++) s[c] += p[c]; return s.map(v => Math.round(v / b.length)); });
    for (let i = 0; i < im.d.length; i += 4) if (im.d[i + 3]) {
      let bj = 0, bd = 1e9;
      pal.forEach((p, j) => { const dd = (p[0] - im.d[i]) ** 2 + (p[1] - im.d[i + 1]) ** 2 + (p[2] - im.d[i + 2]) ** 2; if (dd < bd) { bd = dd; bj = j; } });
      im.d[i] = pal[bj][0]; im.d[i + 1] = pal[bj][1]; im.d[i + 2] = pal[bj][2];
    }
    return im;
  }
  function despeckle(im, passes = 2) {         // a pixel with no same-colour 8-neighbour takes the commonest neighbour colour
    const key = (x, y) => (x < 0 || y < 0 || x >= im.w || y >= im.h || !im.d[(y * im.w + x) * 4 + 3]) ? -1 : (im.d[(y * im.w + x) * 4] << 16) | (im.d[(y * im.w + x) * 4 + 1] << 8) | im.d[(y * im.w + x) * 4 + 2];
    for (let p = 0; p < passes; p++) {
      const ch = [];
      for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) {
        const k = key(x, y); if (k < 0) continue;
        const nb = []; let same = false;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { if (!dx && !dy) continue; const v = key(x + dx, y + dy); if (v === k) same = true; if (v >= 0) nb.push(v); }
        if (same || nb.length < 3) continue;
        const cnt = {}; nb.forEach(v => cnt[v] = (cnt[v] || 0) + 1);
        const best = +Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a] || a - b)[0];
        ch.push([x, y, best]);
      }
      for (const [x, y, v] of ch) { const q = (y * im.w + x) * 4; im.d[q] = v >> 16 & 255; im.d[q + 1] = v >> 8 & 255; im.d[q + 2] = v & 255; }
    }
    return im;
  }
  function outline(im) {                       // silhouette (4-neighbour of transparency) in the darkest colour
    let ink = null, il = 1e9;
    for (let i = 0; i < im.d.length; i += 4) if (im.d[i + 3]) { const l = lum(im.d[i], im.d[i + 1], im.d[i + 2]); if (l < il) { il = l; ink = [im.d[i], im.d[i + 1], im.d[i + 2]]; } }
    const op = (x, y) => x >= 0 && y >= 0 && x < im.w && y < im.h && im.d[(y * im.w + x) * 4 + 3] > 0, e = [];
    for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) if (op(x, y) && !(op(x - 1, y) && op(x + 1, y) && op(x, y - 1) && op(x, y + 1))) e.push((y * im.w + x) * 4);
    for (const q of e) { im.d[q] = ink[0]; im.d[q + 1] = ink[1]; im.d[q + 2] = ink[2]; }
    return im;
  }
  function mirror(im) { const o = sub(im, 0, 0, im.w, im.h); for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) for (let k = 0; k < 4; k++) o.d[(y * im.w + x) * 4 + k] = im.d[(y * im.w + im.w - 1 - x) * 4 + k]; return o; }
  async function png(im) {
    const c = new OffscreenCanvas(im.w, im.h); c.getContext('2d').putImageData(new ImageData(im.d, im.w, im.h), 0, 0);
    return await c.convertToBlob({ type: 'image/png' });
  }
  const rider = (im, H) => outline(crop(despeckle(medianCut(fitHeight(im, H), 20))));
  return { decode, binarize, crop, splitColumns, boxResize, fitHeight, medianCut, despeckle, outline, mirror, png, rider };
})();
