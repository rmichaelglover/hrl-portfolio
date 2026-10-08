# The Lion and the Lamb

An imagined world by Manny Glover and Cypher. A garden, small creeks, a pond, a human hearth, a transitional guardian landscape, and deep wilderness. Lions, tigers, bears, raccoons, and opossums are characters in this fiction. The place is invented; no private address or real-property map appears.

The fictional rule is that animals can choose bonds with people, be cared for, keep private retreats, and guard a shared boundary. That rule is a story premise, not a biological finding. A generous table does not prove real predator loyalty. The story includes filed teeth and claws as a premise but supplies no training, acquisition, fence, breeding, dental, claw, or animal-handling procedures.

## Three zones

1. **Normal human civilization**: homes, towns, families, farms, and familiar domesticated animals. The earlier inner-world daydream included altered guardian anatomy; that premise does not apply automatically to the buffer.
2. **Managed wildlife buffer**: animals retain natural teeth and claws. In the fiction, extensive training encourages general friendliness to people. Additional layers include trained supervision, protected observation, restricted contact, separate prey refuges, private retreats, and separation when tension appears. The model does not establish training efficacy, compliance, or safety.
3. **Wild-wild**: minimal intervention and minimal permanent human habitation. National parks, national forests, and state parks inspire the outer zone, but real examples vary in law, management, habitation, and use. The fictional ideal is not a universal factual classification of those lands.

Day/night views change narrative and appearance, not training effectiveness or containment. Animals are fictional characters; no care, training, enclosure, or emergency procedure is provided. The current visualization focuses on Zone 2, with its weapons intact.

## Optional mathematical sketch

The visual story comes first. Under it is a deliberately small, uncalibrated discrete-time model. All inputs and states are normalized to [0,1]. Species changes illustration and narrative, **not coefficients**. This is not a bear, lion, tiger, raccoon, or opossum behavior predictor.

Inputs:

- c: care quality
- r: retreat/choice availability
- e: enrichment
- a: human-food attraction
- x: exposure to people
- n: one or two animals
- p: a conceptual separated-contact multiplier (0.12) or shared-space multiplier (1)

States: H = habituation, F = food association, S = stress. Initial conditions: H₀ = 0.35, F₀ = 0.10, S₀ = 0.45. Let C(z) = min(1, max(0,z)). One step is labeled one illustrative day.

Hₜ₊₁ = C(Hₜ + 0.035x(1 − Hₜ) − 0.008(1 − x)Hₜ)

Fₜ₊₁ = C(Fₜ + 0.06a(1 − Fₜ) − 0.02(1 − a)Fₜ)

q = 0.15(n − 1)(1 − r)

Sₜ₊₁ = C(Sₜ + 0.035[0.35x + 0.35(1 − r) + 0.30(1 − e) + q](1 − Sₜ) − 0.045[0.5c + 0.5r]Sₜ)

Wₜ = C(0.30c + 0.25r + 0.25e + 0.20(1 − Sₜ))

Iₜ = C(x[0.35 + 0.35Hₜ + 0.30Fₜ]p)

W is a modeled welfare index. I is a contact-pressure index, **not injury probability**. A low I does not certify safety. There is no equation for affection, obedience, reliable defense, domestication, inheritance, genetic selection, mating, predator/prey compatibility, or suppression of aggression. No coefficient has been estimated from observations. No confidence interval or empirical validation is claimed. Changing retreat or enrichment can change stress by construction; that result is not independent evidence for the assumptions.

## What future research could investigate

For an evidence-based study separate from this fiction, distinguish individual approach behavior, habituation, food conditioning, welfare, and inherited domestication. Use species-specific expert review and authorized observations. Record retreat choices and behavior without treating calm appearances as proof of safe contact. The present model is a sandbox for questions, not a study protocol.

## References for the real-world distinctions

- Georgia DNR, [Guide to Legal Pets](https://georgiawildlife.com/node/765).
- National Park Service, [Habituated grizzly bears](https://www.nps.gov/yell/learn/habituated-grizzly-bears.htm).
- AVMA, [The veterinarian’s role in animal welfare](https://ebusiness.avma.org/files/productdownloads/vetsroleinaw.pdf).
- GFAS, [Bear sanctuary standards](https://sanctuaryfederation.org/wp-content/uploads/2020/02/Bear-Standards-2019.pdf) and [position statements](https://sanctuaryfederation.org/about-gfas/position-statements/).

These inform conceptual distinctions and professional-care context; they do not validate the numerical coefficients. The scientific/legal references primarily concern the original bear scenario and general sanctuary principles. They are not species-specific validation of the other illustrated animals.

## Files

`index.html`, `style.css`, `app.js`, and `model.js` are the editable interactive visualization. `THE-LION-AND-THE-LAMB.html` is a portable single-file version that works locally without a server, installation, data download, or network connection. No private data is stored. This is a creative artifact, not a deployed service or animal-care product.

## Anatomy and scope

The earlier human-world daydream stipulated filed teeth and claws. The later buffer zone is distinct: its residents retain their built-in weapons and receive extensive training in the fiction. The illustration now focuses on that buffer. No anatomical-alteration procedures or training instructions are supplied. Neither the anatomical premise nor training is a mathematically established route to safe contact. No magical suppression of predation is assumed.

## Landscape-derived corridors and subzones

The three main zones are conceptual habitat regimes, not concentric bands. Their local boundaries and connections emerge from mountain ranges, rivers, creeks, lakes, ponds, roads, canals, railroads, large highways, and small dirt roads. The visualization marks these features and one fictional crossing.

A future spatial model can represent habitat pockets as nodes and traversable routes as edges, with species-specific permeability and human activity attached to each edge. A single feature can be a corridor for one inhabitant and a barrier for another. The current numerical sketch is not spatial: these map features do not yet change its equations. No surveyed geography, inferred migration route, engineered crossing, or validated barrier effectiveness is claimed.
