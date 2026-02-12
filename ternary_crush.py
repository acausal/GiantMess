"""
Ternary Crush Algorithm - Compress phantom patterns to ternary grains
Phase 2A: Convert validated phantoms to compressed 256-bit grains

Purpose: Take a pattern of persistent observations and compress them into
ternary (+1, -1, 0) weights that are ~90% smaller than embeddings.

Process:
1. Collect observations from phantom (fact + context)
2. Build composite representation (aggregate semantic features)
3. Slice into parallel bit-arrays (+1 and -1)
4. Compress to binary format (~250 bytes per grain)
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import statistics
from shannon_grain import PhantomCandidate, GrainMetadata, EpistemicLevel


# ============================================================================
# TERNARY REPRESENTATION
# ============================================================================

@dataclass
class TernaryWeight:
    """Single ternary weight and its properties"""
    position: int         # Bit position (0-255)
    value: int           # -1, 0, or +1
    confidence: float    # How confident in this weight
    sources: List[str]   # Which observations support this weight
    
    def to_int(self) -> int:
        """Convert to compact integer representation"""
        if self.value == 1:
            return 1
        elif self.value == -1:
            return 2
        else:
            return 0


class TernaryCrush:
    """
    Converts persistent phantom patterns into ternary-encoded grains.
    
    Algorithm:
    1. Aggregate observation confidences into weight values
    2. Determine which bits should be +1 (positive evidence)
    3. Determine which bits should be -1 (negative evidence)
    4. Pack into bit arrays for storage
    """
    
    def __init__(self, num_bits: int = 256):
        """
        Initialize crusher.
        
        Args:
            num_bits: Total bits in grain representation (usually 256)
        """
        self.num_bits = num_bits
        self.confidence_threshold = 0.7  # Threshold for setting weights
    
    # ========================================================================
    # WEIGHT INFERENCE
    # ========================================================================
    
    def infer_weights(self, phantom: PhantomCandidate,
                     observation_vectors: Optional[List[List[float]]] = None
                     ) -> List[TernaryWeight]:
        """
        Infer ternary weights from phantom's observation history.
        
        If observation_vectors provided, uses them. Otherwise creates synthetic
        vectors based on confidence scores.
        
        Returns:
            List of ternary weights
        """
        weights = []
        
        # If we have explicit observation vectors, use them
        if observation_vectors:
            weights = self._infer_from_vectors(observation_vectors, phantom.confidence_scores)
        else:
            # Synthetic: use confidence history to seed weights
            weights = self._infer_synthetic(phantom)
        
        return weights
    
    def _infer_synthetic(self, phantom: PhantomCandidate) -> List[TernaryWeight]:
        """
        Infer weights synthetically from confidence history.
        
        Since we don't have actual observations, use phantom statistics to
        create a reasonable weight distribution.
        """
        weights = []
        avg_conf = phantom.avg_confidence()
        
        # Positive weights: where confidence is high
        positive_count = int(self.num_bits * 0.30)  # ~30% positive
        negative_count = int(self.num_bits * 0.20)  # ~20% negative
        void_count = self.num_bits - positive_count - negative_count  # ~50% void
        
        # Distribute positive weights
        for i in range(positive_count):
            weights.append(TernaryWeight(
                position=i,
                value=1,
                confidence=avg_conf + 0.05,  # Slightly boosted
                sources=[f"fact_{fid}" for fid in phantom.fact_ids]
            ))
        
        # Distribute negative weights (opposite confidence pattern)
        for i in range(positive_count, positive_count + negative_count):
            weights.append(TernaryWeight(
                position=i,
                value=-1,
                confidence=1.0 - avg_conf,  # Inverted confidence
                sources=[f"contradiction_{fid}" for fid in phantom.fact_ids]
            ))
        
        # Rest are void (0)
        for i in range(positive_count + negative_count, self.num_bits):
            weights.append(TernaryWeight(
                position=i,
                value=0,
                confidence=0.0,
                sources=[]
            ))
        
        return weights
    
    def _infer_from_vectors(self, vectors: List[List[float]],
                           confidences: List[float]) -> List[TernaryWeight]:
        """
        Infer weights from actual observation vectors.
        
        Aggregates vectors weighted by confidence, then thresholds to ternary.
        """
        if not vectors:
            return []
        
        # Validate dimensions
        if any(len(v) != self.num_bits for v in vectors):
            raise ValueError(f"All vectors must have {self.num_bits} dimensions")
        
        # Aggregate vectors weighted by confidence
        aggregated = [0.0] * self.num_bits
        total_confidence = sum(confidences)
        
        for vector, confidence in zip(vectors, confidences):
            weight = confidence / total_confidence if total_confidence > 0 else 1.0 / len(vectors)
            for i, val in enumerate(vector):
                aggregated[i] += val * weight
        
        # Convert aggregated to ternary
        weights = []
        for position, value in enumerate(aggregated):
            if value > self.confidence_threshold:
                ternary_value = 1
                conf = min(1.0, value)
            elif value < -self.confidence_threshold:
                ternary_value = -1
                conf = min(1.0, abs(value))
            else:
                ternary_value = 0
                conf = 0.0
            
            weights.append(TernaryWeight(
                position=position,
                value=ternary_value,
                confidence=conf,
                sources=[]
            ))
        
        return weights
    
    # ========================================================================
    # BIT-SLICED STORAGE
    # ========================================================================
    
    def slice_to_bits(self, weights: List[TernaryWeight]) -> Tuple[bytes, bytes]:
        """
        Slice ternary weights into parallel bit arrays.
        
        Returns:
            (bits_positive, bits_negative) - two byte arrays
        
        Storage format:
        - bits_positive[i] = 1 if weight[i] == +1, else 0
        - bits_negative[i] = 1 if weight[i] == -1, else 0
        - Both 0 means weight is 0 (void)
        """
        # Initialize bit arrays
        bits_pos = bytearray((self.num_bits + 7) // 8)  # Ceil division for bytes
        bits_neg = bytearray((self.num_bits + 7) // 8)
        
        # Set bits
        for weight in weights:
            byte_idx = weight.position // 8
            bit_idx = weight.position % 8
            
            if weight.value == 1:
                bits_pos[byte_idx] |= (1 << bit_idx)
            elif weight.value == -1:
                bits_neg[byte_idx] |= (1 << bit_idx)
            # value == 0: neither bit is set
        
        return bytes(bits_pos), bytes(bits_neg)
    
    def bits_to_weights(self, bits_pos: bytes, bits_neg: bytes) -> List[TernaryWeight]:
        """
        Reverse operation: reconstruct weights from bit arrays.
        """
        weights = []
        
        for position in range(self.num_bits):
            byte_idx = position // 8
            bit_idx = position % 8
            
            has_pos = (bits_pos[byte_idx] >> bit_idx) & 1
            has_neg = (bits_neg[byte_idx] >> bit_idx) & 1
            
            if has_pos:
                value = 1
                conf = 1.0
            elif has_neg:
                value = -1
                conf = 1.0
            else:
                value = 0
                conf = 0.0
            
            weights.append(TernaryWeight(
                position=position,
                value=value,
                confidence=conf,
                sources=[]
            ))
        
        return weights
    
    # ========================================================================
    # GRAIN CREATION
    # ========================================================================
    
    def crystallize_grain(self, phantom: PhantomCandidate,
                         observation_vectors: Optional[List[List[float]]] = None,
                         axiom_ids: Optional[List[str]] = None
                         ) -> GrainMetadata:
        """
        Convert a phantom to a crystallized grain.
        
        Args:
            phantom: Locked phantom ready for crystallization
            observation_vectors: Optional explicit observation vectors
            axiom_ids: Which axioms this grain validates
            
        Returns:
            Complete GrainMetadata with ternary representation
        """
        # Step 1: Infer weights
        weights = self.infer_weights(phantom, observation_vectors)
        
        # Step 2: Analyze weight distribution
        positive_count = sum(1 for w in weights if w.value == 1)
        negative_count = sum(1 for w in weights if w.value == -1)
        void_count = self.num_bits - positive_count - negative_count
        
        # Step 3: Slice to bit arrays
        bits_pos, bits_neg = self.slice_to_bits(weights)
        
        # Step 4: Calculate quality metrics
        internal_hamming = self._calculate_internal_hamming(weights)
        weight_skew = self._calculate_weight_skew(positive_count, negative_count)
        
        # Step 5: Generate grain ID and evidence hash
        grain_id = self._generate_grain_id(phantom)
        evidence_hash = self._generate_evidence_hash(phantom, weights)
        
        # Step 6: Create grain
        grain = GrainMetadata(
            grain_id=grain_id,
            source_phantom_id=phantom.phantom_id,
            cartridge_id=phantom.cartridge_id,
            num_bits=self.num_bits,
            bits_positive=positive_count,
            bits_negative=negative_count,
            bits_void=void_count,
            axiom_ids=axiom_ids or [],
            evidence_hash=evidence_hash,
            internal_hamming=internal_hamming,
            weight_skew=weight_skew,
            avg_confidence=phantom.avg_confidence(),
            observation_count=phantom.hit_count,
            bit_array_plus=bits_pos,
            bit_array_minus=bits_neg,
            epistemic_level=phantom.epistemic_level,
        )
        
        return grain
    
    # ========================================================================
    # QUALITY METRICS
    # ========================================================================
    
    def _calculate_internal_hamming(self, weights: List[TernaryWeight]) -> float:
        """
        Calculate average internal Hamming distance within weight set.
        
        Lower = more coherent.
        """
        # Simplified: use variance of weight values
        values = [w.confidence for w in weights]
        if len(values) < 2:
            return 0.0
        
        try:
            variance = statistics.variance(values)
            # Normalize to 0-8 scale (max hamming)
            return min(variance * 10, 8.0)
        except:
            return 0.0
    
    def _calculate_weight_skew(self, positive_count: int, negative_count: int) -> float:
        """
        Calculate weight distribution skew.
        
        Skew = std dev / mean of {positive_count, negative_count}
        Lower = more balanced.
        """
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        values = [positive_count, negative_count]
        mean = statistics.mean(values)
        
        if mean == 0:
            return 0.0
        
        try:
            std = statistics.stdev(values) if len(values) > 1 else 0.0
            return std / mean if mean > 0 else 0.0
        except:
            return 0.0
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _generate_grain_id(self, phantom: PhantomCandidate) -> str:
        """Generate unique grain ID from phantom"""
        # Combine phantom ID + timestamp for uniqueness
        key = f"{phantom.phantom_id}:{phantom.created_at}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _generate_evidence_hash(self, phantom: PhantomCandidate,
                               weights: List[TernaryWeight]) -> str:
        """Generate hash of evidence supporting this grain"""
        evidence = {
            "phantom_id": phantom.phantom_id,
            "fact_ids": sorted(list(phantom.fact_ids)),
            "hit_count": phantom.hit_count,
            "avg_confidence": phantom.avg_confidence(),
            "query_concepts": phantom.query_concepts,
        }
        
        evidence_str = json.dumps(evidence, sort_keys=True)
        return hashlib.sha256(evidence_str.encode()).hexdigest()
    
    def get_compression_stats(self, grain: GrainMetadata) -> Dict:
        """
        Calculate compression efficiency of a grain.
        
        Compares ternary storage to float32 embeddings.
        """
        # Size of ternary grain
        ternary_size = len(grain.bit_array_plus) + len(grain.bit_array_minus)
        
        # Size of equivalent float32 embedding (256 dimensions)
        embedding_size = 256 * 4  # 256 floats × 4 bytes each
        
        return {
            "ternary_size_bytes": ternary_size,
            "embedding_size_bytes": embedding_size,
            "compression_ratio": round(ternary_size / embedding_size, 3),
            "savings_percent": round(100 * (1 - ternary_size / embedding_size), 1),
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Ternary Crush Algorithm Examples\n")
    
    # Create a test phantom
    phantom = PhantomCandidate(
        phantom_id="phantom_crush_test",
        fact_ids={1, 2, 3},
        cartridge_id="test",
        hit_count=15,
        confidence_scores=[0.85, 0.87, 0.84, 0.86] * 4,
        query_concepts=["concept_a", "concept_b"],
    )
    phantom.status = "locked"
    phantom.cycle_consistency = 0.85
    
    # Create crusher and crystallize
    crusher = TernaryCrush(num_bits=256)
    grain = crusher.crystallize_grain(phantom, axiom_ids=["axiom_001"])
    
    print(f"Grain created: {grain.grain_id}")
    print(f"  Positive weights: {grain.bits_positive}")
    print(f"  Negative weights: {grain.bits_negative}")
    print(f"  Void weights: {grain.bits_void}")
    print(f"  Internal Hamming: {grain.internal_hamming:.2f}")
    print(f"  Weight skew: {grain.weight_skew:.2f}")
    
    # Show compression stats
    stats = crusher.get_compression_stats(grain)
    print(f"\nCompression stats:")
    print(f"  Ternary size: {stats['ternary_size_bytes']} bytes")
    print(f"  Embedding size: {stats['embedding_size_bytes']} bytes")
    print(f"  Compression ratio: {stats['compression_ratio']:.2f}")
    print(f"  Savings: {stats['savings_percent']}%")
    
    # Test round-trip (crush → slice → unslice)
    print(f"\nRound-trip test:")
    weights = crusher.infer_weights(phantom)
    bits_pos, bits_neg = crusher.slice_to_bits(weights)
    weights_recovered = crusher.bits_to_weights(bits_pos, bits_neg)
    
    # Count matches
    matches = sum(1 for w1, w2 in zip(weights, weights_recovered) if w1.value == w2.value)
    print(f"  Original weights: {len(weights)}")
    print(f"  Recovered weights: {len(weights_recovered)}")
    print(f"  Matches: {matches}/{len(weights)} ({100*matches/len(weights):.1f}%)")
