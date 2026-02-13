#!/usr/bin/env python3
"""
Grain Inspection Tool - Windows-friendly grain analysis

Inspect crystallized grains, show statistics, sample contents, etc.
"""

import json
import os
from pathlib import Path
from typing import Dict, List


def find_all_grains(cartridges_dir: str = "./cartridges") -> Dict[str, List[str]]:
    """Find all grain files across all cartridges."""
    grains = {}
    
    for cartridge_dir in Path(cartridges_dir).glob("*.kbc"):
        grains_dir = cartridge_dir / "grains"
        if grains_dir.exists():
            grain_files = list(grains_dir.glob("*.json"))
            if grain_files:
                cart_name = cartridge_dir.name.replace('.kbc', '')
                grains[cart_name] = [str(f) for f in sorted(grain_files)]
    
    return grains


def print_grain_summary(cartridges_dir: str = "./cartridges"):
    """Print summary of all crystallized grains."""
    grains = find_all_grains(cartridges_dir)
    
    print("\n" + "="*70)
    print("CRYSTALLIZED GRAINS SUMMARY")
    print("="*70)
    
    total_grains = 0
    total_size = 0
    
    for cart_name in sorted(grains.keys()):
        grain_files = grains[cart_name]
        cart_size = 0
        
        for grain_file in grain_files:
            cart_size += os.path.getsize(grain_file)
        
        total_grains += len(grain_files)
        total_size += cart_size
        
        avg_size = cart_size / len(grain_files) if grain_files else 0
        print(f"{cart_name:20} | {len(grain_files):3d} grains | {cart_size:>10,} bytes | {avg_size:>7.0f} bytes/grain")
    
    print("-"*70)
    avg_grain = total_size / total_grains if total_grains else 0
    print(f"{'TOTAL':20} | {total_grains:3d} grains | {total_size:>10,} bytes | {avg_grain:>7.0f} bytes/grain")
    print("="*70 + "\n")


def inspect_grain(grain_file: str):
    """Inspect a single grain file."""
    try:
        with open(grain_file, 'r') as f:
            grain = json.load(f)
        
        print(f"\nGrain: {grain.get('grain_id')}")
        print(f"File: {grain_file}")
        print(f"Size: {os.path.getsize(grain_file):,} bytes")
        print("\nStructure:")
        print(f"  - Fact ID: {grain.get('fact_id')}")
        print(f"  - Cartridge: {grain.get('cartridge_source')}")
        print(f"  - Lock State: {grain.get('lock_state')}")
        print(f"  - Confidence: {grain.get('confidence', 0):.4f}")
        print(f"  - Weight: {grain.get('weight')} bits")
        print(f"  - Cycles Locked: {grain.get('cycles_locked')}")
        
        delta = grain.get('delta', {})
        print(f"\nTernary Delta:")
        print(f"  - Positive ({len(delta.get('positive', []))}): {delta.get('positive', [])[:3]}")
        print(f"  - Negative ({len(delta.get('negative', []))}): {delta.get('negative', [])[:3]}")
        print(f"  - Void ({len(delta.get('void', []))}): {delta.get('void', [])[:3]}")
        
        pointer_map = grain.get('pointer_map', {})
        print(f"\nPointer Map:")
        print(f"  - Positive Ptrs: {len(pointer_map.get('positive_ptrs', {}))}")
        print(f"  - Negative Ptrs: {len(pointer_map.get('negative_ptrs', {}))}")
        print(f"  - Void Ptrs: {len(pointer_map.get('void_ptrs', {}))}")
        print(f"  - Total Bits: {pointer_map.get('total_bits', 0)}")
        
        if 'access_pattern' in pointer_map:
            ap = pointer_map['access_pattern']
            print(f"\nAccess Pattern:")
            print(f"  - Hit Count: {ap.get('hit_count')}")
            print(f"  - Confidence: {ap.get('confidence', 0):.4f}")
            print(f"  - First Seen: Cycle {ap.get('first_seen')}")
            print(f"  - Last Seen: Cycle {ap.get('last_seen')}")
        
        print()
    
    except Exception as e:
        print(f"Error reading grain: {e}")


def list_grains_by_cartridge(cartridge: str, cartridges_dir: str = "./cartridges"):
    """List all grains in a specific cartridge."""
    grains = find_all_grains(cartridges_dir)
    
    if cartridge not in grains:
        print(f"Cartridge '{cartridge}' not found")
        return
    
    grain_files = grains[cartridge]
    
    print(f"\nGrains in '{cartridge}' ({len(grain_files)} total):")
    print("-"*70)
    print(f"{'Grain ID':<15} {'Fact ID':<10} {'Confidence':<12} {'Size':<10}")
    print("-"*70)
    
    for grain_file in grain_files:
        try:
            with open(grain_file, 'r') as f:
                grain = json.load(f)
            
            grain_id = grain.get('grain_id', 'unknown')
            fact_id = grain.get('fact_id', 'unknown')
            confidence = grain.get('confidence', 0.0)
            size = os.path.getsize(grain_file)
            
            print(f"{grain_id:<15} {str(fact_id):<10} {confidence:<12.4f} {size:<10,}")
        except Exception as e:
            print(f"Error reading grain: {e}")
    
    print()


def main():
    """Main menu."""
    import sys
    
    grains = find_all_grains()
    
    if not grains:
        print("No crystallized grains found")
        return
    
    while True:
        print("\n" + "="*70)
        print("GRAIN INSPECTION TOOL")
        print("="*70)
        print("\nOptions:")
        print("  1. Show summary of all grains")
        print("  2. List grains by cartridge")
        print("  3. Inspect a specific grain")
        print("  4. Compare cartridge compression")
        print("  5. Exit")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            print_grain_summary()
        
        elif choice == "2":
            print("\nAvailable cartridges:")
            for i, cart in enumerate(sorted(grains.keys()), 1):
                print(f"  {i}. {cart} ({len(grains[cart])} grains)")
            
            cart_choice = input("\nSelect cartridge number (or name): ").strip()
            
            # Try numeric index first
            try:
                idx = int(cart_choice) - 1
                cart_name = sorted(grains.keys())[idx]
            except (ValueError, IndexError):
                # Try by name
                cart_name = cart_choice
            
            if cart_name in grains:
                list_grains_by_cartridge(cart_name)
            else:
                print(f"Cartridge '{cart_name}' not found")
        
        elif choice == "3":
            print("\nAvailable grains:")
            grain_list = []
            for cart in sorted(grains.keys()):
                for grain_file in grains[cart][:3]:  # Show first 3 per cartridge
                    grain_id = json.load(open(grain_file)).get('grain_id', 'unknown')
                    grain_list.append((grain_file, grain_id))
            
            for i, (grain_file, grain_id) in enumerate(grain_list[:20], 1):
                print(f"  {i}. {grain_id}")
            
            if len(grain_list) > 20:
                print(f"  ... and {len(grain_list) - 20} more")
            
            grain_idx = input("\nGrain number (or path): ").strip()
            
            try:
                idx = int(grain_idx) - 1
                grain_file = grain_list[idx][0]
            except (ValueError, IndexError):
                grain_file = grain_idx
            
            if os.path.exists(grain_file):
                inspect_grain(grain_file)
            else:
                print(f"Grain file '{grain_file}' not found")
        
        elif choice == "4":
            print("\nCartridge Compression Comparison:")
            print("-"*70)
            print(f"{'Cartridge':<20} {'Grains':<8} {'Total Size':<15} {'Avg Size':<12}")
            print("-"*70)
            
            for cart in sorted(grains.keys()):
                grain_files = grains[cart]
                total_size = sum(os.path.getsize(f) for f in grain_files)
                avg_size = total_size / len(grain_files) if grain_files else 0
                print(f"{cart:<20} {len(grain_files):<8} {total_size:<15,} {avg_size:<12.0f}")
            
            print()
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
