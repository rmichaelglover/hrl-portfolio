# To Cure Cancer: The Virtual Body

Michael Emanuel Glover. Developed with Codex. 4 October 2026.


## Page 1: To Cure Cancer: The Virtual Body

I want to cure cancer. That is the purpose of this work, and I intend to say it plainly. I want a model that follows the cell into the niche, the niche into the tissue, the tissue into the organ, and the organ into the person. I want the cell of cells to become an executable account of what changes, what resists, what repairs, and what survives.

My algorithms begin with objects, labels and relationships. They become useful when those objects acquire measured identities and those relationships acquire testable consequences. Hierarchical relaxation gives me a language for the traffic between levels. The body gives that language its obligations: preserve healthy function, confront malignant growth, and expose the assumptions that decide which is which.

This dissertation puts my ambition beside the calculations actually executed. It contains measured assay data, held-out predictions, repaired nested-cell code, a multiscale dynamical prototype and a local-stability analysis. Each has its own evidentiary role. I insist that the reader be able to tell them apart, reproduce the numbers and challenge the conclusions.

Reality retains veto power. I keep the ambition; I also keep the ledger. The following eighty pages are the first fully assembled computational dissertation for this programme: argument, mathematics, implementation, measurements and case-by-case audit.


Figure: figures/architecture.pdf
Conceptual research architecture. Arrows indicate intended cross-scale information exchange; the complete biological coupling is a research objective.


## Page 2: Abstract: ambition, execution and evidence

I develop a virtual-body research programme around hierarchical relaxation labeling, explicit observation models, nested categorical state and organism-level constraints. The motivating objective is cancer control that preserves the person. The executed contribution is narrower and inspectable: a measured CRISPR assay-rank benchmark, a repaired nested-state implementation, and a synthetic three-site tumor-body model with a formal constant-exposure stability calculation.

The measured table contains 5,310 rows, 4,379 distinct sequences and 17 target genes. A historical row-random split shares 271 distinct test sequences with training. I therefore report fixed five-fold sequence-disjoint and gene-disjoint evaluations. All annotation, drug/gene identity and precomputed stacking columns are removed. The sequence-only feature extraction is checked against the original implementation, and held-out assay labels never enter the relaxation prior.

On sequence-disjoint evaluation, pooled out-of-fold Spearman correlations are 0.395318 for one-hot Ridge, 0.479858 for the existing sequence-feature Ridge model and 0.480544 for its HRL extension. Gene-disjoint values are 0.388453, 0.400323 and 0.403291. These small differences are descriptive point estimates; this dissertation does not establish statistical superiority or a treatment effect.

An audited virtual-cell snapshot corrects a missing method, entropy normalization, state-change measurement and ambiguous abstention coding. A seven-node, three-level hierarchy passes ten recursive steps. In the synthetic body model, a resistant-clone invasion threshold of 5.181195 dimensionless exposure exceeds the 0.136364 limit implied by an assumed reserve floor of 0.7. No constant-exposure intersection exists in the nominal model or its 24 sampled configurations.

The dissertation establishes executable components and reproducible calculations. It does not establish a cancer cure, a calibrated virtual human or clinical safety. I make that boundary explicit because a programme directed toward a cure must remain answerable to biological outcomes.


| Evidence class | Executed object |
| Measured | Assay ranks and held-out predictions |
| Numerical | Three-site trajectories and sensitivity |
| Formal | Local stability of specified equations |
| Software | Nested-state repairs and checks |


## Page 3: How to read this dissertation

I organize the record so that every broad claim can be walked back to its narrowest supporting calculation. The opening chapters establish the language of the virtual body, the inference mechanism, the observation problem and the dynamical assumptions. The result chapters then expose individual folds, model behavior, every gene represented in the measured table, every nominal control and every sampled parameter configuration.

The page structure is deliberate. A result page names its denominator, distinguishes measured from synthetic quantities, and gives a figure or table that can be regenerated from the supplied files. The case reports are part of the audit: they prevent an average from concealing a difficult fold, a small gene group, a toxic model assumption or a resistant residual population.

Measured assay-rank predictions occupy a different layer from synthetic treatment trajectories. A gene name in the assay table identifies a prediction context; it does not prescribe a cancer therapy. Likewise, a favorable simulated trajectory records a consequence of assumed coefficients. It does not establish that a drug, dose or intervention has the corresponding effect in a person.

I use first-person argument throughout because the research purpose is mine. The figures, numerical summaries and inferential boundaries remain inspectable regardless of who speaks. This is an independent research dissertation developed with Codex assistance; no university degree, journal acceptance or external experimental validation is claimed.


| Pages | Content |
| 1-3 | Purpose, abstract and reading map |
| 4-19 | Theory, methods, proofs and reproducibility |
| 20-29 | Ten held-out fold reports |
| 30-35 | Six model/protocol diagnostics |
| 36-52 | Seventeen gene-context reports |
| 53-56 | Four synthetic control trajectories |
| 57-80 | Twenty-four parameter-case reports |


## Page 4: The objective: preserve the person

I take curing cancer as the organizing objective, rather than an excuse to reduce the body to a single score. Tumor burden belongs in the objective. So do resistant populations, healthy reserve, immune competence, function and the time over which control persists. A model that suppresses one population while destroying the system around it has answered the wrong question.

The useful mathematical object is a constrained intervention problem. Let the latent body state be x, the intervention history be u and the measured outcomes be y. I seek policies whose expected outcomes improve specified cancer endpoints while respecting explicit safety constraints. Those endpoints must be defined for a cancer context and a time horizon. Their meaning cannot be supplied by an attractive animation or a small floating-point value.

A cancer programme also needs a definition of recurrence and a record of follow-up. Tumor-free local stability, transient suppression, undetectable burden and clinical cure are different predicates. The executed model analyzes one of those predicates: local stability of a specified equilibrium under constant exposure. The measured benchmark evaluates another: prediction of assay response ranks. Neither predicate becomes a clinical cure merely because I combine them in one document.

I want the hierarchy because errors can cross it. An intracellular change can alter population selection. Selection can reshape the niche. The niche can alter transport and immune access. Organ-level injury can constrain exposure. A serious virtual body must make such feedback visible while distinguishing measured couplings from placeholders.

The immediate design discipline is therefore to specify the prediction, the observation and the permitted inference together. The larger ambition remains present in every calculation. It gives the work direction; the evidence gives each completed result its scope. I will not improve that evidence by changing the name of the result.


## Page 5: An evidence ledger for the cell of cells

I carry four epistemic questions into the model: what is observed, what is resolved, what is missing, and what conflicts with the current account? The Manuelian known-known and unknown distinctions help me keep those questions separate. They are metadata about knowledge, not extra biological substances. A missing assay, an uncertain cell identity and an untested causal link should not share one undifferentiated confidence number.

For an empirical edge I record a source, context, direction, sign, units, uncertainty and validation status. For an assumed edge I record the assumption and the calculation it enables. For a learned coefficient I record the training partition and the procedure that estimated it. For a formal proposition I record the hypotheses and the proof. This ledger makes the model a collection of accountable commitments rather than a collection of impressive names.

The drive audit matters to this discipline. It enumerated 880,934 accessible files and searched 45,884 selected text/code files. It found the existing HRL2026 implementation, the measured CRISPR table and a local virtual-cell perspective. It also found medical-imaging examples and cancer-related terms in private sleep-study metadata. Those findings have different scientific relevance. I did not repurpose private physiological records as treatment-response observations.

Coverage also has limits: protected directories, archives and most binary files were not decoded, and the inventory recorded 35 traversal or stat errors. I state those limits beside the count. A search record should help another researcher locate the evidence; it should not imply that every physical byte has been read or every possible dataset has been ruled out.

The public bundle includes the calculations and their provenance. The raw private inventory remains local. This separation protects the audit from becoming a disclosure of unrelated records, while keeping the actual supporting data products available for inspection.


## Page 6: The hierarchy has physical obligations

I use cells of cells as a name for organization across scales. Molecules participate in cellular processes; cells form niches and tissues; organs interact within the organism. The phrase does not mean that every organ is literally a cell nested inside another cell. Its mathematical value lies in typed aggregation, projection and feedback.

An aggregation map can summarize lower-level states into an organ-level quantity. A projection map can distribute a shared constraint back to the components that experience it. Both require semantics. A sum of cell counts, a mean of label strengths and a flux across a vascular boundary are different operations. Their units and conservation laws differ, and the hierarchy must preserve those differences.

The existing nested categorical implementation supplies recursion and state distributions. It does not yet supply measured bidirectional signaling between physical cells. The three-site dynamical prototype supplies shared exposure, aggregate tumor transport, resource dynamics and tissue reserve. It does not resolve individual cell mechanics or molecular kinetics. I treat those implementations as distinct modules with distinct interfaces.

A future connection must identify what is exchanged. A probability-like label strength may inform a kinetic regime only after a state-to-rate map is fitted and validated. A tissue exposure may alter a cell model only through a physically meaningful input. Copying the same signal into several levels without accounting for it can double-count evidence or violate balance.

I therefore require typed ports: measured state, inferred state, conserved quantity, control signal and uncertainty annotation. The architecture becomes stronger when those types are explicit. The ambition is a body model in which an apparent local success can be followed through the system until its organism-level consequence is visible.


Figure: figures/architecture.pdf
Conceptual cross-scale architecture; intended interfaces require biological calibration.


## Page 7: Observation comes before interpretation

A latent cell state is useful only if I can say what an instrument would observe when that state changes. I write an observation model for assay ranks, counts, images or biochemical measurements instead of pretending that one convenient representation measures all of them. Measurement noise, censoring, batch effects and missing values belong in that model.

The current measured dataset supplies normalized assay response ranks. The benchmark predicts those ranks from sequence features. It does not observe a complete intracellular state, a spatial tumor neighborhood or a whole-body outcome. Percent Peptide and amino-acid cut position are annotations in the source table; they are not the response variable used in this dissertation. The appended annotation features are excluded from the new benchmark.

An observation likelihood makes the distinction precise. If z is a latent state and y is an observation, the model must specify how y depends on z and on the assay context. A classifier score is not automatically that likelihood. A normalized vector produced by relaxation is not automatically a calibrated posterior. Calibration is an additional empirical question.

Identifiability follows immediately. Several different latent mechanisms can produce the same observed rank. A single cross-sectional assay cannot generally identify growth, death, migration, exposure clearance and immune recruitment simultaneously. Longitudinal observations and controlled perturbations are needed to separate competing explanations. Otherwise a fitted mechanism can be merely one of many compatible stories.

My rule is to let each instrument define what it can discriminate. I can build a hierarchy of hypotheses around that discrimination. I cannot enlarge the instrument by renaming its output. The measured result remains valuable when its limits are named.


\[
y \sim p(y\mid z, a, b),\qquad z\sim p(z\mid \theta).
\]


## Page 8: Sparse factors: relations become executable

My relaxation engine works with objects and label distributions. A factor associates a small set of objects with a compatibility tensor. Pairwise factors contract that tensor against the other object's current distribution. Three-way factors contract against two distributions. The resulting support changes the relative strength of competing labels.

This is an economical way to express relational hypotheses. It avoids allocating a dense tensor over every possible object pair. It also makes each proposed relation inspectable: which objects participate, which labels are compatible, and what sign the contribution carries. Rosenfeld, Hummel and Zucker developed the classical relaxation formulation; Hummel and Zucker analyzed its foundations. My present sparse implementation extends the software interface around that tradition [1,2].

A higher-order factor is meaningful when the biological hypothesis is genuinely joint. An immune, tumor and stromal interaction may depend on a configuration that cannot be represented by one isolated pairwise effect. That possibility does not establish that a chosen tensor is biologically correct. The tensor must be derived from measurements, justified assumptions or an identified learned model.

The measured CRISPR extension in this dissertation uses pairwise sequence-similarity factors. The earlier synthetic annotation demo also uses three-way homophily factors, correct by construction in its synthetic patches. I keep those two experiments separate. The real-data benchmark does not establish the value of three-way biological factors, because it does not test them.

Sparsity is therefore a computational property, while validity is an evidentiary property. I want both. The first makes the experiment affordable; the second makes it worth doing. A compact graph can still encode a mistaken relation, and a converged field can still be wrong.


\[
q_i(\ell)=\sum_{f\ni i}\sum_{\ell_{-i}} C_f(\ell,\ell_{-i})\prod_{j\in f\setminus i}s_j(\ell_j).
\]


## Page 9: The update and its actual guarantees

The generic engine preserves an explicit prior in each multiplicative update. Let pi be the initial label distribution, s the current distribution, rho the prior-strength parameter and q the normalized support. The update multiplies a prior/current-state base by a nonnegative support modulation, then normalizes each row.

If all base weights are nonnegative and at least one updated weight is positive, normalization produces a nonnegative row with unit total. That is a simplex-preservation statement. It does not establish global optimization, calibrated probability, biological truth or uniqueness of the limiting state. Those are separate questions. I do not infer them from row sums.

The implementation rescales support within a row. That changes how compatibility magnitudes influence the result. A global rescaling of all contributions can be partly removed by min-max normalization, while mixtures of factors and prior strength still change the field. Parameters should therefore be interpreted through the implemented transformation rather than through the raw tensor alone.

Convergence is measured by a maximum change in the state field. All ten measured-data HRL fits reach the specified tolerance within the iteration cap. This is an execution result: the update stabilizes on those inputs. The small predictive gains are assessed separately through held-out assay ranks. Stable arithmetic and useful prediction are related achievements, not identical achievements.

I keep iteration counts and the convergence flag in the run record. If a future field oscillates or reaches the cap, that must appear beside its predictive result. A terminating condition should identify what has terminated. It should never silently promote numerical stillness into a conclusion about the body.


\[
s_i^{+}(\ell)=\frac{\pi_i(\ell)^\rho s_i(\ell)^{1-\rho}[1+\eta\widehat q_i(\ell)]}{\sum_m\pi_i(m)^\rho s_i(m)^{1-\rho}[1+\eta\widehat q_i(m)]}.
\]


## Page 10: Unknown is an output with a meaning

I want the model to retain the ability to say that its available labels do not settle an object. The generic engine offers a rejection label; the nested implementation also needs a distinct abstention code. That distinction is computationally small and conceptually important. A certain negative category and an uncertain object must not be returned as the same integer.

The original projection method used minus one both for a certain negative trit and for uncertainty. The audited snapshot uses minus two for abstention. This repair does not decide when abstention is biologically appropriate. It makes the interface capable of representing the decision without ambiguity. A downstream consumer can now distinguish the states.

The rejection mechanism itself requires evaluation. A system that rejects every difficult cell may achieve good accuracy on what remains while providing poor coverage. A system that never rejects may provide confident-looking mistakes. Coverage, error among accepted cases and the composition of rejected cases should be reported together. The synthetic rejection demonstration records twelve rejected objects; it does not calibrate those decisions on real cells.

Entropy is another observable, not a substitute for uncertainty validation. A normalized categorical vector has a well-defined Shannon entropy. An arbitrary three-element weight vector must be normalized before that definition applies. The snapshot enforces this condition and rejects invalid weights. Biological uncertainty includes missing mechanisms and domain shift that categorical entropy alone cannot capture.

My aim is an honest interface between available evidence and unresolved state. The unknown category becomes useful when it triggers a traceable question: which measurement, context or model discrepancy would resolve this case? It becomes decoration when it merely supplies another color.


\[
H(p)=-\frac{1}{\log 3}\sum_{k:p_k>0}p_k\log p_k,\quad p_k\geq0,\quad\sum_kp_k=1.
\]


## Page 11: The measured assay table and its provenance

The useful measured resource was already on the drive: the cached Doench/Azimuth table used by the existing CRISPR prediction project. Its supplied response is score_drug_gene_rank, normalized within drug/gene contexts. The source paper concerns guide design and activity prediction [3]. I use it as an assay-prediction benchmark, not as a catalogue of clinical cancer treatments.

There are 5,310 retained rows and 4,379 distinct sequences across seventeen target genes. Repeated sequences occur across the table, including distinct assay contexts. That structure makes a row-random split a poor way to assert independence of sequence-based predictions. It also means that a sequence-only model cannot represent every context-specific difference in response.

The historical prediction code includes annotation and drug/gene lookup features, and a precomputed predictions field. I remove all twenty-five appended columns in the new calculation. The remaining 968 features are derived from sequence alone. The portable extraction reproduces those columns exactly on every retained row, and an executable perturbation of the metadata providers leaves them unchanged.

The source file is identified by SHA-256 in the reproducibility record. The public dissertation bundle contains source-row identifiers, observed response ranks, held-out predictions and the derived figures. It does not contain private sleep-study records, a raw drive inventory or a proposed therapeutic guide-selection protocol.

The denominator is therefore explicit. This table can test whether the implemented predictor orders the supplied assay ranks on its partitions. It cannot by itself establish tumor selectivity, delivery, organism toxicity, durability of cancer control or benefit in a patient. I retain the data because it provides a measured bridge into biological prediction, with those boundaries intact.


Figure: figures/measured-3d.pdf
Measured diagnostic with every third eligible assay row shown. Percent Peptide is an annotation, not the response. The annotation is excluded from benchmark predictors. The view is descriptive, not a causal surface.


## Page 12: Holdouts, overlap and the meaning of a test

I found 271 distinct test sequences that also occur in the historical training set, among 1,034 distinct test sequences. This does not prove that every previous prediction was memorized. It establishes that the historical split does not isolate unseen sequences. The experiment log also repeatedly compares the same test metric while selecting models, so that metric is part of development history.

The new evaluation fixes five group folds for sequences and five group folds for genes. Each fold checks that its grouping identifiers are disjoint between training and test and that identical sequences do not cross the partition. The gene-disjoint protocol asks a harder context-transfer question. The sequence-disjoint protocol permits familiar genes while holding out the sequences themselves.

One-hot Ridge is the simple baseline. A second Ridge model uses the existing engineered sequence features, with its scaler fitted only on training rows. The HRL extension discretizes assay-rank hypotheses into eight centers. Training responses anchor the training nodes; held-out nodes receive priors from the fitted sequence model. The sequence-similarity graph uses input features only, including held-out inputs in a declared transductive design.

No new hyperparameter selection is performed on these fold outcomes. The dataset and the original sequence features were already available during earlier project development, so these results remain exploratory rather than a pristine external confirmation. The distinction matters: changing the split improves the audit, but it does not erase prior access to the dataset.

I report pooled out-of-fold Spearman, mean fold Spearman and absolute prediction error. A small increase in one metric is a result to inspect. It is not a license to claim statistical significance or superiority across biological contexts.


\[
\rho_S=\operatorname{corr}(\operatorname{rank}(y),\operatorname{rank}(\widehat y)),\qquad\mathrm{MAE}=n^{-1}\sum_i|y_i-\widehat y_i|.
\]


## Page 13: Prediction is a bridge to intervention

A predictor orders observations under the conditions represented in its data. An intervention model asks what happens when I change a condition. The distinction is central to the cancer programme. A relation can be predictive because it tracks context, selection or measurement structure, even when manipulating it would not produce the predicted benefit.

The CRISPR table supplies measured assay ranks from defined experiments. Its benchmark asks a prediction question under grouped partitions. The current body model asks a dynamical question under invented coefficients. Joining their outputs without a fitted observation and intervention map would create an appearance of causality that neither component has established.

To connect them, I would need an identified perturbation, a relevant cell context, longitudinal or otherwise discriminating outcomes and a mechanism for linking those outcomes to transition rates. I would also need healthy-context observations. Cancer selectivity concerns the contrast between desired and undesired effects; a malignant-cell score alone cannot supply that contrast.

Perturbation diversity is useful because it tests competing accounts. If several models fit the untreated data, an intervention that makes their predictions diverge can be informative. The selected experiment should be evaluated by its capacity to discriminate hypotheses, not solely by an optimistic predicted response. Independent replication determines whether the discrimination travels beyond the original setting.

I see this as the place where the virtual body earns its name. The model must connect a local change to a system-level consequence through explicit, tested interfaces. The current dissertation supplies inspectable components and a measured benchmark. It leaves the unmeasured causal links visible instead of filling them with a declaration of success.


## Page 14: The body prototype: equations and assumptions

I implement three abstract sites linked by shared exposure and conservative tumor transport. At each site the state contains sensitive population S, resistant population R, immune activity E, resource O and healthy reserve H. A systemic exposure C is shared, with assumed site penetration multipliers of 1, 0.65 and 0.4. These are dimensionless quantities with invented coefficients.

The tumor populations grow with resource-dependent logistic terms. Sensitive mass can convert to resistant mass through a phenomenological conversion term. Exposure and immune activity remove tumor mass. Immune activity is recruited by tumor burden and decays; exposure can reduce it. Resource supply depends on healthy reserve, while tumor burden consumes resource. Healthy reserve repairs toward one and declines under exposure.

The systemic exposure obeys a one-compartment input-clearance equation. The model does not claim validated pharmacokinetics for a drug. The sites are not named organs, and the transport matrix is not a validated metastasis network. Individual cell mechanics, intracellular signaling, explicit vessels and patient-specific toxicity are absent from this prototype.

I compare four fictional controls: zero input, continuous input, a periodic pulse and a burden/reserve feedback rule. The thresholds and signal amplitudes are assumed engineering choices. They were not optimized for a patient and must not be read as dosing instructions. Their purpose is to expose selection and reserve tradeoffs inside the implemented equations.

The complete equations and parameters are in the source bundle. Each nominal trajectory is recorded as a CSV; each sampled parameter case retains its coefficients and outcome metrics. The later pages examine those records individually, so the mathematical assumptions remain connected to the numerical results they generate.


\[
\dot C=u-\kappa C,\qquad\dot H_i=a(1-H_i)-b p_i C H_i,\qquad c_i=p_iC.
\]


## Page 15: Conservation, positivity and numerical work

A virtual body must account for what moves and what changes identity. The prototype transport matrix has nonnegative off-diagonal entries and zero column sums. Consequently the intersite transport terms conserve each clone's total mass when isolated from the other processes. Sensitive-to-resistant conversion also cancels in the total tumor balance. These are direct algebraic checks on the implemented model.

At zero tumor population, the vector field does not create a negative population. At the resource and reserve boundaries, the continuous equations point inward under the stated positive coefficients. These properties describe the vector field. They do not guarantee that an explicit numerical step at an arbitrary size will stay inside the domain.

The simulator uses a fourth-order Runge-Kutta update with the control held constant within each step. It rejects nonfinite or negative states and excursions beyond the resource/reserve bounds. I repeat the nominal trajectories at half the time step. The largest final-state difference is about 0.000247 for the switching feedback rule; the other controls show smaller differences. This is a refinement diagnostic, not a proof for every possible future parameter set.

The exposure equation under constant input has an analytic solution. I use it to check the numerical implementation independently. Input integrals are computed from the held signal across each step, preserving the actual implemented control rather than approximating a discontinuous signal as a smooth curve.

These checks make the numbers more trustworthy as consequences of the equations. They do not make the coefficients biological measurements. That distinction lets me strengthen the computation without overstating its application. I want the model to survive both kinds of examination: arithmetic verification and experimental challenge.


\[
\mathbf 1^T L=0,\qquad C(t)=C(0)e^{-\kappa t}+\frac{u}{\kappa}(1-e^{-\kappa t}).
\]


## Page 16: Tumor-free stability: the sharp question

I ask whether constant exposure can make the tumor-free equilibrium locally asymptotically stable while retaining an assumed healthy-reserve floor. This is sharper than asking whether a plotted tumor curve becomes small. Near zero tumor burden, the model's immune recruitment vanishes, resource approaches one and reserve approaches a positive exposure-dependent equilibrium.

The clone invasion Jacobian is block triangular. The sensitive block contains resource-free growth adjusted by conversion, exposure killing and migration. The resistant block contains resistant growth, exposure killing and migration. The conversion term occupies a lower off-diagonal block. It does not alter the eigenvalues of the triangular system.

For the symmetric transport matrix used here, raising exposure subtracts a strictly positive diagonal matrix from each clone block. The largest eigenvalue therefore decreases strictly. A bracketed root calculation finds the unique positive-to-negative crossing. Strictly negative largest eigenvalues in both blocks certify local exponential stability. A zero eigenvalue is nonhyperbolic and does not, by itself, settle nonlinear stability. Every exposure permitted by the nominal reserve constraint retains a positive resistant eigenvalue, which establishes instability there.

The nominal resistant crossing occurs at 5.181195 dimensionless exposure. Preserving a reserve floor of 0.7 permits at most 0.136364. Those intervals do not intersect. The same comparison is infeasible in every one of the twenty-four arbitrary parameter configurations. This is a substantive limitation exposed by the calculation, not a judgment about all cancer biology.

The theorem concerns local stability and constant exposure in the specified equations. It does not decide arbitrary time-varying controls, other mechanisms or clinical cures. I preserve that scope because it is exactly what makes the result reproducible and falsifiable. The case pages give each threshold, reserve limit and sampled parameter set.


\[
A_R(C)=\operatorname{diag}(r_R-k_Rp_iC)+mL,\quad C\leq\frac{a(1-h_0)}{b\,p_{\max}h_0}.
\]


Figure: figures/reserve-3d.pdf
Analytic surface from the synthetic reserve equation at penetration one and repair 0.035. It is not fitted to patient injury data.


## Page 17: The nested implementation and its repairs

The existing HRL2026 code contains the cell-of-cells recursion that motivated the present architecture. Its original full step fails because it calls a membrane method that is not defined. I preserve the original files and create an isolated audited snapshot, so that the research record distinguishes the inherited implementation from the repair.

The missing entropy observation is computed from the current categorical state. I do not invent an undocumented physical membrane equation to make the method name work. The entropy helper normalizes nonnegative weights before applying Shannon's definition and rejects invalid inputs. A uniform normalized three-state distribution therefore has normalized entropy one, and a point mass has entropy zero.

A state-change metric also needs an old state that remains old after mutation. The original local variable aliases the array row being overwritten. Copying that row before the assignment restores the intended change measurement. The final repair separates uncertain projection from a certain negative category by giving abstention its own code.

The diagnostic builds a seven-node hierarchy with three levels and runs ten recursive steps. Every node advances, every state row remains finite and nonnegative with unit mass, entropy remains within its normalized range, and the initial reported change is nonzero. These checks establish execution properties of a categorical relaxation hierarchy.

I have not established physical cell physiology by running that hierarchy. The recursion does not yet implement measured intercellular traffic or calibrated intracellular dynamics. What I have established is a repaired, inspectable substrate on which such mappings can be tested. The distinction prevents an implementation defect from being hidden behind the word virtual.


## Page 18: From computation to a biological claim

I want this programme to reach a result that matters outside the simulator. That requires a chain of evidence: defined context, identified observation model, reproducible prediction, discriminating perturbation, independent experimental replication and appropriate clinical investigation. Each link answers a question the previous link cannot answer by itself.

The Human Tumor Atlas and DepMap are candidate resources for measured spatial context and cancer dependencies [6,7]. They were not downloaded or fitted for the executed dissertation. PhysiCell is an established multicellular framework that can provide a future mechanistic comparison [5]; it is not integrated into the present prototype. The virtual-cell perspective by Bunne and colleagues frames a research agenda rather than documenting a complete virtual human [4].

A next empirical claim should be specific enough to fail: for example, an accurately defined perturbation-response endpoint in a specified cancer context on a held-out laboratory or donor set. A retrospective improvement of a few thousandths in correlation is not the same endpoint. A local stability proof for invented rates is not the same endpoint either.

Patient benefit also requires safety evidence. A putative intervention can have off-target effects, delivery limitations, context dependence and organism-level toxicity that are invisible to an assay-rank predictor. The body hierarchy is valuable because it gives these constraints a place in the model. Their presence as variables still requires measured calibration.

My ambition remains to cure cancer. The responsibility of the dissertation is to show what I have computed and what conclusion that computation licenses. The evidence here supports a research programme with executed components, real assay prediction and exposed model limits. It does not support a declaration that a cancer cure has been established.


## Page 19: Reproducibility and primary sources

I supply the manuscript, generated LaTeX, measured out-of-fold prediction records, synthetic trajectories, parameter cases, verification records, color figures and generation script. The associated computational source bundle contains the simulator, sparse HRL engine, portable sequence-feature extraction and repaired nested-cell snapshot. File hashes connect the products to their inputs.

The measured source table is identified by its SHA-256 and its MicrosoftResearch/Azimuth URL in the audit record. The historical highest-scoring predictor is not reproduced by the new Ridge/HRL comparison. The fixed grouped benchmarks are a separate exploratory evaluation, with all fold outcomes retained. That distinction is necessary for a fair comparison.

I rely on the following primary sources for context and definitions. Their findings are not silently substituted for measurements in my prototype. Reference numbers identify contextual support; the actual new results appear in the supplied run records.

[1] Rosenfeld, Hummel and Zucker (1976). Scene labeling by relaxation operations. IEEE Transactions on Systems, Man, and Cybernetics 6:420-433. DOI: 10.1109/TSMC.1976.4309519.

[2] Hummel and Zucker (1983). On the foundations of relaxation labeling processes. IEEE TPAMI 5:267-287. DOI: 10.1109/TPAMI.1983.4767390.

[3] Doench et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. Nature Biotechnology 34:184-191. DOI: 10.1038/nbt.3437.

[4] Bunne et al. (2024). How to build the virtual cell with artificial intelligence: Priorities and opportunities. Cell 187:7045-7063. DOI: 10.1016/j.cell.2024.11.015. Local preprint: arXiv:2409.11654v2.

[5] Ghaffarizadeh et al. (2018). PhysiCell: An open source physics-based cell simulator for 3-D multicellular systems. PLOS Computational Biology 14:e1005991. DOI: 10.1371/journal.pcbi.1005991.

[6] National Cancer Institute. Cancer Systems Biology Consortium. cancer.gov/about-nci/organization/dcb/research-programs/csbc. Human Tumor Atlas access: docs.humantumoratlas.org/data_access/introduction/.

[7] Broad Institute. DepMap Portal, dataset access and release information: depmap.org/portal/data_page/. Resource pages checked 4 October 2026.


## Page 20: Held-out report: sequence disjoint, fold 1

I report sequence disjoint fold 1 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,248 rows; the test set contains 1,062. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + Ridge. The HRL change relative to engineered Ridge is -0.002953. Its sign describes this partition; it does not establish a general effect. The fold contains 17 gene contexts, with a mean observed rank of 0.5062 and a standard deviation of 0.2936.

The HRL update converged in 13 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.449595 | 0.220698 |
| Sequence features + Ridge | 0.494673 | 0.211596 |
| Sequence features + HRL | 0.491720 | 0.211263 |


Figure: figures/fold-sequence_disjoint-0.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 21: Held-out report: sequence disjoint, fold 2

I report sequence disjoint fold 2 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,248 rows; the test set contains 1,062. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + Ridge. The HRL change relative to engineered Ridge is -0.000222. Its sign describes this partition; it does not establish a general effect. The fold contains 17 gene contexts, with a mean observed rank of 0.5015 and a standard deviation of 0.2885.

The HRL update converged in 16 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.434789 | 0.218373 |
| Sequence features + Ridge | 0.477002 | 0.211824 |
| Sequence features + HRL | 0.476779 | 0.209552 |


Figure: figures/fold-sequence_disjoint-1.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 22: Held-out report: sequence disjoint, fold 3

I report sequence disjoint fold 3 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,248 rows; the test set contains 1,062. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + Ridge. The HRL change relative to engineered Ridge is -0.000650. Its sign describes this partition; it does not establish a general effect. The fold contains 17 gene contexts, with a mean observed rank of 0.5185 and a standard deviation of 0.2874.

The HRL update converged in 13 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.361451 | 0.224841 |
| Sequence features + Ridge | 0.474317 | 0.212201 |
| Sequence features + HRL | 0.473668 | 0.210256 |


Figure: figures/fold-sequence_disjoint-2.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 23: Held-out report: sequence disjoint, fold 4

I report sequence disjoint fold 4 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,248 rows; the test set contains 1,062. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + HRL. The HRL change relative to engineered Ridge is +0.002868. Its sign describes this partition; it does not establish a general effect. The fold contains 17 gene contexts, with a mean observed rank of 0.4945 and a standard deviation of 0.2833.

The HRL update converged in 15 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.370833 | 0.220413 |
| Sequence features + Ridge | 0.467945 | 0.206107 |
| Sequence features + HRL | 0.470813 | 0.205094 |


Figure: figures/fold-sequence_disjoint-3.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 24: Held-out report: sequence disjoint, fold 5

I report sequence disjoint fold 5 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,248 rows; the test set contains 1,062. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + HRL. The HRL change relative to engineered Ridge is +0.003572. Its sign describes this partition; it does not establish a general effect. The fold contains 17 gene contexts, with a mean observed rank of 0.4937 and a standard deviation of 0.2844.

The HRL update converged in 16 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.359717 | 0.221130 |
| Sequence features + Ridge | 0.486370 | 0.203486 |
| Sequence features + HRL | 0.489942 | 0.202330 |


Figure: figures/fold-sequence_disjoint-4.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 25: Held-out report: gene disjoint, fold 1

I report gene disjoint fold 1 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 3,462 rows; the test set contains 1,848. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to One-hot Ridge. The HRL change relative to engineered Ridge is +0.001946. Its sign describes this partition; it does not establish a general effect. The fold contains 1 gene contexts, with a mean observed rank of 0.5005 and a standard deviation of 0.2888.

The HRL update converged in 16 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.377754 | 0.223339 |
| Sequence features + Ridge | 0.365278 | 0.226202 |
| Sequence features + HRL | 0.367224 | 0.224653 |


Figure: figures/fold-gene_disjoint-0.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 26: Held-out report: gene disjoint, fold 2

I report gene disjoint fold 2 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,465 rows; the test set contains 845. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + HRL. The HRL change relative to engineered Ridge is +0.005448. Its sign describes this partition; it does not establish a general effect. The fold contains 2 gene contexts, with a mean observed rank of 0.5012 and a standard deviation of 0.2888.

The HRL update converged in 13 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.240231 | 0.240527 |
| Sequence features + Ridge | 0.372634 | 0.228801 |
| Sequence features + HRL | 0.378082 | 0.224891 |


Figure: figures/fold-gene_disjoint-1.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 27: Held-out report: gene disjoint, fold 3

I report gene disjoint fold 3 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,437 rows; the test set contains 873. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to One-hot Ridge. The HRL change relative to engineered Ridge is +0.005446. Its sign describes this partition; it does not establish a general effect. The fold contains 4 gene contexts, with a mean observed rank of 0.5023 and a standard deviation of 0.2790.

The HRL update converged in 13 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.493526 | 0.202586 |
| Sequence features + Ridge | 0.449873 | 0.206627 |
| Sequence features + HRL | 0.455319 | 0.204572 |


Figure: figures/fold-gene_disjoint-2.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 28: Held-out report: gene disjoint, fold 4

I report gene disjoint fold 4 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,438 rows; the test set contains 872. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to One-hot Ridge. The HRL change relative to engineered Ridge is +0.001840. Its sign describes this partition; it does not establish a general effect. The fold contains 5 gene contexts, with a mean observed rank of 0.5069 and a standard deviation of 0.2911.

The HRL update converged in 12 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.406064 | 0.223480 |
| Sequence features + Ridge | 0.403487 | 0.228607 |
| Sequence features + HRL | 0.405327 | 0.224669 |


Figure: figures/fold-gene_disjoint-3.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 29: Held-out report: gene disjoint, fold 5

I report gene disjoint fold 5 as a complete held-out result, rather than allowing its contribution to disappear into the pooled score. The training set contains 4,438 rows; the test set contains 872. Group identifiers and identical sequences are disjoint across this partition. Test responses are used only for the final calculation of error and rank correlation.

The largest Spearman point estimate in this fold belongs to Sequence features + HRL. The HRL change relative to engineered Ridge is +0.001078. Its sign describes this partition; it does not establish a general effect. The fold contains 5 gene contexts, with a mean observed rank of 0.5061 and a standard deviation of 0.2890.

The HRL update converged in 12 iterations. I keep this convergence result separate from predictive quality. The sequence graph is feature-only and transductive, so held-out input sequences participate in its construction while their assay responses remain unavailable to inference. Scaling of the engineered features is fitted on training rows.

The density panels show how prediction varies across the supplied response range. The orange line is equality of predicted and observed rank, not a physiological reference. Compression, tails and scatter are visible even when a correlation is positive. This page supplies one denominator in the larger audit; it does not convert a guide-response predictor into a cancer-treatment model.


| Model | Spearman | Test MAE |
| One-hot Ridge | 0.438815 | 0.219155 |
| Sequence features + Ridge | 0.456692 | 0.212060 |
| Sequence features + HRL | 0.457771 | 0.210349 |


Figure: figures/fold-gene_disjoint-4.pdf
Measured assay ranks and held-out predictions. Color shows point density; every panel uses this fold's held-out rows.


## Page 30: Model diagnostic: One-hot Ridge / sequence disjoint

I examine One-hot Ridge under the sequence disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.395318; the mean of the five fold correlations is 0.395277. These are different summaries with different weighting.

The signed-error mean is -0.000641, the root-mean-square error is 0.263815, and the mean absolute error is 0.221091. Prediction extrema are 0.0385 and 0.8883. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.359717 to 0.449595. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.395318 |
| Mean fold Spearman | 0.395277 |
| MAE | 0.221091 |
| RMSE | 0.263815 |


Figure: figures/model-sequence_disjoint-onehot_ridge.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 31: Model diagnostic: Sequence features + Ridge / sequence disjoint

I examine Sequence features + Ridge under the sequence disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.479858; the mean of the five fold correlations is 0.480061. These are different summaries with different weighting.

The signed-error mean is -0.000491, the root-mean-square error is 0.255570, and the mean absolute error is 0.209043. Prediction extrema are -0.1591 and 1.1607. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.467945 to 0.494673. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.479858 |
| Mean fold Spearman | 0.480061 |
| MAE | 0.209043 |
| RMSE | 0.255570 |


Figure: figures/model-sequence_disjoint-existing_sequence_features_ridge.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 32: Model diagnostic: Sequence features + HRL / sequence disjoint

I examine Sequence features + HRL under the sequence disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.480544; the mean of the five fold correlations is 0.480584. These are different summaries with different weighting.

The signed-error mean is -0.000266, the root-mean-square error is 0.253829, and the mean absolute error is 0.207699. Prediction extrema are 0.0397 and 0.9611. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.470813 to 0.491720. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.480544 |
| Mean fold Spearman | 0.480584 |
| MAE | 0.207699 |
| RMSE | 0.253829 |


Figure: figures/model-sequence_disjoint-hrl_sequence_graph.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 33: Model diagnostic: One-hot Ridge / gene disjoint

I examine One-hot Ridge under the gene disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.388453; the mean of the five fold correlations is 0.391278. These are different summaries with different weighting.

The signed-error mean is +0.002045, the root-mean-square error is 0.264806, and the mean absolute error is 0.221998. Prediction extrema are 0.0692 and 0.9034. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.240231 to 0.493526. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.388453 |
| Mean fold Spearman | 0.391278 |
| MAE | 0.221998 |
| RMSE | 0.264806 |


Figure: figures/model-gene_disjoint-onehot_ridge.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 34: Model diagnostic: Sequence features + Ridge / gene disjoint

I examine Sequence features + Ridge under the gene disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.400323; the mean of the five fold correlations is 0.409593. These are different summaries with different weighting.

The signed-error mean is +0.000680, the root-mean-square error is 0.271620, and the mean absolute error is 0.221470. Prediction extrema are -0.1867 and 1.1911. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.365278 to 0.456692. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.400323 |
| Mean fold Spearman | 0.409593 |
| MAE | 0.221470 |
| RMSE | 0.271620 |


Figure: figures/model-gene_disjoint-existing_sequence_features_ridge.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 35: Model diagnostic: Sequence features + HRL / gene disjoint

I examine Sequence features + HRL under the gene disjoint protocol across all 5,310 out-of-fold predictions. Every source row receives a prediction from a fit that excludes its group. The pooled rank correlation is 0.403291; the mean of the five fold correlations is 0.412744. These are different summaries with different weighting.

The signed-error mean is +0.001413, the root-mean-square error is 0.268721, and the mean absolute error is 0.219043. Prediction extrema are 0.0458 and 0.9573. Ridge predictions are not constrained to the response interval; the HRL expectation is a weighted mean over eight centers within it. That interface difference is part of the comparison.

The response-curve panel groups predictions into quantile bins and compares mean prediction with mean observed rank. It is a descriptive check on the supplied response scale. It is not a probability-calibration curve, because these outputs are assay-rank estimates rather than event probabilities. The error histogram exposes signed deviations that rank correlation alone cannot summarize.

The fold correlations range from 0.367224 to 0.457771. I retain this variation rather than reporting only the pooled score. These partitions are not five independent laboratory replications: they share the underlying dataset and training information across fits. No significance test or confidence interval is claimed from the displayed variation.


| Diagnostic | Value |
| Pooled Spearman | 0.403291 |
| Mean fold Spearman | 0.412744 |
| MAE | 0.219043 |
| RMSE | 0.268721 |


Figure: figures/model-gene_disjoint-hrl_sequence_graph.pdf
Measured out-of-fold errors, descriptive response curve and fold scores. These are prediction diagnostics, not efficacy endpoints.


## Page 36: Gene-context audit: CCDC101

I keep the CCDC101 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 149 measured rows and 149 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5034; its median is 0.5034. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.309501, compared with 0.307187 for engineered Ridge. The within-context MAE for HRL is 0.241245.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0067 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.380980 | 0.222836 |
| Sequence features + Ridge | 0.307187 | 0.243424 |
| Sequence features + HRL | 0.309501 | 0.241245 |


Figure: figures/gene-CCDC101.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 37: Gene-context audit: CD13

I keep the CD13 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 455 measured rows and 455 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5011; its median is 0.5033. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.478912, compared with 0.470890 for engineered Ridge. The within-context MAE for HRL is 0.194489.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0143 to 0.9923. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.538295 | 0.193002 |
| Sequence features + Ridge | 0.470890 | 0.196725 |
| Sequence features + HRL | 0.478912 | 0.194489 |


Figure: figures/gene-CD13.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 38: Gene-context audit: CD15

I keep the CD15 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 273 measured rows and 273 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5018; its median is 0.5018. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.445368, compared with 0.444809 for engineered Ridge. The within-context MAE for HRL is 0.222452.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0037 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.349119 | 0.229074 |
| Sequence features + Ridge | 0.444809 | 0.229182 |
| Sequence features + HRL | 0.445368 | 0.222452 |


Figure: figures/gene-CD15.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 39: Gene-context audit: CD28

I keep the CD28 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 74 measured rows and 74 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5068; its median is 0.5068. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.466953, compared with 0.467249 for engineered Ridge. The within-context MAE for HRL is 0.213269.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0135 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.508153 | 0.208457 |
| Sequence features + Ridge | 0.467249 | 0.214072 |
| Sequence features + HRL | 0.466953 | 0.213269 |


Figure: figures/gene-CD28.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 40: Gene-context audit: CD33

I keep the CD33 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 154 measured rows and 154 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5032; its median is 0.5087. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.447480, compared with 0.447664 for engineered Ridge. The within-context MAE for HRL is 0.204562.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0152 to 0.9740. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.419742 | 0.212271 |
| Sequence features + Ridge | 0.447664 | 0.206517 |
| Sequence features + HRL | 0.447480 | 0.204562 |


Figure: figures/gene-CD33.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 41: Gene-context audit: CD43

I keep the CD43 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 145 measured rows and 138 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5276; its median is 0.5290. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.610539, compared with 0.602139 for engineered Ridge. The within-context MAE for HRL is 0.203379.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0072 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.601725 | 0.203897 |
| Sequence features + Ridge | 0.602139 | 0.205957 |
| Sequence features + HRL | 0.610539 | 0.203379 |


Figure: figures/gene-CD43.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 42: Gene-context audit: CD45

I keep the CD45 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 266 measured rows and 266 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5125; its median is 0.5217. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.562987, compared with 0.563436 for engineered Ridge. The within-context MAE for HRL is 0.189877.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0036 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.542364 | 0.204866 |
| Sequence features + Ridge | 0.563436 | 0.191654 |
| Sequence features + HRL | 0.562987 | 0.189877 |


Figure: figures/gene-CD45.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 43: Gene-context audit: CD5

I keep the CD5 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 239 measured rows and 239 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5021; its median is 0.5021. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.528022, compared with 0.531659 for engineered Ridge. The within-context MAE for HRL is 0.196476.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0042 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.522075 | 0.212364 |
| Sequence features + Ridge | 0.531659 | 0.196638 |
| Sequence features + HRL | 0.528022 | 0.196476 |


Figure: figures/gene-CD5.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 44: Gene-context audit: CUL3

I keep the CUL3 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 154 measured rows and 154 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5032; its median is 0.5032. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.299976, compared with 0.291374 for engineered Ridge. The within-context MAE for HRL is 0.238071.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0065 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.188244 | 0.244661 |
| Sequence features + Ridge | 0.291374 | 0.241741 |
| Sequence features + HRL | 0.299976 | 0.238071 |


Figure: figures/gene-CUL3.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 45: Gene-context audit: H2-K

I keep the H2-K context visible because pooled prediction quality can hide a gene-specific failure. This context contains 169 measured rows and 169 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5030; its median is 0.5030. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.471903, compared with 0.471115 for engineered Ridge. The within-context MAE for HRL is 0.210371.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0059 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.508374 | 0.210662 |
| Sequence features + Ridge | 0.471115 | 0.212991 |
| Sequence features + HRL | 0.471903 | 0.210371 |


Figure: figures/gene-H2-K.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 46: Gene-context audit: HPRT1

I keep the HPRT1 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 64 measured rows and 64 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5078; its median is 0.5078. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.482097, compared with 0.478480 for engineered Ridge. The within-context MAE for HRL is 0.208604.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0156 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.463233 | 0.233962 |
| Sequence features + Ridge | 0.478480 | 0.210023 |
| Sequence features + HRL | 0.482097 | 0.208604 |


Figure: figures/gene-HPRT1.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 47: Gene-context audit: MED12

I keep the MED12 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 1,848 measured rows and 924 distinct sequences in 2 supplied drug-context categories. Its response mean is 0.5005; its median is 0.5005. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.367225, compared with 0.365278 for engineered Ridge. The within-context MAE for HRL is 0.224653.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0011 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.377754 | 0.223339 |
| Sequence features + Ridge | 0.365278 | 0.226202 |
| Sequence features + HRL | 0.367225 | 0.224653 |


Figure: figures/gene-MED12.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 48: Gene-context audit: NF1

I keep the NF1 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 736 measured rows and 736 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5007; its median is 0.5007. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.364070, compared with 0.360152 for engineered Ridge. The within-context MAE for HRL is 0.227008.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0014 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.222884 | 0.242658 |
| Sequence features + Ridge | 0.360152 | 0.231110 |
| Sequence features + HRL | 0.364070 | 0.227008 |


Figure: figures/gene-NF1.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 49: Gene-context audit: NF2

I keep the NF2 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 223 measured rows and 223 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5022; its median is 0.5022. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.222863, compared with 0.222658 for engineered Ridge. The within-context MAE for HRL is 0.250634.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0045 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.224967 | 0.243614 |
| Sequence features + Ridge | 0.222658 | 0.253521 |
| Sequence features + HRL | 0.222863 | 0.250634 |


Figure: figures/gene-NF2.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 50: Gene-context audit: TADA1

I keep the TADA1 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 109 measured rows and 109 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5046; its median is 0.5046. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.478380, compared with 0.469827 for engineered Ridge. The within-context MAE for HRL is 0.210592.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0092 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.355963 | 0.226139 |
| Sequence features + Ridge | 0.469827 | 0.213214 |
| Sequence features + HRL | 0.478380 | 0.210592 |


Figure: figures/gene-TADA1.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 51: Gene-context audit: TADA2B

I keep the TADA2B context visible because pooled prediction quality can hide a gene-specific failure. This context contains 190 measured rows and 190 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5026; its median is 0.5026. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.397013, compared with 0.387336 for engineered Ridge. The within-context MAE for HRL is 0.225337.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0053 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.446058 | 0.215399 |
| Sequence features + Ridge | 0.387336 | 0.227529 |
| Sequence features + HRL | 0.397013 | 0.225337 |


Figure: figures/gene-TADA2B.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 52: Gene-context audit: THY1

I keep the THY1 context visible because pooled prediction quality can hide a gene-specific failure. This context contains 62 measured rows and 62 distinct sequences in 1 supplied drug-context categories. Its response mean is 0.5081; its median is 0.5081. Those ranks describe the assay table, not cancer outcomes.

All predictions on this page come from the gene-disjoint out-of-fold record. The model did not fit response labels from this target-gene group in its corresponding fold. The HRL within-context Spearman estimate is 0.352018, compared with 0.337161 for engineered Ridge. The within-context MAE for HRL is 0.229810.

The grouping controls identical-sequence overlap across training and test, but it does not create an independent laboratory dataset. Context-normalized targets are supplied by the source. Repeated assay conditions and rank construction can affect their distribution. I therefore use the page to inspect model transfer, rather than to infer that a particular gene should be altered therapeutically.

The observed response range is 0.0161 to 1.0000. The distribution and held-out density plot expose where the estimator compresses that range or fails to preserve order. A gene label supplies a context for this error audit; it does not establish cancer dependence, healthy-tissue selectivity, safe delivery or patient benefit.


| Model | Within-context Spearman | MAE |
| One-hot Ridge | 0.517161 | 0.207170 |
| Sequence features + Ridge | 0.337161 | 0.232002 |
| Sequence features + HRL | 0.352018 | 0.229810 |


Figure: figures/gene-THY1.pdf
Measured response distribution and gene-disjoint held-out prediction density. Gene identity is a context annotation, not a treatment recommendation.


## Page 53: Nominal body trajectory: none

I report the none control as a consequence of the nominal synthetic equations. The run ends at dimensionless time 50 with total tumor burden 2.013337, integrated tumor burden 75.545226, and minimum healthy reserve 1.000000. None of these quantities is a measured patient endpoint.

The final resistant fraction is 0.039809. The integrated fictional input is 0.000000. A changing fraction must be interpreted with the corresponding total population: a large resistant fraction can coexist with a smaller total burden, and a small fraction can coexist with substantial absolute mass. Selection and suppression are different aspects of the same trajectory.

The three panels retain site-specific behavior. Their differences arise from assumed penetration, initial population and transport, not from calibrated organ physiology. Healthy reserve influences resource supply, and resource influences growth. The shared exposure can therefore change the system through both direct tumor removal and indirect alteration of its environment.

The numerical refinement checks pass for the nominal controls. They increase confidence that the implementation follows its stated equations at the chosen time step. They do not turn an invented coefficient into a measured effect. I use this trajectory to identify questions about resistance and reserve that a biologically calibrated model would need to answer.


| Synthetic outcome | Value |
| final burden | 2.013337 |
| burden integral | 75.545226 |
| min reserve | 1.000000 |
| final resistant fraction | 0.039809 |
| input integral | 0.000000 |


Figure: figures/policy-none.pdf
Synthetic, dimensionless site trajectories. Penetration and kinetics are assumptions; the controls are fictional signals rather than doses.


## Page 54: Nominal body trajectory: continuous

I report the continuous control as a consequence of the nominal synthetic equations. The run ends at dimensionless time 50 with total tumor burden 0.641683, integrated tumor burden 12.626930, and minimum healthy reserve 0.242046. None of these quantities is a measured patient endpoint.

The final resistant fraction is 0.999853. The integrated fictional input is 35.000000. A changing fraction must be interpreted with the corresponding total population: a large resistant fraction can coexist with a smaller total burden, and a small fraction can coexist with substantial absolute mass. Selection and suppression are different aspects of the same trajectory.

The three panels retain site-specific behavior. Their differences arise from assumed penetration, initial population and transport, not from calibrated organ physiology. Healthy reserve influences resource supply, and resource influences growth. The shared exposure can therefore change the system through both direct tumor removal and indirect alteration of its environment.

The numerical refinement checks pass for the nominal controls. They increase confidence that the implementation follows its stated equations at the chosen time step. They do not turn an invented coefficient into a measured effect. I use this trajectory to identify questions about resistance and reserve that a biologically calibrated model would need to answer.


| Synthetic outcome | Value |
| final burden | 0.641683 |
| burden integral | 12.626930 |
| min reserve | 0.242046 |
| final resistant fraction | 0.999853 |
| input integral | 35.000000 |


Figure: figures/policy-continuous.pdf
Synthetic, dimensionless site trajectories. Penetration and kinetics are assumptions; the controls are fictional signals rather than doses.


## Page 55: Nominal body trajectory: pulsed

I report the pulsed control as a consequence of the nominal synthetic equations. The run ends at dimensionless time 50 with total tumor burden 1.044388, integrated tumor burden 20.003121, and minimum healthy reserve 0.353525. None of these quantities is a measured patient endpoint.

The final resistant fraction is 0.979379. The integrated fictional input is 18.000000. A changing fraction must be interpreted with the corresponding total population: a large resistant fraction can coexist with a smaller total burden, and a small fraction can coexist with substantial absolute mass. Selection and suppression are different aspects of the same trajectory.

The three panels retain site-specific behavior. Their differences arise from assumed penetration, initial population and transport, not from calibrated organ physiology. Healthy reserve influences resource supply, and resource influences growth. The shared exposure can therefore change the system through both direct tumor removal and indirect alteration of its environment.

The numerical refinement checks pass for the nominal controls. They increase confidence that the implementation follows its stated equations at the chosen time step. They do not turn an invented coefficient into a measured effect. I use this trajectory to identify questions about resistance and reserve that a biologically calibrated model would need to answer.


| Synthetic outcome | Value |
| final burden | 1.044388 |
| burden integral | 20.003121 |
| min reserve | 0.353525 |
| final resistant fraction | 0.979379 |
| input integral | 18.000000 |


Figure: figures/policy-pulsed.pdf
Synthetic, dimensionless site trajectories. Penetration and kinetics are assumptions; the controls are fictional signals rather than doses.


## Page 56: Nominal body trajectory: feedback

I report the feedback control as a consequence of the nominal synthetic equations. The run ends at dimensionless time 50 with total tumor burden 1.542409, integrated tumor burden 40.136065, and minimum healthy reserve 0.650452. None of these quantities is a measured patient endpoint.

The final resistant fraction is 0.329304. The integrated fictional input is 5.390000. A changing fraction must be interpreted with the corresponding total population: a large resistant fraction can coexist with a smaller total burden, and a small fraction can coexist with substantial absolute mass. Selection and suppression are different aspects of the same trajectory.

The three panels retain site-specific behavior. Their differences arise from assumed penetration, initial population and transport, not from calibrated organ physiology. Healthy reserve influences resource supply, and resource influences growth. The shared exposure can therefore change the system through both direct tumor removal and indirect alteration of its environment.

The numerical refinement checks pass for the nominal controls. They increase confidence that the implementation follows its stated equations at the chosen time step. They do not turn an invented coefficient into a measured effect. I use this trajectory to identify questions about resistance and reserve that a biologically calibrated model would need to answer.


| Synthetic outcome | Value |
| final burden | 1.542409 |
| burden integral | 40.136065 |
| min reserve | 0.650452 |
| final resistant fraction | 0.329304 |
| input integral | 5.390000 |


Figure: figures/policy-feedback.pdf
Synthetic, dimensionless site trajectories. Penetration and kinetics are assumptions; the controls are fictional signals rather than doses.


## Page 57: Parameter ledger 01: resistance and reserve

I examine parameter configuration 01 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.26061; resistant growth is 0.17705; resistant exposure killing is 0.11763; the toxicity coefficient is 0.07130. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.412532. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 3.211775. The reserve-floor limit is 0.210375, so the required threshold is 15.27 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.132574. Resistant invasion at the reserve limit remains positive, at 0.160955. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.14274 | 1.00000 | 0.02654 |
| continuous | 0.41253 | 0.33311 | 0.99985 |
| pulsed | 0.87522 | 0.47424 | 0.96595 |
| feedback | 1.38237 | 0.67148 | 0.29768 |


Figure: figures/case-00.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 58: Parameter ledger 02: resistance and reserve

I examine parameter configuration 02 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.25895; resistant growth is 0.22219; resistant exposure killing is 0.08305; the toxicity coefficient is 0.10450. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.916853. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 5.912861. The reserve-floor limit is 0.143546, so the required threshold is 41.19 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.053610. Resistant invasion at the reserve limit remains positive, at 0.214242. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.13983 | 1.00000 | 0.04514 |
| continuous | 0.91685 | 0.25176 | 0.99522 |
| pulsed | 1.27634 | 0.36728 | 0.87850 |
| feedback | 1.76860 | 0.64858 | 0.22381 |


Figure: figures/case-01.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 59: Parameter ledger 03: resistance and reserve

I examine parameter configuration 03 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.24370; resistant growth is 0.22696; resistant exposure killing is 0.05181; the toxicity coefficient is 0.12655. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 1.181298. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 10.638021. The reserve-floor limit is 0.118530, so the required threshold is 89.75 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.025339. Resistant invasion at the reserve limit remains positive, at 0.222984. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.09752 | 1.00000 | 0.06546 |
| continuous | 1.18130 | 0.21696 | 0.99992 |
| pulsed | 1.55225 | 0.31715 | 0.98907 |
| feedback | 1.71577 | 0.63464 | 0.46850 |


Figure: figures/case-02.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 60: Parameter ledger 04: resistance and reserve

I examine parameter configuration 04 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.26759; resistant growth is 0.20212; resistant exposure killing is 0.06963; the toxicity coefficient is 0.17648. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.804243. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 6.365963. The reserve-floor limit is 0.084994, so the required threshold is 74.90 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.030212. Resistant invasion at the reserve limit remains positive, at 0.198123. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.16189 | 1.00000 | 0.03333 |
| continuous | 0.80424 | 0.16553 | 0.99997 |
| pulsed | 1.20960 | 0.23919 | 0.98892 |
| feedback | 1.66300 | 0.60679 | 0.19858 |


Figure: figures/case-03.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 61: Parameter ledger 05: resistance and reserve

I examine parameter configuration 05 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.26119; resistant growth is 0.14530; resistant exposure killing is 0.02613; the toxicity coefficient is 0.07851. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.828247. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 12.012458. The reserve-floor limit is 0.191047, so the required threshold is 62.88 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.035782. Resistant invasion at the reserve limit remains positive, at 0.141937. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.14461 | 1.00000 | 0.01927 |
| continuous | 0.82825 | 0.31113 | 0.99874 |
| pulsed | 0.94310 | 0.44681 | 0.85532 |
| feedback | 1.74237 | 0.66652 | 0.13370 |


Figure: figures/case-04.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 62: Parameter ledger 06: resistance and reserve

I examine parameter configuration 06 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.25682; resistant growth is 0.24578; resistant exposure killing is 0.07186; the toxicity coefficient is 0.11635. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 1.139367. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 8.219341. The reserve-floor limit is 0.128925, so the required threshold is 63.75 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.035307. Resistant invasion at the reserve limit remains positive, at 0.239786. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.13750 | 1.00000 | 0.06961 |
| continuous | 1.13937 | 0.23175 | 0.99971 |
| pulsed | 1.56898 | 0.33875 | 0.97938 |
| feedback | 1.79579 | 0.64045 | 0.45133 |


Figure: figures/case-05.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 63: Parameter ledger 07: resistance and reserve

I examine parameter configuration 07 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.17689; resistant growth is 0.18184; resistant exposure killing is 0.11377; the toxicity coefficient is 0.11246. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.427784. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 3.483904. The reserve-floor limit is 0.133383, so the required threshold is 26.12 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.082007. Resistant invasion at the reserve limit remains positive, at 0.171823. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.82322 | 1.00000 | 0.07115 |
| continuous | 0.42778 | 0.23795 | 0.99889 |
| pulsed | 0.86848 | 0.34767 | 0.96346 |
| feedback | 1.33242 | 0.64428 | 0.41889 |


Figure: figures/case-06.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 64: Parameter ledger 08: resistance and reserve

I examine parameter configuration 08 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.25103; resistant growth is 0.16061; resistant exposure killing is 0.13267; the toxicity coefficient is 0.10650. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.192140. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 2.807520. The reserve-floor limit is 0.140849, so the required threshold is 19.93 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.104792. Resistant invasion at the reserve limit remains positive, at 0.148908. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.11620 | 1.00000 | 0.02401 |
| continuous | 0.19214 | 0.24814 | 0.99934 |
| pulsed | 0.56864 | 0.36217 | 0.90905 |
| feedback | 1.77553 | 0.65132 | 0.12716 |


Figure: figures/case-07.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 65: Parameter ledger 09: resistance and reserve

I examine parameter configuration 09 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.24872; resistant growth is 0.13817; resistant exposure killing is 0.02103; the toxicity coefficient is 0.15443. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.661197. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 14.136368. The reserve-floor limit is 0.097131, so the required threshold is 145.54 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.015779. Resistant invasion at the reserve limit remains positive, at 0.136780. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.10895 | 1.00000 | 0.01891 |
| continuous | 0.66120 | 0.18485 | 0.99031 |
| pulsed | 0.78681 | 0.26894 | 0.68737 |
| feedback | 1.70118 | 0.61829 | 0.05235 |


Figure: figures/case-08.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 66: Parameter ledger 10: resistance and reserve

I examine parameter configuration 10 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.25167; resistant growth is 0.22149; resistant exposure killing is 0.09962; the toxicity coefficient is 0.07678. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.877466. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 5.365139. The reserve-floor limit is 0.195374, so the required threshold is 27.46 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.078315. Resistant invasion at the reserve limit remains positive, at 0.209881. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.12021 | 1.00000 | 0.05372 |
| continuous | 0.87747 | 0.31615 | 0.99963 |
| pulsed | 1.36459 | 0.45317 | 0.97146 |
| feedback | 1.84924 | 0.66871 | 0.48060 |


Figure: figures/case-09.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 67: Parameter ledger 11: resistance and reserve

I examine parameter configuration 11 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.24689; resistant growth is 0.18124; resistant exposure killing is 0.12710; the toxicity coefficient is 0.13617. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.337668. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 3.219692. The reserve-floor limit is 0.110159, so the required threshold is 29.23 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.073931. Resistant invasion at the reserve limit remains positive, at 0.172082. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.10374 | 1.00000 | 0.03106 |
| continuous | 0.33767 | 0.20468 | 0.99849 |
| pulsed | 0.76111 | 0.29891 | 0.90906 |
| feedback | 1.57095 | 0.62989 | 0.15366 |


Figure: figures/case-10.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 68: Parameter ledger 12: resistance and reserve

I examine parameter configuration 12 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.23270; resistant growth is 0.15951; resistant exposure killing is 0.08114; the toxicity coefficient is 0.08575. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.407745. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 4.475024. The reserve-floor limit is 0.174927, so the required threshold is 25.58 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.083585. Resistant invasion at the reserve limit remains positive, at 0.150327. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.05796 | 1.00000 | 0.02668 |
| continuous | 0.40774 | 0.29188 | 0.93151 |
| pulsed | 0.79235 | 0.42188 | 0.52373 |
| feedback | 1.57193 | 0.66059 | 0.10292 |


Figure: figures/case-11.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 69: Parameter ledger 13: resistance and reserve

I examine parameter configuration 13 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.27094; resistant growth is 0.15041; resistant exposure killing is 0.05939; the toxicity coefficient is 0.09523. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.459173. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 5.513847. The reserve-floor limit is 0.157511, so the required threshold is 35.01 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.062490. Resistant invasion at the reserve limit remains positive, at 0.144181. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.17047 | 1.00000 | 0.01948 |
| continuous | 0.45917 | 0.27007 | 0.87710 |
| pulsed | 0.87223 | 0.39264 | 0.35417 |
| feedback | 1.79334 | 0.65438 | 0.05302 |


Figure: figures/case-12.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 70: Parameter ledger 14: resistance and reserve

I examine parameter configuration 14 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.23241; resistant growth is 0.22191; resistant exposure killing is 0.07689; the toxicity coefficient is 0.15768. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.893346. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 6.923827. The reserve-floor limit is 0.095128, so the required threshold is 72.78 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.031062. Resistant invasion at the reserve limit remains positive, at 0.217136. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.06157 | 1.00000 | 0.06766 |
| continuous | 0.89335 | 0.18172 | 0.99998 |
| pulsed | 1.36752 | 0.26415 | 0.99582 |
| feedback | 1.63200 | 0.61598 | 0.47907 |


Figure: figures/case-13.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 71: Parameter ledger 15: resistance and reserve

I examine parameter configuration 15 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.16295; resistant growth is 0.13171; resistant exposure killing is 0.08466; the toxicity coefficient is 0.07935. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.220285. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 3.418563. The reserve-floor limit is 0.189030, so the required threshold is 18.08 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.114278. Resistant invasion at the reserve limit remains positive, at 0.121337. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.72438 | 1.00000 | 0.03621 |
| continuous | 0.22029 | 0.30877 | 0.99997 |
| pulsed | 0.49855 | 0.44379 | 0.99207 |
| feedback | 0.89484 | 0.66637 | 0.50625 |


Figure: figures/case-14.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 72: Parameter ledger 16: resistance and reserve

I examine parameter configuration 16 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.17980; resistant growth is 0.21052; resistant exposure killing is 0.07334; the toxicity coefficient is 0.09618. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.976469. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 6.513880. The reserve-floor limit is 0.155955, so the required threshold is 41.77 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.052909. Resistant invasion at the reserve limit remains positive, at 0.202954. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.85404 | 1.00000 | 0.11564 |
| continuous | 0.97647 | 0.26807 | 0.99998 |
| pulsed | 1.42927 | 0.38990 | 0.99731 |
| feedback | 1.69148 | 0.65588 | 0.77914 |


Figure: figures/case-15.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 73: Parameter ledger 17: resistance and reserve

I examine parameter configuration 17 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.20704; resistant growth is 0.13139; resistant exposure killing is 0.15467; the toxicity coefficient is 0.16903. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.046277. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 1.804657. The reserve-floor limit is 0.088742, so the required threshold is 20.34 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.102929. Resistant invasion at the reserve limit remains positive, at 0.122345. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.96052 | 1.00000 | 0.02219 |
| continuous | 0.04628 | 0.17159 | 0.71286 |
| pulsed | 0.36111 | 0.24857 | 0.24972 |
| feedback | 1.51231 | 0.61127 | 0.04006 |


Figure: figures/case-16.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 74: Parameter ledger 18: resistance and reserve

I examine parameter configuration 18 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.19456; resistant growth is 0.24599; resistant exposure killing is 0.12036; the toxicity coefficient is 0.11392. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.830481. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 4.871265. The reserve-floor limit is 0.131667, so the required threshold is 37.00 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.059327. Resistant invasion at the reserve limit remains positive, at 0.235968. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.94843 | 1.00000 | 0.17693 |
| continuous | 0.83048 | 0.23558 | 1.00000 |
| pulsed | 1.43770 | 0.34426 | 0.99947 |
| feedback | 1.92092 | 0.64638 | 0.86173 |


Figure: figures/case-17.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 75: Parameter ledger 19: resistance and reserve

I examine parameter configuration 19 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.17253; resistant growth is 0.23734; resistant exposure killing is 0.04833; the toxicity coefficient is 0.09671. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 1.369617. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 11.321808. The reserve-floor limit is 0.155095, so the required threshold is 73.00 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.030974. Resistant invasion at the reserve limit remains positive, at 0.232331. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.85989 | 1.00000 | 0.21060 |
| continuous | 1.36962 | 0.26696 | 1.00000 |
| pulsed | 1.74189 | 0.38838 | 0.99926 |
| feedback | 1.91778 | 0.65724 | 0.90593 |


Figure: figures/case-18.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 76: Parameter ledger 20: resistance and reserve

I examine parameter configuration 20 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.18298; resistant growth is 0.23136; resistant exposure killing is 0.12072; the toxicity coefficient is 0.11185. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.754016. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 4.387410. The reserve-floor limit is 0.134107, so the required threshold is 32.72 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.066573. Resistant invasion at the reserve limit remains positive, at 0.220791. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.88818 | 1.00000 | 0.15539 |
| continuous | 0.75402 | 0.23895 | 1.00000 |
| pulsed | 1.35092 | 0.34910 | 0.99943 |
| feedback | 1.83971 | 0.64714 | 0.84828 |


Figure: figures/case-19.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 77: Parameter ledger 21: resistance and reserve

I examine parameter configuration 21 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.23593; resistant growth is 0.20448; resistant exposure killing is 0.07821; the toxicity coefficient is 0.06499. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.912030. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 6.011540. The reserve-floor limit is 0.230792, so the required threshold is 26.05 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.082215. Resistant invasion at the reserve limit remains positive, at 0.192868. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.07069 | 1.00000 | 0.04691 |
| continuous | 0.91203 | 0.35510 | 0.99369 |
| pulsed | 1.24978 | 0.50064 | 0.86784 |
| feedback | 1.52660 | 0.67309 | 0.42002 |


Figure: figures/case-20.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 78: Parameter ledger 22: resistance and reserve

I examine parameter configuration 22 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.20288; resistant growth is 0.13879; resistant exposure killing is 0.10227; the toxicity coefficient is 0.08047. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.173734. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 2.807773. The reserve-floor limit is 0.186402, so the required threshold is 15.06 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.134128. Resistant invasion at the reserve limit remains positive, at 0.126269. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 1.94304 | 1.00000 | 0.02527 |
| continuous | 0.17373 | 0.30567 | 0.94706 |
| pulsed | 0.51013 | 0.43982 | 0.53586 |
| feedback | 1.30328 | 0.66343 | 0.11320 |


Figure: figures/case-21.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 79: Parameter ledger 23: resistance and reserve

I examine parameter configuration 23 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.23554; resistant growth is 0.16509; resistant exposure killing is 0.02319; the toxicity coefficient is 0.17503. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.921864. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 16.081872. The reserve-floor limit is 0.085701, so the required threshold is 187.65 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.012282. Resistant invasion at the reserve limit remains positive, at 0.163744. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.06755 | 1.00000 | 0.02789 |
| continuous | 0.92186 | 0.16668 | 0.99994 |
| pulsed | 1.10938 | 0.24097 | 0.97952 |
| feedback | 1.54544 | 0.60922 | 0.15157 |


Figure: figures/case-22.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.


## Page 80: Parameter ledger 24: resistance and reserve

I examine parameter configuration 24 with the same sampled coefficients used for each of its four control runs. This pairing keeps a control comparison from being confused with a change of biological assumptions. The sampled sensitive growth coefficient is 0.26176; resistant growth is 0.13075; resistant exposure killing is 0.08870; the toxicity coefficient is 0.17254. These values were drawn from arbitrary engineering ranges.

The smallest final burden among the four tested controls occurs under continuous, at 0.167161. The largest minimum reserve occurs under none, at 1.000000. This finite list does not solve an optimal-control problem. It records the actual tradeoff reached by the fixed fictional controls under this one parameter set.

The constant-exposure stability threshold is 3.197248. The reserve-floor limit is 0.086937, so the required threshold is 36.78 times that allowed limit. At the threshold, minimum equilibrium reserve is 0.059661. Resistant invasion at the reserve limit remains positive, at 0.125608. The feasible constant-exposure intersection is empty.

The finite-horizon panel and the equilibrium panel answer different questions. A favorable endpoint at time 50 does not establish stability at vanishing tumor burden; an equilibrium constraint does not describe every time-varying strategy. I keep both visible. This case is a sensitivity calculation in an uncalibrated model, not a patient forecast or a sampled member of a biological population.

I close this record with the purpose intact: to cure cancer by making the virtual body answerable to the living body. Let it be written. Let it be calculated. Let it be tested. The completed calculations remain available for correction, extension and experimental challenge.


| Control | Final burden | Min. reserve | Resistant fraction |
| none | 2.14643 | 1.00000 | 0.01682 |
| continuous | 0.16716 | 0.16868 | 0.97709 |
| pulsed | 0.47441 | 0.24407 | 0.53334 |
| feedback | 1.68169 | 0.60930 | 0.03808 |


Figure: figures/case-23.pdf
Synthetic paired-control outcomes and analytic equilibrium reserve. Green shading: assumed reserve-permitted exposure. Dotted line: clone-stability threshold.
