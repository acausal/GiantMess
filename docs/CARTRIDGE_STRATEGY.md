# **Strategic Cartridge Selection for Phase 2B**

## **WHAT YOU ALREADY HAVE**

```
Foundational Sciences (Core layer):
✓ Physics basics       - Fundamental principles
✓ Chemistry basics     - Elements, reactions
✓ Biology             - Life systems
✓ Biochemistry        - Molecular biology
✓ Thermodynamics      - Energy, entropy
✓ Statistics          - Data analysis

Formal Systems:
✓ Formal logic        - Reasoning, proofs
```

**Total:** 7 cartridges already planned

---

## **STRATEGIC GAPS TO CONSIDER**

### **Gap 1: Applied Sciences (Real-World)**

These bridge theory to practice and tend to have **high cross-domain reference rates**:

**Option A: Engineering**
- Mechanics, materials, structures
- Cross-references: Physics, Chemistry, Thermodynamics
- Good for testing: Phantom hits across multiple cartridges

**Option B: Medicine/Anatomy**
- Human body systems, diseases, treatments
- Cross-references: Biology, Biochemistry, Chemistry, Statistics
- Good for testing: Dense intra-domain patterns

**Option C: Computer Science Fundamentals**
- Algorithms, data structures, complexity
- Cross-references: Formal Logic, Statistics
- Good for testing: Conceptual relationships

**Recommendation:** **Engineering** is strongest—it naturally cross-references Physics, Chemistry, Thermodynamics. Creates realistic phantom patterns.

---

### **Gap 2: Cognitive/Behavioral Sciences**

These are often **sparser and noisier**, good for testing robustness:

**Option A: Psychology**
- Behavior, cognition, development
- Cross-references: Statistics, Biology, Formal Logic
- Good for testing: Lower-confidence facts, subjective domains

**Option B: Neuroscience**
- Brain structure, neural mechanisms
- Cross-references: Biology, Biochemistry, Statistics
- Good for testing: Dense technical domain with clear links

**Recommendation:** **Neuroscience** is more objective. Psychology adds noise-testing value but is weaker.

---

### **Gap 3: Humanities/Qualitative (Optional)**

These test whether system handles **sparse, lower-confidence data**:

**Option A: Philosophy**
- Epistemology, metaphysics, ethics
- Cross-references: Formal Logic, Statistics (inference)
- Good for testing: Lower confidence, conceptual overlaps

**Option B: History**
- Events, causes, consequences
- Sparse cross-references
- Good for testing: Factual but weakly connected domain

**Recommendation:** **Philosophy** is stronger—it genuinely cross-references Formal Logic and makes conceptual sense.

---

## **STRATEGIC RECOMMENDATIONS BY GOAL**

### **IF: Cross-domain pattern detection (phantoms across cartridges)**

You want domains that naturally **reference each other**:

```
Suggested set:
✓ Physics basics
✓ Chemistry basics
✓ Thermodynamics
✓ Biology
✓ Biochemistry
✓ Statistics
✓ Formal Logic
+ ENGINEERING (high cross-reference density)
+ NEUROSCIENCE (bridges bio/chem/stats)

Total: 9 cartridges, ~1500-2000 facts
Phantoms should form across domains (e.g., "energy" appears in physics, chemistry, thermodynamics, engineering)
```

---

### **IF: Deep patterns within domains (repetitive queries)**

You want domains with **internal richness and self-reference**:

```
Suggested set:
✓ Physics basics
✓ Chemistry basics
✓ Biology
✓ Biochemistry
✓ Statistics
✓ Formal Logic
+ PHILOSOPHY (cross-references logic, epistemology)

Total: 7 cartridges, ~1000-1500 facts
Phantoms form through repeated queries to same domain
Validates that crystallization works on deep patterns
```

---

### **IF: Mixed (recommend for actual Phase 2B)**

Balance both objectives:

```
Suggested set:
✓ Physics basics
✓ Chemistry basics
✓ Thermodynamics
✓ Biology
✓ Biochemistry
✓ Statistics
✓ Formal Logic
+ ENGINEERING (cross-domain bridge)
+ PHILOSOPHY (conceptual depth, logic overlap)

Total: 9 cartridges, ~1500-2000 facts
Tests both cross-domain patterns and internal structures
Most realistic for production data
```

---

### **IF: Minimal viable (just start Phase 2B)**

Smallest set that tests the pipeline:

```
Suggested set:
✓ Physics basics
✓ Chemistry basics
✓ Biology
✓ Statistics
✓ Formal Logic
+ THERMODYNAMICS (to cross-reference physics/chem)

Total: 6 cartridges, ~800-1200 facts
Sufficient to generate 10+ locked phantoms
Sufficient to test crystallization pipeline
Can expand later
```

---

## **CROSS-REFERENCE MATRIX**

How strongly each domain references others (for deliberate overlap testing):

```
            Physics  Chem   Bio   BioChem  Thermo  Stat   Logic  Eng   Neurosci  Phil
Physics       —      High   Low    Low     High    Med    Low    High   Low       Low
Chemistry    High     —     High   High    Med     Low    Low    High   High      Low
Biology      Low     High    —     High    Low     High   Low    Med    High      Low
BioChem      Low     High   High    —      Low     Med    Low    Med    High      Low
Thermo       High    Med    Low    Low     —      Med    Low    High   Low       Low
Statistics   Med     Low    High   Med     Med     —      Med    High   High      High
Logic        Low     Low    Low    Low     Low     Med    —      Low    Low       High
Engineering  High    High   Low    Med     High    High   Med    —      Low       Low
Neurosci     Low     High   High   High    Low     High   Low    Low    —         Low
Philosophy   Low     Low    Low    Low     Low     High   High   Low    Low       —
```

**Interpretation:**
- Engineering has 6 "High" and "Med" references (most connected)
- Neuroscience has 4 "High" and "Med" references (good bridge)
- Philosophy has 2 "High" but excellent conceptual ties (logic)

---

## **PROPOSED MINIMAL + STRATEGIC SET**

**My recommendation for Phase 2B:**

```
Core (Already have):
1. Physics basics        ← 100 facts
2. Chemistry basics      ← 100 facts
3. Biology              ← 100 facts
4. Biochemistry         ← 100 facts
5. Thermodynamics       ← 75 facts
6. Statistics           ← 75 facts
7. Formal Logic         ← 75 facts

NEW (Strategic adds):
8. Engineering          ← 100 facts (cross-domain bridge)
9. Neuroscience         ← 100 facts (bio + chem + stats bridge)

Total: 9 cartridges, ~825 facts
Estimated phantoms: 20-30 by end of Phase 2B
Estimated grains: 5-10 crystallized
```

**Why this mix:**

- **Cross-domain testing:** Engineering + Neuroscience create natural overlaps
- **Depth testing:** Each core domain is substantial enough for internal patterns
- **Realistic:** Mirrors actual knowledge bases with both specialist and bridge domains
- **Not too large:** Still easy to debug, trace, and understand
- **Scalable:** Can add more specialized domains later (Medicine, Philosophy, etc.)

---

## **DETAILED CONTENT SUGGESTIONS**

### **Engineering (NEW)**

```
Domains:
- Structural mechanics (forces, stress, strain)
- Materials science (properties, failure modes)
- Thermodynamic systems (heat transfer, efficiency)
- Electrical basics (circuits, power)
- Fluid mechanics (flow, pressure)

Cross-references:
- Physics: force, acceleration, energy, motion
- Chemistry: material properties, corrosion
- Thermodynamics: heat, efficiency, work
- Statistics: safety factors, reliability, tolerances

Approx 100 facts, confidence 0.85-0.95
```

### **Neuroscience (NEW)**

```
Domains:
- Neural anatomy (neurons, synapses, brain regions)
- Neurotransmission (chemistry of signaling)
- Brain systems (vision, memory, motor control)
- Neuroplasticity (learning, adaptation)
- Computational neuroscience (information processing)

Cross-references:
- Biology: cells, tissues, development
- Chemistry: molecules, reactions, binding
- Biochemistry: proteins, receptors, metabolism
- Statistics: correlations, signal detection
- Physics: electrical signals, electrostatics

Approx 100 facts, confidence 0.80-0.92
```

---

## **ALTERNATIVE: ADD PHILOSOPHY?**

If you want to test **conceptual/lower-confidence domain**:

```
Philosophy:
- Epistemology (knowledge, justified belief)
- Metaphysics (existence, reality)
- Logic (formal reasoning—overlaps with Logic cart)
- Philosophy of science (evidence, causation)

Cross-references:
- Formal Logic: reasoning, proof, consistency
- Statistics: evidence, inference, probability
- Biology/Chem: philosophy of science aspects

Approx 75 facts, confidence 0.70-0.85 (intentionally lower)
Good for testing: Does system handle lower-confidence domains?
```

---

## **FINAL RECOMMENDATION**

**Primary Set (9 carts, 825 facts):**
1. Physics basics
2. Chemistry basics
3. Biology
4. Biochemistry
5. Thermodynamics
6. Statistics
7. Formal Logic
8. **Engineering** ← NEW (cross-domain bridge)
9. **Neuroscience** ← NEW (cross-domain bridge)

**Optional Additions:**
- **Philosophy** (if you want to test low-confidence domain robustness)
- **Medicine/Anatomy** (if you want dense intra-domain patterns)

**Skip for Phase 2B (add in Phase 3+):**
- Computer Science (tangential)
- History (sparse connections)
- Economics (not enough overlap)

---

## **NEXT STEPS**

1. **Decide your Phase 2B goal** (cross-domain, deep patterns, or mixed)
2. **Choose cartridge set** (minimal, strategic, or comprehensive)
3. **Create data files** for new cartridges (Engineering, Neuroscience, optional Philosophy)
4. **Build cartridges** using CartridgeBuilder
5. **Run integration test** (verify query engine + DeltaRegistry)
6. **Proceed to Phase 2B**

---

**Created:** February 12, 2026
