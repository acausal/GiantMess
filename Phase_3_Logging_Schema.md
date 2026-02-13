# Phase 3 Logging Schema
## Complete Event Logging for Sleep Cycle, Metabolism, and Promotion

**Version:** 1.0  
**Date:** February 12, 2026  
**Purpose:** Provide full audit trail and morning reports for Phase 3 (Sleeping Giant + Metabolism)

---

## Overview

**Logging Architecture:**
- **Format:** JSONL (one JSON object per line, append-only)
- **Location:** `logs/` directory with phase-specific subdirectories
- **Retention:** Keep indefinitely (immutable audit trail)
- **Rotation:** Daily files by UTC date (e.g., `2026-02-13.jsonl`)
- **Access:** Read-only after close-of-day

**Flow:**
```
Day: flux_buffer.append(signals)
Night: sleep_cycle processes → writes to logs/
Morning: morning_report.md reads from logs/ → generates report
Next day: logs are archived, new logs begin
```

---

## Log Files Structure

```
logs/
├─ metadata/
│  └─ log_manifest.json          # Index of all logs, rotation schedule
│
├─ signals/
│  ├─ 2026-02-13_signals.jsonl   # Raw day's signals (queries, corrections, feedback)
│  └─ flux_buffer_pending.jsonl  # Waiting to be processed
│
├─ phantoms/
│  ├─ 2026-02-13_phantom_tracking.jsonl   # Phantom detection events
│  └─ phantom_registry.json                # Current phantom state
│
├─ validation/
│  ├─ 2026-02-13_validation.jsonl         # Axiom validation events
│  └─ validation_failures.jsonl           # Rejected candidates with reasons
│
├─ crystallization/
│  ├─ 2026-02-13_crystallization.jsonl    # Grain creation events
│  └─ grain_ledger.jsonl                  # Current grain inventory
│
├─ sleeping_giant/
│  ├─ 2026-02-13_reasoning.jsonl          # Deep reasoning events
│  └─ reasoning_decisions.jsonl           # Approved/rejected with rationale
│
├─ promotion/
│  ├─ 2026-02-13_promotions.jsonl         # Facts promoted to fixed
│  └─ promotion_history.jsonl             # All-time promotion ledger
│
├─ performance/
│  ├─ 2026-02-13_metrics.jsonl            # Query latency, error rates, confidence
│  └─ performance_baseline.json           # Moving averages for delta reporting
│
└─ reports/
   ├─ morning_report_2026-02-13.md        # Generated human-readable report
   └─ weekly_summary_2026_week_06.md      # Weekly aggregation
```

---

## Log Schemas by Phase

### PHASE 0: Signals

**File:** `logs/signals/2026-02-13_signals.jsonl`

**Entry schema:**
```json
{
  "event_id": "sig_20260213_001847",
  "timestamp": "2026-02-13T14:23:45.123456Z",
  "signal_type": "query|correction|failure|deferral|feedback",
  
  "query_context": {
    "query_text": "What is F=ma?",
    "query_hash": "sha256:a1b2c3...",
    "query_id": "q_20260213_001847"
  },
  
  "response_context": {
    "response_text": "Force equals mass times acceleration...",
    "response_hash": "sha256:d4e5f6...",
    "confidence": 0.92,
    "cartridge_source": "physics",
    "source_fact_ids": [1247],
    "latency_ms": 45
  },
  
  "outcome": {
    "type": "correction|failure|success|deferral",
    "user_feedback": "!correct Actually, let me explain better",
    "corrected_text": null,
    "severity": "critical|high|medium|low",
    "epistemic_impact": "L0|L1|L2|L3"
  },
  
  "metadata": {
    "user_id": "user_default",
    "session_id": "sess_20260213_001",
    "model_version": "hermes-3-8b",
    "system_state": "conscious"
  }
}
```

**Examples:**

**Success query:**
```json
{
  "event_id": "sig_20260213_001847",
  "timestamp": "2026-02-13T14:23:45.123456Z",
  "signal_type": "query",
  "query_context": {
    "query_text": "What is F=ma?",
    "query_hash": "sha256:abc123",
    "query_id": "q_20260213_001847"
  },
  "response_context": {
    "response_text": "Force equals mass times acceleration, where F is force, m is mass, and a is acceleration",
    "response_hash": "sha256:def456",
    "confidence": 0.96,
    "cartridge_source": "physics",
    "source_fact_ids": [1247],
    "latency_ms": 18
  },
  "outcome": {
    "type": "success",
    "user_feedback": null,
    "corrected_text": null,
    "severity": "none",
    "epistemic_impact": "L2"
  },
  "metadata": {
    "user_id": "user_default",
    "session_id": "sess_20260213_001",
    "model_version": "hermes-3-8b",
    "system_state": "conscious"
  }
}
```

**User correction:**
```json
{
  "event_id": "sig_20260213_002156",
  "timestamp": "2026-02-13T14:24:10.456789Z",
  "signal_type": "correction",
  "query_context": {
    "query_text": "What time is it?",
    "query_hash": "sha256:xyz789",
    "query_id": "q_20260213_002156"
  },
  "response_context": {
    "response_text": "It's 14:24 EST",
    "response_hash": "sha256:aaa111",
    "confidence": 0.85,
    "cartridge_source": "time_utils",
    "source_fact_ids": [342],
    "latency_ms": 12
  },
  "outcome": {
    "type": "correction",
    "user_feedback": "!correct Actually that's UTC, not EST",
    "corrected_text": "It's 14:24 UTC",
    "severity": "medium",
    "epistemic_impact": "L1"
  },
  "metadata": {
    "user_id": "user_default",
    "session_id": "sess_20260213_001",
    "model_version": "hermes-3-8b",
    "system_state": "conscious"
  }
}
```

---

### PHASE 1: Phantom Tracking

**File:** `logs/phantoms/2026-02-13_phantom_tracking.jsonl`

**Entry schema:**
```json
{
  "event_id": "pht_20260213_031523",
  "timestamp": "2026-02-13T03:15:23.654321Z",
  "event_type": "phantom_hit|phantom_locked|phantom_promoted",
  
  "phantom": {
    "phantom_id": "pg_force_eq_mass_accel",
    "pattern_text": "force equals mass times acceleration",
    "pattern_hash": "sha256:pattern_abc",
    "domain": "physics",
    "subdomain": "mechanics"
  },
  
  "hit_context": {
    "query_id": "q_20260212_234567",
    "fact_id": 1247,
    "fact_content": "F = ma",
    "confidence": 0.96,
    "match_strength": 0.92
  },
  
  "phantom_state": {
    "hit_count": 847,
    "unique_query_variants": 34,
    "cycle_count": 67,
    "avg_confidence": 0.96,
    "resonance_score": 0.94,
    "locked": true,
    "days_observed": 12
  },
  
  "tracking_info": {
    "first_observed": "2026-02-01T08:30:00Z",
    "last_hit": "2026-02-13T03:15:23Z",
    "observation_sources": ["user_query", "system_response", "correction"],
    "source_cartridges": ["physics", "general_science"]
  },
  
  "decision": {
    "status": "tracking|locked|ready_for_validation",
    "confidence": 0.96,
    "promotion_candidate": true,
    "reason": "Locked after 50+ cycles with high consistency"
  }
}
```

**Example - Phantom locked:**
```json
{
  "event_id": "pht_20260213_031523",
  "timestamp": "2026-02-13T03:15:23.654321Z",
  "event_type": "phantom_locked",
  "phantom": {
    "phantom_id": "pg_force_eq_mass_accel",
    "pattern_text": "force equals mass times acceleration",
    "pattern_hash": "sha256:pattern_abc",
    "domain": "physics",
    "subdomain": "mechanics"
  },
  "hit_context": {
    "query_id": "q_20260212_234567",
    "fact_id": 1247,
    "fact_content": "F = ma",
    "confidence": 0.96,
    "match_strength": 0.92
  },
  "phantom_state": {
    "hit_count": 847,
    "unique_query_variants": 34,
    "cycle_count": 67,
    "avg_confidence": 0.96,
    "resonance_score": 0.94,
    "locked": true,
    "days_observed": 12
  },
  "tracking_info": {
    "first_observed": "2026-02-01T08:30:00Z",
    "last_hit": "2026-02-13T03:15:23Z",
    "observation_sources": ["user_query", "system_response", "correction"],
    "source_cartridges": ["physics", "general_science"]
  },
  "decision": {
    "status": "locked",
    "confidence": 0.96,
    "promotion_candidate": true,
    "reason": "Locked after 50+ cycles with high consistency"
  }
}
```

---

### PHASE 2: Validation

**File:** `logs/validation/2026-02-13_validation.jsonl`

**Entry schema:**
```json
{
  "event_id": "val_20260213_032847",
  "timestamp": "2026-02-13T03:28:47.987654Z",
  "validation_stage": "axiom_validation",
  
  "phantom_input": {
    "phantom_id": "pg_force_eq_mass_accel",
    "pattern_text": "force equals mass times acceleration",
    "hit_count": 847,
    "cycle_count": 67,
    "avg_confidence": 0.96
  },
  
  "validation_rules": {
    "rule_1_persistence": {
      "name": "Persistence Check",
      "description": "5+ hits with high average confidence",
      "threshold": "hit_count >= 5 AND avg_confidence >= 0.75",
      "actual_value": "hit_count=847, avg_confidence=0.96",
      "passed": true
    },
    "rule_2_least_resistance": {
      "name": "Least Resistance (Low Contradiction)",
      "description": "Pattern shows low internal contradiction",
      "threshold": "internal_hamming <= 8",
      "actual_value": "internal_hamming=6",
      "passed": true
    },
    "rule_3_independence": {
      "name": "Independence Check",
      "description": "Not derivable from existing grains",
      "threshold": "not_derivable(pattern, existing_grains)",
      "actual_value": "Checked against 42 existing grains, no derivation found",
      "passed": true
    }
  },
  
  "validation_result": {
    "passed": true,
    "all_rules_met": true,
    "confidence": 0.96,
    "status": "approved_for_crystallization",
    "rejection_reason": null
  },
  
  "validator": {
    "algorithm": "axiom_validator_v1",
    "execution_time_ms": 23,
    "grain_comparisons": 42
  }
}
```

**Example - Rejected phantom:**
```json
{
  "event_id": "val_20260213_032900",
  "timestamp": "2026-02-13T03:29:00.111111Z",
  "validation_stage": "axiom_validation",
  "phantom_input": {
    "phantom_id": "pg_bullet_points",
    "pattern_text": "users always want bullet points",
    "hit_count": 4,
    "cycle_count": 12,
    "avg_confidence": 0.63
  },
  "validation_rules": {
    "rule_1_persistence": {
      "name": "Persistence Check",
      "description": "5+ hits with high average confidence",
      "threshold": "hit_count >= 5 AND avg_confidence >= 0.75",
      "actual_value": "hit_count=4, avg_confidence=0.63",
      "passed": false
    },
    "rule_2_least_resistance": {
      "name": "Least Resistance (Low Contradiction)",
      "description": "Pattern shows low internal contradiction",
      "threshold": "internal_hamming <= 8",
      "actual_value": "internal_hamming=9",
      "passed": false
    },
    "rule_3_independence": {
      "name": "Independence Check",
      "description": "Not derivable from existing grains",
      "threshold": "not_derivable(pattern, existing_grains)",
      "actual_value": "Derivable from rule: pg_user_preference_formatting",
      "passed": false
    }
  },
  "validation_result": {
    "passed": false,
    "all_rules_met": false,
    "confidence": 0.63,
    "status": "rejected",
    "rejection_reason": "Insufficient evidence (4 hits < 5 required), too low confidence (0.63 < 0.75 required), derivable from existing grain"
  },
  "validator": {
    "algorithm": "axiom_validator_v1",
    "execution_time_ms": 18,
    "grain_comparisons": 42
  }
}
```

---

### PHASE 3: Crystallization

**File:** `logs/crystallization/2026-02-13_crystallization.jsonl`

**Entry schema:**
```json
{
  "event_id": "crz_20260213_034501",
  "timestamp": "2026-02-13T03:45:01.222222Z",
  "event_type": "crystallization",
  
  "phantom_source": {
    "phantom_id": "pg_force_eq_mass_accel",
    "pattern_text": "force equals mass times acceleration",
    "hit_count": 847,
    "observations": [
      {"text": "What is F=ma?", "confidence": 0.96},
      {"text": "force formula", "confidence": 0.93},
      {"text": "Newton's second law", "confidence": 0.97}
    ]
  },
  
  "grain_created": {
    "grain_id": "sg_0x7F3A",
    "content": "force equals mass times acceleration",
    "content_hash": "sha256:grain_hash",
    "ternary_vector": [1, 0, -1, 1, 0, 1, ...],  # first 32 bits (full has 256)
    "vector_length": 256,
    "nonzero_count": 128,
    "sparsity": 0.5
  },
  
  "compression_metrics": {
    "original_size_bits": 8192,  # float32 embeddings
    "compressed_size_bits": 256,  # ternary
    "compression_ratio": 0.9375,
    "estimated_savings_mb": 1.2
  },
  
  "quality_metrics": {
    "internal_hamming_distance": 6,
    "internal_hamming_threshold": 8,
    "weight_skew": 1.8,
    "weight_skew_threshold": 2.0,
    "avg_confidence": 0.96,
    "confidence_threshold": 0.75,
    "observation_count": 847,
    "observation_threshold": 5,
    "all_metrics_pass": true
  },
  
  "crystallization": {
    "algorithm": "ternary_crush_v1",
    "execution_time_ms": 234,
    "weight_inference_method": "majority_voting",
    "status": "crystallized",
    "ready_for_activation": true
  }
}
```

---

### PHASE 4: Sleeping Giant Reasoning

**File:** `logs/sleeping_giant/2026-02-13_reasoning.jsonl`

**Entry schema:**
```json
{
  "event_id": "sg_20260213_040523",
  "timestamp": "2026-02-13T04:05:23.333333Z",
  "event_type": "axiom_validation|contradiction_check|expert_reasoning",
  
  "grain_under_review": {
    "grain_id": "sg_0x7F3A",
    "content": "force equals mass times acceleration",
    "source_phantom_id": "pg_force_eq_mass_accel",
    "confidence": 0.96
  },
  
  "reasoning_request": {
    "question": "Is this grain consistent with L0 physics axioms?",
    "validation_type": "L0_axiom_check",
    "cross_reference_cartridges": ["physics", "general_science"],
    "related_grains": ["sg_0x7E2B", "sg_0x8F1C"]
  },
  
  "reasoning_process": {
    "model": "sleeping_giant_80b_moe",
    "reasoning_tokens": 4200,
    "wall_clock_seconds": 8.7,
    "steps": [
      {
        "step": 1,
        "content": "Checking if 'force = mass × acceleration' aligns with Newtonian mechanics L0 facts",
        "confidence": 0.98
      },
      {
        "step": 2,
        "content": "Cross-referencing with existing 'F=ma' facts in physics cartridge, found 3 existing statements, all identical in meaning",
        "confidence": 0.99
      },
      {
        "step": 3,
        "content": "Validating against contradictory facts: zero contradictions found",
        "confidence": 0.99
      },
      {
        "step": 4,
        "content": "Assessing uniqueness: This is a fundamental axiom, not derivable from simpler principles (already L0)",
        "confidence": 0.95
      }
    ]
  },
  
  "decision": {
    "approved": true,
    "confidence": 0.96,
    "proposed_epistemic_level": "L2_AXIOMATIC",
    "rationale": "Fundamental physics law, consistent with L0 seeds, no contradictions, high confidence from many observations",
    "caveats": []
  },
  
  "reasoning_artifact": {
    "moe_expert_activated": "physics_expert_3",
    "expert_specialization": "Classical mechanics, Newtonian dynamics",
    "token_breakdown": {
      "input": 320,
      "reasoning": 4200,
      "output": 180
    }
  }
}
```

**Example - Sleeping Giant rejects grain:**
```json
{
  "event_id": "sg_20260213_040645",
  "timestamp": "2026-02-13T04:06:45.444444Z",
  "event_type": "contradiction_check",
  "grain_under_review": {
    "grain_id": "sg_0x8E4B",
    "content": "Python is the best language for all purposes",
    "source_phantom_id": "pg_python_universal",
    "confidence": 0.78
  },
  "reasoning_request": {
    "question": "Is this grain consistent with existing axioms about language choice?",
    "validation_type": "contradiction_and_universality_check",
    "cross_reference_cartridges": ["user_model", "programming_philosophy"],
    "related_grains": ["sg_0x7C2A", "sg_0x9D5F"]
  },
  "reasoning_process": {
    "model": "sleeping_giant_80b_moe",
    "reasoning_tokens": 2800,
    "wall_clock_seconds": 5.2,
    "steps": [
      {
        "step": 1,
        "content": "Checking universality claim: 'best for ALL purposes'",
        "confidence": 0.92
      },
      {
        "step": 2,
        "content": "Cross-referencing with user axioms: found sg_0x7C2A 'Low-level systems work better in Rust or C'",
        "confidence": 0.99
      },
      {
        "step": 3,
        "content": "Direct contradiction detected: Python not suitable for real-time OS kernels",
        "confidence": 0.97
      }
    ]
  },
  "decision": {
    "approved": false,
    "confidence": 0.97,
    "proposed_epistemic_level": null,
    "rationale": "Contradicts existing L1/L2 axioms about language suitability for specific domains. Statement is L3 (personal preference) masquerading as L2 (universal rule). Should demote pattern.",
    "caveats": ["Could be reframed as L1 narrative: 'User prefers Python for scripting'"]
  },
  "reasoning_artifact": {
    "moe_expert_activated": "programming_philosophy_expert_1",
    "expert_specialization": "Language design, ecosystem comparison",
    "token_breakdown": {
      "input": 280,
      "reasoning": 2800,
      "output": 220
    }
  }
}
```

---

### PHASE 5: Promotion to Fixed

**File:** `logs/promotion/2026-02-13_promotions.jsonl`

**Entry schema:**
```json
{
  "event_id": "prm_20260213_060047",
  "timestamp": "2026-02-13T06:00:47.555555Z",
  "event_type": "promotion_to_fixed",
  
  "source": {
    "grain_id": "sg_0x7F3A",
    "phantom_id": "pg_force_eq_mass_accel",
    "source_cartridge_working": "physics.working.kbc"
  },
  
  "fact_created": {
    "fact_id": 1248,
    "content": "force equals mass times acceleration",
    "content_hash": "sha256:fact_hash"
  },
  
  "target": {
    "cartridge_name": "physics",
    "cartridge_variant": "fixed",
    "cartridge_path": "physics.kbc",
    "epistemic_level": "L2_AXIOMATIC",
    "fact_status": "validated"
  },
  
  "promotion_chain": {
    "day_0": "2026-02-01",
    "first_observation": "2026-02-01T08:30:00Z",
    "observations_count": 847,
    "observations_days": 12,
    "phantom_locked": "2026-02-13T03:15:23Z",
    "validation_passed": "2026-02-13T03:28:47Z",
    "crystallization_complete": "2026-02-13T03:45:01Z",
    "sleeping_giant_approved": "2026-02-13T04:05:23Z",
    "promotion_complete": "2026-02-13T06:00:47Z",
    "total_time_hours": 285
  },
  
  "metadata": {
    "confidence": 0.96,
    "quality_score": 0.97,
    "user_corrections_count": 12,
    "system_failures_count": 0,
    "validation_gates_passed": 7,
    "sleeping_giant_reasoning_tokens": 4200
  },
  
  "archival": {
    "working_cartridge_cleaned": true,
    "working_cartridge_backup": "backups/physics.working.kbc_2026-02-13_060000",
    "fact_removed_from_provisional": true
  }
}
```

---

### PHASE 6: Performance Metrics

**File:** `logs/performance/2026-02-13_metrics.jsonl`

**Entry schema:**
```json
{
  "event_id": "prf_20260213_235959",
  "timestamp": "2026-02-13T23:59:59.999999Z",
  "event_type": "daily_metrics_snapshot",
  
  "latency_metrics": {
    "avg_query_latency_ms": 38.2,
    "p50_latency_ms": 35,
    "p95_latency_ms": 52,
    "p99_latency_ms": 78,
    "min_latency_ms": 8,
    "max_latency_ms": 124,
    "query_count": 847
  },
  
  "accuracy_metrics": {
    "hallucination_rate": 0.018,
    "user_correction_rate": 0.079,
    "deferral_rate": 0.032,
    "unambiguous_success_rate": 0.871,
    "partial_success_rate": 0.098
  },
  
  "confidence_metrics": {
    "avg_response_confidence": 0.89,
    "median_response_confidence": 0.91,
    "low_confidence_queries": 34,  # < 0.60
    "high_confidence_queries": 812  # > 0.85
  },
  
  "cartridge_metrics": {
    "cartridges_queried": 9,
    "facts_accessed": 423,
    "grains_used": 12,
    "working_vs_fixed_ratio": "18:82",  # 18% from working (provisional), 82% from fixed (validated)
    "new_facts_added_to_working": 23
  },
  
  "deltas_from_baseline": {
    "latency_delta_ms": -6.8,
    "latency_delta_percent": "-15.1%",
    "hallucination_rate_delta": "-21%",
    "user_correction_rate_delta": "-3.6%",
    "avg_confidence_delta": "+2.3%",
    "baseline_date": "2026-02-12",
    "days_since_baseline": 1
  }
}
```

---

## Morning Report Generation

**File:** `reports/morning_report_2026-02-13.md`

**Generated from:** All logs from previous day

**Template:**
```markdown
# Morning Report
## February 13, 2026 - 06:00 AM UTC

**System Status:** ✅ HEALTHY

---

## Overnight Metabolism Summary

| Metric | Value |
|--------|-------|
| Signals Processed | 2,847 |
| Phantoms Detected | 23 |
| Phantoms Locked | 5 |
| Axioms Crystallized | 5 |
| Grains Created | 5 |
| Sleeping Giant Reviews | 5 |
| **Facts Promoted to Fixed** | **3** |
| Rejected Candidates | 2 |
| Sleep Cycle Duration | 3h 47m |

---

## Promoted Facts (New Ground Truth)

### 1. Force equals mass times acceleration
- **Type:** Axiom (L2_AXIOMATIC)
- **Confidence:** 0.96
- **Origin:** 847 query hits over 12 days
- **Path:** Phantom → Grain → Sleeping Giant ✅
- **Added to:** physics.kbc
- **Timestamp:** 2026-02-13 06:00:47 UTC

### 2. User prefers Python for scripting
- **Type:** Narrative (L1_NARRATIVE)
- **Confidence:** 0.88
- **Origin:** 34 user corrections
- **Path:** Phantom → Grain → Sleeping Giant ✅
- **Added to:** user_model.kbc
- **Timestamp:** 2026-02-13 06:03:15 UTC

### 3. Timezone questions → route to chronos_specialist
- **Type:** Routing Rule (L2_AXIOMATIC)
- **Confidence:** 0.91
- **Origin:** 12 timezone errors now resolved
- **Path:** Phantom → Grain → Sleeping Giant ✅
- **Added to:** routing_rules.kbc
- **Timestamp:** 2026-02-13 06:05:22 UTC

---

## Rejected Candidates

### 1. "Users always want bullet points"
- **Reason:** Insufficient evidence (4 hits < 5 required)
- **Confidence:** 0.63 (below 0.75 threshold)
- **Decision:** Keep in working, monitoring

### 2. "Markdown syntax rule X"
- **Reason:** Pattern too incoherent (Hamming distance 12 > 8 threshold)
- **Sleeping Giant Note:** "Likely spurious pattern from formatting noise"
- **Decision:** Archive, do not promote

---

## Performance Improvement

| Metric | Yesterday | Today | Change |
|--------|-----------|-------|--------|
| Avg Query Latency | 45.0 ms | 38.2 ms | **-15.1%** ✅ |
| Hallucination Rate | 2.3% | 1.8% | **-21%** ✅ |
| User Correction Rate | 8.2% | 7.9% | **-3.6%** ✅ |
| Avg Confidence | 0.87 | 0.89 | **+2.3%** ✅ |

**Analysis:** Performance improved across all metrics. New grains providing faster lookup paths.

---

## Grain Inventory Status

- **Total grains in L3 cache:** 47
- **New grains today:** 5
- **Cache utilization:** 2.1 MB / 4.0 MB (52%)
- **Grains aged out:** 0
- **Grains demoted:** 0

---

## System Health

**Sleeping Giant Status:** ✅ Normal operation
- Reasoning tokens consumed: 18,400 (budget: 50,000/day)
- Expert activations: 5 (expert_1: physics, expert_2: user_modeling, ...)
- Contradictions detected: 2 (resolved via demotion)
- Decision latency: avg 6.2 seconds per grain

**Cartridge Status:** ✅ All healthy
- physics.kbc: 1,248 facts (+1 today)
- user_model.kbc: 423 facts (+1 today)
- routing_rules.kbc: 87 facts (+1 today)
- Working cartridges: 9 (average 23 provisional facts waiting)

---

## Next 24 Hours

- Continue monitoring rejected candidates (bullet_points pattern)
- Watch timezone rule performance (new routing in effect)
- Baseline new grains for week-over-week comparison

---

**Report Generated:** 2026-02-13 06:00:47 UTC  
**Next Report:** 2026-02-14 06:00:00 UTC  
**System Online:** Ready for conscious layer
```

---

## Log Retention & Archival

### Daily Rotation
```python
def rotate_logs():
    """Called at 00:00 UTC each day"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Archive yesterday's logs
    for log_type in ["signals", "phantoms", "validation", "crystallization", "sleeping_giant", "promotion", "performance"]:
        old_log = f"logs/{log_type}/{yesterday}_*.jsonl"
        new_log = f"logs/archive/{yesterday}/{log_type}.jsonl"
        compress_and_archive(old_log, new_log)
    
    # Generate morning report
    generate_morning_report(yesterday)
    
    # Reset working logs
    open_new_log_files(today)
```

### Retention Policy
- **Hot logs** (current day): Keep in `logs/`
- **Recent archives** (7 days): Keep in `logs/archive/YYYY-MM-DD/`
- **Old archives** (7+ days): Compress to `logs/archive/YYYY-week-NN/`
- **Permanent record**: Compress monthly to `logs/archive/YYYY-MM/` (gzip format)

### Integrity
- All logs are append-only (never edited)
- SHA256 hash of each day's logs stored in manifest
- Tamper detection: Compare file hash against manifest
- Reconstruction: Any day can be reconstructed from log files + morning report

---

## Log Reading API

**Query helpers (Python):**
```python
def read_promotions(start_date, end_date):
    """Get all promotions in date range"""
    return read_jsonl(f"logs/promotion/{start_date}_promotions.jsonl", 
                     filter=lambda x: x["timestamp"] < end_date)

def read_signals_by_type(date, signal_type):
    """Get specific signal type (query, correction, failure)"""
    return read_jsonl(f"logs/signals/{date}_signals.jsonl",
                     filter=lambda x: x["signal_type"] == signal_type)

def get_morning_report(date):
    """Read generated morning report"""
    return read_markdown(f"reports/morning_report_{date}.md")

def compute_weekly_summary(week_start):
    """Aggregate 7 days of logs into summary"""
    summaries = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        summaries.append(read_jsonl(f"logs/performance/{date}_metrics.jsonl"))
    return aggregate_summaries(summaries)
```

---

## Summary

**Phase 3 logging provides:**

1. **Complete audit trail** - Every signal → phantom → grain → promotion
2. **Reproducibility** - Can replay any night's metabolism
3. **Debugging** - Understand why grains were promoted or rejected
4. **Transparency** - User gets morning reports showing what system learned
5. **Analytics** - Measure performance deltas, identify patterns
6. **Accountability** - Every decision has a reasoning trail

**Total logs per day:** ~150-200 KB (negligible storage cost)
**Morning report generation:** <5 seconds from logs
**Historical queries:** Can analyze entire metabolic history for tuning/learning
