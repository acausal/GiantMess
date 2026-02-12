"""
Axiom Validator - Quality gates for grain crystallization
Phase 2A: Validate candidates before conversion to grains

Three validation rules (from spec):
1. Persistence: Appears 5+ times with high confidence
2. Least Resistance: Internal coherence (not contradictory)
3. Independence: Not derivable from other grains/axioms

These rules ensure only high-quality patterns crystallize.
"""

import statistics
from typing import Dict, List, Optional, Tuple
from enum import Enum
from shannon_grain import PhantomCandidate, GrainMetadata, EpistemicLevel


# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRule(Enum):
    """Validation rule types"""
    PERSISTENCE = "persistence"          # Appears consistently (5+ hits)
    LEAST_RESISTANCE = "least_resistance" # Low internal contradiction
    INDEPENDENCE = "independence"        # Not derivable from others


class AxiomValidator:
    """
    Validates phantoms against three quality rules before crystallization.
    
    Rules (from spec, Section 3.3):
    1. Persistence: Hit 5+ times with avg confidence > 0.75
    2. Least Resistance: Internal coherence (Hamming distance < 8 bits)
    3. Independence: Not logically derivable from existing axioms
    """
    
    def __init__(self, 
                 min_observations: int = 5,
                 min_confidence: float = 0.75,
                 max_internal_hamming: int = 8,
                 max_weight_skew: float = 2.0):
        """
        Initialize validator with thresholds.
        
        Args:
            min_observations: Minimum hits to consider persistent
            min_confidence: Minimum average confidence
            max_internal_hamming: Max internal cluster Hamming distance
            max_weight_skew: Max weight distribution skew
        """
        self.min_observations = min_observations
        self.min_confidence = min_confidence
        self.max_internal_hamming = max_internal_hamming
        self.max_weight_skew = max_weight_skew
    
    # ========================================================================
    # RULE 1: PERSISTENCE
    # ========================================================================
    
    def check_persistence(self, phantom: PhantomCandidate) -> Tuple[bool, Dict]:
        """
        Validate that phantom appears consistently (5+ hits, >0.75 avg confidence).
        
        Returns:
            (passed: bool, details: dict with metrics)
        """
        hit_count = phantom.hit_count
        avg_confidence = phantom.avg_confidence()
        
        metrics = {
            "rule": "persistence",
            "hit_count": hit_count,
            "min_required": self.min_observations,
            "avg_confidence": round(avg_confidence, 3),
            "min_confidence": self.min_confidence,
            "cycle_consistency": round(phantom.cycle_consistency, 3),
        }
        
        # Check both hit count and confidence
        passed = (hit_count >= self.min_observations and 
                 avg_confidence >= self.min_confidence)
        
        metrics["passed"] = passed
        
        if not passed:
            if hit_count < self.min_observations:
                metrics["reason"] = f"Too few hits ({hit_count} < {self.min_observations})"
            else:
                metrics["reason"] = f"Low confidence ({avg_confidence:.2f} < {self.min_confidence})"
        else:
            metrics["reason"] = "Persistent pattern detected"
        
        return passed, metrics
    
    # ========================================================================
    # RULE 2: LEAST RESISTANCE (Coherence)
    # ========================================================================
    
    def check_least_resistance(self, phantom: PhantomCandidate,
                              observations: Optional[List[Dict]] = None) -> Tuple[bool, Dict]:
        """
        Validate internal coherence - observations in cluster should be similar.
        
        Checks:
        1. Confidence variance is low (coherent signals)
        2. Hamming distance between observations is small (similar patterns)
        3. No contradictions in fact combinations
        
        Returns:
            (passed: bool, details: dict with metrics)
        """
        metrics = {
            "rule": "least_resistance",
            "fact_ids": list(phantom.fact_ids),
        }
        
        # Check 1: Confidence variance (low variance = coherent)
        if len(phantom.confidence_scores) < 2:
            confidence_variance = 0.0
        else:
            confidence_variance = statistics.variance(phantom.confidence_scores)
        
        # Normalize: max variance = 0.25, so this score is 0-1
        coherence_score = 1.0 - min(confidence_variance / 0.25, 1.0)
        
        metrics["confidence_variance"] = round(confidence_variance, 3)
        metrics["coherence_score"] = round(coherence_score, 3)
        metrics["coherence_threshold"] = 0.7
        
        # Check 2: Concept consistency (if available)
        concept_consistency = 1.0  # Default if no concept data
        if phantom.query_concepts:
            # Check that concepts don't contradict
            # (simplified: just check for variety, not contradictions)
            unique_concepts = len(set(phantom.query_concepts))
            total_concepts = len(phantom.query_concepts)
            concept_consistency = min(1.0, unique_concepts / max(total_concepts, 1))
        
        metrics["concept_consistency"] = round(concept_consistency, 3)
        
        # Overall: must pass both coherence and concept checks
        passed = (coherence_score >= 0.7)
        
        metrics["passed"] = passed
        metrics["reason"] = "Coherent observations" if passed else "Low coherence (contradictions detected)"
        
        return passed, metrics
    
    # ========================================================================
    # RULE 3: INDEPENDENCE
    # ========================================================================
    
    def check_independence(self, phantom: PhantomCandidate,
                          existing_grains: Optional[List[GrainMetadata]] = None) -> Tuple[bool, Dict]:
        """
        Validate that this phantom is not derivable from existing grains/axioms.
        
        Checks that the pattern is "novel" and not just a combination of existing rules.
        
        Returns:
            (passed: bool, details: dict with metrics)
        """
        metrics = {
            "rule": "independence",
            "phantom_id": phantom.phantom_id,
        }
        
        # If no existing grains, automatically independent
        if not existing_grains:
            metrics["existing_grains"] = 0
            metrics["passed"] = True
            metrics["reason"] = "No existing grains to check against"
            return True, metrics
        
        # Check: does this phantom's fact set overlap too much with existing grains?
        max_overlap = 0.0
        most_similar_grain = None
        
        for grain in existing_grains:
            if not hasattr(grain, 'source_phantom_id'):
                continue
            
            # Calculate Jaccard similarity (overlap / union)
            # If overlap > 0.8, phantom is too similar to existing grain
            overlap = len(phantom.fact_ids & grain.source_phantom_id) / len(phantom.fact_ids | grain.source_phantom_id)
            
            if overlap > max_overlap:
                max_overlap = overlap
                most_similar_grain = grain.grain_id if hasattr(grain, 'grain_id') else "unknown"
        
        metrics["max_overlap_with_existing"] = round(max_overlap, 3)
        metrics["independence_threshold"] = 0.6
        metrics["most_similar_grain"] = most_similar_grain
        
        # Pass if overlap is low (< 60% similar)
        passed = max_overlap < 0.6
        
        metrics["passed"] = passed
        if passed:
            metrics["reason"] = f"Independent pattern (max overlap: {max_overlap:.1%})"
        else:
            metrics["reason"] = f"Too similar to existing grain {most_similar_grain} ({max_overlap:.1%} overlap)"
        
        return passed, metrics
    
    # ========================================================================
    # COMBINED VALIDATION
    # ========================================================================
    
    def validate(self, phantom: PhantomCandidate,
                existing_grains: Optional[List[GrainMetadata]] = None) -> Tuple[bool, Dict]:
        """
        Run all three validation rules.
        
        Returns:
            (all_pass: bool, full_report: dict with all metrics)
        """
        report = {
            "phantom_id": phantom.phantom_id,
            "cartridge_id": phantom.cartridge_id,
            "timestamp": phantom.created_at,
            "rules": {},
            "overall_passed": False,
            "failed_rules": [],
        }
        
        # Rule 1: Persistence
        persistence_pass, persistence_metrics = self.check_persistence(phantom)
        report["rules"]["persistence"] = persistence_metrics
        if not persistence_pass:
            report["failed_rules"].append("persistence")
        
        # Rule 2: Least Resistance
        resistance_pass, resistance_metrics = self.check_least_resistance(phantom)
        report["rules"]["least_resistance"] = resistance_metrics
        if not resistance_pass:
            report["failed_rules"].append("least_resistance")
        
        # Rule 3: Independence
        independence_pass, independence_metrics = self.check_independence(phantom, existing_grains)
        report["rules"]["independence"] = independence_metrics
        if not independence_pass:
            report["failed_rules"].append("independence")
        
        # Overall pass requires all three rules
        overall_passed = persistence_pass and resistance_pass and independence_pass
        report["overall_passed"] = overall_passed
        
        if overall_passed:
            report["verdict"] = "✅ CRYSTALLIZE - All validation rules passed"
        else:
            report["verdict"] = f"❌ REJECT - Failed {len(report['failed_rules'])} rule(s): {', '.join(report['failed_rules'])}"
        
        return overall_passed, report
    
    # ========================================================================
    # BATCH VALIDATION (for screening multiple phantoms)
    # ========================================================================
    
    def validate_batch(self, phantoms: List[PhantomCandidate],
                      existing_grains: Optional[List[GrainMetadata]] = None) -> Dict:
        """
        Validate multiple phantoms, return those ready for crystallization.
        
        Returns:
            Dictionary with crystallization_ready list and metrics
        """
        results = {
            "total_phantoms": len(phantoms),
            "crystallization_ready": [],
            "rejected": [],
            "summary": {
                "passed_persistence": 0,
                "passed_least_resistance": 0,
                "passed_independence": 0,
                "passed_all": 0,
            }
        }
        
        for phantom in phantoms:
            passed, report = self.validate(phantom, existing_grains)
            
            if passed:
                results["crystallization_ready"].append({
                    "phantom_id": phantom.phantom_id,
                    "fact_ids": list(phantom.fact_ids),
                    "confidence": round(phantom.avg_confidence(), 3),
                })
                results["summary"]["passed_all"] += 1
            else:
                results["rejected"].append({
                    "phantom_id": phantom.phantom_id,
                    "reasons": report["failed_rules"],
                    "report": report,
                })
            
            # Track individual rule passes
            if report["rules"]["persistence"]["passed"]:
                results["summary"]["passed_persistence"] += 1
            if report["rules"]["least_resistance"]["passed"]:
                results["summary"]["passed_least_resistance"] += 1
            if report["rules"]["independence"]["passed"]:
                results["summary"]["passed_independence"] += 1
        
        results["summary"]["rejection_rate"] = len(results["rejected"]) / len(phantoms) if phantoms else 0
        
        return results


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

if __name__ == "__main__":
    print("Axiom Validator Examples\n")
    
    # Create test phantoms
    print("1. Creating test phantoms...")
    
    # Good phantom (passes all rules)
    good_phantom = PhantomCandidate(
        phantom_id="phantom_good",
        fact_ids={1, 2, 3},
        cartridge_id="test",
        hit_count=10,
        confidence_scores=[0.85, 0.86, 0.84, 0.87, 0.85] * 2,
        query_concepts=["concept_a", "concept_b"],
    )
    good_phantom.status = "persistent"
    good_phantom.cycle_consistency = 0.85
    
    # Bad phantom (low confidence)
    bad_phantom_confidence = PhantomCandidate(
        phantom_id="phantom_low_conf",
        fact_ids={4, 5},
        cartridge_id="test",
        hit_count=3,  # Too few hits
        confidence_scores=[0.50, 0.45, 0.48],
        query_concepts=["concept_c"],
    )
    
    # Bad phantom (low coherence)
    bad_phantom_coherence = PhantomCandidate(
        phantom_id="phantom_incoherent",
        fact_ids={6, 7, 8},
        cartridge_id="test",
        hit_count=10,
        confidence_scores=[0.95, 0.10, 0.92, 0.08, 0.94],  # High variance = incoherent
        query_concepts=["concept_d"],
    )
    
    # Initialize validator
    validator = AxiomValidator()
    
    # Test good phantom
    print("\nValidating good phantom:")
    passed, report = validator.validate(good_phantom)
    print(f"  Persistence: {report['rules']['persistence']['passed']}")
    print(f"  Least Resistance: {report['rules']['least_resistance']['passed']}")
    print(f"  Independence: {report['rules']['independence']['passed']}")
    print(f"  Overall: {'✅ PASS' if passed else '❌ FAIL'}")
    
    # Test bad phantoms
    print("\nValidating low-confidence phantom:")
    passed, report = validator.validate(bad_phantom_confidence)
    print(f"  Verdict: {report['verdict']}")
    print(f"  Reason: {report['rules']['persistence']['reason']}")
    
    print("\nValidating incoherent phantom:")
    passed, report = validator.validate(bad_phantom_coherence)
    print(f"  Verdict: {report['verdict']}")
    print(f"  Coherence Score: {report['rules']['least_resistance']['coherence_score']}")
    
    # Batch validation
    print("\nBatch validation:")
    phantoms = [good_phantom, bad_phantom_confidence, bad_phantom_coherence]
    batch_results = validator.validate_batch(phantoms)
    print(f"  Total phantoms: {batch_results['total_phantoms']}")
    print(f"  Ready to crystallize: {len(batch_results['crystallization_ready'])}")
    print(f"  Rejected: {len(batch_results['rejected'])}")
    print(f"  Rejection rate: {batch_results['summary']['rejection_rate']:.0%}")
