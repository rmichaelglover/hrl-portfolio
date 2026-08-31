/* Calabi–Yau Vane: dependency-free classical-AI × online-learning MIDI engine. */
(() => {
  "use strict";

  const configurations = [
    {name: "orbital", scale: [0, 2, 4, 7, 9], intervals: [0, 5, 7], bpm: 92},
    {name: "respirating", scale: [0, 2, 3, 5, 7, 9, 10], intervals: [0, 3, 7], bpm: 76},
    {name: "geomagnetic", scale: [0, 1, 4, 6, 7, 10], intervals: [0, 6, 7], bpm: 108}
  ];
  const learned = new Float32Array(12).fill(0.5);
  let configIndex = 0, playing = false, timer = 0, previous = 60, audio;
  const history = [];

  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
  const currentState = () => window.vaneState ? window.vaneState() :
    ({rotation: 0, wind: 0, weatherMode: 0, dmMode: 0, breath: 0, available: 4, tick: 0});

  // Classical AI: interpretable compatibility constraints over note candidates.
  function ruleSupport(note, state, cfg) {
    const pc = note % 12;
    const scale = cfg.scale.includes(pc) ? 1.4 : -1.8;
    const gesture = cfg.scale[(Math.floor(state.tick / 90) + state.weatherMode + state.dmMode) % cfg.scale.length];
    const movement = pc === gesture ? 2.2 : 0;
    const motion = -Math.abs(note - previous) * 0.025;
    const targetInterval = cfg.intervals[(state.weatherMode + state.dmMode) % cfg.intervals.length];
    const interval = Math.abs(note - previous) % 12;
    const geometry = interval === targetInterval ? 0.9 : 0;
    const compass = 0.28 * Math.cos((pc / 12) * Math.PI * 2 - state.wind);
    return scale + movement + motion + geometry + compass;
  }

  // Online learner: a bounded preference trace, updated only from visited states.
  function learn(note, state) {
    const pc = note % 12;
    const reward = clamp(0.5 + 0.18 * state.breath + 0.04 * state.available, 0, 1);
    learned[pc] += 0.08 * (reward - learned[pc]);
  }

  // Relaxation: local evidence and learned priors repeatedly negotiate a label.
  function chooseNote(state = currentState()) {
    const cfg = configurations[configIndex], candidates = [];
    const center = 60 + Math.round(5 * Math.sin(state.rotation) + state.dmMode * 2);
    for (let note = center - 9; note <= center + 9; note++) {
      let belief = Math.exp(ruleSupport(note, state, cfg) + learned[note % 12]);
      candidates.push({note, belief});
    }
    for (let iteration = 0; iteration < 4; iteration++) {
      const total = candidates.reduce((sum, x) => sum + x.belief, 0);
      for (const candidate of candidates) {
        const neighbor = candidates.reduce((sum, other) => {
          const interval = Math.abs(candidate.note - other.note) % 12;
          return sum + other.belief * (cfg.intervals.includes(interval) ? 0.06 : -0.008);
        }, 0) / total;
        candidate.belief *= Math.exp(neighbor);
      }
    }
    const selected = candidates.sort((a, b) => b.belief - a.belief)[0].note;
    learn(selected, state);
    previous = selected;
    return selected;
  }

  function sound(note, duration, velocity) {
    audio ||= new (window.AudioContext || window.webkitAudioContext)();
    const now = audio.currentTime, oscillator = audio.createOscillator(), gain = audio.createGain();
    oscillator.type = ["sine", "triangle", "sine"][configIndex];
    oscillator.frequency.value = 440 * 2 ** ((note - 69) / 12);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.035 * velocity / 127, now + 0.025);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    oscillator.connect(gain).connect(audio.destination);
    oscillator.start(now); oscillator.stop(now + duration + 0.02);
  }

  function step() {
    if (!playing) return;
    const state = currentState(), cfg = configurations[configIndex];
    const note = chooseNote(state), velocity = Math.round(clamp(52 + state.available * 9 + state.breath * 14, 28, 112));
    const beat = 60000 / cfg.bpm, duration = beat * (state.weatherMode === 2 ? 0.8 : 0.46) / 1000;
    sound(note, duration, velocity);
    history.push({note, velocity, ticks: state.weatherMode === 2 ? 360 : 240});
    if (history.length > 96) history.shift();
    musicReadout.textContent = `${cfg.name} · MIDI ${note} · v${velocity} · ${state.dmMode ? "H₁" : "H₀"} · learned ${learned[note % 12].toFixed(2)}`;
    timer = window.setTimeout(step, beat * (state.weatherMode === 1 ? 0.5 : 1));
  }

  function variableLength(value) {
    const bytes = [value & 127];
    while ((value >>= 7)) bytes.unshift((value & 127) | 128);
    return bytes;
  }

  function midiBytes(events) {
    const track = [0, 255, 81, 3, 7, 161, 32]; // 120 BPM; rhythm remains in event ticks.
    for (const event of events) {
      track.push(0, 144, event.note, event.velocity);
      track.push(...variableLength(event.ticks), 128, event.note, 0);
    }
    track.push(0, 255, 47, 0);
    const word = n => [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255];
    return new Uint8Array([... [..."MThd"].map(x => x.charCodeAt()), ...word(6), 0, 0, 0, 1, 1, 224,
      ...[..."MTrk"].map(x => x.charCodeAt()), ...word(track.length), ...track]);
  }

  musicPlay.onclick = () => {
    playing = !playing; musicPlay.textContent = playing ? "pause movement" : "play movement";
    if (playing) step(); else clearTimeout(timer);
  };
  musicConfig.onclick = () => {
    configIndex = (configIndex + 1) % configurations.length;
    musicConfig.textContent = `configuration: ${configurations[configIndex].name}`;
  };
  musicMidi.onclick = () => {
    if (!history.length) for (let i = 0; i < 24; i++) history.push({note: chooseNote({...currentState(), tick:i * 90}), velocity:72, ticks:240});
    const url = URL.createObjectURL(new Blob([midiBytes(history)], {type:"audio/midi"}));
    const link = Object.assign(document.createElement("a"), {href:url, download:"calabi-yau-vane-movement.mid"});
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  window.CalabiYauMusic = {configurations, learned, chooseNote, midiBytes};
})();
