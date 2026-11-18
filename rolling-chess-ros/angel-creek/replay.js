"use strict";

const byId = (id) => document.getElementById(id);
const canvas = byId("world");
const ctx = canvas.getContext("2d");
const time = byId("time");
const play = byId("play");
let rows = [];
let timer;

function dot(x, y, radius, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function label(text, x, y, color = "#d5e8d8", size = 23) {
  ctx.fillStyle = color;
  ctx.font = `${size}px system-ui`;
  ctx.fillText(text, x, y);
}

function draw(row) {
  const shade = ctx.createLinearGradient(0, 0, 1040, 460);
  shade.addColorStop(0, "#1b4140");
  shade.addColorStop(1, "#152b23");
  ctx.fillStyle = shade;
  ctx.fillRect(0, 0, 1040, 460);

  const water = ctx.createLinearGradient(0, 100, 0, 350);
  water.addColorStop(0, "#88c5bb");
  water.addColorStop(0.55, "#327f81");
  water.addColorStop(1, "#204b5a");
  ctx.strokeStyle = water;
  ctx.lineWidth = 105;
  ctx.beginPath();
  ctx.moveTo(-20, 150);
  ctx.bezierCurveTo(120, 135, 100, 340, 360, 270);
  ctx.stroke();

  for (let i = 0; i < 18; i += 1) {
    const phase = (i / 18 + row.tracer_x_m * 0.45) % 1;
    const x = 350 * phase;
    const y = 150 + 145 * Math.sin(phase * 1.8) + 14 * Math.cos(i * 3);
    dot(x, y, i % 5 === 0 ? 4 : 2, "#c1ebda");
  }

  ctx.strokeStyle = row.pulse_j ? "#ffdb92" : "#628e78";
  ctx.lineWidth = row.pulse_j ? 5 : 2;
  ctx.beginPath();
  ctx.moveTo(320, 255);
  ctx.lineTo(589, 255);
  ctx.stroke();

  ctx.fillStyle = "#102722";
  ctx.fillRect(404, 205, 110, 100);
  ctx.strokeStyle = "#a4ccb6";
  ctx.strokeRect(404, 205, 110, 100);
  ctx.fillStyle = "#edca83";
  ctx.fillRect(415, 294 - 78 * row.stored_j / 0.5, 88, 78 * row.stored_j / 0.5);

  const map = ([x, y]) => [640 + x * 39, 368 - y * 42];
  for (let x = 0; x <= 8; x += 1) {
    for (let y = 0; y <= 6; y += 1) dot(...map([x, y]), 2, "#648777");
  }
  for (const wall of row.garden.walls) {
    const [x, y] = map(wall);
    ctx.fillStyle = "#445f50";
    ctx.fillRect(x - 13, y - 13, 26, 26);
  }
  for (const rose of row.garden.roses) dot(...map(rose), 8, "#dd9f9f");
  dot(...map(row.garden.frog), 8, "#9ad57b");
  const colors = ["#ffda92", "#e7aeae", "#b9aedc", "#93c6d4", "#a7e3ca"];
  row.garden.people.forEach((person, i) => {
    const [x, y] = map(person.position);
    dot(x, y, 15, colors[i]);
    label(person.name[0], x - 5, y + 6, "#11231e", 16);
  });
  label("Tiny Creek", 30, 60);
  label("Capacitor", 406, 183);
  label("Peaceful Garden", 640, 60);
}

function show(index) {
  const row = rows[index];
  time.value = index;
  byId("clock").value = `${String(index).padStart(2, "0")} s`;
  byId("flow").textContent = `${row.flow_lps.toFixed(3)} L/s`;
  byId("energy").textContent = `${(row.stored_j * 1000).toFixed(1)} mJ`;
  byId("brownian").textContent = `${(row.brownian_increment_m * 1e6).toFixed(2)} µm`;
  byId("step").textContent = row.garden_tick;
  const verdict = row.forecast_high_flow ? "Pulse requested" : "Angel waits";
  const delivery = row.pulse_j ? ` · ${(row.pulse_initial_a * 1000).toFixed(0)} mA initial current` :
    row.forecast_high_flow ? " · Charge below pulse requirement" : "";
  const observation = row.sampled_outcome_high_flow === null ? "" :
    ` · Downstream sample: ${row.sampled_outcome_high_flow ? "high flow" : "low flow"}`;
  byId("reading").textContent = verdict + delivery + observation;
  draw(row);
}

function pause() {
  clearInterval(timer);
  timer = undefined;
  play.textContent = "Play";
}

play.addEventListener("click", () => {
  if (timer !== undefined) return pause();
  if (+time.value === rows.length - 1) show(0);
  play.textContent = "Pause";
  timer = setInterval(() => {
    const next = Number(time.value) + 1;
    show(next);
    if (next === rows.length - 1) pause();
  }, 1000);
});
time.addEventListener("input", () => {
  pause();
  show(Number(time.value));
});

fetch("replay.json").then((response) => {
  if (!response.ok) throw new Error("Replay unavailable");
  return response.json();
}).then((trace) => {
  if (!trace.length) throw new Error("Replay is empty");
  rows = trace;
  time.max = rows.length - 1;
  show(0);
  play.disabled = time.disabled = false;
}).catch(() => {
  byId("reading").textContent = "Could not load the replay. Reload this page to try again.";
});
