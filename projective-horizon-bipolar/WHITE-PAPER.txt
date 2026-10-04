# An Axiomatic and Numerical Approach to Modeling Bipolar Disorder

Michael Emanuel Glover. Developed in dialogue with Codex. 4 October 2026.


## 1. An Axiomatic and Numerical Approach to Modeling Bipolar Disorder

I propose a projective horizon: an observer-dependent view of a statistical landscape. My starting image is a hypergaussian field in four dimensions, with three components intended to separate self-directed harm-related content, other-directed harm-related content and a broader field of activation, appraisal and context. I want that image to become a mathematical object that can be checked, not merely a phrase that feels explanatory.

I am interested in the tension between imagined capability and achieved action. The wish to accomplish something substantial can be constructive. An escalating appraisal of personal power can also become detached from evidence. My model must keep those possibilities distinguishable. It cannot decide a person's value, diagnosis or future violence from a geometric position.

The work proceeds through primitives, definitions, declared axioms, proofs and numerical illustrations. I give the projective transformation an explicit domain and Jacobian, explain how Gaussian source coordinates can generate heavy-tailed ratios, and identify the conflict between a full four-dimensional density and an exactly three-dimensional support.

My larger objective is better understanding and eventually better treatment research. The completed contribution is a formal proposal with synthetic calculations. No patient cohort, fitted psychiatric mechanism, clinical risk predictor or medication optimizer is supplied. I make that scope part of the theory because a hypothesis becomes more useful when another investigator can see precisely what would test it.

Real analysis belongs to anyone prepared to define the objects and inspect the argument. I bring it to this problem with ambition, and I leave the empirical verdict open. Selah.


## 2. Abstract and contribution ledger

I define a three-component Gaussian mixture on a four-dimensional latent space, an observer-specific projective map and an optional rank-three trait representation with ambient observation noise. The components are statistical hypotheses, not mutually exclusive kinds of people and not the diagnostic categories of bipolar disorder.

The mathematical results establish mixture normalization, affine Gaussian transformation, the projective change-of-variables formula, a Cauchy ratio example, incompatibility of full-dimensional Gaussian support with an exact lower-dimensional manifold, label-permutation ambiguity and loss of depth under projection. These statements follow from declared assumptions. They do not establish a clinical mechanism.

The numerical record uses seed 20261004, 100,000 synthetic mixture samples and 200,000 independent normal pairs. The retained projective mass is 0.951191 analytically and 0.951260 by sampling. The normal-ratio tail probability beyond magnitude five is 0.125666 analytically and 0.126140 in the simulated sample.

I propose a validation programme based on longitudinal measurements, explicitly defined endpoints, patient-level holdouts, prospective evaluation and separation of prediction from intervention. The projective model remains a research hypothesis. It is not a tool for diagnosing someone, classifying them as dangerous or changing medication.


| Contribution | Evidence |
| Density and projective results | Proofs under stated assumptions |
| Horizon and manifold figures | Synthetic and analytic calculations |
| Bipolar interpretation | Unvalidated research proposal |
| Treatment optimization | Future clinical research objective |


## 3. Clinical context has its own authority

Bipolar disorder concerns episodes and longitudinal changes in mood, energy and activity. NIMH distinguishes bipolar I, bipolar II and cyclothymic disorder; clinical assessment considers history and the course of symptoms [1]. A mixture-component label is not one of those diagnoses. Grandiose appraisals, reduced sleep, depressed mood or unusual ambition cannot be interpreted adequately from one isolated coordinate.

NICE describes comprehensive assessment, differential diagnosis, psychosocial context, treatment history and collaborative care planning [2]. I retain clinical history as information the geometric proposal would have to explain. I do not allow the proposal to overwrite an assessment simply because its mathematical notation is elegant.

The same separation applies to harm-related content. Thoughts, intent, behavior and events are different endpoints. They may need different observation models and different time windows. This paper does not infer that people with bipolar disorder are homicidal, nor that unusual achievement is evidence of a psychiatric diagnosis.

The contribution of geometry is to make a representation explicit. The contribution of clinical evidence is to determine whether that representation captures anything useful. Each has a standard of checking that the other cannot replace. My purpose is to connect them through measured observations rather than through a claim that one subsumes the other.


## 4. Primitives and names that begin the system

I begin with primitive sorts: person, observation, time, context and observer. I do not claim to define experience exhaustively. A formal primitive supplies a role in a system; its interpretation still requires a measurement procedure and an account of how the symbol is used.

An observer is an index for a specified perspective map. It may represent an observation context or a reporting frame. It is not an omniscient witness. A person is a participant identifier. Time is ordered. An observation is a recorded value with a measurement process, units, provenance and missingness information.

Capability, greatness, suffering and meaning are initially informal names. They cannot enter a numerical objective merely by being evocative. If I want to measure appraisal of capability, I must define what is reported, how it is recorded and how its reliability is evaluated. If I want to measure achievement, I need a separate endpoint that does not simply reward agreement with the appraisal.

This is how I keep an unnamed intuition productive. I can name its place in the argument while declining to assign it a coefficient before it has an operational definition. The formal system gains clarity from that restraint. Undefined primitives and undefined empirical measurements are related problems, but they are not the same problem.


## 5. Four dimensions and three components

I distinguish a dimension from a component. A dimension is one coordinate of the latent state. A component is one probability distribution contributing to a mixture. Three components can each occupy the same four-dimensional space. There is no requirement that a component correspond to one coordinate.

The initial coordinate names are provisional: self-directed harm-related content, other-directed harm-related content, activation and appraisal/context. They designate proposed latent constructs in dimensionless units. They are not probabilities. A negative coordinate is permitted mathematically and does not mean a negative chance of an event.

The three mixture labels index proposed statistical regimes. Their names carry a hypothesis about interpretation, not a verified diagnostic meaning. Because a mixture uses one latent component index per draw, treating its components literally as three exclusive human moral types would be a mistake. Harm-related outcomes can coexist and need separate observation models.

The fourth coordinate supplies a geometric depth in the projective example. Its proposed psychological interpretation must be tested rather than taken for granted. This distinction is important: a geometric construction can be internally valid while the coordinate assigned to it fails to correspond to a stable clinical construct.


\[
x\in\mathbb R^4,\quad K\in\{1,2,3\},\quad x\mid K=k\sim\mathcal N_4(\mu_k,\Sigma_k).
\]


Figure: figures/latent-mixture.pdf
Synthetic three-coordinate marginal of the four-dimensional mixture; the fourth coordinate is integrated out.


## 6. Axioms of the ambient model

Axiom A1 specifies nonnegative component weights whose sum is one. Axiom A2 requires symmetric positive-definite covariance matrices in the full ambient model. Axiom A3 defines the mixture density as the weighted sum of the three Gaussian densities. These are modeling commitments that permit a probability calculation.

Axiom A4 indexes all parameters by an observation context and, in a longitudinal extension, by time. It does not silently assume that people have fixed lifetime coordinates. Axiom A5 requires observation and outcome variables to be defined separately from the latent representation. Axiom A6 prevents future outcome labels from entering a held-out inference procedure.

Axiom A7 limits a mathematical theorem to its formal assumptions. An interpretation in terms of bipolar disorder is an empirical hypothesis outside that theorem. Axiom A8 requires reporting of uncertainty, exclusions and failed predictions. These last commitments are rules of the research protocol; they are not properties deduced from Gaussian algebra.

The point of writing the axioms is to expose where a conclusion comes from. If a covariance loses rank, A2 changes. If the observation map changes, the projected law changes. If clinical data reject a Gaussian regime, the fitted model must change. Axiomatization makes those alterations visible instead of turning every disagreement into a dispute about authority.


\[
q(x)=\sum_{k=1}^3w_k\varphi_4(x;\mu_k,\Sigma_k),\quad w_k\geq0,\quad\sum_kw_k=1,\quad\Sigma_k\succ0.
\]


## 7. The fuzzy trait field and its manifold

I want the broader trait component to have an interpretable lower-dimensional structure, rather than become a bin for everything unexplained. A proposed three-dimensional manifold can supply that structure, but it must be distinguished from the ambient four-dimensional Gaussian density.

For an affine version, I define a three-dimensional coordinate u, a rank-three loading matrix B and a small ambient noise vector. The resulting covariance has a low-dimensional contribution plus an isotropic noise term. At positive noise the law is a full Gaussian in four dimensions. At zero noise it is degenerate and lives on an affine three-plane.

A curved manifold requires a nonlinear map. The pushforward of a Gaussian chart distribution through a nonlinear map is generally not Gaussian in ambient coordinates. I therefore cannot demand curvature, full Gaussian form and exact three-dimensional support simultaneously without changing the model. Naming that incompatibility improves the proposal.

The fuzzy trait field also needs boundaries of interpretation. A residual component should identify a remaining modeling question, rather than hide every social, developmental and biological influence in one scalar. Dimensionality can be selected and evaluated, but a catch-all label is not a validation result.


\[
X_O=\mu_O+B U+\eta,\quad U\sim\mathcal N_3(0,\Lambda),\quad\eta\sim\mathcal N_4(0,\tau^2I),
\]


\[
\Sigma_O=B\Lambda B^T+\tau^2I,\qquad\operatorname{rank}(B)=3.
\]


Figure: figures/manifold-noise.pdf
Synthetic covariance eigenvalues as ambient noise shrinks. Positive noise gives full rank; the zero-noise limit has rank three.


## 8. Defining the observer and the horizon

I define the projective horizon through a denominator. The observer selects an affine coordinate frame, a horizon parameter h and a positive exclusion scale epsilon. The admissible source points satisfy x4 less than h minus epsilon. Their depth is d equal to h minus x4, and their displayed coordinates are the first three coordinates divided by d.

This map changes the appearance of a fixed latent distribution. A source point near the horizon can appear distant in the displayed coordinates. That is a geometric fact about division. It does not establish that a person near a supposed psychological horizon is suicidal, violent, exceptional or manic.

The exclusion condition matters. Points outside the domain are not assigned an arbitrary huge value; they are excluded and the retained distribution is renormalized. The omitted probability mass must be reported. Different observers can choose different frames, and the proposal needs an account of which aspects of those choices can be measured.

I reserve the term projective for the specified transformation. A colloquial first-person perspective could involve attention, language, memory and social interpretation that this map does not represent. The transformation is an explicit candidate, not a complete account of consciousness.


\[
d=h-x_4>\epsilon,\qquad\Pi_h(x)=\left(\frac{x_1}{d},\frac{x_2}{d},\frac{x_3}{d}\right).
\]


## 9. Theorem 1: mixture normalization

Theorem. Under A1-A3, q is a nonnegative density with integral one on four-dimensional Euclidean space. Proof. Every Gaussian density is nonnegative and integrates to one. A finite nonnegative weighted sum is nonnegative, and integration distributes over that sum. Its total mass is the sum of the weights, which A1 fixes at one.

The result is modest and useful. It licenses probabilities for regions of the declared latent space. It does not tell me which region represents a clinically defined event. To obtain such an event probability I need a measurement or outcome model whose meaning is established independently.

For an observer domain D, let Z be the mass of q inside D. If Z is positive, the conditional density q times the domain indicator divided by Z again integrates to one. The projective calculation uses this conditional law. Failing to divide by Z would make the displayed density lose exactly the excluded source mass.

These normalizations are formal statements, not estimates fitted from the numerical sample. Sampling supplies a diagnostic comparison to the analytic retained mass. I keep that distinction because a Monte Carlo fraction near one is neither a proof of normalization nor an empirical validation of a psychiatric interpretation.


\[
\int_{\mathbb R^4}q(x)\,dx=\sum_{k=1}^3w_k=1,\qquad q_D(x)=Z^{-1}q(x)\mathbf1_D(x).
\]


## 10. Theorem 2: an affine view preserves Gaussian components

Theorem. An invertible affine transformation of a Gaussian component is Gaussian, with transformed mean and covariance. Proof. Apply the usual change of variables to y equal to A x plus b. The inverse is A inverse times y minus b. The determinant supplies the volume change, while completing the quadratic gives the transformed parameters.

The entire mixture transforms component by component with the same weights. This result gives a baseline for perspective. Rotation, translation and invertible linear scaling can change axes without introducing a non-Gaussian component. A ratio transformation is different because its denominator depends on the source state.

An affine observation map of lower rank loses dimensions. Its Gaussian pushforward can still be defined, but its covariance and support require the appropriate dimension. I should not place a singular transformed law into the formula for an invertible transformation and pretend the determinant remains available.

For clinical research, a coordinate convention should be documented. Reversing the sign of a scale, changing its units or rotating a latent basis can alter apparent component means without changing the fitted observation law. Interpretation therefore needs anchoring measurements as well as a mathematically valid transformation.


\[
Y=AX+b\quad\Longrightarrow\quad Y\sim\mathcal N(A\mu+b,A\Sigma A^T).
\]


## 11. Theorem 3: the projected density

Theorem. For positive retained mass and positive depth exclusion, the displayed three-dimensional density is the integral of the source density along depth, weighted by the cube of depth. Proof. Write the inverse joint transformation as x1=d y1, x2=d y2, x3=d y3 and x4=h-d. Its Jacobian has absolute determinant d cubed.

Changing variables gives a joint density for displayed coordinate y and depth d. Integrating over d greater than epsilon removes the unobserved depth. Division by retained source mass supplies the conditional normalization. Nonnegative integrands permit the interchange of integrations needed to confirm that the displayed density has unit total mass.

The formula is the precise version of the horizon intuition. It also exposes a loss: each displayed point collects source points at many depths. The observer cannot recover a unique source state from that display alone. A sharp-looking surface can therefore conceal a non-identifiability problem.

In the numerical figure, I show a cross-section at the third displayed coordinate equal to zero. This is a slice of a three-dimensional density. It is not a normalized two-dimensional marginal. The caption states that distinction because a familiar surface plot can otherwise suggest the wrong integral.


\[
p_h(y)=\frac1Z\int_\epsilon^\infty d^3q(dy_1,dy_2,dy_3,h-d)\,dd.
\]


Figure: figures/projected-density.pdf
Numerically integrated cross-section of the projected three-dimensional density. All coefficients are invented; no participants are represented.


## 12. Theorem 4: Gaussian source, Cauchy ratio

Theorem. If X and Z are independent standard normals, their ratio has the standard Cauchy density. Proof. The joint density is proportional to exp of minus one half times x squared plus z squared. Substitute x equal to y z and integrate the transformed density with the absolute Jacobian factor |z| over all real z. The resulting integral is one divided by pi times one plus y squared.

This example demonstrates that a heavy tail in displayed coordinates does not require a heavy-tailed source coordinate. A denominator near zero is enough. In the three-dimensional version, three independent standard normal numerators divided by a common independent standard normal denominator give a multivariate t law with one degree of freedom.

The theorem concerns geometry and probability. It does not identify a mental disorder, a human capacity distribution or an event mechanism. It provides a counterexample to an overly quick inference from apparent extremity to an intrinsically exceptional source state.

The simulated ratio fraction beyond magnitude five is 0.126140; the exact probability is 0.125666. The histogram uses unconditional mass, so observations outside the displayed window are not silently renormalized into the window.


\[
f_{X/Z}(y)=\frac1{\pi(1+y^2)},\qquad\Pr(|X/Z|>a)=1-\frac2\pi\arctan a.
\]


Figure: figures/cauchy-ratio.pdf
Independent synthetic normal ratios, exact Cauchy density and a Gaussian reference. This is a mathematical example, not a clinical score.


## 13. Theorem 5: a manifold cannot carry full Gaussian mass

Theorem. A smooth embedded three-dimensional manifold in four-dimensional Euclidean space has zero four-dimensional Lebesgue measure. A Gaussian with positive-definite covariance has a density with respect to that measure. It therefore assigns probability zero to the manifold.

Proof. Locally the embedded manifold is represented by smooth charts of rank three. Its four-dimensional volume is zero; a countable chart cover preserves that property. Integrating an absolutely continuous density over a zero-volume set gives zero. The conclusion concerns an exact support claim, not points lying near a manifold.

The affine rank-three construction supplies a consistent alternative. With zero ambient noise it is a degenerate Gaussian supported on an affine plane, requiring its intrinsic measure rather than a full four-dimensional density. With positive ambient noise it is full-dimensional and concentrated near the plane. These are different models with a well-defined limiting relationship.

For a curved manifold, a chart distribution can be pushed forward through a nonlinear map. The result may express the intended trait geometry while losing ambient Gaussian form. I can choose that extension. I cannot obtain it by declaring that an unrestricted Gaussian already lives entirely on the curved manifold.


## 14. Theorem 6: the horizon loses depth

Theorem. The projective map is not injective on its admissible domain. Proof. Fix a displayed vector y. For every depth d greater than epsilon, the source point (d y1, d y2, d y3, h-d) maps to y. Distinct depths give distinct source points with the same displayed vector.

The displayed vector therefore determines a fiber, not a unique source state. A prior distribution over depth can support a posterior over that fiber, but the result depends on the prior and on any additional measurements. It is not recovered by projective algebra alone.

This matters to a first-person interpretation. A change in displayed magnitude can arise through a numerator change, a denominator change or both. Without an independently measured depth-related construct, those explanations may be observationally inseparable. A confident narrative about which mechanism occurred can exceed what the model identifies.

I treat this result as a guide to measurement design. Repeated observations, context reports or independently anchored scales might help distinguish competing states. Their usefulness would have to be tested. The theorem tells me why an extra observation may be needed; it does not supply that observation.


\[
\Pi_h(dy_1,dy_2,dy_3,h-d)=y\quad\text{for every }d>\epsilon.
\]


## 15. Theorem 7: labels are not identified by mixture likelihood

Theorem. Permuting the component labels together with their weights and parameters leaves the mixture density unchanged. Proof. A finite sum does not depend on the order of its terms. The likelihood of any dataset under that density is therefore unchanged by the same permutation.

The density can be statistically useful while the intended meaning of a component remains unanchored. Calling a component self-directed, other-directed or residual does not identify it from the likelihood. Such meanings require independent observations or justified constraints. Otherwise the names can switch while the fit stays the same.

The numerical record checks all six permutations at eighty synthetic probe points. The largest density difference is 3.47e-18. This is an implementation check of the algebraic symmetry, not an empirical test of component interpretation.

The same issue prevents me from equating three mixture components with bipolar diagnostic subtypes. A diagnosis depends on a clinical course and specified evidence. A mixture component is a distributional index. I can investigate associations after defining the observation model and validation procedure, but the association cannot be manufactured by relabeling the fitted indices.


## 16. Three components do not make two harms complementary

I give self-directed and other-directed harm-related outcomes separate event variables. Their probability estimates, if a future study validates them, must specify the endpoint and the time window. Ideation, intent, self-harm, suicide, threats, violence and homicide cannot be compressed into two interchangeable labels.

Two event indicators need not be complements. Both can be absent, both can be present, and one can occur without the other. Their marginals do not identify their joint distribution. A three-component latent mixture does not change this elementary probability fact.

The third component also cannot serve as a residual probability obtained by subtracting two unrelated event probabilities from one. That subtraction would require an exclusive and exhaustive event partition. The proposed latent regimes are not such a partition of clinical outcomes.

I therefore leave the event observation model separate from the latent Gaussian construction. Its parameters are unknown here. The separation preserves the proposed geometry while preventing it from imposing a false clinical taxonomy. It also prevents an ordinary statistical component label from becoming an accusation about a person.


\[
\max(0,p_S+p_H-1)\leq\Pr(S\cap H)\leq\min(p_S,p_H).
\]


## 17. Numerical design: inspectable artificial data

I generate 100,000 samples from the declared three-component mixture. Its weights are 0.25, 0.20 and 0.55. The means and covariances are invented and stored in results.json. They were selected to make mixture, projection and low-rank structure visible. They are not estimated from people with bipolar disorder.

The experiment checks positive-definite component covariances, mixture weights, projective retained mass, the Cauchy integral and tail fraction, label permutations and the analytic projection derivative against finite differences. Every numerical illustration has a mathematical target that can be examined separately from its proposed interpretation.

The source sample and its displayed projection share the same underlying draws. Comparing them isolates the geometric effect of the specified transformation. A finite display window necessarily omits some projected points. The plot records the window rather than claiming it contains the entire law.

No patient cohort, medication record, diagnostic label or real-world harm event enters this calculation. The available achievement is a tested numerical implementation of the proposed mathematical structure. The next evidentiary question is whether a measured observation model can connect that structure to a defined clinical research endpoint.


Figure: figures/perspective-samples.pdf
Synthetic source coordinates and their projective display. The second panel shows a finite window, not all transformed observations.


## 18. The covariance calculation and the third field

The third Gaussian is generated from a rank-three linear chart plus isotropic ambient noise. I examine noise scales 1, 0.3, 0.1, 0.03, 0.01 and zero. As noise decreases, the smallest covariance eigenvalue approaches zero while three directions retain positive variance.

This calculation explains what an approximate manifold means in the ambient model. At nonzero noise, the distribution has a full density and allows departures from the idealized chart. At zero noise, it loses a fourth independent direction. The density formula and reference measure must then change.

A small eigenvalue is a property of this chosen covariance. It is not evidence that the remainder of human personality has exactly three dimensions. That empirical claim would require appropriate data, an operational definition and comparison to alternative dimensions. The present example is a consistency construction.

The same distinction applies to interpretability. A loading matrix can be printed and understood as an algebraic object. Its columns acquire psychological meaning only through measurements that anchor them. I want a readable model, but readability alone does not establish that the selected constructs capture human experience.


| Ambient noise | Smallest eigenvalue | Numerical rank |
| 1.00 | 1 | 4 |
| 0.30 | 0.09 | 4 |
| 0.10 | 0.01 | 4 |
| 0.03 | 0.0009 | 4 |
| 0.01 | 0.0001 | 4 |
| 0.00 | -5.8984e-17 | 3 |


## 19. Horizon sensitivity and observer dependence

I vary the horizon parameter while keeping the same source sample. The transformation changes the displayed coordinate distribution and the fraction of source points that remain admissible. The table gives the retained sample count and the displayed first-coordinate median with its fifth and ninety-fifth percentiles.

These are descriptive simulation quantiles, not confidence intervals for patients. A change in their width arises from the assumed geometry. If a psychological interpretation of depth is proposed, this sensitivity tells me that its measurement and stability will matter to any clinical application.

The derivative has an inverse-depth term for the numerator coordinates and an inverse-squared-depth term for the fourth coordinate. Consequently small depth perturbations can have large displayed effects near the horizon. A model that ignores depth uncertainty may present excessive numerical precision.

An observer effect is therefore something to quantify, rather than an excuse to make every perspective equally predictive. A future measured comparison could test whether the specified transformation explains reporting differences better than an affine or nonprojective alternative. The current calculation supplies the candidate and the sensitivity record.


\[
\frac{\partial y}{\partial x}=\left[d^{-1}I_3\ \middle|\ d^{-2}x_{1:3}\right].
\]


| Horizon | Retained | Median |
| 0.5 | 77759 | 0.03415 |
| 1.0 | 95126 | 0.15890 |
| 2.0 | 99968 | 0.10540 |
| 3.0 | 100000 | 0.06971 |


Figure: figures/horizon-sensitivity.pdf
Same invented source sample, different horizon parameters. Bars show sample 5-95% intervals, not inferential confidence limits.


## 20. Rare-event arithmetic and its limits

I include a generic base-rate example because a model can look accurate while producing many false positives on a rare endpoint. With assumed sensitivity 0.8 and specificity 0.95, the positive predictive value depends strongly on the assumed event prevalence. The example does not use clinical event rates or a tested psychiatric predictor.

At an invented prevalence of 0.005, the positive predictive value is about 0.0744. A favorable-looking sensitivity cannot remove the denominator contributed by false positives among the much larger event-free population. This is arithmetic about a hypothetical binary classifier, not a validation result.

NICE NG225 advises against using risk scales to predict suicide or repeated self-harm and against using stratification to determine access to care or discharge [3]. The projective proposal supplies no basis for departing from that guidance. It is not a clinical triage score.

The practical research consequence is to specify outcomes, prevalence, calibration, false-positive consequences and external validation before interpreting a predictive number. A component posterior is not an event risk. A high displayed coordinate is not an assessment of intent. The model must preserve these distinctions to avoid turning a geometrical hypothesis into an unjustified decision about a person.


\[
\mathrm{PPV}=\frac{\mathrm{Se}\,p}{\mathrm{Se}\,p+(1-\mathrm{Sp})(1-p)}.
\]


Figure: figures/base-rates.pdf
Generic classifier arithmetic at assumed sensitivity and specificity. No actual suicide or violence prevalence is plotted.


## 21. A longitudinal extension that could be tested

A static mixture is a starting representation. Bipolar research requires an account of changes through time. I would extend the latent state with transition dynamics, context covariates and a measurement process that preserves the distinction between a changing report and a changing underlying state.

The transition law could be a state-space model with continuous dynamics, a switching process or an explicitly defined non-Gaussian alternative. Its parameters would need repeated observations. A mixture fitted to one cross-section cannot determine how an individual moves between regimes, nor how that movement responds to treatment.

I would specify outcomes and time windows before fitting, split participants rather than visits across holdouts, document missing observations and keep future information out of predictors. Measurements might include validated assessments, functioning, sleep and treatment exposure where appropriate and ethically collected. These are proposed inputs, not data present in this manuscript.

The projective hypothesis would be compared with simpler observation maps. Its value would lie in improved, externally evaluated description or prediction, with uncertainty and failures retained. A flexible horizon that fits every report retrospectively would need a complexity penalty and an identifiability analysis; it would not count as a discovery by flexibility alone.


\[
x_{t+1}=F_\theta(x_t,c_t)+\xi_t,\qquad o_t\sim p_\psi(o_t\mid\Pi_h(x_t),c_t).
\]


## 22. Treatment optimization needs causal evidence

My objective includes improving treatment research, but an observational representation is not a medication policy. A fitted association between a state and an outcome may reflect clinical selection, adherence, severity, context or other unmeasured factors. Changing a treatment is a causal intervention, with potential benefits and harms not established by the mixture density.

I therefore define treatment optimization as a future constrained research problem. Actions must be specified, outcomes must include adverse effects and functioning, and the evidence must identify the counterfactual comparison. Prospective evaluation and appropriate clinical oversight are required. No medication, dose, combination or change is calculated in this paper.

NIMH describes medication and psychotherapy as established treatment approaches [1]. That clinical context motivates a question about better evidence; it does not validate the new geometry. The proposed model would have to earn its relevance through a well-defined comparison within appropriate research settings.

A mathematical objective can include several losses and safety constraints. Their numerical weights are value judgments or estimated preferences that require documentation. Assigning a large coefficient to an invented harm score does not establish safety. I leave those weights unestimated here rather than allowing a symbolic optimization to impersonate a clinical decision.


\[
\min_\pi\mathbb E_\pi[L_{\rm symptoms}+\lambda L_{\rm adverse}+\gamma L_{\rm functioning}]\quad\text{subject to validated constraints.}
\]


## 23. Relations to logic, geometry and other sciences

The formal proposal uses ordinary classical logic for its deductions, measure theory for probability, linear algebra for covariance, differential geometry for support and change of variables, and statistical inference for its proposed relation to observations. These are distinct parts of one research design.

A model axiom is adopted to define a class of objects. A theorem states what follows inside that class. An empirical hypothesis states that the class usefully describes some observations. A clinical conclusion requires further evidence about outcomes and interventions. I do not collapse those forms of justification into one terminating declaration.

The same discipline applies to physics, biology, chemistry and economics. Each can define state, observation and transformation. Each must also determine whether the chosen representation corresponds to its subject matter. A formally valid projective density does not become a law of psychology because similar mathematics appears in another field.

Real analysis is for all who undertake its work. Its accessibility does not reduce its obligations: specify domains, handle singularities, distinguish densities from probabilities and preserve the conditions of a theorem. The broader intellectual project is a transferable method of inquiry, with application-specific measurements rather than application-free certainty.


## 24. Achievement, history and selection bias

I began with an image of people who imagine a larger contribution than they have yet achieved. That image can motivate a question about appraisal, action and feedback. It cannot establish that unusual achievement, masculinity or a particular political role identifies a bipolar mechanism.

Historical figures selected for dramatic influence do not form a representative cohort. They do not supply clinical measurements, a defined comparison population or an outcome denominator. I make no retrospective diagnosis of Hitler, Stalin, Mao, Nietzsche, Kierkegaard or Marx. Their inclusion in an initial rhetorical list does not become evidence for the Gaussian components.

Likewise, a claim about testosterone, sex or enduring political authority would require a separate causal model and supporting observations. It does not follow from probability normalization, projective geometry or a covariance matrix. Such claims are not adopted as axioms of this proposal.

The model also cannot confer human worth. Greatness is an interpretive term until an outcome is operationalized; ambition and appraisal must be measured separately from that outcome. My research question remains open to people across backgrounds and identities. The formal work concerns a representation and its testable consequences, not a hierarchy of who deserves power.


## 25. References, reproducibility and the completed result

I provide the source manuscript, LaTeX, all seven color figures, the experiment script and the complete numeric record. The calculations require NumPy, SciPy and Matplotlib. The density plots are analytic or synthetic; no patient-derived observations are reported.

The checks passed for covariance positivity, retained probability mass, Cauchy normalization and tail sampling, rank-three limiting structure, all component permutations and a finite-difference check of the projective derivative. These are checks of the mathematical implementation. They do not validate the interpretation in terms of bipolar disorder.

The completed result is a precise candidate model with proofs, numerical illustrations and identified observational limits. I keep the hypothesis available for challenge. Let it be written, let its assumptions be named, and let the evidence decide how far the model travels. Selah.

[1] National Institute of Mental Health. Bipolar Disorder. Clinical context; accessed 4 October 2026. https://www.nimh.nih.gov/health/publications/bipolar-disorder

[2] NICE. CG185: Bipolar disorder, assessment and management. Recommendations. https://www.nice.org.uk/guidance/cg185/chapter/recommendations

[3] NICE. NG225: Self-harm, assessment, management and preventing recurrence. Risk tools and scales. https://www.nice.org.uk/guidance/ng225/chapter/recommendations
