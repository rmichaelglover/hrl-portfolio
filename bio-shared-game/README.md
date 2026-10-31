# Bio Shared Game — first research prototype

Manny Glover's proposal: comfortable ant and spider habitats, mostly RGB observation, and a translation between the animals' own activities and useful machine problem solving. The long-term ambition is a biosupercomputer. The immediate hypothesis is narrower: **can a preregistered mapping between a physical task and a digital task produce useful, reproducible information in both directions?**

Status: runnable offline observation decoder, synthetic smoke-test dataset, controls, and experiment design. No real animal data, live vision model, habitat actuator, or demonstrated biological computing advantage yet. No purchases, animal collection, or public deployment have been made.

## The two parties

Default: a biological participant and a digital participant. Ant colony and individual spider are separate biological systems, initially investigated separately. An optional later experiment can connect ant and spider habitats through the same software bus. They never need to meet or share an enclosure. Do not assume all spiders build prey-capture webs or that all ants recruit through pheromone trails.

The animals' activity need not resemble a human game, and successful task coupling need not imply they understand our digital objective.

## First shared game: route selection

1. A foraging ant colony explores an optional observation arena connected to its normal habitat. Two or three measurable paths lead to an ordinary feeding location. Normal water, food, refuge, and colony access remain available; no deprivation or punishment.
2. Fixed overhead RGB video records crossing events at calibrated path boundaries. Begin with aggregate directional traffic, not persistent ant identities. Compare against manually annotated footage.
3. A mapping fixed before evaluation associates arena paths with digital graph routes. For a valid computation experiment, physical differences must encode the specified digital instance. Merely giving arbitrary names to unrelated ant movements cannot communicate unknown route quality.
4. The decoder chooses a route from traffic rates, or abstains when observations are weak/tied. A digital routing task evaluates the decoded choice against costs withheld from the decoder.
5. In a later feedback study, a digital policy may suggest a reversible arena configuration between sessions. Physical feasibility, species requirements, and humane operating bounds must be established first. Nothing in this repository moves gates, changes food access, or stimulates animals.

For the animal, success could mean efficient ordinary foraging with no adverse change in normal activity. For the computer, success means reduced route cost or improved adaptation to a changed graph. These are separate measurements; improvement in one does not establish improvement in the other. Throughput, observation latency, preparation, energy, and care costs count in the machine comparison.

A tiny graph has a cheap exact software solution. Use it to validate the interface, not to claim a competitive solver. More difficult problems come only after a nontrivial mapping is demonstrated. A physical layout constructed from an already-computed optimum would leak the answer.

## Spider track: observe first, define the task second

Start with one spider in an appropriate separate habitat. Observe activity/rest, visible locomotion, web building and repair if applicable, and repeated use of attachment sites. Potential machine analogies include sensing networks, material allocation, repair, and structure-dependent signal processing. These are hypotheses, not proven equivalences.

An initial spider dataset should measure visible web topology and repair sequences; missing or reflective silk stays marked unknown. A later candidate shared task is network repair under material constraints: compare measured repair patterns with software network designs on held-out geometries. A vibration-classification task is another possibility, but ordinary RGB footage may not resolve the relevant signals. Additional high-speed imaging or vibration sensing must be justified by calibration; do not infer invisible vibration or internal decisions from a standard video.

Do not combine ant traffic and spider events into a common score until each has a validated task mapping and decoder. The replay schema can transport either kind of aggregate event, but it does not validate their biological interpretation.

## Mostly RGB measurement design

- Fixed camera, scale reference, timestamped frames, stable diffuse lighting, and a view of the optional observation region. Preserve normal species-appropriate light cycles and refuge; camera visibility is not more important than habitat quality.
- Measure pixels per body length and motion blur on pilot footage before selecting frame rate/resolution. RGB sees movement and visible structure, not pheromone concentration, intent, or hidden nest activity.
- Pipeline to implement: capture → calibration → segmentation/detection → short tracklets → directional line-crossing events → manually validated aggregates → decoder. Use region hysteresis and track continuity to avoid counting boundary jitter as repeated crossings.
- Maintain source-video IDs, frame/time ranges, calibration versions, detector versions, occlusion flags, and manual annotations alongside aggregates. `confidence` in the current CSV is a supplied quality field, not a calibrated probability produced by this code.
- Occlusion, merged ants, shadows, glass reflections, and fine silk are expected failure cases. Mark uncertainty and abstain. Do not invent identity continuity through occlusion.
- Evaluate crossing-count error, detection precision/recall, missing coverage, and timing error against blinded human labels. Split datasets by session and biological replicate; adjacent frames are not independent replicates.

Existing tracking software worth evaluating on pilot footage: [idtracker.ai documentation](https://idtracker.ai/latest/). Its stated laboratory capabilities are not a guarantee for this habitat or species.

## Run the prototype

Python standard library only:

```sh
python3 -m unittest -v
python3 replay.py --demo demo
python3 replay.py --observations demo/observations.csv --tasks demo/tasks.json --output results.json
```

CSV fields: `trial,party,candidate,events,visible_seconds,confidence`.
Every candidate, including a region with zero events, needs a row. `events` is a nonnegative integer; `visible_seconds` is positive usable observation duration; quality is in [0,1]. Repeated trial/party/candidate keys are rejected. Event rates account for visible duration, but this does not eliminate activity-dependent missingness or validate unequal observation windows. Use synchronized matched windows in actual experiments.

Tasks JSON maps each trial to candidate costs, for example `{"trial-01":{"A":2,"B":8}}`. Task cost files must be held out from the observation extractor and decoder. Lower cost is better. Low-quality groups, ties, all-zero groups, and single-candidate groups abstain. Costs are evaluated only for accepted decisions; report coverage and compare all baselines on the same accepted subset. The current harness does not implement a fallback policy for abstentions.

Outputs compare decoded route cost with uniform-random expected cost, 1,000 shuffled label mappings, and an exact best-route reference. Label shuffling is a simple plumbing null, not a full causal test. It is inappropriate if a study's exchangeability assumptions fail.

**Synthetic demo caveat:** the generator explicitly creates more traffic on cheaper routes. Its favorable score demonstrates only that the decoder can recover an injected association. It is not an ant behavior model, a spider model, evidence of cognition, or evidence of a computing advantage.

## Experimental sequence and success criteria

A. Identify species and establish habitat-specific care and normal activity baselines. No animal experiment begins from a generic care prescription.

B. Record passive footage. Validate camera measurements against manual annotation. Set quality thresholds from pilot error, not from which threshold gives the best task score.

C. Freeze the task encoding and decoder. Evaluate unseen task layouts/sessions. Record all attempted trials and exclusion reasons. Measure preference for side, brightness, geometry, prior trails, and feeding location as possible confounds.

D. Run open-loop playback and shuffled, delayed, or yoked-feedback controls before a live feedback pilot. Ordinary software, random policy, simple traffic heuristics, and an animal-inspired algorithm are comparisons. Repeated choices within one colony are not independent colonies; independent biological replicates are required for population-level claims.

E. Test a bounded feedback pilot only after the physical interface and normal behavior are characterized. Compare biological efficiency and digital task performance separately, with uncertainty across independent units. Two-way benefit requires both to improve against matched controls, not merely a correlation.

F. Extract candidate mechanisms into software. Test whether an algorithm inspired by those measurements generalizes, even when no animals are involved. Distinguish biological computing, biomimetic algorithms, and a hybrid feedback system in all reports.

Until species and baseline data are available, physical feedback remains disabled. Stop a pilot if normal access or activity is disrupted; return to baseline conditions. Housing and care choices require species-specific evidence, not assumptions derived from the synthetic demonstration.

## Research grounding

- [Ant route adaptation in a physical maze, Journal of Experimental Biology](https://doi.org/10.1242/jeb.048173): supports investigating collective routing; does not show general-purpose computing.
- [Comparing cooperative geometric puzzle solving in ants versus humans](https://pmc.ncbi.nlm.nih.gov/articles/PMC11725855/): collective performance depends on task and group conditions.
- [Extended spider cognition](https://pmc.ncbi.nlm.nih.gov/articles/PMC5394149/): discusses the spider–web system and competing interpretations; it is not proof that every web is a universal computer.
- [Web transmission properties vary with past and current noise exposure](https://www.sciencedirect.com/science/article/pii/S0960982225002052): motivates studying adaptive sensing and environmental history.

The proposed cross-task coupling and experimental sequence are our research design, not established findings from these papers.
