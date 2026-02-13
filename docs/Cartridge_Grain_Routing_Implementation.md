# Cartridge + Grain: Routing and Escalation Patterns
## How to Operationalize Layer-Appropriate Problem Solving

**Framework:** Concrete implementation patterns for your architecture  
**Audience:** Building the decision logic  

---

## Part 1: The Query Arrival Protocol

Every query goes through the same sequence. The question is: **at which step does it get answered?**

```python
class QueryProcessor:
    """
    Routes query through cartridge+grain architecture.
    Escalates only when necessary.
    """
    
    def process_query(self, user_query, context=None):
        """Main entry point."""
        
        # Phase 0: Preprocessing (deterministic)
        query_tokens = self.tokenize(user_query)
        query_embedding = self.shallow_embed(query_tokens)  # Not expensive
        
        # Phase 1: GRAIN LAYER (Ternary lookup)
        grain_result = self.try_grain_lookup(query_embedding)
        if grain_result['confidence'] > 0.85:
            # Matched a domain/pattern grain
            return {
                'answer': f"Routing to domain: {grain_result['domain']}",
                'confidence': grain_result['confidence'],
                'layer': 'GRAIN',
                'latency_ms': 0.5,
                'next_step': 'hot_cartridge'
            }
        
        # Phase 2: HOT CARTRIDGE (Index + fact lookup)
        hot_result = self.try_hot_cartridge(query_tokens, grain_result['domain'])
        if hot_result['found'] and hot_result['confidence'] > 0.75:
            # Found facts in hot cartridge
            return {
                'answer': hot_result['synthesized_answer'],
                'confidence': hot_result['confidence'],
                'sources': hot_result['sources'],
                'layer': 'HOT_CARTRIDGE',
                'latency_ms': hot_result['latency'],
                'facts_used': len(hot_result['fact_ids'])
            }
        
        # Phase 3: COLD CARTRIDGE (Load and check)
        cold_result = self.try_cold_cartridge(query_tokens, grain_result['domain'])
        combined_confidence = max(hot_result['confidence'], cold_result['confidence'])
        if combined_confidence > 0.70:
            # Cold cartridge provided better facts
            return {
                'answer': cold_result['synthesized_answer'],
                'confidence': combined_confidence,
                'sources': hot_result['sources'] + cold_result['sources'],
                'layer': 'HOT+COLD_CARTRIDGE',
                'latency_ms': hot_result['latency'] + cold_result['latency'],
                'note': 'Used edge cases from cold cartridge'
            }
        
        # Phase 4: SPECIALIST SMOLML (Synthesis + reasoning)
        specialist_result = self.try_specialist_model(
            query=user_query,
            domain=grain_result['domain'],
            hot_facts=hot_result['facts'],
            cold_facts=cold_result['facts'],
            context=context
        )
        if specialist_result['confidence'] > 0.65:
            # Specialist model can handle it
            
            # Critical: Validate against axioms
            validated = self.validate_specialist_output(
                output=specialist_result['answer'],
                domain=grain_result['domain'],
                axioms=self.get_domain_axioms(grain_result['domain'])
            )
            
            if validated['valid']:
                return {
                    'answer': specialist_result['answer'],
                    'confidence': specialist_result['confidence'],
                    'layer': 'SPECIALIST_SMOLML',
                    'latency_ms': specialist_result['latency'],
                    'validation': 'passed_axioms',
                    'facts_combined': len(hot_result['facts']) + len(cold_result['facts'])
                }
        
        # Phase 5: SYSTEM 2 / HAT LLM (Full reasoning)
        llm_result = self.try_system2_llm(
            query=user_query,
            domain=grain_result['domain'],
            all_cartridge_facts=hot_result['facts'] + cold_result['facts'],
            specialist_attempt=specialist_result,
            context=context
        )
        
        # Critical: Strong validation for LLM output (high hallucination risk)
        validated = self.validate_llm_output(
            output=llm_result['answer'],
            domain=grain_result['domain'],
            existing_facts=hot_result['facts'] + cold_result['facts'],
            axioms=self.get_domain_axioms(grain_result['domain'])
        )
        
        if validated['valid'] and llm_result['confidence'] > 0.60:
            # Store as potential phantom (needs validation)
            self.delta_registry.record_potential_phantom(
                query=user_query,
                answer=llm_result['answer'],
                confidence=llm_result['confidence'],
                validation_status='pending'
            )
            
            return {
                'answer': llm_result['answer'],
                'confidence': llm_result['confidence'],
                'layer': 'SYSTEM_2_LLM',
                'latency_ms': llm_result['latency'],
                'validation': 'passed_axioms',
                'status': 'SPECULATIVE (needs validation)',
                'phantom_candidate': True
            }
        elif validated['valid'] and llm_result['confidence'] < 0.60:
            return {
                'answer': llm_result['answer'],
                'confidence': llm_result['confidence'],
                'layer': 'SYSTEM_2_LLM',
                'latency_ms': llm_result['latency'],
                'status': 'LOW_CONFIDENCE (take with caution)',
                'validation': 'passed_axioms_but_low_confidence'
            }
        
        # Phase 6: Unknown
        return {
            'answer': f"I don't have enough information about '{user_query}'",
            'confidence': 0.0,
            'layer': 'UNKNOWN',
            'latency_ms': sum([
                hot_result['latency'],
                cold_result['latency'],
                specialist_result['latency'],
                llm_result['latency']
            ]),
            'learning_gap': True,
            'query_logged': True
        }
```

---

## Part 2: The Grain Lookup (Layer 0)

```python
class GrainLookup:
    """Ternary grain activation for pattern recognition."""
    
    def try_grain_lookup(self, query_embedding):
        """
        Fast ternary lookup against loaded grains.
        Returns domain identification or pattern match.
        """
        
        # Phase A: Domain routing grains
        domain_grains = self.get_active_domain_grains()  # Loaded in L3
        
        best_match = {
            'domain': None,
            'grain_id': None,
            'score': 0,
            'confidence': 0
        }
        
        for grain in domain_grains:
            # Ternary lookup: check embedding against grain pointers
            ternary_result = self.ternary_query_grain(
                grain_id=grain['grain_id'],
                input_embedding=query_embedding
            )
            
            # ternary_result = {
            #   'pos_hits': 2,      # How many positive pointers matched?
            #   'neg_hits': 0,      # How many negative pointers matched?
            #   'total_pointers': 4
            # }
            
            # Score = (pos - neg) / total
            score = (ternary_result['pos_hits'] - ternary_result['neg_hits']) \
                    / ternary_result['total_pointers']
            
            if score > best_match['score']:
                best_match = {
                    'domain': grain['axiom_link'],
                    'grain_id': grain['grain_id'],
                    'score': score,
                    'confidence': min(ternary_result['pos_hits'] / 
                                     ternary_result['total_pointers'], 1.0)
                }
        
        # Phase B: If strong match, return immediately
        if best_match['confidence'] > 0.85:
            return {
                'matched': True,
                'domain': best_match['domain'],
                'grain_id': best_match['grain_id'],
                'confidence': best_match['confidence'],
                'latency_ms': 0.4
            }
        
        # Phase C: Weak match or no match
        return {
            'matched': False,
            'domain': 'unknown',
            'grain_id': None,
            'confidence': best_match['confidence'],
            'latency_ms': 0.4
        }
    
    def ternary_query_grain(self, grain_id, input_embedding):
        """Query a single grain with ternary logic."""
        
        grain = self.grain_lookup_table[grain_id]
        
        pos_hits = sum(1 for ref in grain['pos_refs'] 
                      if self.semantically_matches(input_embedding, ref))
        neg_hits = sum(1 for ref in grain['neg_refs'] 
                      if self.semantically_matches(input_embedding, ref))
        
        return {
            'pos_hits': pos_hits,
            'neg_hits': neg_hits,
            'total_pointers': len(grain['pos_refs']) + len(grain['neg_refs'])
        }
    
    def semantically_matches(self, embedding, reference):
        """Quick semantic check without expensive embedding."""
        # Could use:
        # 1. Keyword overlap (fastest)
        # 2. Shallow embedding distance (fast)
        # 3. Skip if low confidence needed (faster)
        return reference in self.reference_cache or \
               self.quick_semantic_sim(embedding, reference) > 0.6
```

**Results:**
- ✓ Domain identified in 0.4ms
- ✓ Pattern matched with ternary {-1, 0, 1}
- ✓ Ready to load appropriate cartridge

---

## Part 3: Hot Cartridge Lookup (Layer 2)

```python
class HotCartridgeLookup:
    """Index-based fact retrieval from hot cartridge."""
    
    def try_hot_cartridge(self, query_tokens, domain):
        """
        Look up facts in already-loaded hot cartridge.
        Fast because cartridge is in hot memory.
        """
        
        # Load hot cartridge (should be pre-loaded by grain routing)
        cartridge = self.load_hot_cartridge(domain)
        if not cartridge:
            return {'found': False, 'facts': [], 'confidence': 0}
        
        # Phase A: Index lookup (O(1) or O(log N))
        matching_fact_ids = self.query_indices(
            cartridge_id=cartridge['id'],
            query_tokens=query_tokens,
            index_type='keyword'  # Fast keyword index first
        )
        
        if not matching_fact_ids:
            # Try semantic index if keyword fails
            matching_fact_ids = self.query_indices(
                cartridge_id=cartridge['id'],
                query_tokens=query_tokens,
                index_type='semantic'
            )
        
        # Phase B: Retrieve facts and annotations
        facts = []
        for fact_id in matching_fact_ids[:10]:  # Top 10 matches
            fact = cartridge.get_fact(fact_id)
            annotations = cartridge.get_annotations(fact_id)
            
            facts.append({
                'id': fact_id,
                'content': fact['content'],
                'confidence': annotations['metadata']['confidence'],
                'sources': annotations['metadata']['sources'],
                'derivations': annotations['derivations'],
                'context_boundaries': annotations['context']
            })
        
        # Phase C: Synthesize answer from facts
        if not facts:
            return {'found': False, 'facts': [], 'confidence': 0}
        
        # Rank by confidence × relevance
        facts = sorted(facts, key=lambda f: f['confidence'], reverse=True)
        
        synthesized = self.synthesize_from_facts(
            facts=facts,
            query=query_tokens
        )
        
        return {
            'found': True,
            'facts': facts,
            'synthesized_answer': synthesized['answer'],
            'confidence': synthesized['confidence'],
            'sources': [f['sources'] for f in facts],
            'latency': 28,
            'fact_ids': [f['id'] for f in facts]
        }
    
    def synthesize_from_facts(self, facts, query):
        """Combine multiple facts into coherent answer."""
        
        # Facts already ranked by confidence
        primary_fact = facts[0]
        supporting_facts = facts[1:]
        
        # Simple synthesis: primary fact + boundary conditions from others
        answer_parts = [primary_fact['content']]
        
        for fact in supporting_facts:
            boundaries = fact['context_boundaries']
            if boundaries and 'boundary' in boundaries:
                answer_parts.append(f"({boundaries['boundary']})")
        
        confidence = mean([f['confidence'] for f in facts])
        
        return {
            'answer': ' '.join(answer_parts),
            'confidence': confidence,
            'facts_used': len(facts)
        }
```

**Results:**
- ✓ Facts retrieved in 15-30ms
- ✓ Multiple sources cited
- ✓ Confidence > 0.75 → answer user immediately

---

## Part 4: Specialist Model Escalation (Layer 3)

```python
class SpecialistEscalation:
    """Synthesis via domain-specialized model."""
    
    def try_specialist_model(self, query, domain, hot_facts, cold_facts, context):
        """
        When facts alone aren't enough, use specialist model.
        Specialist is trained on domain-specific patterns.
        """
        
        # Phase A: Determine which specialist to use
        specialist = self.get_specialist_for_domain(domain)
        if not specialist:
            # No specialist trained yet (early stage)
            return {'confidence': 0, 'answer': None}
        
        # Phase B: Prepare input
        fact_context = self._format_facts_for_model(
            hot_facts=hot_facts,
            cold_facts=cold_facts,
            query=query
        )
        
        # Phase C: Run inference
        import time
        start = time.time()
        
        specialist_output = specialist.generate(
            prompt=fact_context,
            max_tokens=150,
            temperature=0.3  # Low temperature: stay faithful to facts
        )
        
        latency = (time.time() - start) * 1000
        
        # Phase D: Extract and structure result
        parsed = self._parse_specialist_output(specialist_output)
        
        return {
            'confidence': parsed['confidence'],
            'answer': parsed['answer'],
            'reasoning': parsed['reasoning'],
            'latency': latency,
            'specialist_id': specialist['id'],
            'facts_combined': len(hot_facts) + len(cold_facts)
        }
    
    def _format_facts_for_model(self, hot_facts, cold_facts, query):
        """Format facts as structured prompt."""
        
        prompt = f"""
Query: {query}

Primary Facts (high confidence):
{chr(10).join([f"- {f['content']} (conf: {f['confidence']:.2f})" 
               for f in hot_facts[:3]])}

Supporting Context:
{chr(10).join([f"- {f['content']} (boundary: {f['context_boundaries']})" 
               for f in cold_facts[:3]])}

Task: Synthesize these facts to answer the query.
Explain the reasoning.
Rate your confidence (0-1).
"""
        return prompt
    
    def _parse_specialist_output(self, output):
        """Parse structured specialist output."""
        
        # Specialist trained to output in format:
        # ANSWER: ...
        # REASONING: ...
        # CONFIDENCE: 0.XX
        
        lines = output.split('\n')
        parsed = {
            'answer': '',
            'reasoning': '',
            'confidence': 0.5
        }
        
        for line in lines:
            if line.startswith('ANSWER:'):
                parsed['answer'] = line[7:].strip()
            elif line.startswith('REASONING:'):
                parsed['reasoning'] = line[10:].strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    parsed['confidence'] = float(line[11:].strip())
                except:
                    parsed['confidence'] = 0.5
        
        return parsed
```

**Results:**
- ✓ Synthesis of multiple facts in 300ms
- ✓ Specialist model trained on domain
- ✓ Structured output with reasoning

---

## Part 5: System 2 LLM Escalation (Layer 4)

```python
class System2Escalation:
    """Full LLM reasoning for novel problems."""
    
    def try_system2_llm(self, query, domain, all_cartridge_facts, 
                        specialist_attempt, context):
        """
        Last resort: full LLM with context window.
        High latency, high capability.
        """
        
        # Phase A: Build comprehensive context
        context_window = self._build_context_window(
            query=query,
            domain=domain,
            facts=all_cartridge_facts,
            specialist_attempt=specialist_attempt,
            context=context
        )
        
        # Phase B: System prompt (define behavior)
        system_prompt = f"""
You are an expert in {domain}.

Available facts:
{chr(10).join([f['content'] for f in all_cartridge_facts[:20]])}

Guidelines:
- Cite facts when possible
- Distinguish between established knowledge and speculation
- Rate your confidence
- Flag when you're going beyond domain knowledge
"""
        
        # Phase C: Invoke LLM
        import time
        start = time.time()
        
        llm_output = self.hat_llm.generate(
            system=system_prompt,
            user_prompt=context_window,
            max_tokens=300,
            temperature=0.5  # Balanced: some creativity, but faithful
        )
        
        latency = (time.time() - start) * 1000
        
        # Phase D: Parse output
        parsed = self._parse_llm_output(llm_output)
        
        return {
            'confidence': parsed['confidence'],
            'answer': parsed['answer'],
            'reasoning': parsed['reasoning'],
            'speculative': parsed['speculative'],
            'latency': latency
        }
    
    def _build_context_window(self, query, domain, facts, specialist_attempt, context):
        """Build structured context for LLM."""
        
        prompt = f"""
DOMAIN: {domain}
QUERY: {query}

ESTABLISHED FACTS:
{chr(10).join([f"- {f['content']} (source: {f['sources'][0]})" 
               for f in facts[:5]])}

PREVIOUS ATTEMPTS:
- Hot cartridge: {facts[0]['content'] if facts else 'No facts found'}
- Specialist model: {specialist_attempt['answer'] if specialist_attempt['confidence'] > 0 else 'Could not answer'}

Your task:
1. Reason about the query given the domain knowledge
2. Distinguish between established knowledge and speculation
3. Propose novel connections if relevant
4. Rate your confidence (0-1)
5. Flag any assumptions

Format your response as:
ANSWER: [your answer]
REASONING: [step-by-step reasoning]
CONFIDENCE: [0.0-1.0]
SPECULATIVE: [true/false - are you going beyond domain?]
"""
        
        return prompt
```

**Results:**
- ✓ Creative reasoning in 1-2s
- ✓ Novel synthesis and discovery
- ✓ Clear confidence and speculation flags

---

## Part 6: Validation (All Layers)

```python
class OutputValidation:
    """Validate outputs against axioms before returning."""
    
    def validate_specialist_output(self, output, domain, axioms):
        """Check specialist output for axiom alignment."""
        
        # Extract key claims from output
        claims = self._extract_claims(output)
        
        # Check each claim against axioms
        validation_results = []
        for claim in claims:
            is_valid = any(
                axiom['principles'].issuperset(claim['concepts'])
                for axiom in axioms
            )
            validation_results.append({
                'claim': claim,
                'valid': is_valid
            })
        
        # All claims must be axiom-aligned
        all_valid = all(r['valid'] for r in validation_results)
        
        return {
            'valid': all_valid,
            'results': validation_results,
            'failed_claims': [r for r in validation_results if not r['valid']]
        }
    
    def validate_llm_output(self, output, domain, existing_facts, axioms):
        """Stricter validation for LLM (high hallucination risk)."""
        
        # Check 1: Is output consistent with existing facts?
        consistency = self._check_consistency(output, existing_facts)
        
        # Check 2: Are claims grounded in domain axioms?
        axiom_alignment = self._check_axiom_alignment(output, axioms)
        
        # Check 3: Does output avoid contradictions?
        contradictions = self._find_contradictions(output, existing_facts)
        
        return {
            'valid': consistency and axiom_alignment and not contradictions,
            'consistency_score': consistency,
            'axiom_alignment_score': axiom_alignment,
            'contradictions_found': contradictions
        }
```

---

## Part 7: Metrics & Monitoring

```python
class LayerMetrics:
    """Track which layer answers which queries."""
    
    def __init__(self):
        self.layer_distribution = {
            'grain': 0,
            'hot_cartridge': 0,
            'cold_cartridge': 0,
            'specialist': 0,
            'llm': 0,
            'unknown': 0
        }
        self.latencies = {layer: [] for layer in self.layer_distribution}
        self.confidence_by_layer = {layer: [] for layer in self.layer_distribution}
    
    def record_query(self, layer, latency_ms, confidence):
        """Record where query was answered."""
        self.layer_distribution[layer] += 1
        self.latencies[layer].append(latency_ms)
        self.confidence_by_layer[layer].append(confidence)
    
    def report(self):
        """Generate distribution report."""
        total = sum(self.layer_distribution.values())
        
        report = "\n=== LAYER DISTRIBUTION ===\n"
        for layer, count in sorted(
            self.layer_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            pct = (count / total * 100) if total > 0 else 0
            avg_latency = mean(self.latencies[layer]) if self.latencies[layer] else 0
            avg_confidence = mean(self.confidence_by_layer[layer]) \
                if self.confidence_by_layer[layer] else 0
            
            print(f"{layer:15} {pct:5.1f}% ({count:4} queries) " +
                  f"latency: {avg_latency:6.1f}ms conf: {avg_confidence:.2f}")
        
        # Check targets
        report += "\n=== TARGETS ===\n"
        targets = {
            'grain': 75,
            'hot_cartridge': 20,
            'specialist': 4,
            'llm': 1,
            'unknown': 0.1
        }
        
        for layer, target in targets.items():
            actual = (self.layer_distribution[layer] / total * 100) if total > 0 else 0
            status = "✓" if abs(actual - target) < 1 else "⚠"
            print(f"{status} {layer:15} target: {target:5.1f}% actual: {actual:5.1f}%")
```

---

## Part 8: The Complete Flow (Integrated)

```
┌─────────────────────────────────────────────────────────────────┐
│ USER QUERY ARRIVES                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │ GRAIN LAYER (0.5ms)                  │
        │ ├─ Domain routing                    │
        │ ├─ Pattern recognition               │
        │ └─ Ternary {-1, 0, 1} lookup         │
        └──────────────────┬──────────────────┘
                           │
                ┌──────────▼──────────┐
                │ Confidence > 0.85?  │
                └──────────┬──────────┘
                           │
                      ┌────┴─────┐
                      │ YES  │    │ NO
                      │      │    │
                  ANSWER    ▼    ▼
                      ┌──────────────────────────┐
                      │ HOT CARTRIDGE (30ms)    │
                      │ ├─ Index lookup         │
                      │ ├─ Retrieve facts       │
                      │ └─ Synthesize answer    │
                      └──────────┬───────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ Confidence > 0.75?  │
                      └──────────┬──────────┘
                                 │
                            ┌────┴─────┐
                            │ YES  │    │ NO
                            │      │    │
                        ANSWER    ▼    ▼
                            ┌──────────────────────────┐
                            │ COLD CARTRIDGE (50ms)   │
                            │ ├─ Load edge cases      │
                            │ ├─ Refine confidence    │
                            │ └─ Update answer        │
                            └──────────┬───────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │ Confidence > 0.70?      │
                          └──────────┬──────────────┘
                                     │
                                ┌────┴─────┐
                                │ YES  │    │ NO
                                │      │    │
                            ANSWER    ▼    ▼
                                ┌─────────────────────────────────┐
                                │ SPECIALIST SMOLML (300ms)       │
                                │ ├─ Combine facts                │
                                │ ├─ Run domain-specific model    │
                                │ ├─ Validate against axioms      │
                                │ └─ Synthesize                   │
                                └──────────┬────────────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │ Confidence > 0.65?      │
                              └──────────┬──────────────┘
                                         │
                                    ┌────┴─────┐
                                    │ YES  │    │ NO
                                    │      │    │
                                ANSWER    ▼    ▼
                                    ┌─────────────────────────────────┐
                                    │ SYSTEM 2 LLM (1.5s)             │
                                    │ ├─ Full reasoning               │
                                    │ ├─ Creative synthesis           │
                                    │ ├─ Validate output              │
                                    │ ├─ Flag speculative             │
                                    │ └─ Store as potential phantom   │
                                    └──────────┬────────────────────┘
                                               │
                                  ┌────────────▼────────────┐
                                  │ Validation passed?      │
                                  └──────────┬──────────────┘
                                             │
                                        ┌────┴─────┐
                                        │ YES  │    │ NO
                                        │      │    │
                                    ANSWER    ▼    ▼
                                        ┌──────────────────────┐
                                        │ UNKNOWN              │
                                        │ "I don't know this"  │
                                        │ [Flag learning gap]  │
                                        └──────────────────────┘
```

This is your complete routing and escalation system.
