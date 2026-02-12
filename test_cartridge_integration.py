#!/usr/bin/env python3
"""
Integration test: Cartridges → Queries → DeltaRegistry
Simulates Phase 2B query stream.
"""

from kitbash_query_engine import CartridgeQueryEngine
from kitbash_registry import DeltaRegistry
import random


def test_integration():
    """
    1. Load cartridges
    2. Run simulated query stream
    3. Track hits in DeltaRegistry
    4. Show results
    """
    
    # Initialize
    print("\n" + "="*70)
    print("PHASE 2B CARTRIDGE INTEGRATION TEST")
    print("="*70)
    
    # Load cartridges
    print("\nLoading cartridges...")
    engine = CartridgeQueryEngine("./cartridges")
    
    if not engine.cartridges:
        print("X No cartridges loaded!")
        return False
    
    print(f"+ Loaded {len(engine.cartridges)} cartridges")
    
    # Initialize registry
    print("\nInitializing DeltaRegistry...")
    registry = DeltaRegistry("phase2b_test")
    
    # Test queries (multiple domains)
    test_queries = [
        "force acceleration motion",
        "DNA genes protein",
        "energy heat temperature",
        "logic reasoning truth",
        "enzyme catalyst reaction",
        "thermodynamic entropy disorder",
        "atoms molecules bonds",
        "cells mitochondria energy",
        "probability statistics inference",
        "pressure flow dynamics",
        "motion forces Newton",
        "structure atoms electrons",
        "information genes protein",
        "evolution adaptation fitness",
        "metabolism ATP energy",
    ]
    
    # Run query cycles
    print("\nRunning query cycles...")
    for cycle in range(10):
        print(f"\n--- Cycle {cycle + 1} ---")
        cycle_queries = random.sample(test_queries, min(5, len(test_queries)))
        
        for query in cycle_queries:
            # Run query
            result = engine.keyword_query(query)
            print(f"Query: '{query}' -> {len(result.fact_ids)} hits")
            
            # Log hits in registry
            for fact_id in result.fact_ids:
                registry.record_hit(fact_id, query.split(), result.confidences.get(fact_id, 0.7))
        
        # Cycle complete
        registry.advance_cycle()
    
    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nTotal cycles: {registry.cycle_count}")
    print(f"Total phantom candidates: {len(registry.phantoms)}")
    
    if len(registry.phantoms) > 0:
        total_hits = sum(p.hit_count for p in registry.phantoms.values())
        print(f"Total hits recorded: {total_hits}")
        
        # Sort by hit count
        sorted_phantoms = sorted(
            registry.phantoms.values(), 
            key=lambda p: p.hit_count, 
            reverse=True
        )[:10]
        
        print("\nTop 10 facts by hit count:")
        for i, phantom in enumerate(sorted_phantoms, 1):
            print(f"  {i:2d}. Fact {phantom.fact_id:3d}: {phantom.hit_count:2d} hits")
    else:
        print("\nNo phantom candidates tracked.")
    
    # Save registry
    registry.save("registry/delta_registry.json")
    print("\n+ Registry saved to ./registry/delta_registry.json")
    
    # Statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    
    print(f"Cartridges loaded: {len(engine.cartridges)}")
    print(f"Cartridge breakdown:")
    total_facts = 0
    for cart_name in sorted(engine.cartridges.keys()):
        cart = engine.cartridges[cart_name]
        count = len(cart.facts)
        total_facts += count
        print(f"  - {cart_name}: {count} facts")
    
    print(f"Total facts available: {total_facts}")
    print(f"Unique facts hit: {len(registry.phantoms)}")
    
    if total_facts > 0:
        hit_rate = len(registry.phantoms) / total_facts * 100
        print(f"Hit rate: {hit_rate:.1f}%")
    
    # Verify minimum criteria for Phase 2B
    print("\n" + "="*70)
    print("PHASE 2B READINESS CHECK")
    print("="*70)
    
    checks = [
        ("Cartridges loaded", len(engine.cartridges) >= 6),
        ("Total facts available", total_facts >= 100),
        ("Unique facts hit", len(registry.phantoms) >= 10),
        ("Query engine working", len(registry.phantoms) > 0),
        ("DeltaRegistry tracking", registry.cycle_count >= 10),
    ]
    
    all_pass = True
    for check_name, passed in checks:
        status = "+ PASS" if passed else "X FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_pass = False
    
    print("\n" + "="*70)
    if all_pass:
        print("+ PHASE 2B READINESS: PASS")
        print("All checks passed. Phase 2B is ready to proceed.")
        return True
    else:
        print("X PHASE 2B READINESS: FAIL")
        print("Some checks failed. Review results above.")
        return False


if __name__ == "__main__":
    import sys
    success = test_integration()
    sys.exit(0 if success else 1)
