# Mirror Garden — optics and evidence notebook

Created 2026-09-26 in response to the user's DemystifySci link and request to
assess, connect to Trool/HRL, and add it to the portfolio.

## Review scope

The user identifies Paradox Lost as the creators’ forthcoming physics book.

The video metadata reports title, creators and duration 7032 seconds. The
creator-provided description and https://demystifysci.com/paradoxlost were read.
YouTube auto-captions were listed but downloading English JSON3 captions returned
HTTP 429. No full transcript or audio/video review was completed. No unverified
speaker quotations, chapter positions, or detailed mechanisms are attributed.
The evaluation is preliminary and applies to the description's framing only.

Reference baseline: Feynman Lectures I.31, II.32, II.33 at
https://www.feynmanlectures.caltech.edu/ . The page links each relevant source.
The two calculators implement standard optical formulas, not the proposed
alternative model. No empirical data or claim of new physics is presented.

## Reproduction

`node optics-lab/test.cjs` checks numerical limits, Brewster's angle, total
internal reflection, Snell's law, energy conservation and the complex-index
normal-incidence result. Browser interaction checks cover presets and sliders.

The dielectric model assumes isotropic, nonmagnetic, lossless homogeneous media,
a monochromatic plane wave, and a flat abrupt interface. Indices are real and
frequency-independent in the UI. Reflectance for unpolarized light averages the
s and p power fractions. T=1-R is valid for this lossless interface; this is not
an electric-field amplitude transmission coefficient. A reflected ray is omitted
when its modeled power is zero. In total internal reflection the diagram omits
the evanescent field and explicitly labels the lack of a propagating ray.

The second calculator assumes normal incidence from n=1 into a semi-infinite
nonmagnetic medium with complex index n+iκ (sign convention immaterial for R).
Values are hypothetical, not metal optical constants. At κ=0, entering energy is
transmitted, not absorbed. No coating thickness, roughness, wavelength dependence,
polarization conversion or fluorescence is simulated.

## Connection to HRL

The prose gives object/label roles, hierarchical pooling and a potential joint
factor for future measured-data tests. The claim ledger uses scoped Trool states.
It is an authored review, not a trained or numerically calibrated classifier.
The actual calculations are Fresnel optics; a completed HRL comparison would need
candidate equations, datasets and independent tests. No support score can supply
missing empirical evidence.

No external request occurs until the user chooses to load the YouTube player or
follows a source link. No analytics or cookies are added by this page itself.

## Recursive HyperStar extension

User requested infinite downward recursion. The page includes a finite SVG
visualization (depth 0–3; 1, 7, 43, 259 stars) and conditional geometric-series
bounds. Role recursion is a proposed extension, not part of the reviewed video.
If per-layer magnitude is <= M alpha^d for 0<=alpha<1, tail after D is
<= M alpha^(D+1)/(1-alpha). In a naive six-branch additive tree with branch gain g,
the absolute layer bound is M(6g)^d, hence 6g<1 is sufficient for summability.
This is not necessary for all possible signed/canceling models. Contraction
requires a complete invariant domain and a global Lipschitz constant below one.
No claim is made that arbitrary recursive HRL or nature meets these conditions.
