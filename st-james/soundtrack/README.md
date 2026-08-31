# St. James soundtrack generation

This directory provides a provider-neutral soundtrack brief with an ACE-Step
manifest for the St. James Park concept.

## Open music backend

[ACE-Step](https://github.com/ace-step/ACE-Step) is the preferred local,
open-source alternative to proprietary services such as Suno. ACE-Step is a
separate project; this portfolio does not bundle its code, model weights, or
services and is not affiliated with or endorsed by ACE-Step or Suno.

The manifest in `ace-step-fairest-lord-jesus.json` records the creative brief,
structure, seed, duration, and rights checks. Its fields can be entered in the
ACE-Step local interface: use `caption` for the overall vision and translate
`structure` into section tags. Lyrics are intentionally blank until Manny adds
an approved text or instrumental direction.

## Optional local setup

Follow the current instructions in the official ACE-Step repository and use a
dedicated virtual environment. The upstream application normally launches a
local interface on `127.0.0.1:7865`; do not enable public sharing for private
drafts. Model weights are intentionally not installed by this repository.

This machine currently has no detected NVIDIA GPU. Confirm that the selected
ACE-Step release supports the available hardware before downloading weights.

## Publication checklist

1. Generate multiple drafts locally and retain the prompt, seed, and model version.
2. Reject outputs that imitate a recognizable artist, melody, or recording.
3. Have a human review musical quality, lyrics, cultural context, and accessibility.
4. Export only the selected master and record its license and provenance.
5. Credit the traditional hymn, performers, arrangers, and AI assistance accurately.
