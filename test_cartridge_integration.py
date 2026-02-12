#!/usr/bin/env python3
"""
Integration test: Cartridges → Queries → DeltaRegistry
Simulates Phase 2B query stream.
"""

from kitbash_query_engine import CartridgeQueryEngine
from kitbash_delta_registry import DeltaRegistry
import random


def test_integration():
    """
    1. Load cartridges
    2. Run simulated query stream
    3. Track hits in DeltaRegistry
    4. Show results
    """
    
    # Initialize
    engine = CartridgeQueryEngine("./cartridges")
    registry = DeltaRegistry("./registry")
    
    # Simulated queries (like what users would ask)
    test_queries = [
        "force acceleration motion",
        "energy heat temperature",
        "atoms molecules bonds",
        "evolution adaptation fitness",
        "DNA genes inheritance",
        "cells mitochondria energy",
        "logic reasoning proof",
        "probability statistics inference",
        "pressure flow dynamics",
        "metabolism ATP energy",
        "enzyme catalyst reaction",
        "structure atoms electrons",
        "motion forces Newton",
        "thermodynamic entropy disorder",
        "information genes protein",
    ]
    
    print("="*70)
    print("PHASE 2B CARTRIDGE INTEGRATION TEST")
    print("="*70)
    
    # Run 10 query cycles
    for cycle in range(10):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # Pick random queries for this cycle
        cycle_queries = random.sample(test_queries, min(5, len(test_queries)))
        
        for query in cycle_queries:
            result = engine.keyword_query(query)
            print(f"Query: '{query}' → {len(result.fact_ids)} hits")
            
            # Record each hit in registry
            for fact_id in result.fact_ids:
                confidence = result.confidences[fact_id]
                
                # Find which cartridge this fact is from
                cart_name = "unknown"
                for cn, cart in engine.cartridges.items():
                    if fact_id in cart.facts:
                        cart_name = cn
                        break
                
                registry.record_hit(fact_id, cart_name, confidence)
        
        registry.advance_cycle()
    
    # Report
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nTotal cycles: {registry.current_cycle}")
    print(f"Total unique facts hit: {len(registry.fact_stats)}")
    print(f"Total hits recorded: {sum(s.hit_count for s in registry.fact_stats.values())}")
    
    print("\nTop 15 hot facts:")
    for i, stats in enumerate(registry.get_hot_facts(15), 1):
        avg_conf = registry.get_average_confidence(stats.fact_id)
        print(f"  {i:2d}. Fact {stats.fact_id:3d}: {stats.hit_count:2d} hits, "
              f"avg conf={avg_conf:.2f}, cycles_active={stats.cycles_active}")
    
    # Save for later use
    registry.save()
    print("\n✓ Registry saved to ./registry/delta_registry.json")
    
    # Statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    print(f"Cartridges loaded: {len(engine.cartridges)}")
    print(f"Total facts available: {sum(len(c.facts) for c in engine.cartridges.values())}")
    print(f"Facts hit in test: {len(registry.fact_stats)}")
    print(f"Hit rate: {len(registry.fact_stats) / sum(len(c.facts) for c in engine.cartridges.values()) * 100:.1f}%")
    
    # Verify minimum criteria for Phase 2B
    print("\n" + "="*70)
    print("PHASE 2B READINESS CHECK")
    print("="*70)
    
    checks = [
        ("Cartridges loaded", len(engine.cartridges) >= 6),
        ("Total facts available", sum(len(c.facts) for c in engine.cartridges.values()) >= 500),
        ("Unique facts hit", len(registry.fact_stats) >= 20),
        ("Query engine working", len(registry.fact_stats) > 0),
        ("DeltaRegistry tracking", registry.current_cycle >= 10),
    ]
    
    all_pass = True
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_pass = False
    
    print("\n" + "="*70)
    if all_pass:
        print("✓ READY FOR PHASE 2B")
    else:
        print("✗ NOT READY - Fix issues above")
    print("="*70)


if __name__ == "__main__":
    test_integration()
