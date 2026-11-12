#!/usr/bin/env python3
"""Calibrated local EDF eye-movement features with independently scored labels."""
from pathlib import Path
import argparse, csv, hashlib, json
import numpy as np
from scipy.signal import butter, sosfiltfilt

def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda : f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

class EDF:

    def __init__(self, path):
        self.path = Path(path)
        with self.path.open('rb') as f:
            h = f.read(256)
            if len(h) != 256 or h[:8].strip() != b'0':
                raise ValueError('Expected fixed-record EDF')
            self.offset = int(h[184:192])
            self.records = int(h[236:244])
            self.duration = float(h[244:252])
            self.n = int(h[252:256])
            self.clock = h[176:184].decode().replace('.', ':')

            def field(w):
                return [f.read(w).decode('ascii').strip() for _ in range(self.n)]
            self.labels = field(16)
            field(80)
            self.units = field(8)
            self.pmin = np.array(field(8), float)
            self.pmax = np.array(field(8), float)
            self.dmin = np.array(field(8), float)
            self.dmax = np.array(field(8), float)
            field(80)
            self.samples = np.array(field(8), int)
            field(32)
            if f.tell() != self.offset or self.records <= 0 or self.duration <= 0:
                raise ValueError('Invalid EDF header')
        self.width = int(self.samples.sum())
        if self.path.stat().st_size != self.offset + 2 * self.records * self.width:
            raise ValueError('EDF record size mismatch')
        self.raw = np.memmap(self.path, dtype='<i2', mode='r', offset=self.offset, shape=(self.records, self.width))

    def channel(self, label, start, duration):
        i = self.labels.index(label)
        fs = float(self.samples[i] / self.duration)
        if start < 0 or duration <= 0 or start + duration > self.records * self.duration:
            raise ValueError('Window outside EDF')
        if self.units[i] != 'uV':
            raise ValueError('Expected calibrated microvolts')
        lo = int(start // self.duration)
        hi = int(np.ceil((start + duration) / self.duration))
        offset = int(self.samples[:i].sum())
        raw = np.asarray(self.raw[lo:hi, offset:offset + self.samples[i]], float).reshape(-1)
        begin = round((start - lo * self.duration) * fs)
        raw = raw[begin:begin + round(duration * fs)]
        span = self.dmax[i] - self.dmin[i]
        if span <= 0:
            raise ValueError('Invalid EDF scale')
        return ((raw - self.dmin[i]) * (self.pmax[i] - self.pmin[i]) / span + self.pmin[i], fs)

def clock(v):
    (h, m, s) = map(int, v.strip().split(':'))
    return h * 3600 + m * 60 + s

def codebook(stages, events):
    lookup = {int(r['Epoch']): r['Sleep'] for r in stages}
    sets = {}
    for r in events:
        try:
            code = lookup[int(r['Epoch'])]
        except (KeyError, ValueError):
            continue
        sets.setdefault(code, set()).add(r['Stage'].strip())
    if any((len(s) != 1 for s in sets.values())):
        raise ValueError('Stage-code disagreement')
    return {k: next(iter(v)) for (k, v) in sets.items()}

def features(x, fs):
    if fs <= 12 or not np.all(np.isfinite(x)):
        raise ValueError('Invalid EOG sampling')
    y = sosfiltfilt(butter(3, [0.3, 5], btype='bandpass', fs=fs, output='sos'), x)
    return dict(rms_uv=float(np.sqrt(np.mean(y * y))), slope_rms_uv_per_s=float(np.sqrt(np.mean((np.diff(y) * fs) ** 2))), peak_to_peak_uv=float(np.ptp(x)), flatline=bool(np.ptp(x) <= 1e-06))

def main():
    p = argparse.ArgumentParser()
    for name in ['edf', 'stages', 'events', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--session', default='local-sleep-session-1')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    with a.stages.open() as f:
        stages = list(csv.DictReader(f))
    with a.events.open() as f:
        events = list(csv.DictReader(f))
    mapping = codebook(stages, events)
    edf = EDF(a.edf)
    offset = (clock(stages[0]['Clock Time']) - clock(edf.clock)) % 86400
    if offset > 43200:
        offset -= 86400
    if offset < 0:
        raise ValueError('Scoring begins before EDF: explicit alignment needed')
    output = []
    first = int(stages[0]['Epoch'])
    skipped = 0
    for row in stages:
        elapsed = (int(row['Epoch']) - first) * 30
        onset = offset + elapsed
        if clock(row['Clock Time']) != (clock(stages[0]['Clock Time']) + elapsed) % 86400:
            raise ValueError('Nonuniform stage clocks')
        if onset + 30 > edf.records * edf.duration:
            skipped += 1
            continue
        r = dict(session=a.session, onset_seconds=onset, duration_seconds=30, stage=mapping.get(row['Sleep'], 'Unknown'), reference_code=row['Sleep'])
        for (side, label) in [('left', 'E1-M2'), ('right', 'E2-M2')]:
            (signal, fs) = edf.channel(label, onset, 30)
            r.update({f'eog_{side}_{k}': v for (k, v) in features(signal, fs).items()})
        output.append(r)
    if not output:
        raise ValueError('No complete aligned epochs')
    with (a.output / 'epochs.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(output[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(output)
    counts = {s: sum((r['stage'] == s for r in output)) for s in sorted({r['stage'] for r in output})}
    report = dict(session=a.session, epochs=len(output), incomplete_epochs_skipped=skipped, stage_counts=counts, rem_minutes=0.5 * counts.get('REM', 0), flatline_epochs=sum((r['eog_left_flatline'] or r['eog_right_flatline'] for r in output)), codebook=mapping, stage_offset_seconds=offset, channels=['E1-M2', 'E2-M2'], filter_hz=[0.3, 5], source_sha256={k: digest(getattr(a, k)) for k in ['edf', 'stages', 'events']}, note='Scored reference labels; measured EOG features are not detected REM events. No synchronization with separate motion session.')
    (a.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    (fig, axs) = plt.subplots(2, 1, figsize=(11, 6), sharex=True, layout='constrained')
    codes = {'AWAKE': 0, 'N1': 1, 'N2': 2, 'N3': 3, 'REM': 4}
    h = [r['onset_seconds'] / 3600 for r in output]
    axs[0].step(h, [codes.get(r['stage'], -1) for r in output], where='post')
    axs[0].set_yticks([-1, 0, 1, 2, 3, 4], ['Unknown', 'Wake', 'N1', 'N2', 'N3', 'REM'])
    axs[0].set_title('Local PSG reference stages and measured EOG')
    for side in ['left', 'right']:
        axs[1].plot(h, [r[f'eog_{side}_rms_uv'] for r in output], label=side, alpha=0.7)
    axs[1].set(xlabel='Hours since PSG start', ylabel='Band RMS (µV)')
    axs[1].legend()
    fig.savefig(a.output / 'sleep-eog.png', dpi=160)
    plt.close(fig)
    print(json.dumps({k: report[k] for k in ['epochs', 'incomplete_epochs_skipped', 'stage_counts', 'rem_minutes', 'stage_offset_seconds']}, indent=2))
if __name__ == '__main__':
    main()
