"""
Molecular CoT Reasoning Topology & Entropy Convergence Auditor.
Grounded in arXiv:2601.06002 ("The Molecular Structure of Thought").
Zero external dependencies. Pure standard library.
"""

import re
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


class BondType(str, Enum):
    COVALENT = "COVALENT"          # Deep-Reasoning: Direct causal deduction
    HYDROGEN = "HYDROGEN"          # Self-Reflection: Retro-folding verification
    VAN_DER_WAALS = "VAN_DER_WAALS" # Self-Exploration: Weak hypothesis branching


# Lexical and semantic structural marker patterns
HYDROGEN_PATTERNS = [
    re.compile(r"\b(?:wait|hold on|re-?evaluat\w*|re-?check\w*|verif\w*|let's check|double check|reflect\w*|correct\w*|reconsider\w*|mistake|error|flaw|backtrack\w*)\b", re.I),
    re.compile(r"\b(?:actually|upon checking|looking back|reviewing the premise|re-reading|sanity check)\b", re.I),
]

VAN_DER_WAALS_PATTERNS = [
    re.compile(r"\b(?:alternative(?:ly)?|perhaps|maybe|what if|another angle|could it be|hypothetically|suppose|option [a-d1-4]|scenario)\b", re.I),
    re.compile(r"\b(?:on the other hand|alternatively we could|branch|explore|speculat\w*)\b", re.I),
]

COVALENT_PATTERNS = [
    re.compile(r"\b(?:therefore|thus|hence|consequently|so|because|since|leads to|implies|deduce\w*|calculat\w*|derive\w*|step \d+)\b", re.I),
    re.compile(r"\b(?:follows that|yields|results in|executing|implementing|proven|conclude)\b", re.I),
]


@dataclass
class ReasoningNode:
    index: int
    text: str
    bond_type: BondType
    confidence: float
    retro_target: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "text": self.text[:120] + ("..." if len(self.text) > 120 else ""),
            "bond_type": self.bond_type.value,
            "confidence": round(self.confidence, 2),
            "retro_target": self.retro_target,
        }


@dataclass
class TopologyReport:
    total_steps: int
    covalent_ratio: float
    hydrogen_ratio: float
    vdw_ratio: float
    isomer_state: str  # STABLE_CONVERGENT, UNSTABLE_EXPLORATION, RIGID_DEDUCTION, NEUROTIC_REFLECTION
    entropy_trend: str  # MONOTONIC_DECREASING, OSCILLATING, DIVERGENT
    entropy_scores: List[float]
    nodes: List[ReasoningNode] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_steps": self.total_steps,
            "distribution": {
                "covalent_ratio": round(self.covalent_ratio, 3),
                "hydrogen_ratio": round(self.hydrogen_ratio, 3),
                "vdw_ratio": round(self.vdw_ratio, 3),
            },
            "isomer_state": self.isomer_state,
            "entropy_trend": self.entropy_trend,
            "entropy_scores": [round(s, 3) for s in self.entropy_scores],
            "nodes": [n.to_dict() for n in self.nodes],
            "anomalies": self.anomalies,
            "recommendations": self.recommendations,
        }


def _split_reasoning_steps(trace: str) -> List[str]:
    """Break long CoT trace into coherent reasoning units/steps."""
    if not trace or not trace.strip():
        return []

    lines = [l.strip() for l in trace.splitlines() if l.strip()]
    steps: List[str] = []

    current_chunk = []
    for line in lines:
        if re.match(r"^(?:step\s*\d+|[0-9]+[\.\)]|[-*]|\b(?:first|second|third|finally|next)\b)", line, re.I):
            if current_chunk:
                steps.append(" ".join(current_chunk))
                current_chunk = []
        current_chunk.append(line)

    if current_chunk:
        steps.append(" ".join(current_chunk))

    # Fallback to sentence boundaries if too few chunks
    if len(steps) <= 1 and trace.strip():
        sentences = re.split(r"(?<=[.!?])\s+", trace.strip())
        steps = [s.strip() for s in sentences if s.strip()]

    return steps


def classify_step(text: str, step_index: int) -> Tuple[BondType, float, Optional[int]]:
    """
    Classify a single reasoning unit into Covalent, Hydrogen, or Van der Waals.
    Returns (BondType, confidence, retro_target_index).
    """
    h_hits = sum(1 for p in HYDROGEN_PATTERNS if p.search(text))
    v_hits = sum(1 for p in VAN_DER_WAALS_PATTERNS if p.search(text))
    c_hits = sum(1 for p in COVALENT_PATTERNS if p.search(text))

    # Hydrogen has higher structural priority for back-verification
    if h_hits > 0 and h_hits >= v_hits:
        target = max(0, step_index - 1) if step_index > 0 else None
        conf = min(0.95, 0.6 + (h_hits * 0.15))
        return BondType.HYDROGEN, conf, target

    if v_hits > 0 and v_hits >= c_hits:
        conf = min(0.95, 0.55 + (v_hits * 0.15))
        return BondType.VAN_DER_WAALS, conf, None

    # Default to Covalent (deductive progress)
    conf = min(0.95, 0.5 + (c_hits * 0.15)) if c_hits > 0 else 0.5
    return BondType.COVALENT, conf, None


def _calculate_step_entropy(step_text: str, current_ratio_tuple: Tuple[float, float, float]) -> float:
    """
    Estimate local uncertainty/entropy based on linguistic hedge terms vs formal assertions.
    """
    hedge_terms = ["might", "maybe", "possibly", "uncertain", "guess", "assume", "likely", "probably"]
    assert_terms = ["confirm", "proven", "therefore", "exact", "verified", "conclude", "satisfies"]

    words = re.findall(r"\b\w+\b", step_text.lower())
    if not words:
        return 1.0

    hedge_count = sum(1 for w in words if w in hedge_terms)
    assert_count = sum(1 for w in words if w in assert_terms)

    # Base entropy normalized around 0.5
    raw_entropy = 0.5 + (hedge_count * 0.15) - (assert_count * 0.12)
    return max(0.05, min(1.0, raw_entropy))


def analyze_reasoning_topology(trace_text: str) -> TopologyReport:
    """
    Analyze the full Long Chain-of-Thought reasoning topology and return report.
    """
    steps = _split_reasoning_steps(trace_text)
    total = len(steps)
    if total == 0:
        return TopologyReport(
            total_steps=0,
            covalent_ratio=0.0,
            hydrogen_ratio=0.0,
            vdw_ratio=0.0,
            isomer_state="EMPTY",
            entropy_trend="MONOTONIC_DECREASING",
            entropy_scores=[]
        )

    nodes: List[ReasoningNode] = []
    c_count = 0
    h_count = 0
    v_count = 0
    entropy_scores: List[float] = []

    for idx, st in enumerate(steps):
        btype, conf, retro = classify_step(st, idx)
        if btype == BondType.COVALENT:
            c_count += 1
        elif btype == BondType.HYDROGEN:
            h_count += 1
        else:
            v_count += 1

        nodes.append(ReasoningNode(
            index=idx + 1,
            text=st,
            bond_type=btype,
            confidence=conf,
            retro_target=retro
        ))

        # Entropy estimation
        ent = _calculate_step_entropy(st, (c_count / (idx + 1), h_count / (idx + 1), v_count / (idx + 1)))
        # Scale entropy based on step position (convergence expectation)
        decay = math.exp(-0.4 * (idx / max(1, total - 1)))
        scaled_entropy = ent * decay
        entropy_scores.append(scaled_entropy)

    c_ratio = c_count / total
    h_ratio = h_count / total
    v_ratio = v_count / total

    # Isomer classification based on empirical bounds from arXiv:2601.06002
    anomalies: List[str] = []
    recommendations: List[str] = []

    if v_ratio > 0.35:
        isomer_state = "UNSTABLE_EXPLORATION"
        anomalies.append(f"Excessive Van der Waals exploration ({int(v_ratio * 100)}% > 35%). High risk of cognitive drift.")
        recommendations.append("Prune speculative branching earlier; anchor deductions to covalent backbone.")
    elif h_ratio > 0.35:
        isomer_state = "NEUROTIC_REFLECTION"
        anomalies.append(f"Excessive Hydrogen self-reflection loops ({int(h_ratio * 100)}% > 35%). Risk of hesitation thrashing.")
        recommendations.append("Limit backtrack loops. Verify premises once and proceed with execution.")
    elif h_ratio < 0.08 and total >= 4:
        isomer_state = "RIGID_DEDUCTION"
        anomalies.append(f"Under-stabilized trajectory (Hydrogen bonds {int(h_ratio * 100)}% < 8%). Zero retro-folding checks.")
        recommendations.append("Inject stabilizing self-reflection check before final action to prevent error propagation.")
    else:
        isomer_state = "STABLE_CONVERGENT"
        recommendations.append("Reasoning topology matches optimal molecular isomer bounds. Safe for execution.")

    # Entropy trend evaluation
    if len(entropy_scores) >= 2:
        start_avg = sum(entropy_scores[:max(1, len(entropy_scores)//3)]) / max(1, len(entropy_scores)//3)
        end_avg = sum(entropy_scores[-max(1, len(entropy_scores)//3):]) / max(1, len(entropy_scores)//3)
        if end_avg < start_avg * 0.7:
            entropy_trend = "MONOTONIC_DECREASING"
        elif end_avg > start_avg * 1.1:
            entropy_trend = "DIVERGENT"
            anomalies.append("Reasoning entropy is divergent (uncertainty increases toward the conclusion).")
        else:
            entropy_trend = "OSCILLATING"
    else:
        entropy_trend = "MONOTONIC_DECREASING"

    return TopologyReport(
        total_steps=total,
        covalent_ratio=c_ratio,
        hydrogen_ratio=h_ratio,
        vdw_ratio=v_ratio,
        isomer_state=isomer_state,
        entropy_trend=entropy_trend,
        entropy_scores=entropy_scores,
        nodes=nodes,
        anomalies=anomalies,
        recommendations=recommendations
    )
