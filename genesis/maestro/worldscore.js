/*
 * WorldScore — the voxel world, sung.
 *
 * A zero-dependency Web Audio sonifier for a Maestro frame. It does NOT play the
 * moves; it plays the *terrain* — the same relaxation-labeling influence field the
 * renderer draws as elevation and water. What you see is what you hear:
 *
 *   contested seam (water)  → the pad.  A lone pond is a thin high shimmer; a
 *                             sprawling ocean is a low, wide, detuned drone.
 *                             Sized by connected-component area via Maestro.waterBodies().
 *   land elevation          → the pluck. The highest held peak picks the melody note.
 *   coherence               → brightness. Coherence is 1 − normalised entropy of the
 *                             role distribution: a clear plan opens the filter and
 *                             tightens the detune; chaos closes it down and lets the
 *                             oscillators beat against each other.
 *   material advantage      → the third. Ahead is major, behind is minor, level is sus.
 *   who holds the board     → the stereo field. White-held squares pull left, black
 *                             right, so a one-sided position is audibly lopsided.
 *   captures                → percussion.
 *
 * Runs in the browser and renders offline (OfflineAudioContext) so the score can be
 * regression-tested without a speaker — see test/worldscore.assert.js.
 *
 * By Manny Glover.
 */
(function (root) {
  "use strict";

  /* ---------- musical vocabulary ---------- */
  var AEOLIAN = [0, 2, 3, 5, 7, 8, 10];   // behind / level: minor colour
  var IONIAN  = [0, 2, 4, 5, 7, 9, 11];   // ahead: major colour
  var VALUE   = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };

  // A lone contested square is a pond; a sprawl is an ocean. Bigger water sits
  // lower and wider, because that is what big water sounds like.
  var WATER_VOICE = {
    pond:  { oct: 1, spread: 2,  gain: 0.055 },
    creek: { oct: 1, spread: 3,  gain: 0.060 },
    river: { oct: 0, spread: 5,  gain: 0.070 },
    lake:  { oct: 0, spread: 7,  gain: 0.080 },
    sea:   { oct: -1, spread: 9, gain: 0.090 },
    ocean: { oct: -1, spread: 12, gain: 0.100 }
  };

  var mtof = function (m) { return 440 * Math.pow(2, (m - 69) / 12); };
  var clamp = function (v, a, b) { return v < a ? a : (v > b ? b : v); };

  /* ---------- read the world ---------- */
  /* Everything the score needs, derived from one frame. Pure — no audio here,
     which is what makes it testable on its own. */
  function readWorld(frame, Maestro) {
    var inf = frame.influence, roles = frame.roles || [];

    // water: kind of the largest contested body, and how much of the board is wet
    var kinds = {}, wet = 0, i;
    if (Maestro && Maestro.waterBodies) {
      // waterBodies() returns a flat 64-entry array of kind strings ("" where dry)
      var wb = Maestro.waterBodies(inf);
      for (i = 0; i < 64; i++) {
        var e = wb[i], k = (typeof e === "string") ? e : (e && e.kind);
        if (k) { kinds[k] = (kinds[k] || 0) + 1; wet++; }
      }
    }
    if (!wet) { for (i = 0; i < 64; i++) if (inf[i].water) wet++; if (wet) kinds[wet > 12 ? "lake" : "pond"] = wet; }
    var order = ["ocean", "sea", "lake", "river", "creek", "pond"], biggest = "pond";
    for (i = 0; i < order.length; i++) if (kinds[order[i]]) { biggest = order[i]; break; }

    // land: the highest held elevation, and which side holds more board
    var peak = 0, w = 0, b = 0;
    for (i = 0; i < 64; i++) {
      var c = inf[i];
      if (typeof c.height === "number" && c.height > peak) peak = c.height;
      if (c.terrain === "white") w++; else if (c.terrain === "black") b++;
    }

    // coherence = 1 − normalised entropy of the role distribution.
    // One role dominating = a clear plan. Roles spread evenly = noise.
    var counts = {}, n = 0;
    for (i = 0; i < roles.length; i++) { counts[roles[i].role] = (counts[roles[i].role] || 0) + 1; n++; }
    var keys = Object.keys(counts), H = 0;
    for (i = 0; i < keys.length; i++) { var p = counts[keys[i]] / n; if (p > 0) H -= p * Math.log(p); }
    var Hmax = keys.length > 1 ? Math.log(keys.length) : 1;
    var coherence = n ? clamp(1 - H / Hmax, 0, 1) : 0.5;

    // material, from the pieces still labelled
    var mw = 0, mb = 0;
    for (i = 0; i < roles.length; i++) {
      var v = VALUE[roles[i].type] || 0;
      if (roles[i].color === "w") mw += v; else mb += v;
    }

    var noisy = (counts.noise || 0) / Math.max(1, n);

    // Raw coherence over a real game only spans ~0.00–0.35, and peak elevation only
    // 2–4, so mapping either straight onto a filter or a scale degree barely moves.
    // These are the same quantities stretched over the range they actually occupy
    // (measured across the games in the corpus) — the raw values are kept for display.
    var bright  = clamp((coherence - 0.03) / 0.28, 0, 1);
    var settled = clamp(1 - (noisy - 0.15) / 0.42, 0, 1);

    return {
      water: biggest, wetness: wet / 64, peak: peak,
      balance: (w - b) / Math.max(1, w + b),      // −1 black owns it … +1 white owns it
      coherence: coherence, advantage: mw - mb, noisy: noisy,
      bright: bright, settled: settled
    };
  }

  /* ---------- the instrument ---------- */
  function WorldScore(ctx, opts) {
    opts = opts || {};
    this.ctx = ctx;
    this.root = (typeof opts.root === "number") ? opts.root : 50;   // D3
    this.hero = opts.hero === "b" ? -1 : 1;    // flip the stereo field for a black hero
    this.gain = (typeof opts.gain === "number") ? opts.gain : 1;

    var master = ctx.createGain(); master.gain.value = 0.85 * this.gain;
    var comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -18; comp.ratio.value = 4; comp.attack.value = 0.004; comp.release.value = 0.25;
    master.connect(comp); comp.connect(ctx.destination);

    // A small synthesised room. No asset, no fetch — just decaying noise.
    var conv = ctx.createConvolver(), sr = ctx.sampleRate, len = Math.floor(sr * 1.9);
    var ir = ctx.createBuffer(2, len, sr);
    for (var ch = 0; ch < 2; ch++) {
      var d = ir.getChannelData(ch);
      for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6);
    }
    conv.buffer = ir;
    var wet = ctx.createGain(); wet.gain.value = 0.30;
    conv.connect(wet); wet.connect(master);

    // percussion noise, generated once
    var nlen = Math.floor(sr * 0.25), nb = ctx.createBuffer(1, nlen, sr), nd = nb.getChannelData(0);
    for (var j = 0; j < nlen; j++) nd[j] = Math.random() * 2 - 1;

    this.master = master; this.revIn = conv; this.noise = nb;
    this.voices = [];
  }

  WorldScore.prototype._pan = function (x) {
    var ctx = this.ctx;
    if (ctx.createStereoPanner) { var p = ctx.createStereoPanner(); p.pan.value = clamp(x, -1, 1); return p; }
    var pn = ctx.createPanner(); pn.panningModel = "equalpower";
    pn.setPosition(clamp(x, -1, 1), 0, 1 - Math.abs(clamp(x, -1, 1)) * 0.4);
    return pn;
  };

  /* The contested seam, held. Bigger water → lower, wider, more voices. */
  WorldScore.prototype.pad = function (w, t, dur) {
    var ctx = this.ctx, v = WATER_VOICE[w.water] || WATER_VOICE.pond;
    var scale = w.advantage > 1 ? IONIAN : AEOLIAN;
    var third = Math.abs(w.advantage) <= 1 ? 5 : scale[2];   // level board → sus4
    var notes = [this.root + 12 * v.oct, this.root + 12 * v.oct + third, this.root + 12 * v.oct + 7];

    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v.gain * (0.55 + w.wetness), t + dur * 0.35);
    g.gain.linearRampToValueAtTime(0.0001, t + dur);

    var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.Q.value = 0.7;
    // coherence opens the filter: a clear plan is bright, chaos is muffled
    lp.frequency.setValueAtTime(420 + 2600 * w.bright, t);

    var pan = this._pan(w.balance * 0.55 * this.hero);
    g.connect(lp); lp.connect(pan); pan.connect(this.master);
    var send = ctx.createGain(); send.gain.value = 0.4; pan.connect(send); send.connect(this.revIn);

    // and it tightens the tuning: incoherent positions beat against themselves
    var det = v.spread * (1.5 - w.bright);
    for (var n = 0; n < notes.length; n++) {
      for (var s = -1; s <= 1; s += 2) {
        var o = ctx.createOscillator(); o.type = "sawtooth";
        o.frequency.value = mtof(notes[n]); o.detune.value = s * det;
        o.connect(g); o.start(t); o.stop(t + dur + 0.05);
        this.voices.push(o);
      }
    }
  };

  /* The highest land the position holds. */
  WorldScore.prototype.pluck = function (w, t) {
    var ctx = this.ctx;
    var scale = w.advantage > 1 ? IONIAN : AEOLIAN;
    // peak alone spans only 2–4; fold in how settled the roles are so the
    // melody actually walks the scale instead of hovering on one note.
    var deg = Math.round(clamp((w.peak - 2) * 1.5 + w.settled * 4, 0, 9));
    var m = this.root + 12 + scale[deg % 7] + 12 * Math.floor(deg / 7);
    var f = mtof(m);
    var o = ctx.createOscillator(), o2 = ctx.createOscillator();
    o.type = "triangle"; o2.type = "sine";
    o.frequency.setValueAtTime(f * 0.993, t); o.frequency.setTargetAtTime(f, t, 0.03);
    o2.frequency.value = f * 2;
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(0.16, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 1.0);
    var lp = ctx.createBiquadFilter(); lp.type = "lowpass";
    lp.frequency.value = 1200 + 2400 * w.bright;
    var pan = this._pan(-w.balance * 0.7 * this.hero);
    o.connect(lp); o2.connect(lp); lp.connect(g); g.connect(pan); pan.connect(this.master);
    var send = ctx.createGain(); send.gain.value = 0.55; g.connect(send); send.connect(this.revIn);
    o.start(t); o2.start(t); o.stop(t + 1.1); o2.stop(t + 1.1);
    this.voices.push(o, o2);
  };

  WorldScore.prototype.bass = function (w, t, dur) {
    var ctx = this.ctx;
    var o = ctx.createOscillator(); o.type = "triangle";
    o.frequency.value = mtof(this.root - 12);
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(0.20, t + 0.03);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 380;
    o.connect(lp); lp.connect(g); g.connect(this.master);
    o.start(t); o.stop(t + dur + 0.05);
    this.voices.push(o);
  };

  /* Something was taken. */
  WorldScore.prototype.strike = function (t, hard) {
    var ctx = this.ctx;
    var s = ctx.createBufferSource(); s.buffer = this.noise;
    var f = ctx.createBiquadFilter();
    f.type = hard ? "bandpass" : "highpass";
    f.frequency.value = hard ? 900 : 6200; f.Q.value = hard ? 1.4 : 0.7;
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(hard ? 0.14 : 0.035, t + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, t + (hard ? 0.42 : 0.10));
    s.connect(f); f.connect(g); g.connect(this.master);
    var send = ctx.createGain(); send.gain.value = 0.3; g.connect(send); send.connect(this.revIn);
    s.start(t); s.stop(t + 0.5);
  };

  /* One frame of world → one bar of sound. */
  WorldScore.prototype.frame = function (frame, Maestro, o) {
    o = o || {};
    var t = (typeof o.at === "number") ? o.at : this.ctx.currentTime + 0.02;
    var dur = o.dur || 1.6;
    var w = readWorld(frame, Maestro);
    this.pad(w, t, dur);
    this.bass(w, t, dur * 0.55);
    this.pluck(w, t + 0.06);
    if (o.capture) this.strike(t, true);
    else if (frame.san && /\+|#/.test(frame.san)) this.strike(t + 0.02, false);
    return w;
  };

  WorldScore.prototype.stop = function () {
    for (var i = 0; i < this.voices.length; i++) { try { this.voices[i].stop(); } catch (e) {} }
    this.voices.length = 0;
  };

  WorldScore.readWorld = readWorld;
  WorldScore.WATER_VOICE = WATER_VOICE;

  if (typeof module !== "undefined" && module.exports) module.exports = WorldScore;
  if (typeof window !== "undefined") window.WorldScore = WorldScore;
})(this);
