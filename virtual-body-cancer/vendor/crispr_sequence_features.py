"""Sequence-only functions extracted from the existing CRISPR project; metadata stubs are discarded by the benchmark."""

import numpy as np

SEQ_LEN = 30

NUC_ORDER = {"A": 0, "C": 1, "G": 2, "T": 3}

def _gene_features(X):
    return np.zeros((len(X), 4), dtype=np.float32)

def _drug_gene_features(X):
    return np.zeros((len(X), 21), dtype=np.float32)

def one_hot(sequences) -> np.ndarray:
    """
    Encode a list/array of 30-mer strings as a float32 array.

    Returns shape (N, 30, 4)  —  axis-2 order is A, C, G, T.
    Unknown nucleotides (N, etc.) are encoded as all-zeros.
    """
    n = len(sequences)
    X = np.zeros((n, SEQ_LEN, 4), dtype=np.float32)
    for i, seq in enumerate(sequences):
        for j, nuc in enumerate(seq[:SEQ_LEN]):
            idx = NUC_ORDER.get(nuc.upper(), -1)
            if idx >= 0:
                X[i, j, idx] = 1.0
    return X

_NN_RNA_DNA = {
    'AA': (-7.8, -21.9), 'AC': (-5.9, -12.3), 'AG': (-9.1, -23.5), 'AT': (-8.3, -23.9),
    'CA': (-9.0, -26.1), 'CC': (-9.3, -23.2), 'CG': (-16.3, -47.1), 'CT': (-7.0, -19.7),
    'GA': (-5.5, -13.5), 'GC': (-8.0, -17.1), 'GG': (-12.8, -31.9), 'GT': (-7.8, -21.6),
    'TA': (-7.8, -23.2), 'TC': (-5.5, -15.3), 'TG': (-9.4, -26.4), 'TT': (-7.8, -21.9),
}

_R_GAS = 1.987

_CT = 250e-9

_NUC_STR = 'ACGT'

def _tm_subwindow(seq_idx_2d: np.ndarray, start: int, end: int) -> np.ndarray:
    """
    Compute approximate melting temperature for sub-window [start:end] of each sequence.
    seq_idx_2d: (N, 30) integer indices (A=0,C=1,G=2,T=3)
    Returns (N,) float32 Tm in Celsius.
    """
    N = len(seq_idx_2d)
    tm = np.zeros(N, dtype=np.float32)
    sub = seq_idx_2d[:, start:end]  # (N, window)
    L = end - start
    for i in range(N):
        dH = 0.1  # kcal/mol init (initiation)
        dS = -2.8  # cal/mol/K init
        for pos in range(L - 1):
            n1, n2 = sub[i, pos], sub[i, pos + 1]
            dinuc = _NUC_STR[n1] + _NUC_STR[n2]
            dH_nn, dS_nn = _NN_RNA_DNA.get(dinuc, (-8.0, -22.0))
            dH += dH_nn
            dS += dS_nn
        # Tm = dH*1000 / (dS + R*ln(CT/4)) - 273.15
        denom = dS + _R_GAS * np.log(_CT / 4.0)
        if abs(denom) > 1e-6:
            tm[i] = (dH * 1000.0 / denom) - 273.15
        else:
            tm[i] = 50.0
    return tm

def build_features(X: np.ndarray) -> np.ndarray:
    """
    Build Azimuth-style feature vector from one-hot (N, 30, 4).

    Features:
      - 120 position-specific mononucleotide one-hots (already in X flattened)
      - 464 position-specific dinucleotide one-hots (29 positions x 16)
      - GC scalar features: gc_count, gc_frac (20-mer guide), gc>10, gc<10
      - 4 position-independent nucleotide counts in guide (20-mer, pos 4-23)
      - 1 poly-T: count of TT dinucleotides in 30-mer
      - 4 Tm sub-window features (full 30-mer, PAM-proximal 5-mer, 8-mer, distal 5-mer)

    Total: 120 + 464 + 4 + 4 + 1 + 4 = 597 features
    """
    N = len(X)
    # Decode sequences from one-hot: (N, 30) integer indices (0-3), -1 for unknown
    # X[i, j, k] = 1 means position j is nucleotide k (A=0,C=1,G=2,T=3)
    seq_idx = X.argmax(axis=2)  # (N, 30); 0 where all-zero too, but we handle below
    # Mark positions with no nucleotide (all-zero rows) as -1
    has_nuc = X.max(axis=2) > 0  # (N, 30) bool

    # 1. Mononucleotide one-hot: (N, 120)
    mono = X.reshape(N, -1)  # already done in baseline

    # 2. Dinucleotide one-hot: 29 consecutive pairs x 16 = 464... wait, 29*16=464
    # Actually Azimuth uses 29 positions x 16 = 464 dinucleotide features
    dinu = np.zeros((N, 29, 16), dtype=np.float32)
    for pos in range(29):
        # nucleotide index at pos and pos+1
        n1 = seq_idx[:, pos]    # (N,)
        n2 = seq_idx[:, pos+1]  # (N,)
        valid = has_nuc[:, pos] & has_nuc[:, pos+1]
        # dinucleotide index: n1*4 + n2  (A=0,C=1,G=2,T=3)
        di_idx = n1 * 4 + n2  # (N,)
        # set one-hot
        rows = np.where(valid)[0]
        if len(rows) > 0:
            dinu[rows, pos, di_idx[rows]] = 1.0
    dinu_flat = dinu.reshape(N, -1)  # (N, 464)

    # 3. GC scalar features
    # Guide region: positions 4-23 (20-mer guide; 4bp context + 20bp guide)
    guide_oh = X[:, 4:24, :]  # (N, 20, 4)
    guide_idx = seq_idx[:, 4:24]  # (N, 20)
    gc_in_guide = ((guide_idx == 1) | (guide_idx == 2)).sum(axis=1).astype(np.float32)  # C=1, G=2
    gc_count_30 = ((seq_idx == 1) | (seq_idx == 2)).sum(axis=1).astype(np.float32)
    gc_frac = gc_in_guide / 20.0
    gc_above_10 = (gc_count_30 > 10).astype(np.float32)
    gc_below_10 = (gc_count_30 < 10).astype(np.float32)
    gc_feats = np.stack([gc_count_30, gc_frac, gc_above_10, gc_below_10], axis=1)  # (N, 4)

    # 4. Position-independent nucleotide counts in guide (20-mer)
    nuc_counts = np.zeros((N, 4), dtype=np.float32)
    for k in range(4):
        nuc_counts[:, k] = (guide_idx == k).sum(axis=1)

    # 5. Poly-T: count of TT dinucleotides in full 30-mer
    tt_count = np.zeros((N, 1), dtype=np.float32)
    for pos in range(29):
        tt_count[:, 0] += ((seq_idx[:, pos] == 3) & (seq_idx[:, pos+1] == 3)).astype(np.float32)

    # 6. PAM-context dinucleotide: positions flanking the GGG PAM
    #    30-mer layout: [0-3 context][4-23 guide][24-26 PAM=NGG][27-29 context]
    #    PAM bookend dinucleotide: positions 24 and 27 (flanking the GG)
    pam_dinu = np.zeros((N, 16), dtype=np.float32)
    pam_valid = has_nuc[:, 24] & has_nuc[:, 27]
    pam_di_idx = seq_idx[:, 24] * 4 + seq_idx[:, 27]
    rows = np.where(pam_valid)[0]
    if len(rows) > 0:
        pam_dinu[rows, pam_di_idx[rows]] = 1.0

    # Guide-start G indicator: position 4 in 30-mer (first nt of 20-mer guide)
    guide_start_g = (seq_idx[:, 4] == 2).astype(np.float32).reshape(N, 1)  # G=2
    # Guide-end G indicator: position 23 (last nt of 20-mer guide, PAM-proximal)
    guide_end_g = (seq_idx[:, 23] == 2).astype(np.float32).reshape(N, 1)
    # TTTT 4-mer count (Pol III termination signal)
    tttt_count = np.zeros((N, 1), dtype=np.float32)
    for pos in range(27):
        mask = ((seq_idx[:, pos] == 3) & (seq_idx[:, pos+1] == 3) &
                (seq_idx[:, pos+2] == 3) & (seq_idx[:, pos+3] == 3))
        tttt_count[:, 0] += mask.astype(np.float32)

    pam_feats = np.concatenate([pam_dinu, guide_start_g, guide_end_g, tttt_count], axis=1)  # (N, 19)

    # 7. Tm sub-window features (Azimuth uses 4 Tm values)
    #    30-mer: 0-29, PAM-proximal 5-mer: 20-25, 8-mer: 12-20, distal 5-mer: 7-12
    tm_30  = _tm_subwindow(seq_idx, 0, 30)
    tm_pam = _tm_subwindow(seq_idx, 20, 25)   # 5-mer PAM-proximal
    tm_8   = _tm_subwindow(seq_idx, 12, 20)   # 8-mer mid-guide
    tm_5   = _tm_subwindow(seq_idx, 7, 12)    # 5-mer distal
    tm_feats = np.stack([tm_30, tm_pam, tm_8, tm_5], axis=1)  # (N, 4)

    # 8. Position-independent 3-mer counts over 20-mer guide (64 features)
    kmer3 = np.zeros((N, 64), dtype=np.float32)
    for pos in range(4, 22):  # 18 positions give 18 trigrams within guide
        valid = has_nuc[:, pos] & has_nuc[:, pos+1] & has_nuc[:, pos+2]
        idx3 = seq_idx[:, pos] * 16 + seq_idx[:, pos+1] * 4 + seq_idx[:, pos+2]
        rows = np.where(valid)[0]
        if len(rows) > 0:
            np.add.at(kmer3, (rows, idx3[rows]), 1.0)

    # 9. Position-independent 4-mer counts over 20-mer guide (256 features)
    kmer4 = np.zeros((N, 256), dtype=np.float32)
    for pos in range(4, 21):  # 17 positions give 17 4-grams within guide
        valid = has_nuc[:, pos] & has_nuc[:, pos+1] & has_nuc[:, pos+2] & has_nuc[:, pos+3]
        idx4 = (seq_idx[:, pos] * 64 + seq_idx[:, pos+1] * 16 +
                seq_idx[:, pos+2] * 4  + seq_idx[:, pos+3])
        rows = np.where(valid)[0]
        if len(rows) > 0:
            np.add.at(kmer4, (rows, idx4[rows]), 1.0)

    # 10. Rolling 5-mer window GC fraction across guide (16 windows)
    # Windows: guide pos 0-4, 1-5, ..., 15-19 (guide positions 4-23 in 30-mer)
    win_gc = np.zeros((N, 16), dtype=np.float32)
    for w in range(16):
        start_pos = 4 + w  # in 30-mer coords
        window_idx = seq_idx[:, start_pos:start_pos+5]  # (N, 5)
        gc_in_win = ((window_idx == 1) | (window_idx == 2)).sum(axis=1).astype(np.float32)
        win_gc[:, w] = gc_in_win / 5.0

    # 10. Position-independent dinucleotide counts over full 30-mer (Azimuth pi feature)
    pi_dinu = np.zeros((N, 16), dtype=np.float32)
    for pos in range(29):
        valid = has_nuc[:, pos] & has_nuc[:, pos+1]
        di_idx2 = seq_idx[:, pos] * 4 + seq_idx[:, pos+1]
        rows = np.where(valid)[0]
        if len(rows) > 0:
            np.add.at(pi_dinu, (rows, di_idx2[rows]), 1.0)

    # 11. Gene annotation features (Azimuth full model: Percent Peptide, AA cut position, <50%)
    gene_feats = _gene_features(X)  # (N, 3)

    dg_feats = _drug_gene_features(X)  # (N, 4+17=21) drug+gene one-hot
    feats = np.concatenate([mono, dinu_flat, gc_feats, nuc_counts, tt_count, pam_feats, tm_feats, kmer3, kmer4, win_gc, pi_dinu, gene_feats, dg_feats], axis=1)
    return feats
