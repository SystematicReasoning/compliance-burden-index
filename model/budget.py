"""
Knowledge Currency Budget — model implementation.

The version of this methodology is loaded from the VERSION file at the repo
root by scripts that need it. Source code does not embed the version.

The budget for regime R, persona p:

    H(R, p) = (W * d_p) / (60 * r) * n_passes
            + V * t_diff * I_p
            + E * d_p * t_assess
            + E * d_p * c_p * phi * t_propagate

where
    W       = corpus word count
    d_p     = persona corpus depth (fraction of corpus held in working memory)
    r       = reading rate (wpm) — note explicit /60 to convert to hours
    n_passes = re-read passes per year, derived from decay tau and threshold tau_min
    V       = versions per year
    t_diff  = hours per version-level diff review
    I_p     = indicator: 1 if persona does version diff review, else 0
    E       = total changes per year
    t_assess = hours per change for triage
    c_p     = persona change responsibility
    phi     = substantive-change fraction
    t_propagate = hours per substantive change for propagation work

Persona-level capacity is:

    C(p) = effective_hours * focused_fraction * domain_allocation_p

The capacity ratio H(R, p) / C(p) is the structural diagnostic.

The team-level budget is sum over personas. Team-level capacity is sum over
personas. The team-level capacity ratio is the team aggregate.
"""

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Parameter loading
# ---------------------------------------------------------------------------

@dataclass
class Persona:
    persona_id: str
    description: str
    corpus_depth: float
    change_responsibility: float
    domain_allocation: float
    requires_version_diff_review: bool


@dataclass
class Parameters:
    """Parameters at a specific scenario level (low / central / high).

    Convention:
      - low  = optimistic for the analyst (lower budget):
                   faster reading, lower threshold, longer decay,
                   lower per-change times, lower substantive fraction
      - high = pessimistic for the analyst (higher budget):
                   slower reading, higher threshold, shorter decay,
                   higher per-change times, higher substantive fraction
    """

    reading_wpm: float
    working_accuracy_threshold: float
    decay_time_constant_days: float
    per_version_diff_review_hours: float
    per_change_triage_hours: float
    per_substantive_change_propagation_hours: float
    substantive_change_fraction: float
    effective_hours_per_year: float
    focused_work_fraction: float
    personas: List[Persona] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path, scenario: str = "central") -> "Parameters":
        with open(path) as f:
            cfg = yaml.safe_load(f)

        if scenario not in {"low", "central", "high"}:
            raise ValueError(f"Unknown scenario: {scenario}")

        # For each parameter, choose the bound aligned with the scenario semantics
        if scenario == "central":
            wpm = cfg["reading_rate"]["central_wpm"]
            tau_min = cfg["working_accuracy_threshold"]["central"]
            decay = cfg["decay_time_constant_days"]["central"]
            t_diff = cfg["per_version_diff_review_hours"]["central"]
            t_assess = cfg["per_change_triage_hours"]["central"]
            t_propagate = cfg["per_substantive_change_propagation_hours"]["central"]
            phi = cfg["substantive_change_fraction"]["central"]
            eff_hours = cfg["capacity"]["effective_hours_per_year"]["central"]
            focused = cfg["capacity"]["focused_work_fraction"]["central"]
        elif scenario == "low":
            # Optimistic: faster reading, lower threshold, longer decay, lower per-change costs
            wpm = cfg["reading_rate"]["high_wpm"]
            tau_min = cfg["working_accuracy_threshold"]["low"]
            decay = cfg["decay_time_constant_days"]["high"]
            t_diff = cfg["per_version_diff_review_hours"]["low"]
            t_assess = cfg["per_change_triage_hours"]["low"]
            t_propagate = cfg["per_substantive_change_propagation_hours"]["low"]
            phi = cfg["substantive_change_fraction"]["low"]
            # Capacity: optimistic = MORE capacity (high effective hours, high focus, etc.)
            eff_hours = cfg["capacity"]["effective_hours_per_year"]["high"]
            focused = cfg["capacity"]["focused_work_fraction"]["high"]
        else:  # high
            # Pessimistic: slower reading, higher threshold, shorter decay, higher per-change costs
            wpm = cfg["reading_rate"]["low_wpm"]
            tau_min = cfg["working_accuracy_threshold"]["high"]
            decay = cfg["decay_time_constant_days"]["low"]
            t_diff = cfg["per_version_diff_review_hours"]["high"]
            t_assess = cfg["per_change_triage_hours"]["high"]
            t_propagate = cfg["per_substantive_change_propagation_hours"]["high"]
            phi = cfg["substantive_change_fraction"]["high"]
            # Capacity: pessimistic = LESS capacity
            eff_hours = cfg["capacity"]["effective_hours_per_year"]["low"]
            focused = cfg["capacity"]["focused_work_fraction"]["low"]

        personas = [
            Persona(
                persona_id=pid,
                description=pcfg["description"],
                corpus_depth=pcfg["corpus_depth"],
                change_responsibility=pcfg["change_responsibility"],
                domain_allocation=pcfg["domain_allocation"],
                requires_version_diff_review=pcfg["requires_version_diff_review"],
            )
            for pid, pcfg in cfg["personas"].items()
        ]

        return cls(
            reading_wpm=wpm,
            working_accuracy_threshold=tau_min,
            decay_time_constant_days=decay,
            per_version_diff_review_hours=t_diff,
            per_change_triage_hours=t_assess,
            per_substantive_change_propagation_hours=t_propagate,
            substantive_change_fraction=phi,
            effective_hours_per_year=eff_hours,
            focused_work_fraction=focused,
            personas=personas,
        )


# ---------------------------------------------------------------------------
# Core model functions
# ---------------------------------------------------------------------------

def re_read_passes_per_year(decay_tau_days: float, accuracy_threshold: float) -> int:
    """
    Number of full corpus re-reads per year required to keep working accuracy
    above threshold given exponential decay with time constant tau.

    A(t) = exp(-t / tau).
    t_max = -tau * ln(threshold).
    n_passes = ceil(365 / t_max), floor of 1.
    """
    max_interval_days = -decay_tau_days * math.log(accuracy_threshold)
    if max_interval_days <= 0:
        return 1
    return max(1, math.ceil(365.0 / max_interval_days))


def baseline_corpus_hours(word_count: int, n_passes: int, wpm: float, depth: float = 1.0) -> float:
    """Hours per year for baseline corpus reads, weighted by persona corpus depth."""
    return n_passes * (word_count * depth) / (60.0 * wpm)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PersonaBudget:
    persona_id: str
    corpus_depth: float
    change_responsibility: float
    domain_allocation: float

    baseline_hours: float
    diff_review_hours: float
    triage_hours: float
    propagation_hours: float
    total_hours: float

    capacity_hours: float
    capacity_ratio: float

    def as_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "corpus_depth": self.corpus_depth,
            "change_responsibility": self.change_responsibility,
            "domain_allocation": self.domain_allocation,
            "baseline_hours": round(self.baseline_hours, 1),
            "diff_review_hours": round(self.diff_review_hours, 1),
            "triage_hours": round(self.triage_hours, 1),
            "propagation_hours": round(self.propagation_hours, 1),
            "total_hours": round(self.total_hours, 1),
            "capacity_hours": round(self.capacity_hours, 1),
            "capacity_ratio": round(self.capacity_ratio, 2),
        }


@dataclass
class TeamBudget:
    """Team-level aggregate across personas."""
    word_count: int
    versions_per_year: float
    changes_per_year: float
    n_passes: int
    personas: List[PersonaBudget]

    @property
    def total_hours(self) -> float:
        return sum(p.total_hours for p in self.personas)

    @property
    def total_capacity(self) -> float:
        return sum(p.capacity_hours for p in self.personas)

    @property
    def aggregate_capacity_ratio(self) -> float:
        if self.total_capacity <= 0:
            return float("inf")
        return self.total_hours / self.total_capacity

    def as_dict(self) -> dict:
        return {
            "word_count": self.word_count,
            "versions_per_year": round(self.versions_per_year, 2),
            "changes_per_year": round(self.changes_per_year, 1),
            "n_passes": self.n_passes,
            "team_total_hours": round(self.total_hours, 1),
            "team_total_capacity_hours": round(self.total_capacity, 1),
            "team_aggregate_capacity_ratio": round(self.aggregate_capacity_ratio, 2),
            "personas": [p.as_dict() for p in self.personas],
        }


# ---------------------------------------------------------------------------
# Budget computation
# ---------------------------------------------------------------------------

def compute_persona_budget(
    persona: Persona,
    word_count: int,
    versions_per_year: float,
    changes_per_year: float,
    params: Parameters,
    n_passes: int,
) -> PersonaBudget:
    """Knowledge currency budget for a single persona."""
    baseline = baseline_corpus_hours(
        word_count=word_count,
        n_passes=n_passes,
        wpm=params.reading_wpm,
        depth=persona.corpus_depth,
    )
    diff_review = (
        versions_per_year * params.per_version_diff_review_hours
        if persona.requires_version_diff_review else 0.0
    )
    triage = changes_per_year * persona.corpus_depth * params.per_change_triage_hours
    propagation = (
        changes_per_year
        * persona.corpus_depth
        * persona.change_responsibility
        * params.substantive_change_fraction
        * params.per_substantive_change_propagation_hours
    )
    total = baseline + diff_review + triage + propagation

    capacity = (
        params.effective_hours_per_year
        * params.focused_work_fraction
        * persona.domain_allocation
    )
    ratio = total / capacity if capacity > 0 else float("inf")

    return PersonaBudget(
        persona_id=persona.persona_id,
        corpus_depth=persona.corpus_depth,
        change_responsibility=persona.change_responsibility,
        domain_allocation=persona.domain_allocation,
        baseline_hours=baseline,
        diff_review_hours=diff_review,
        triage_hours=triage,
        propagation_hours=propagation,
        total_hours=total,
        capacity_hours=capacity,
        capacity_ratio=ratio,
    )


def compute_team_budget(
    word_count: int,
    versions_per_year: float,
    changes_per_year: float,
    params: Parameters,
) -> TeamBudget:
    """Aggregate budget across all personas."""
    n_passes = re_read_passes_per_year(
        params.decay_time_constant_days,
        params.working_accuracy_threshold,
    )
    persona_budgets = [
        compute_persona_budget(
            persona=p,
            word_count=word_count,
            versions_per_year=versions_per_year,
            changes_per_year=changes_per_year,
            params=params,
            n_passes=n_passes,
        )
        for p in params.personas
    ]
    return TeamBudget(
        word_count=word_count,
        versions_per_year=versions_per_year,
        changes_per_year=changes_per_year,
        n_passes=n_passes,
        personas=persona_budgets,
    )
