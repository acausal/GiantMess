# Markdown Parser Enhancement Specification
## YAML Frontmatter & Temporal Bounds Support

**Version:** 1.0  
**Date:** February 13, 2026  
**Phase:** 2B (Foundation for enrichment pipeline)  
**Status:** Ready for implementation

---

## Overview

The markdown parser needs to support two new features:

1. **YAML Frontmatter** - Cartridge-level metadata (epistemic level, domain, description, tags)
2. **Temporal Bounds** - Fact validity windows (when facts are true/relevant)

These enable:
- Seed cartridge creation with explicit knowledge classification
- Temporal awareness (facts expire, future events are uncertain)
- Audit trail metadata (who validated this? when?)
- Enrichment signals (temporal patterns help with hypothesis generation)

---

## Feature 1: YAML Frontmatter

### Current Markdown Format

```markdown
# Physics
## Mechanics
- Newton's First Law: An object at rest stays at rest | Newton's Laws | 0.96
- Newton's Second Law: F = ma | Newton's Laws | 0.96
```

### New Format with Frontmatter

```markdown
---
cartridge_name: Physics
epistemic_level: L0_EMPIRICAL
domain: Physics
description: Universal physical laws and observations
tags: [empirical, fundamental, validated]
author: Isaac
created: 2026-02-13
baseline_confidence: 0.95
---

# Classical Mechanics
## Mechanics
- Newton's First Law: An object at rest stays at rest | Newton's Laws | 0.96
- Newton's Second Law: F = ma | Newton's Laws | 0.96
```

### YAML Fields

| Field | Type | Required | Example | Purpose |
|-------|------|----------|---------|---------|
| cartridge_name | string | YES | "Physics" | Override name from filename |
| epistemic_level | enum | YES | L0_EMPIRICAL | Base level for all facts (can override per-fact) |
| domain | string | YES | Physics | Primary domain |
| description | string | NO | "Universal physical laws..." | Cartridge purpose |
| tags | array[string] | NO | [empirical, fundamental] | Classification tags |
| author | string | NO | Isaac | Who created this |
| created | ISO8601 | NO | 2026-02-13 | Creation date |
| baseline_confidence | float | NO | 0.95 | Default confidence for facts without explicit score |
| temporal_scope | string | NO | "eternal" or "2020-2030" | What time period this applies to |

### Implementation in CartridgeBuilder

**File:** `kitbash_builder.py`

**Add method:**
```python
def _parse_yaml_frontmatter(self, text: str) -> Tuple[dict, str]:
    """
    Extract YAML frontmatter from markdown.
    
    Returns: (frontmatter_dict, remaining_markdown_text)
    """
    # Check if text starts with ---
    if not text.strip().startswith("---"):
        return {}, text  # No frontmatter
    
    # Find closing ---
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text  # Malformed, treat as no frontmatter
    
    yaml_text = parts[1]
    markdown_text = parts[2]
    
    # Parse YAML
    try:
        import yaml
        frontmatter = yaml.safe_load(yaml_text)
        return frontmatter or {}, markdown_text
    except ImportError:
        # Fallback: simple key-value parsing (no external dep)
        return self._parse_yaml_simple(yaml_text), markdown_text

def _parse_yaml_simple(self, yaml_text: str) -> dict:
    """
    Simple YAML parser (no external dependencies).
    Only handles basic key: value and key: [item1, item2] formats.
    """
    result = {}
    for line in yaml_text.strip().split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Parse arrays [item1, item2]
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            result[key] = [item.strip() for item in items]
        # Parse booleans
        elif value.lower() == 'true':
            result[key] = True
        elif value.lower() == 'false':
            result[key] = False
        # Parse numbers
        elif value.replace('.', '', 1).isdigit():
            result[key] = float(value) if '.' in value else int(value)
        # Parse strings
        else:
            result[key] = value.strip('"\'')  # Remove quotes if present
    
    return result
```

**Modify method:** `from_markdown()`

```python
def from_markdown(self, filepath: str, 
                 domain_pattern: str = "#",
                 subdomain_pattern: str = "##",
                 fact_pattern: str = "-") -> None:
    """
    Load facts from markdown file with optional YAML frontmatter.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # STEP 1: Parse YAML frontmatter
    frontmatter, markdown_content = self._parse_yaml_frontmatter(content)
    
    # STEP 2: Apply frontmatter to cartridge
    if frontmatter:
        self._apply_frontmatter(frontmatter)
    
    # STEP 3: Parse markdown facts (existing logic)
    lines = markdown_content.split('\n')
    current_domain = ""
    current_subdomains = []
    baseline_confidence = frontmatter.get('baseline_confidence', 0.8)
    
    for line in lines:
        line = line.rstrip()
        
        # ... existing domain/subdomain logic ...
        
        # Check for fact
        if line.startswith(fact_pattern + " "):
            fact_text = line.lstrip(fact_pattern).strip()
            
            # Parse: "content | source | confidence | temporal_bounds"
            parts = [p.strip() for p in fact_text.split("|")]
            content = parts[0]
            source = parts[1] if len(parts) > 1 else "markdown"
            confidence = float(parts[2]) if len(parts) > 2 else baseline_confidence
            temporal_bounds = parts[3] if len(parts) > 3 else None
            
            # Parse temporal bounds (see Feature 2)
            temporal_validity = self._parse_temporal_bounds(temporal_bounds)
            
            # Create annotation
            ann = AnnotationMetadata(
                fact_id=0,
                confidence=confidence,
                sources=[source],
                context_domain=current_domain or frontmatter.get('domain', 'general'),
                context_subdomains=current_subdomains,
                epistemic_level=EpistemicLevel[frontmatter.get('epistemic_level', 'L2_AXIOMATIC')],
                temporal_validity_start=temporal_validity['start'],
                temporal_validity_end=temporal_validity['end'],
            )
            
            self.cart.add_fact(content, ann)
            self.fact_count += 1
    
    print(f"✓ Loaded {self.fact_count} facts from {filepath}")

def _apply_frontmatter(self, frontmatter: dict) -> None:
    """
    Apply YAML frontmatter to cartridge manifest and builder state.
    """
    if 'cartridge_name' in frontmatter:
        # Note: already set during __init__, but could override
        pass
    
    if not self.cart.manifest:
        self.cart.manifest = {}
    
    # Apply frontmatter fields to manifest
    self.cart.manifest['description'] = frontmatter.get('description', '')
    self.cart.manifest['epistemic_level'] = frontmatter.get('epistemic_level', 'L2_AXIOMATIC')
    self.cart.manifest['domain'] = frontmatter.get('domain', 'general')
    self.cart.manifest['tags'] = frontmatter.get('tags', [])
    self.cart.manifest['author'] = frontmatter.get('author', 'unknown')
    self.cart.manifest['created'] = frontmatter.get('created', datetime.now().isoformat())
    self.cart.manifest['baseline_confidence'] = frontmatter.get('baseline_confidence', 0.8)
    self.cart.manifest['temporal_scope'] = frontmatter.get('temporal_scope', None)
```

---

## Feature 2: Temporal Bounds Parsing

### What are Temporal Bounds?

Facts can have validity windows:

| Format | Meaning | Example |
|--------|---------|---------|
| `eternal` | Always true (no bounds) | Law of gravity |
| `2025-02-12 to 2028-01-20` | Precise window | Contract expiration |
| `2025 to 2030` | Year range | Market prediction |
| `past to 2025` | Bounded end | Event happened before 2025 |
| `2030 to future` | Bounded start | Future event |
| `~5_billion_years` | Approximate future | Sun will explode |
| `sometime` or `eventually` | Unbounded future | Uncertain event |

### Storage in AnnotationMetadata

Already supported:
```python
@dataclass
class AnnotationMetadata:
    temporal_validity_start: Optional[str] = None  # ISO8601
    temporal_validity_end: Optional[str] = None    # ISO8601
```

**Examples:**

| Input | `temporal_validity_start` | `temporal_validity_end` |
|-------|--------------------------|------------------------|
| `eternal` | `None` | `None` |
| `2025-02-12 to 2028-01-20` | `2025-02-12T00:00:00Z` | `2028-01-20T23:59:59Z` |
| `~5_billion_years` | `2026-02-13T00:00:00Z` | `None` |
| `past to 2025` | `None` | `2025-12-31T23:59:59Z` |

### Implementation

**Add method to CartridgeBuilder:**

```python
def _parse_temporal_bounds(self, temporal_str: Optional[str]) -> dict:
    """
    Parse temporal bounds string into start/end ISO8601 dates.
    
    Returns: {
        'start': ISO8601 string or None,
        'end': ISO8601 string or None,
        'approximate': bool,
        'raw_format': str (for debugging)
    }
    """
    from datetime import datetime, timedelta
    import re
    
    if not temporal_str:
        return {'start': None, 'end': None, 'approximate': False, 'raw_format': None}
    
    temporal_str = temporal_str.strip()
    
    # Handle "eternal" (no bounds)
    if temporal_str.lower() in ['eternal', 'always', 'indefinite']:
        return {'start': None, 'end': None, 'approximate': False, 'raw_format': temporal_str}
    
    # Handle "sometime" / "eventually" (unbounded future)
    if temporal_str.lower() in ['sometime', 'eventually']:
        return {'start': datetime.now(timezone.utc).isoformat(), 'end': None, 'approximate': True, 'raw_format': temporal_str}
    
    # Handle approximate future: "~5_billion_years"
    match = re.match(r'~(\d+)_(\w+)', temporal_str)
    if match:
        # Just use today as start, no end (approximate)
        return {'start': datetime.now(timezone.utc).isoformat(), 'end': None, 'approximate': True, 'raw_format': temporal_str}
    
    # Handle "X to Y" format
    if ' to ' in temporal_str:
        parts = temporal_str.split(' to ')
        start_str = parts[0].strip()
        end_str = parts[1].strip()
        
        start_date = self._parse_date_component(start_str)
        end_date = self._parse_date_component(end_str)
        
        return {'start': start_date, 'end': end_date, 'approximate': False, 'raw_format': temporal_str}
    
    # Single date (treat as start)
    single_date = self._parse_date_component(temporal_str)
    return {'start': single_date, 'end': None, 'approximate': False, 'raw_format': temporal_str}

def _parse_date_component(self, date_str: str) -> Optional[str]:
    """
    Parse a single date component.
    
    Handles:
    - ISO8601: 2025-02-12
    - Year only: 2025
    - Keywords: past, future, today, now
    """
    from datetime import datetime, timezone
    
    date_str = date_str.strip().lower()
    
    # Keywords
    if date_str in ['past', 'beginning', 'always']:
        return None  # Unbounded past
    
    if date_str in ['future', 'forever', 'always']:
        return None  # Unbounded future
    
    if date_str in ['today', 'now']:
        return datetime.now(timezone.utc).isoformat()
    
    # Try ISO8601: 2025-02-12
    try:
        dt = datetime.fromisoformat(date_str + 'T00:00:00' if 'T' not in date_str else date_str)
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        pass
    
    # Try year only: 2025
    if len(date_str) == 4 and date_str.isdigit():
        year = int(date_str)
        dt = datetime(year, 1, 1, tzinfo=timezone.utc)
        return dt.isoformat()
    
    # Try year-month: 2025-02
    if len(date_str) == 7 and '-' in date_str:
        try:
            dt = datetime.fromisoformat(date_str + '-01T00:00:00')
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass
    
    # Can't parse, return None
    print(f"⚠ Warning: Could not parse temporal bound: {date_str}")
    return None
```

---

## Example: Enhanced Physics Cartridge

**File:** `physics_basics_enhanced.md`

```markdown
---
cartridge_name: Physics
epistemic_level: L0_EMPIRICAL
domain: Physics
description: Universal physical laws and observations from classical mechanics through modern physics
tags: [empirical, fundamental, validated, laws_of_motion]
author: Isaac
created: 2026-02-13
baseline_confidence: 0.96
temporal_scope: eternal
---

# Classical Mechanics

## Newton's Laws

- Newton's First Law: An object at rest stays at rest unless acted on by force | Newton's Laws | 0.99 | eternal
- Newton's Second Law: Force equals mass times acceleration (F = ma) | Newton's Laws | 0.99 | eternal
- Newton's Third Law: For every action there is an equal and opposite reaction | Newton's Laws | 0.99 | eternal

## Gravity

- Gravitational force between two masses is proportional to their mass and inversely proportional to distance squared | Universal Gravitation | 0.98 | eternal
- Objects near Earth's surface fall at approximately 9.8 m/s² due to gravity | Measurement | 0.97 | eternal
- The Sun will eventually exhaust its hydrogen | Stellar Evolution | 0.92 | ~5_billion_years

# Thermodynamics

## Laws of Thermodynamics

- First Law: Energy cannot be created or destroyed, only transformed | Thermodynamics | 0.99 | eternal
- Second Law: Entropy of an isolated system always increases | Thermodynamics | 0.98 | eternal
- Heat flows from hot objects to cold objects | Observation | 0.99 | eternal

# Quantum Mechanics

## Uncertainty Principle

- Heisenberg's Uncertainty Principle: Cannot know position and momentum simultaneously with arbitrary precision | Quantum Mechanics | 0.95 | 1927 to future
- Planck's constant is approximately 6.626e-34 J·s | Measurement | 0.99 | eternal
```

---

## Testing the Parser

**Test file:** `test_markdown_parser.py`

```python
#!/usr/bin/env python3
"""Test enhanced markdown parser with frontmatter and temporal bounds"""

from kitbash_builder import CartridgeBuilder
from pathlib import Path


def test_yaml_frontmatter():
    """Test YAML frontmatter parsing"""
    markdown = """---
cartridge_name: TestPhysics
epistemic_level: L0_EMPIRICAL
domain: Physics
description: Test cartridge
tags: [test, physics]
baseline_confidence: 0.95
---

# Physics
- Newton's Law | Source | 0.99
"""
    
    # Write test file
    test_file = Path("test_frontmatter.md")
    test_file.write_text(markdown)
    
    try:
        builder = CartridgeBuilder("test_physics")
        builder.build()
        builder.from_markdown(str(test_file))
        
        # Check manifest
        assert builder.cart.manifest['description'] == 'Test cartridge'
        assert builder.cart.manifest['epistemic_level'] == 'L0_EMPIRICAL'
        assert builder.cart.manifest['baseline_confidence'] == 0.95
        assert 'physics' in builder.cart.manifest['tags']
        
        print("✓ YAML frontmatter parsing works")
        return True
    finally:
        test_file.unlink(missing_ok=True)


def test_temporal_bounds():
    """Test temporal bounds parsing"""
    test_cases = [
        ("eternal", None, None),
        ("2025-02-12 to 2028-01-20", "2025-02-12", "2028-01-20"),
        ("2025 to 2030", "2025-01-01", "2030-12-31"),
        ("past to 2025", None, "2025-12-31"),
        ("2030 to future", "2030-01-01", None),
        ("~5_billion_years", "2026-02-13", None),  # approximate
        ("sometime", "2026-02-13", None),  # unbounded future
    ]
    
    builder = CartridgeBuilder("test")
    builder.build()
    
    for input_str, expected_start_year, expected_end_year in test_cases:
        result = builder._parse_temporal_bounds(input_str)
        
        if expected_start_year is None:
            assert result['start'] is None, f"Failed: {input_str} -> start should be None"
        else:
            assert result['start'].startswith(expected_start_year), f"Failed: {input_str} -> start mismatch"
        
        if expected_end_year is None:
            assert result['end'] is None, f"Failed: {input_str} -> end should be None"
        else:
            assert result['end'].startswith(expected_end_year), f"Failed: {input_str} -> end mismatch"
        
        print(f"  ✓ {input_str:30s} -> {result['start']}/{result['end']}")
    
    print("✓ Temporal bounds parsing works")
    return True


def test_full_roundtrip():
    """Test full markdown parsing with frontmatter + temporal bounds"""
    markdown = """---
cartridge_name: Physics
epistemic_level: L0_EMPIRICAL
domain: Physics
description: Physical laws
baseline_confidence: 0.96
---

# Classical Mechanics
- Newton's First Law | Newton | 0.99 | eternal
- Newton's Second Law | Newton | 0.99 | eternal

# Future Events
- Sun will explode | Astronomy | 0.92 | ~5_billion_years
"""
    
    test_file = Path("test_roundtrip.md")
    test_file.write_text(markdown)
    
    try:
        builder = CartridgeBuilder("physics_test")
        builder.build()
        builder.from_markdown(str(test_file))
        builder.save()
        
        # Check facts loaded
        assert builder.fact_count == 3, f"Expected 3 facts, got {builder.fact_count}"
        
        # Check manifest
        assert builder.cart.manifest['epistemic_level'] == 'L0_EMPIRICAL'
        assert builder.cart.manifest['baseline_confidence'] == 0.96
        
        # Check annotations
        for fact_id, ann in builder.cart.annotations.items():
            if fact_id in [1, 2]:  # Newton's laws
                assert ann.temporal_validity_start is None
                assert ann.temporal_validity_end is None
            elif fact_id == 3:  # Sun exploding
                assert ann.temporal_validity_start is not None
                assert ann.temporal_validity_end is None
        
        print("✓ Full roundtrip works")
        return True
    finally:
        test_file.unlink(missing_ok=True)
        import shutil
        shutil.rmtree("cartridges/physics_test.kbc", ignore_errors=True)


if __name__ == "__main__":
    print("Testing Enhanced Markdown Parser\n")
    
    all_pass = True
    all_pass &= test_yaml_frontmatter()
    all_pass &= test_temporal_bounds()
    all_pass &= test_full_roundtrip()
    
    print("\n" + "="*70)
    if all_pass:
        print("✓ All parser tests passed")
    else:
        print("✗ Some tests failed")
    print("="*70)
```

---

## Implementation Checklist

- [ ] Add `_parse_yaml_frontmatter()` method to CartridgeBuilder
- [ ] Add `_parse_yaml_simple()` method (no external dependencies)
- [ ] Add `_apply_frontmatter()` method
- [ ] Modify `from_markdown()` to call frontmatter parsing
- [ ] Add `_parse_temporal_bounds()` method
- [ ] Add `_parse_date_component()` method
- [ ] Update `AnnotationMetadata.temporal_validity_start/end` usage
- [ ] Create test file `test_markdown_parser.py`
- [ ] Run tests and verify all pass
- [ ] Update `physics_basics.md` to include frontmatter (optional, for testing)
- [ ] Update other cartridge markdown files (optional, can be phased)

---

## Notes

### Why No External YAML Library?

The simple `_parse_yaml_simple()` fallback handles the cases we actually use:
- Simple key-value pairs
- Arrays: `[item1, item2]`
- Booleans, numbers, strings
- No nested structures or complex YAML

This keeps dependencies minimal and system hermetic (no cloud, no pip installs).

### Temporal Bounds are Optional

Facts without temporal bounds default to `eternal` (no start/end). This maintains backward compatibility with existing markdown files.

### Epistemic Level Inheritance

If frontmatter specifies `epistemic_level`, all facts inherit it unless overridden per-fact. This enables seed cartridges to declare their knowledge type upfront.

### Next: Step 2

After this passes testing, Step 2 will:
- Extend `AnnotationMetadata` with confidence history tracking
- Add validation pass metadata to manifest
- Create foundation for enrichment audit trail
