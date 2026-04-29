# Organizational Compliance Capacity Under Continuous Normative Change

### A model and methodology, with the Knowledge Currency Budget as the per-regime accounting unit

**v0.1 — 2026-04-28**
**Compliance Burden Index, Systematic Reasoning, Inc.**

> ### Known data gaps in v0.1
>
> This document is best read as a **disciplined scenario model** with the full CABF stack now fully instrumented at the per-section level (380 per-section change records across TLS BR, S/MIME BR, NetSec, Code Signing BR, and EV Guidelines). The following gaps are open. Headline numbers should be read with these in mind.
>
> | Gap | Status in v0.1 | Resolution target |
> |---|---|---|
> | Per-section change provenance for the full CABF stack | **complete: TLS BR (139), S/MIME BR (29), NetSec (48), Code Signing BR (19), EV Guidelines (145); 380 records total** | covered |
> | Per-version corpus measurements (word count, RFC 2119 keyword count) | TLS BR only (13 versions, 2012–2025); not ingested for S/MIME BR, NetSec, Code Signing BR, EV Guidelines | covered by roadmap (per-version corpus extraction across all five CABF regimes) |
> | EVG v2.0.2 (2026-03-31) | excluded from observed window; published 28 days before snapshot, per-section data not yet ingested | covered by next data refresh |
> | Hand-classified substantive-vs-editorial fraction φ | central value 0.40 is a practitioner estimate, not a measurement | covered by roadmap (hand-classify the 139 TLS BR observed-window changes) |
> | Persona-regime matrix | TLS-shaped persona weights applied uniformly to all five CABF regimes; multi-regime numbers should be read as TLS-persona-weighted | covered by roadmap (per-regime persona weights) |
> | Tier 2 *H(R)* (root programs) | not computed; visible version cadence reported as a floor | covered by roadmap (m.d.s.policy thread classification for Mozilla, then Chrome RPP / Apple / Microsoft equivalents) |
> | Behavioral validation of working-accuracy threshold τ and decay τ_decay | inferential from skill-decay literature | covered by roadmap (partner-CA quiz-based recall study) |
> | Cross-regime coupling term | not modeled; *H(R)* per regime is summed without overlap or reconciliation cost | covered by roadmap |

## Abstract

Compliance regimes are evaluated through periodic audits that implicitly assume an attesting organization can sustain working knowledge of a moving normative corpus between assessments. We make this assumption testable by formalizing the *Knowledge Currency Budget*, *H(R, p)*: the time-equivalent burden, in hours per year, required to maintain operational readiness on regime *R* for a role *p* under observed change cadence λ, decay function δ, and configurable working-accuracy threshold τ. The model parameterizes per-role because organizations stage compliance work across distinct functions (CPS ownership, validation interpretation, audit liaison, root program coordination, engineering, executive sign-off). The load-bearing claim is at team scale: the aggregate budget summed across roles, against the aggregate capacity an organization can plausibly allocate to a single regime. Individual cognition is one mechanism by which currency is maintained; institutional redundancy, schemas, precedent systems, and tooling-supported recall are others. The model abstracts all of these as the time-equivalent burden the team must absorb to keep the organization at the working-accuracy threshold the audit-centric model implicitly assumes.

Using the CA/Browser Forum TLS Baseline Requirements (2012 to 2026) as the principal measurement substrate, we compute the budget from public version histories, ballot records, and RFC 2119 keyword inventories. At observed 2025 to 2026 cadence, the team-aggregate capacity ratio for the TLS BRs alone, at central parameters, is 0.84× of allocated capacity, with two of seven roles individually above the model-implied capacity-deficit threshold of 1.0×. The analysis extends to four additional CABF regimes (S/MIME BRs, Network Security Requirements, Code Signing BRs, Extended Validation Guidelines) using cadence and aggregate change counts ingested from the same tracking system. The modeled CABF-stack change-handling burden, excluding baseline corpus reading and excluding non-CABF regimes, is approximately 1,094 hours per year of team currency-maintenance work under steady-state conditions, plus an additional 208 hours per year attributable to the EV Guidelines transition baseline.

Translating that 1,094 h/yr into person-time depends on what one calls a person-year. Three reasonable denominators give three different readings of the same number: against a nominal 2,080 h/yr FTE the burden is 0.53 person-years; against a realistic focused-expert capacity of 1,500 h/yr it is 0.73 person-years; against the model's own allocated team capacity of 1,012 h/yr (the seven roles at central TLS-BR allocation) it is 1.08 team-equivalents. These are not three different point estimates. They are the same hour total seen through three denominators that emphasize different things. The first two are person-year equivalents. The third is the share of the model's own assumed team capacity, and it sits above 1.0 because CABF currency-maintenance alone exceeds what the model's own role distribution can plausibly afford.

The number measures the organizational cost of staying current. Knowing what changed, what it means, who it affects, and what needs to be done. It does not measure the cost of doing the resulting compliance work: engineering, CPS edits, audit support, incident response, customer assurance. Under the model's stated assumptions, currency-maintenance for the CABF subset of the regime stack alone consumes a substantial fraction of plausibly-available compliance-team capacity before any application work begins.

Per-section change provenance is now complete across the entire CABF stack: TLS BR 139 of 139, S/MIME BR 29 of 29, NetSec 48 of 48, Code Signing BR 19 of 19, and EV Guidelines 145 of 145, for 380 fully-classified change records total. The artifact (data, model, figures, methodology) is reproducible from versioned inputs.

## 1. Motivation

The audit-centric compliance model rests on two implicit assumptions. The first is that the normative corpus is reasonably stable between assessments. The second is that the attesting *organization* can sustain working knowledge of the corpus between assessments, sufficient that audit fieldwork is sampling against operational competence rather than constructing it. Both assumptions are testable. This document tests the second under observed conditions in the WebPKI regime stack, and the result implicates the first.

A note on what "the organization can sustain working knowledge" means in this paper. We are not making a narrow cognitive claim about individual analysts memorizing the corpus. Real compliance functions sustain currency through a portfolio of mechanisms: distributed expertise across roles, structural schemas, exception memory, institutional precedent, peer review, escalation paths, prior-incident anchors, tooling-supported recall, and event-triggered re-engagement. Each of these absorbs some portion of the work that would otherwise fall on individual analyst recall. The model is agnostic about which mechanisms a given organization uses; it computes the time-equivalent burden the organization must absorb in aggregate to keep the team at the working-accuracy threshold the audit-centric model implicitly assumes. Whether that time is spent rereading source material, cross-checking with a colleague, consulting an internal wiki, or running a diff tool is not what the model measures. The model measures whether the time-equivalent burden fits in plausible team capacity.

We formalize a *Knowledge Currency Budget*, denoted *H(R, p)*, defined as the time-equivalent hours per year required to maintain operational readiness on regime *R* for a role *p* before any active review work occurs. *Operational readiness* is the threshold at which a team can perform substantive review without re-reading source material as the primary mode of analysis. *Currency-maintenance* is the work required to remain at operational readiness as the corpus changes.

The model parameterizes per-role because organizations stage compliance work across distinct functions. The load-bearing claim is at team scale: the aggregate budget summed across roles, against the aggregate capacity an organization can plausibly allocate to a single regime. Individual-role readings are intermediate quantities that surface where load concentrates within a team; the diagnostic is the team aggregate.

We extend the model with a *capacity stack* that estimates, from public labor-statistics and knowledge-work research, the hours plausibly available to a compliance team for currency-maintenance on a single regime. The ratio *H / capacity* is the model-implied capacity diagnostic. A ratio at or above 1.0 indicates a *capacity deficit* under the model's stated assumptions: the modeled currency-maintenance burden equals or exceeds the modeled allocated capacity, and the team can sustain operational function only by relaxing one of the model's premises (full corpus depth, working accuracy maintained without lowered thresholds, dedicated allocation untouched by adjacent regimes). A ratio meaningfully below 1.0 indicates slack for currency-maintenance plus the application work the team is also expected to perform.

The TLS Baseline Requirements are the initial measurement substrate because they are the most public, the most consistently versioned, and the most well-instrumented normative corpus in the WebPKI. They are not the only corpus a working CA must remain current on. §9 enumerates the broader regime stack and the implications for total burden.

## 2. Model

### 2.0 Reference archetype

The persona structure, capacity stack, and TLS BR allocation parameters in this methodology describe a specific reference archetype: a mid-sized publicly-trusted Certificate Authority with internal compliance ownership, operating across multiple CABF regimes plus root program and audit obligations, with a dedicated compliance and policy function rather than a generalist legal or product team. Where this methodology reports a number such as "the team's TLS-BR-allocated capacity is 1,012 hours per year," the team in question is this archetype, not any specific organization. CAs operating under different staffing models (smaller CAs without a dedicated compliance function, larger CAs with separate teams per regime, CAs that outsource policy work to external counsel, hosting-provider or cloud-provider CAs whose compliance function is part of a broader security organization) will distribute the same total burden differently across roles. The diagnostic conclusion is structural rather than prescriptive: the model identifies that a regime's currency-maintenance burden, at observed cadences, exceeds what a plausibly-staffed dedicated compliance function can absorb at the working-accuracy threshold the audit-centric model implicitly assumes. Organizations whose staffing differs from the archetype should re-derive the personas and allocations rather than substituting their own structure into the model's denominators; the right reading of a single number against a different archetype is an analogy, not an equality.

### 2.1 Quantities

For regime *R* with corpus *C(t)* of *W(t)* words at time *t*:

| Symbol | Quantity |
|---|---|
| *r* | Adult silent reading rate (words per minute) for non-fiction English text |
| τ | Working-accuracy threshold; minimum recall fraction at which substantive real-time review is feasible without re-reading |
| τ_decay | Exponential decay time constant (days) for declarative working knowledge |
| *V(R)* | Versions released per year |
| *E(R)* | Total edits per year (added + removed + modified at the requirement granularity) |
| φ | Substantive-edit fraction; share of edits requiring propagation work |
| *t_diff* | Hours per version-level diff review |
| *t_assess* | Hours per individual edit triage |
| *t_propagate* | Hours per substantive edit for full propagation work |

### 2.2 Reacquisition frequency

We are not modeling student-style forgetting of vocabulary. We are modeling the time required to restore high-confidence operational readiness on a normative corpus that is itself moving. Real practitioners maintain currency through structural schemas, exception memory, institutional heuristics, prior-incident anchors, and tooling-supported recall, not through literal cover-to-cover re-reads. The model abstracts all of these into a single quantity: the equivalent full-corpus reacquisition burden, expressed as an annual count of refresh-equivalents. We use a memory-decay parameterization to derive the rate because it is the simplest formal model with the right shape; the *H(R, p)* output is interpretable as time-equivalents regardless of how a given analyst actually structures their currency-maintenance practice.

Operational readiness on a corpus held in working memory at threshold τ loses ground over time τ_decay in the absence of rehearsal. Modeling this as exponential decay with time constant τ_decay:

> A(Δt) = exp(−Δt / τ_decay)

The maximum interval between full reacquisitions such that A stays above τ is:

> Δt_max = −τ_decay · ln(τ)

The number of full-corpus reacquisitions per year required to maintain working accuracy is therefore:

> *n_passes* = ⌈365 / Δt_max⌉, with floor 1

For central parameters (τ_decay = 120, τ = 0.70): Δt_max = −120 · ln(0.70) = 42.8 days, giving *n_passes* = ⌈365 / 42.8⌉ = 9 refresh-equivalents per year. This is not a claim that practitioners literally re-read the BRs nine times. It is a claim that the time-equivalent of nine full-corpus reacquisitions is what the model implies as the threshold-maintenance cost at central parameters.

We treat *n_passes* as a derived quantity, not a free parameter. This is the move that distinguishes *H* from a back-of-the-envelope estimate.

### 2.3 Personas

A working publicly-trusted CA does not staff a single generic compliance analyst. Expertise is distributed across roles with distinct corpus depth, change responsibility, and time allocation profiles. We define seven personas representing roles typically present in a CA's compliance and operations function:

| Persona | Corpus depth | Change responsibility | TLS-BR allocation | Diff review |
|---|---|---|---|---|
| CPS owner | 1.00 | 1.00 | 0.30 | yes |
| Validation lead | 0.40 | 0.50 | 0.25 | no |
| Issuance/profile engineer | 0.30 | 0.30 | 0.15 | no |
| Audit liaison | 0.80 | 0.40 | 0.20 | yes |
| Root program manager | 0.60 | 0.50 | 0.20 | yes |
| Engineering lead | 0.20 | 0.30 | 0.10 | no |
| Executive (CTO / compliance director) | 0.10 | 0.05 | 0.05 | no |

*Corpus depth d_p* is the fraction of the corpus the persona must hold in working memory to perform their role. The CPS owner reads everything; the engineering lead engages with implementation-affecting clauses but does not need full policy depth.

*Change responsibility c_p* is the fraction of changes the persona must actively engage with rather than acknowledge. The CPS owner must propagate every relevant change into the CPS; the executive must be aware of material organizational risk but does not draft amendments.

*Diff review I_p* is whether the persona is one of those who reads a version-level diff when a new version is published.

These persona definitions are themselves a calibration target. We chose values that reflect plausible role distinctions in mid-to-large publicly-trusted CAs. Variation across organizations is significant; smaller CAs may collapse multiple personas into a single role, increasing the per-person burden.

### 2.4 Per-persona budget

The Knowledge Currency Budget for persona *p* on regime *R* is:

> *H(R, p)* = (*W* · d_p) / (60 *r*) · *n_passes* + *V* · *t_diff* · I_p + *E* · d_p · *t_assess* + *E* · d_p · c_p · φ · *t_propagate*

The first term is *baseline corpus acquisition*, weighted by persona corpus depth. The second is *per-version diff review*, gated on whether the persona performs that work. The third is *per-change triage*, weighted by corpus depth (a persona engages with changes within their depth scope). The fourth is *substantive propagation*, weighted by both depth and change responsibility, the persona does propagation work only on changes within their depth scope and within their responsibility scope.

The reading-rate term is /(60 *r*) with *r* in words per minute, converting to hours.

### 2.5 Capacity stack

Nominal full-time-equivalent labor in the United States is 2,080 hours per year. This is a ceiling. After paid time off, statutory holidays, sick leave, and training, the *effective hours per year* for a salaried U.S. compliance professional is typically 1,700–1,900. Within those effective hours, only a fraction is *focused individual work*; the remainder is meetings, communication, coordination, and recovery from interruption. The knowledge-work literature converges on 30–55% effective focus time. Of the focused work that is available, only a fraction is allocated to a specific regime's currency-maintenance; a senior compliance role at a CA typically covers ten or more regimes, and TLS BR currency-maintenance is one slice of one focused-work allocation.

Capacity for persona *p* on regime *R* is therefore:

> *C(R, p)* = effective_hours · focused_fraction · domain_allocation_p

At central parameters: 1,800 × 0.45 = 810 hours/year of focused work, of which (per persona) 5–30% is allocated to TLS BRs, giving persona-specific capacities ranging from 40 to 243 hours/year. The team-level aggregate capacity is the sum across personas.

### 2.6 The capacity-deficit diagnostic

The capacity ratio *H(R, p) / C(R, p)* is the model-implied capacity diagnostic. A persona with ratio at or above 1.0 has, under the model's stated assumptions, a *capacity deficit*: the modeled currency-maintenance burden equals or exceeds the modeled allocated capacity. The team aggregate ratio summarizes the model-implied capacity position of the role distribution.

Two clarifications. First, the diagnostic is structural and model-implied, not behavioral. It does not claim that individual analysts are failing. It claims that under the model's stated assumptions, currency-maintenance burden exceeds the time plausibly available within the role distribution that the audit-centric model assumes. Real CAs sustain operational function through team-distribution, escalation, lowered effective accuracy thresholds, deeper specialization, and other compensating mechanisms. These compensations close the operational gap by relaxing the model's premise of a person at working accuracy on the full corpus.

Second, currency-maintenance is only part of compliance work. The application of currency to specific reviews (CPS amendments, ballot drafting, incident response, customer questions, regulator interaction) is additional. *H(R, p)* measures the cost of being ready to do compliance work; it does not measure the compliance work itself. This distinction is central to the headline framing in §6.

## 3. Parameters and evidence grades

Each parameter carries a central estimate, a low/high envelope, a citation, and an *evidence grade* indicating how directly the parameter is supported by published measurement.

| Parameter | Central | Range | Evidence grade | Source |
|---|---|---|---|---|
| Reading rate *r* (wpm) | 238 | 175–300 | literature_supported | Brysbaert (2019), JML |
| Working accuracy τ | 0.70 | 0.50–0.85 | inferential | Defined; sensitivity required |
| Decay τ_decay (days) | 120 | 60–180 | inferential | Murre & Dros (2015); Bahrick (1984); Arthur et al. (1998) |
| Diff review *t_diff* (hr) | 0.5 | 0.25–1.0 | practitioner_estimate | — |
| Triage *t_assess* (hr) | 0.5 | 0.25–1.0 | practitioner_estimate | — |
| Propagation *t_propagate* (hr) | 1.5 | 0.5–4.0 | practitioner_estimate | — |
| Substantive fraction φ | 0.40 | 0.25–0.60 | calibration_target | — |
| Effective hours/year | 1,800 | 1,700–1,900 | literature_supported | U.S. BLS CPS |
| Focused-work fraction | 0.45 | 0.30–0.55 | literature_supported | Mark et al.; Microsoft WTI |
| Persona corpus depth | per-persona | — | inferential | Constructed; calibration target |
| Persona change responsibility | per-persona | — | inferential | Constructed; calibration target |
| Persona TLS-BR allocation | per-persona | — | practitioner_estimate | Constructed; calibration target |

The strongest-cited parameters are the reading rate and the capacity-stack components (effective hours, focused-work fraction). The decay time constant is inferred from skill-decay meta-analyses and is the principal cited-but-not-directly-measured parameter. The persona structure and the per-change time parameters are practitioner estimates and are flagged as calibration targets for behavioral or time-and-motion validation in future versions.

## 4. Empirical inputs

### 4.1 Corpus measurements

For each released version of the CA/Browser Forum TLS Baseline Requirements from v1.0 (2012-07-01) through v2.2.1 (2025-12-16), `data/cabf_tls_br_corpus.csv` records the release date, word count, and RFC 2119 keyword counts (MUST, SHALL, SHOULD, MAY, MUST NOT, SHALL NOT) and their sum.

We refer to the keyword sum as the *RFC 2119 keyword inventory*, not as a "requirement count." Counting RFC 2119 keywords is a coarse proxy for normative obligation density. It overcounts repeated normative language, undercounts obligations expressed without RFC 2119 keywords, and does not capture the real unit of compliance work (clause-level applicability and operational implication). The proxy is useful for trajectory analysis and is what we use; the labeling is honest about what the number measures.

Across the measured period, the corpus grew from 18,500 to 71,500 words (×3.9) and from 492 to 1,177 RFC 2119 keywords (×2.4).

### 4.2 Observed-window cadence

The headline observed window is 2025-08-25 to 2026-03-31, spanning v2.1.7 through v2.2.6 inclusive. In this 218-day window:

- 10 versions were released (16.7 versions per year, annualized).
- 139 changes were tabulated (32 added, 34 removed, 73 modified; 233 changes per year annualized).

These counts are loaded from `data/cabf_tls_br_observed_window.csv` with provenance recorded in the file. They are not embedded as constants in any script. The aggregate change count is auditable in the source from which it was extracted. Per-version change counts within the window are out of scope for v0.1; the aggregate suffices for the v0.1 burden computation.

### 4.3 Note on corpus-version vs cadence-window coverage

The latest *measured* corpus version in this dataset is v2.2.1 (December 2025). The observed cadence window extends through v2.2.6 (March 2026). The headline computation uses the v2.2.1 corpus measurements (W = 71,500 words) with the cadence aggregate over v2.1.7 → v2.2.6 (139 changes across 218 days). The corpus measurements for v2.2.2 through v2.2.6 are out of scope for v0.1, so the headline computation uses the v2.2.1 corpus against the v2.1.7 → v2.2.6 cadence aggregate. The headline is therefore a slight underestimate of the true contemporaneous burden, since the corpus has continued to grow during the cadence window.

## 5. Results

### 5.1 Headline numbers

At observed 2025–2026 cadence and central parameters, the team-level aggregate is:

- **Total currency-maintenance burden: 850 hours / year (across 7 personas)**
- **Total allocated capacity: 1,012 hours / year**
- **Team capacity ratio: 0.84×**

Two of seven personas are individually above the capacity-deficit threshold of 1.0×:

| Persona | Burden (h/yr) | Capacity (h/yr) | Ratio |
|---|---|---|---|
| **CPS owner** | **309** | **243** | **1.27×** |
| **Audit liaison** | **182** | **162** | **1.12×** |
| Root program manager | 147 | 162 | 0.91× |
| Issuance / profile engineer | 61 | 122 | 0.50× |
| Engineering lead | 41 | 81 | 0.50× |
| Validation lead | 92 | 202 | 0.46× |
| Executive | 17 | 40 | 0.42× |

The CPS owner's currency-maintenance burden exceeds the role's plausible time budget by 27%. The audit liaison exceeds by 12%. Three further personas operate above 0.5×, leaving little slack for the application work the roles are also expected to perform.

### 5.2 Scenario envelope

| Scenario | Burden (h/yr) | Capacity (h/yr) | Capacity ratio |
|---|---|---|---|
| Low (optimistic) | 308 | 1,306 | 0.24× |
| Central | 850 | 1,012 | 0.84× |
| High (pessimistic) | 2,824 | 638 | 4.43× |

The envelope is wide because several practitioner-estimate parameters compound. The high scenario is dominated by pessimistic per-change triage and propagation times together with a higher substantive-edit fraction; under those conditions, the team is more than 4× over capacity. The low scenario reflects optimistic per-change handling and a higher capacity baseline.

### 5.3 Composition

In the central scenario, change handling (diff review, triage, propagation) accounts for approximately 80% of the team-level budget. Baseline corpus reads account for approximately 20%. The headline qualitative finding is that **change cadence governs the budget, not corpus size**. This finding is robust across the full sensitivity envelope: even at the most generous decay parameters, the change-driven terms dominate.

### 5.4 Trajectory

The historical trajectory (per-version periods, illustrative cadence estimator) shows the team capacity ratio rising from 0.27–0.45× in 2014–2018 to 0.52–0.73× in 2021–2025. The observed-window measurement (10 versions / 139 changes over 218 days) shows the ratio continuing to rise to 0.84× central.

The historical estimator is illustrative. It uses the requirement-keyword delta as a proxy for change count, multiplied by 2.5 (calibrated against the observed window). It does not capture modifications that leave the requirement-keyword count unchanged, and it has high variance across periods. The trajectory should be read as "the burden has grown over time, and the most recent observed window shows it close to the team-level capacity ceiling," not as a precise growth curve.

### 5.5 Sensitivity

Across the full envelope of decay parameters (τ_decay ∈ [60, 240] days, τ ∈ [0.50, 0.90]), the team capacity ratio ranges from 0.65 to 1.65. The 1.0× contour passes through the upper-left quadrant of the parameter space (short decay, high accuracy threshold), with the central point comfortably inside the sub-1.0× region. The qualitative finding, that change handling dominates and that the most-burdened personas exceed capacity, survives the full envelope.

## 6. What the numbers say

**A note on scale.** The model parameterizes per-role, but the load-bearing claim is at team scale. The headline 0.84× is the team-aggregate capacity ratio. The 1.08 team-equivalents reading is the team's allocated capacity being exceeded by CABF currency-maintenance alone. Per-role readings (CPS owner 1.27×, audit liaison 1.12×, etc.) are intermediate quantities that surface where load concentrates within a team, and they are useful in their own right, but the diagnostic claim of the paper is that *a plausibly-staffed organization* cannot absorb the modeled burden at the working-accuracy threshold the audit-centric model implicitly assumes. Individual analyst behavior — including the specific mechanisms by which currency is maintained, whether through schemas, exception memory, peer review, tooling, or rereading — is abstracted into the time-equivalent burden the team must absorb.

We make five observations from the data, in increasing scope.

**The CPS owner persona has a model-implied capacity deficit.** Under v0.1 assumptions, the CPS owner faces 309 hours per year of TLS-BR currency-maintenance burden against 243 hours per year of model-allocated capacity. The 27% gap is currency-maintenance only, before the application work of drafting CPS amendments, responding to ballots, or supporting audit cycles. Real CPS owners do their jobs; the model's reading is that they do them by violating one of the model's premises (full corpus depth, working accuracy maintained without lowered thresholds, dedicated allocation untouched by adjacent regimes).

**The team aggregate sits near the model's capacity threshold.** The team-aggregate capacity ratio of 0.84× means that under model assumptions, 84% of the team's TLS-BR-allocated capacity is consumed by currency-maintenance alone. The remaining 16% is what the team would have available for application work, specific reviews, amendments, incident response, audit support, training new staff. The lived experience compliance teams report, being "always behind" on something, and the something rotating depending on which regime is currently moving fastest, is consistent with this finding without being directly proved by it.

**Currency-maintenance is what we measure. It is not implementation.** The 1,094 hours per year of CABF stack burden is the cost of staying current enough to know what changed, what it means, who it affects, and what needs to be done. It does not include engineering changes to CA software, CPS drafting and approval, evidence collection for audits, auditor correspondence, operational rollout, root program correspondence, incident investigation and disclosure, customer-facing assurance work, or contract amendments. Those activities consume additional time. The number reported here measures *the cost of keeping the map current*, not the cost of moving the terrain.

**Expressed as headcount, the CABF currency-maintenance burden is roughly one senior expert-year per year.**

| Capacity basis | Hours/year | Person-year equivalent |
|---|---|---|
| Nominal full-time (2,080 h, no PTO/sick/training) | 1,094 | 0.53 FTE |
| Realistic focused-expert (1,500 h, after meetings/interruption recovery) | 1,094 | 0.73 FTE |
| Model-allocated team currency capacity (1,012 h across 7 personas) | 1,094 | 1.08 team-equivalents |

In practice, the burden is fragmented across CPS ownership, validation interpretation, audit liaison, root program coordination, and engineering. It is not one person sitting in a chair. It is the equivalent of one scarce senior person's annual capacity spread across the team, and the team also bears every other compliance activity on top of that. The "1.08 team-equivalents" reading is the most directly interpretable: under the model, the team's TLS-BR-allocated capacity is fully consumed by CABF currency-maintenance alone, with nothing left for the rest of the regime stack or for application work.

**The trajectory is upward and the measurement is a lower bound.** Both corpus size and change cadence have grown monotonically since 2012. The corpus is roughly 3.9× its 2012 size; the most recent observed change cadence implies roughly 233 changes per year, against a long-run trajectory that has risen with each successive version-family. The CABF stack measurement covers five regimes; the broader stack (§9) includes Tier 2 root programs, ETSI, WebTrust, IETF RFCs, NIST cryptographic policy, and the CA's own CPS reconciled against all of the above. The single-stack-subset number is, by construction, a lower bound on the aggregate.

The implication is not that compliance teams are failing or that auditors are negligent. The implication is that the audit-centric model has a model-implied mismatch with the cadence and volume of the regimes it is meant to assess. Periodic assessments against a corpus assumed to be stable, performed by reviewers assumed to be current, presume conditions the data say no longer hold. The mismatch grows with every additional ballot, every additional regime, every additional incorporated specification. Real teams sustain operational function through specialization, triage, delegation, lowered effective working accuracy, selective attention, and other compensating mechanisms. Each of these carries a cost that the audit model does not recognize because the model assumes the working-accuracy premise is met.

What is at risk under sustained capacity deficit is not the existence of compliance work. That gets done. What is at risk is the *quality* of reading and the depth of understanding that the audit model implicitly assumes. Time available for substantive review at the model's assumed level of currency is, by construction, less than what the role distribution can plausibly afford at observed cadences. The work that gets done in the time available is not necessarily wrong, but it is, by construction, not the work the audit model assumes is being done.

## 7. Biases

The model contains biases in both directions. We name them so the reader can adjust intuitively.

**Biases that increase the reported burden (model overstates):**

- *No tooling credit.* The model assumes no automated assistance with currency-maintenance, propagation, or cross-regime reconciliation. Real teams use diff tools, internal wikis, ballot trackers, and various forms of computational assistance. We do not credit these because the activity *H(R, p)* aims to measure, sustaining working accuracy on a normative corpus, sufficient to perform substantive review without re-reading source material, is a property of human cognition, and the model's premise is whether the time available to a human in the role distribution is sufficient to maintain that property. Whatever computational assistance a team employs, the reported budget is the burden the human side of the role would have to carry to satisfy the model's working-accuracy premise unaided. Readers operating with computational assistance should interpret the reported numbers as the upper bound on the human portion of the work.
- *No team-knowledge sharing credit.* The model assumes each persona maintains their own working memory independently. Real teams share notes, debrief in meetings, and circulate ballot summaries; the marginal cost of currency for the second person on a topic is lower than for the first.
- *No expertise-curve credit.* A 10-year veteran of the BRs has lower reacquisition needs than the model assumes, because deeply-learned schemas reduce the time required to restore operational readiness after change. The reacquisition rate is calibrated for material that is not deeply learned.

**Biases that decrease the reported burden (model understates):**

- *Single regime only.* TLS BRs are one of more than ten governing regimes for a publicly-trusted CA. The aggregate is strictly larger.
- *No cross-regime reconciliation term.* When BRs change, the implications must be reconciled against root program policies, ETSI/WebTrust criteria, and incorporated RFCs. The current model contains no coupling term.
- *No application time.* The model measures readiness to do compliance work, not the work itself. The application work (CPS amendments, ballot drafting, audit support, incident response) is additional.
- *Conservative practitioner estimates.* Triage and propagation times reflect routine changes; complex changes (cryptographic transitions, validation method retirements) take materially longer.
- *No incident-driven spikes.* The model assumes steady-state cadence. Real years contain incidents, audits, and program transitions that compress months of normal cadence into weeks.
- *Conservative historical estimator.* The 2.5× keyword-delta multiplier is calibrated against the observed window and likely undercounts modifications that do not change the keyword total.

The biases run in opposite directions. We do not claim they cancel exactly. We do claim that the structural finding, that the burden is comparable to or larger than the plausibly-available capacity, is robust to either resolution.

## 8. Limitations

The decay literature (Murre & Dros 2015; Bahrick 1984; Arthur, Bennett, Stanush & McNelly 1998) does not directly study working accuracy on a complex normative corpus. We use it inferentially: meta-analytic skill-decay studies report approximately 30% performance decrement at 30 days under non-recurrent conditions for cognitive (knowledge) skills, consistent with τ_decay in the 90–150 day range. Sensitivity analysis (§5.5) shows the qualitative finding survives across τ_decay ∈ [60, 240] days, but the parameter is not directly measured. Behavioral validation is out of scope for v0.1 and is the highest-priority empirical extension named in the roadmap.

The substantive-edit fraction φ, the per-change triage time *t_assess*, and the per-substantive-edit propagation time *t_propagate* are practitioner estimates without published measurement. The high-end sensitivity values for these parameters drive the upper bound of the budget envelope. Hand-classification of the 139 observed-window changes for substantive vs. editorial content is the highest-leverage calibration sprint; a labeled sample replaces the practitioner estimate of φ with a measurement and tightens the central estimate.

The persona definitions (corpus depth, change responsibility, domain allocation per persona) are themselves practitioner estimates. They reflect plausible role distinctions in a mid-to-large publicly-trusted CA. Variation across organizations is significant. Calibration against partner-CA staffing data is out of scope for v0.1 and is named in the roadmap.

The historical edit-count estimator (2.5 × Δ keyword count) is calibrated against a single observed window. It is illustrative, not authoritative. Direct per-version change measurement is named in the roadmap as the replacement.

The current model contains no cross-regime coupling term. *H(R, p)* as computed here is a strict lower bound on real-world burden, since real-world burden includes reconciliation across overlapping regimes.

## 9. The regime stack

The TLS Baseline Requirements are one regime out of more than ten that govern the operations of a publicly-trusted Certificate Authority. Two distinct change-propagation models are present in the stack, and the burden model *H(R)* in this document applies cleanly to one of them and not the other. We make this distinction explicit because it determines which regimes we measure with this index and which we do not.

### 9.1 Two tiers of regimes

**Tier 1: versioned, ballot-driven.** CA/Browser Forum documents (TLS BRs, S/MIME BRs, EV Guidelines, Code Signing BRs, Network and Certificate System Security Requirements) are produced through a public ballot process and released as versioned redlines. Each version is the unit of normative change. Per-version edits are auditable from the CA/B Forum redline records, and the count of edits per release is a complete measure of normative change rate over that period. The 139 changes recorded for TLS BR v2.1.7 → v2.2.6 (§4.2) is a complete count of normative changes in the observed window, not a sample of it. Applying *H(R)* to a Tier 1 regime using its version cadence and per-version edits is the operation the model was designed for.

**Tier 2: continuously communicated.** Root programs (Mozilla Root Store Policy, Chrome Root Program Policy, Apple Root Certificate Program, Microsoft Trusted Root Program) operate on a different model. The versioned policy document is a periodic snapshot of decisions communicated to CAs through other channels, m.d.s.policy threads and CCADB records (Mozilla); the Chrome Root Program GitHub repository, blog posts, and CABF ballot positions (Chrome); developer documentation updates and root program email (Apple); TechCommunity posts, security baseline updates, and KB articles (Microsoft). When a new version of a root program policy ships, it codifies decisions that were already operative through those channels, often months or years earlier. Counting versions of a Tier 2 regime to estimate its change rate is a category error: it measures the cadence of codification, not the cadence of normative change.

The classification:

| Regime | Tier | Visible cadence (versions/yr) | Status in this index |
|---|---|---|---|
| CA/Browser Forum TLS BR | 1 | 16.74 | *H(R)* computed; full data |
| CA/Browser Forum S/MIME BR | 1 | 5.76 | *H(R)* computed; cadence and changes ingested |
| CA/Browser Forum NetSec | 1 | 3.51 | *H(R)* computed; single-window note |
| CA/Browser Forum EV Guidelines | 1 | 0.99 | *H(R)* computed; restructure ballot extended-baseline |
| CA/Browser Forum Code Signing BR | 1 | 1.54 | *H(R)* computed |
| Mozilla Root Store Policy | 2 | 1.30 (floor) | *H(R)* not computed; see §9.4 |
| Chrome Root Program Policy | 2 | 3.56 (floor) | *H(R)* not computed; see §9.4 |
| Apple Root Certificate Program | 2 | single tracked version | *H(R)* not computed; see §9.4 |
| Microsoft Trusted Root Program | 2 | single tracked version | *H(R)* not computed; see §9.4 |

The remainder of the stack, WebTrust modules, ETSI EN 319 series, IETF RFCs incorporated by reference, NIST SP 800 series, FIPS 140-3, eIDAS, NIS2, the CA's own CPS, is not yet ingested. Several behave like Tier 1 (versioned standards with cadence-bound ballot or revision processes) and several have hybrid characteristics. Future versions of this index will classify and ingest each.

### 9.2 Tier 1: modeled CABF stack burden

Five CABF regimes have ingested cadence, aggregate change-count, and per-section change-record data sufficient to model team-level change-handling burden using the persona-weighted formula (§2.4). Per-section change records are now complete for all five regimes: TLS BR (139 of 139), S/MIME BR (29 of 29), NetSec (48 of 48), Code Signing BR (19 of 19), and EV Guidelines (145 of 145), totaling 380 fully-classified change events. The aggregate change counts that drive the model's burden computation are sourced from the CPS Dev App tracking system for all five regimes. The change-handling component alone, excluding baseline corpus reading, at central scenario parameters:

| Regime | V/yr | E/yr | Team change-handling burden (h/yr) |
|---|---|---|---|
| TLS BR | 16.74 | 232.7 | 696 |
| Network Security Requirements\* | 3.51 | 84.2 | 248 |
| EV Guidelines (transition baseline) | 0.99 | 71.4 | 208 |
| S/MIME BR | 5.76 | 33.4 | 105 |
| Code Signing BR | 1.54 | 14.7 | 45 |

\* NetSec figure is provisional: annualized from a single 208-day v2.0.4 → v2.0.5 release window, which is likely to overstate steady-state cadence. Read as an upper bound on this regime's contribution.

The Network Security figure is provisional and worth flagging explicitly. The observed window is a single 208-day v2.0.4 → v2.0.5 release containing 48 changes, and a single release is not a steady-state cadence measurement. Annualizing it gives 3.51 versions/yr and 48 changes/yr, which produces 248 h/yr of modeled burden. Once a second release lands the steady-state cadence is almost certainly lower than this; NetSec historically releases on a multi-year cycle. The 248 h/yr should be read as an upper-bound provisional value, and the 1,094 h/yr stack total is correspondingly biased upward by this regime in the current window. We retain NetSec in the table because excluding it would understate the structural burden the model is meant to surface; we flag it as provisional rather than removing it.

The EV Guidelines observation is annualized over the post-restructure baseline because the literal v2.0.0 → v2.0.1 window of 19 days contained 145 changes from a major-restructure ballot and is not representative of steady-state. We extend the EVG annualization window from v2.0.0 (2024-04-17) through the v0.1 snapshot date (2026-04-28), a 741-day post-restructure baseline, giving 71.4 changes per year. **EVG v2.0.2 (2026-03-31) is excluded from this measurement window.** It was published 28 days before the v0.1 snapshot date; per-section change records were not yet ingested at the time of the snapshot. Inclusion would extend the post-restructure baseline by approximately one month and add a small number of additional changes, slightly increasing the EVG transition burden estimate. Ingestion is covered by the next data refresh named in the roadmap.

**Steady-state CABF stack (4 regimes excluding EV transition): ~1,094 hours per year of change-handling burden, before any baseline corpus reading.** Adding the EV transition baseline brings the total to approximately 1,302 hours per year. The sensitivity envelope across scenarios is approximately 421–3,054 hours per year for the steady-state stack.

For comparison, the team's TLS-BR-allocated capacity is 1,012 hours per year. The team's plausible CABF allocation across all five regimes is larger than 1,012 hours per year but bounded. Total team focused-work hours summed across seven personas at central parameters is approximately 5,670 hours per year, of which the team distributes across all of CABF, all root program policies, ETSI, WebTrust, internal CPS reconciliation, and the IETF stack. If CABF receives roughly 30–50% of total compliance focused-work hours (a plausible but unmeasured range), the team's CABF allocation is in the range 1,700–2,800 hours per year.

The modeled change-handling burden of ~1,094 hours per year therefore represents **39–64% of the team's plausibly-available CABF capacity**, and that is change handling alone. Baseline corpus reading and cross-regime reconciliation are not included. This single subset of the stack, five CABF documents of more than ten governing regimes, is consuming a substantial fraction of the team's CABF capacity before baseline reading and before any application work. The implication is consistent across plausible allocation assumptions.

#### A note on persona weighting across the CABF stack

The §9.2 numbers apply the same persona structure (corpus depth, change responsibility, domain allocation per persona) to every CABF regime. This is a deliberate v0.1 scope choice: the *H(R, p)* formula is calibrated against TLS BR role distinctions, and the multi-regime computation reuses those weights. In practice, a validation lead's relationship to S/MIME BR Section 3 is qualitatively different from their relationship to TLS BR Section 3.2, and a validation lead's relationship to NetSec Section 1 (infrastructure security) is different again. Reusing the TLS-shaped persona weights across regimes systematically over-counts persona engagement on regimes where the persona's actual scope is narrower, and undercounts on regimes where it is broader. The directional effect on the aggregate is uncertain and likely small relative to the parameter envelope; the right calibration is a regime-persona matrix where each persona has different (corpus_depth, change_responsibility, domain_allocation) tuples per regime, named as a roadmap item. The §9.2 result should be read as a **TLS-persona-weighted CABF stack burden**, not a fully-calibrated multi-regime staffing model.

### 9.3 Why we do not compute *H(R)* for Tier 2 regimes

Applying the *H(R)* model to a Tier 2 regime using only version cadence would produce a number that looks precise and is in fact systematically wrong. The model takes *V* (versions per year) and *E* (edits per year) as inputs. For Tier 1 regimes, the per-version edits captured in the redline are the operative change events. For Tier 2 regimes, the per-version edits captured when a periodic snapshot ships are a small fraction of the operative change events. The rest live in mailing list archives (m.d.s.policy), bug trackers (Bugzilla), structured policy databases (CCADB), GitHub issues, blog posts, and email correspondence. This index does not yet ingest those channels.

A Tier 2 burden number using only version data would understate the actual burden by an unknown but potentially large factor. We choose to leave Tier 2 burden uncomputed in this version rather than compute a misleading number. The visible version cadence is still useful as a lower-bound floor and as a comparator for thinking about the variation in change-propagation models across the stack. Future versions will ingest the appropriate change-event channels for each Tier 2 regime, m.d.s.policy thread classification for Mozilla, GitHub issue and blog-post tracking for Chrome, root program email and developer documentation diffs for Apple and Microsoft, and apply a tier-appropriate burden computation.

### 9.4 The lower-bound argument, refined

The single-regime TLS BR measurement (team capacity ratio 0.84× at central scenario) and the five-regime CABF stack measurement (1,094 h/yr steady-state change-handling burden, 39–64% of plausibly-available CABF capacity) are both lower bounds on the full-stack burden. The lower-bound argument requires care because the full stack is not purely additive: knowledge overlaps across regimes, regime volatility differs, and the same persona may allocate attention across multiple regimes in ways that share rather than add the work. The right framing is not "the stack burden is N times the single-regime burden" but rather:

> If five Tier 1 CABF regimes alone consume 39–64% of the team's plausibly-available CABF capacity at observed cadence, change-handling only, before baseline corpus reading or cross-regime reconciliation, then the broader regime stack (Tier 2 root programs, ETSI, WebTrust, IETF, NIST, internal CPS) cannot be covered at the working-accuracy threshold the audit-centric model assumes without one or more of the following: deeper specialization that reallocates effective corpus depth across roles; reduced effective working accuracy on regimes where currency-maintenance time is unavailable; additional staffing; or compensating mechanisms outside the model's scope.

This is the careful version of the structural claim. It identifies how real CAs sustain operational function: specialization, lowered effective accuracy in practice, additional staffing, and a portfolio of institutional mechanisms (peer review, escalation paths, precedent systems, tooling-supported recall, event-triggered re-engagement). Each of these absorbs some portion of the time-equivalent burden the model computes. None of them eliminates the burden — they redistribute it across people, tools, and processes. The model's claim is about the time-equivalent total, not the mechanism of expenditure. Whether currency is maintained by an analyst rereading source material, a senior peer cross-checking a junior analyst's reasoning, an internal wiki of precedent, a diff tool flagging changed sections, or all of these together, the question is whether the aggregate time-equivalent fits in plausible team capacity. The trajectory along all of these dimensions is upward.

A reviewer might reasonably ask whether the audit-centric model assumes individual reviewer mastery or organizational redundancy. The answer is that the relevant audit frameworks (WebTrust, ETSI EN 319 411-1) are agnostic on the mechanism: control objectives are specified in terms of organizational outcomes (CA performs validations correctly, manages keys appropriately, produces correct certificate profiles) rather than in terms of how individual analyst recall is sustained. The implicit assumption the model tests is therefore the organizational one: that the attesting organization, by some combination of mechanisms, sustains the working knowledge needed to perform substantive review when called upon. The capacity-deficit finding does not say that individual analysts forget faster than τ_decay implies; it says that the time-equivalent budget required to sustain organizational competence at the working-accuracy threshold exceeds the team's plausibly-allocable capacity. That is an organizational claim, not a cognitive one.

A second source of lower-bound bias deserves explicit mention. The 1,094 h/yr stack number includes baseline corpus reading only for TLS BR; for the four other CABF regimes (S/MIME BR, NetSec, Code Signing BR, EV Guidelines), per-version word counts are not yet ingested, so `scripts/stack_change_burden.py` excludes the *n_passes · W · d_p* term from those four regimes' contributions. As reference, TLS BR's team-aggregate baseline reading at central parameters is in the tens of hours per year. If the four other regimes were of broadly comparable size to TLS BR, including their baseline reading would raise the stack number meaningfully. Per-version corpus extraction across all five regimes is the second-listed item under Open data work in the README and is the highest-priority data work that does not require partner-CA cooperation.

## 10. Reproducibility

This index is computed from versioned inputs and is reproducible by running:

```
pip install -r requirements.txt
python scripts/compute_headline.py
python scripts/per_regime_cadence.py
python scripts/per_regime_workload.py
python scripts/stack_change_burden.py
python scripts/cabf_stack_fte.py
python scripts/make_figures.py
python scripts/build_paper.py
pytest tests/
```

Every reported number is loaded from CSV and YAML inputs. No empirical values are hard-coded in scripts. The methodology document, parameter file, model implementation, corpus measurements, figure-generation code, and academic-paper LaTeX source are all version-controlled. The CI pipeline re-runs the deterministic computation on changes to inputs or model, including a two-pass `pdflatex` rebuild of the paper PDF. The paper build sets `SOURCE_DATE_EPOCH` from the snapshot date so the embedded PDF metadata timestamp is stable across rebuilds.

We use the framing *reproducible from versioned inputs* rather than *continuously recomputed* or *weekly refreshed*. The CI workflow regenerates outputs from data already committed to the repository on a weekly schedule and on every push; **it does not fetch new data from CA/Browser Forum, Mozilla, Chrome, Apple, or Microsoft**. Updates to the underlying data require an explicit commit. Automated upstream ingest is named in the roadmap. Claims like "continuously updated" or "weekly refreshed index" should be avoided in favor of the more precise "regenerated from versioned inputs."

Methodology versioning is explicit. Results are tagged to the methodology version that produced them. Numbers from one methodology version are not directly comparable to numbers from another without explicit reconciliation.

## 11. Citations

- Arthur, W., Bennett, W., Stanush, P. L., & McNelly, T. L. (1998). Factors that influence skill decay and retention: A quantitative review and analysis. *Human Performance*, 11(1), 57–101.
- Bahrick, H. P. (1984). Semantic memory content in permastore: Fifty years of memory for Spanish learned in school. *Journal of Experimental Psychology: General*, 113(1), 1–29.
- Brysbaert, M. (2019). How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 104047.
- Mark, G., Gudith, D., & Klocke, U. (2008). The cost of interrupted work: more speed and stress. *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '08)*, 107–110.
- Murre, J. M. J., & Dros, J. (2015). Replication and analysis of Ebbinghaus' forgetting curve. *PLoS ONE*, 10(7), e0120644.
- U.S. Bureau of Labor Statistics. *Current Population Survey, Table A-7: Hours of work and earnings for occupational categories.* (Annual.)
- Microsoft Work Trend Index (annual report series). https://www.microsoft.com/en-us/worklab/work-trend-index

Additional citations on regulatory and legal corpus measurement, cognitive load, and related work will be added as the related-work section is expanded in subsequent releases.

## 12. Release history

- **v0.1 (2026-04-28).** Initial public release.
