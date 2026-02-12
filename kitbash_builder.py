"""
Kitbash CartridgeBuilder
Populates cartridges from various data formats

Supports:
- Markdown files (# heading = domain, ## heading = subdomain, list items = facts)
- CSV files (header row = metadata, one fact per row)
- JSON files (array of objects with content/metadata)
- Plain text files (one fact per line, optional metadata)
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from kitbash_cartridge import (
    Cartridge, AnnotationMetadata, EpistemicLevel,
    Derivation
)


class CartridgeBuilder:
    """Build and populate cartridges from various data sources."""
    
    def __init__(self, cartridge_name: str, cartridge_path: str = "./cartridges"):
        """
        Initialize builder (doesn't create cartridge yet).
        
        Args:
            cartridge_name: Name for the cartridge
            cartridge_path: Parent directory for cartridge files
        """
        self.cartridge_name = cartridge_name
        self.cartridge_path = cartridge_path
        self.cart = Cartridge(cartridge_name, cartridge_path)
        self.fact_count = 0
    
    def build(self) -> Cartridge:
        """Create the cartridge and return it."""
        self.cart.create()
        print(f"✓ Created cartridge: {self.cartridge_name}")
        return self.cart
    
    def save(self) -> None:
        """Save cartridge to disk."""
        self.cart.save()
        print(f"✓ Saved {self.fact_count} facts to {self.cartridge_name}")
    
    def load_cartridge(self) -> Cartridge:
        """Load existing cartridge."""
        self.cart.load()
        return self.cart
    
    # ========================================================================
    # MARKDOWN FORMAT
    # ========================================================================
    
    def from_markdown(self, filepath: str, 
                     domain_pattern: str = "#",
                     subdomain_pattern: str = "##",
                     fact_pattern: str = "-") -> None:
        """
        Load facts from markdown file.
        
        Format:
        # Domain Name
        ## Subdomain (optional)
        - Fact 1
        - Fact 2 | source | confidence
        
        Args:
            filepath: Path to markdown file
            domain_pattern: Marker for domain heading (default: #)
            subdomain_pattern: Marker for subdomain heading (default: ##)
            fact_pattern: Marker for facts (default: -)
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_domain = ""
        current_subdomains = []
        
        for line in lines:
            line = line.rstrip()
            
            # Check for domain heading
            if line.startswith(domain_pattern + " "):
                current_domain = line.lstrip(domain_pattern).strip()
                current_subdomains = []
                if self.cart.manifest:
                    if current_domain not in self.cart.manifest.get("domains", []):
                        self.cart.manifest.setdefault("domains", []).append(current_domain)
                continue
            
            # Check for subdomain heading
            if line.startswith(subdomain_pattern + " "):
                subdomain = line.lstrip(subdomain_pattern).strip()
                if subdomain not in current_subdomains:
                    current_subdomains.append(subdomain)
                continue
            
            # Check for fact
            if line.startswith(fact_pattern + " "):
                fact_text = line.lstrip(fact_pattern).strip()
                
                # Parse optional metadata: "fact | source | confidence"
                parts = [p.strip() for p in fact_text.split("|")]
                content = parts[0]
                source = parts[1] if len(parts) > 1 else "markdown"
                confidence = float(parts[2]) if len(parts) > 2 else 0.8
                
                # Create annotation
                ann = AnnotationMetadata(
                    fact_id=0,
                    confidence=confidence,
                    sources=[source],
                    context_domain=current_domain,
                    context_subdomains=current_subdomains,
                )
                
                self.cart.add_fact(content, ann)
                self.fact_count += 1
        
        print(f"✓ Loaded {self.fact_count} facts from {filepath}")
    
    # ========================================================================
    # CSV FORMAT
    # ========================================================================
    
    def from_csv(self, filepath: str, 
                domain_col: str = "domain",
                content_col: str = "content",
                confidence_col: Optional[str] = "confidence",
                source_col: Optional[str] = "source") -> None:
        """
        Load facts from CSV file.
        
        Expected columns:
        - content (required): fact text
        - domain (optional): domain name
        - confidence (optional): 0-1 value
        - source (optional): source reference
        - Any other columns treated as context tags
        
        Args:
            filepath: Path to CSV file
            domain_col: Column name for domain
            content_col: Column name for fact content
            confidence_col: Column name for confidence (optional)
            source_col: Column name for source (optional)
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if not row.get(content_col):
                    continue
                
                content = row[content_col].strip()
                domain = row.get(domain_col, "").strip() or "general"
                confidence = float(row.get(confidence_col, "0.8")) if confidence_col else 0.8
                source = row.get(source_col, "csv").strip()
                
                # Collect other columns as context tags
                context_tags = [
                    v.strip() for k, v in row.items()
                    if k not in [content_col, domain_col, confidence_col, source_col]
                    and v and v.strip()
                ]
                
                ann = AnnotationMetadata(
                    fact_id=0,
                    confidence=confidence,
                    sources=[source],
                    context_domain=domain,
                    context_applies_to=context_tags,
                )
                
                self.cart.add_fact(content, ann)
                self.fact_count += 1
        
        print(f"✓ Loaded {self.fact_count} facts from {filepath}")
    
    # ========================================================================
    # JSON FORMAT
    # ========================================================================
    
    def from_json(self, filepath: str,
                 content_key: str = "content",
                 metadata_key: Optional[str] = "metadata") -> None:
        """
        Load facts from JSON file.
        
        Format:
        [
            {
                "content": "fact text",
                "metadata": {
                    "confidence": 0.9,
                    "domain": "name",
                    "sources": ["source1"]
                }
            }
        ]
        
        Args:
            filepath: Path to JSON file
            content_key: Key containing fact text
            metadata_key: Key containing metadata dict (optional)
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and single object
        if isinstance(data, dict):
            data = [data]
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            content = item.get(content_key)
            if not content:
                continue
            
            # Parse metadata if present
            meta = item.get(metadata_key, {}) if metadata_key else {}
            confidence = meta.get("confidence", 0.8)
            domain = meta.get("domain", "general")
            sources = meta.get("sources", [])
            applies_to = meta.get("applies_to", [])
            excludes = meta.get("excludes", [])
            
            ann = AnnotationMetadata(
                fact_id=0,
                confidence=confidence,
                sources=sources if sources else ["json"],
                context_domain=domain,
                context_applies_to=applies_to,
                context_excludes=excludes,
            )
            
            self.cart.add_fact(content, ann)
            self.fact_count += 1
        
        print(f"✓ Loaded {self.fact_count} facts from {filepath}")
    
    # ========================================================================
    # PLAIN TEXT FORMAT
    # ========================================================================
    
    def from_text(self, filepath: str,
                 domain: str = "general",
                 confidence: float = 0.7,
                 one_fact_per_line: bool = True) -> None:
        """
        Load facts from plain text file.
        
        Simple format: one fact per line, or multiline sentences.
        
        Args:
            filepath: Path to text file
            domain: Domain to assign all facts
            confidence: Default confidence for all facts
            one_fact_per_line: If False, split on sentence boundaries
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if one_fact_per_line:
            lines = text.split('\n')
            facts = [line.strip() for line in lines if line.strip()]
        else:
            # Split on sentence boundaries
            facts = [s.strip() + "." for s in re.split(r'[.!?]+', text) if s.strip()]
        
        for fact in facts:
            if len(fact) > 10:  # Skip very short lines
                ann = AnnotationMetadata(
                    fact_id=0,
                    confidence=confidence,
                    sources=["text"],
                    context_domain=domain,
                )
                self.cart.add_fact(fact, ann)
                self.fact_count += 1
        
        print(f"✓ Loaded {self.fact_count} facts from {filepath}")
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def from_directory(self, dirpath: str,
                      pattern: str = "*",
                      auto_domain: bool = True) -> None:
        """
        Load facts from multiple files in a directory.
        Automatically detects format by extension.
        
        Args:
            dirpath: Directory path
            pattern: File pattern (default: all files)
            auto_domain: Use subdirectory names as domain (if True)
        """
        dirpath = Path(dirpath)
        if not dirpath.is_dir():
            raise NotADirectoryError(f"Not a directory: {dirpath}")
        
        files = list(dirpath.glob(pattern))
        for filepath in sorted(files):
            if filepath.is_file():
                domain = filepath.parent.name if auto_domain else None
                
                try:
                    if filepath.suffix == '.md':
                        self.from_markdown(str(filepath))
                    elif filepath.suffix == '.csv':
                        self.from_csv(str(filepath))
                    elif filepath.suffix == '.json':
                        self.from_json(str(filepath))
                    elif filepath.suffix == '.txt':
                        self.from_text(str(filepath), domain=domain or "general")
                except Exception as e:
                    print(f"⚠ Skipped {filepath}: {e}")
        
        print(f"✓ Processed {len(files)} files from {dirpath}")
    
    # ========================================================================
    # MANUAL OPERATIONS
    # ========================================================================
    
    def add_fact(self, content: str,
                domain: str = "general",
                confidence: float = 0.8,
                sources: Optional[List[str]] = None,
                context_tags: Optional[List[str]] = None) -> int:
        """
        Manually add a single fact.
        
        Args:
            content: Fact text
            domain: Domain/category
            confidence: 0-1 confidence score
            sources: List of sources
            context_tags: Tags describing where it applies
            
        Returns:
            fact_id
        """
        ann = AnnotationMetadata(
            fact_id=0,
            confidence=confidence,
            sources=sources or ["manual"],
            context_domain=domain,
            context_applies_to=context_tags or [],
        )
        
        fact_id = self.cart.add_fact(content, ann)
        self.fact_count += 1
        return fact_id
    
    def add_batch(self, facts: List[Tuple[str, str, float]],
                 domain: str = "general",
                 sources: Optional[List[str]] = None) -> List[int]:
        """
        Add multiple facts at once.
        
        Args:
            facts: List of (content, context_tag, confidence) tuples
            domain: Domain for all facts
            sources: Sources for all facts
            
        Returns:
            List of fact_ids
        """
        fact_ids = []
        for content, context_tag, confidence in facts:
            fact_id = self.add_fact(
                content,
                domain=domain,
                confidence=confidence,
                sources=sources,
                context_tags=[context_tag] if context_tag else None,
            )
            fact_ids.append(fact_id)
        return fact_ids
    
    # ========================================================================
    # MANIFEST UPDATES
    # ========================================================================
    
    def set_metadata(self, description: str = "",
                    domains: Optional[List[str]] = None,
                    tags: Optional[List[str]] = None,
                    author: str = "CartridgeBuilder") -> None:
        """
        Update cartridge manifest metadata.
        
        Args:
            description: Cartridge description
            domains: List of domains covered
            tags: List of tags
            author: Author name
        """
        if description:
            self.cart.manifest["description"] = description
        
        if domains:
            self.cart.manifest["domains"] = list(set(self.cart.manifest.get("domains", []) + domains))
        
        if tags:
            self.cart.manifest["tags"] = list(set(self.cart.manifest.get("tags", []) + tags))
        
        self.cart.manifest["author"] = author
    
    # ========================================================================
    # INTROSPECTION
    # ========================================================================
    
    def get_stats(self) -> Dict:
        """Get current builder stats."""
        return {
            "cartridge": self.cartridge_name,
            "facts_added": self.fact_count,
            "exists": self.cart.cartridge_dir.exists(),
        }


# ============================================================================
# EXAMPLE USAGE & PRESETS
# ============================================================================

def create_from_markdown_example():
    """Example: Create cartridge from markdown."""
    builder = CartridgeBuilder("example")
    builder.build()
    
    # Create a sample markdown file
    markdown = """
# Physics
## Thermodynamics
- Water boils at 100°C at sea level | Handbook_Physics | 0.99
- Temperature affects molecular motion | basic_science | 0.95
- Heat flows from hot to cold objects | Thermodynamics | 0.98

## Mechanics
- F = ma | Newton | 0.99
- Objects fall due to gravity | Observation | 0.95
"""
    
    with open("sample.md", "w") as f:
        f.write(markdown)
    
    builder.from_markdown("sample.md")
    builder.save()


def create_from_csv_example():
    """Example: Create cartridge from CSV."""
    import csv
    
    builder = CartridgeBuilder("example_csv")
    builder.build()
    
    # Create sample CSV
    with open("sample.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["content", "domain", "confidence", "source", "tags"])
        writer.writeheader()
        writer.writerow({
            "content": "PLA gels at 60°C",
            "domain": "bioplastics",
            "confidence": "0.92",
            "source": "Handbook_2023",
            "tags": "PLA,polymers"
        })
        writer.writerow({
            "content": "Synthetic polymers are stable",
            "domain": "materials",
            "confidence": "0.85",
            "source": "Research",
            "tags": "polymers,synthetic"
        })
    
    builder.from_csv("sample.csv", source_col="source")
    builder.save()


if __name__ == "__main__":
    print("Cartridge Builder Examples\n")
    
    # Example 1: Manual
    print("1. Manual fact addition:")
    builder = CartridgeBuilder("manual_example")
    builder.build()
    
    builder.add_fact("Water boils at 100°C", domain="physics", confidence=0.99)
    builder.add_fact("Gravity pulls downward", domain="physics", confidence=0.99)
    builder.add_fact("PLA requires 60°C for gelling", domain="bioplastics", confidence=0.92)
    
    builder.set_metadata(
        description="Basic physics and materials science",
        domains=["physics", "bioplastics"],
        tags=["temperature", "materials", "polymers"],
    )
    
    builder.save()
    print(f"Created: {builder.get_stats()}\n")
    
    # Example 2: From markdown
    print("2. From markdown:")
    markdown_content = """# Bioplastics
## PLA
- PLA requires 60°C ±5°C for optimal gelling | Handbook_2023 | 0.92
- Temperature affects polymer crystallinity | Research_2024 | 0.85

## General
- Synthetic polymers are more stable than natural ones | BasicScience | 0.9
"""
    
    with open("/tmp/test.md", "w") as f:
        f.write(markdown_content)
    
    builder2 = CartridgeBuilder("markdown_example")
    builder2.build()
    builder2.from_markdown("/tmp/test.md")
    builder2.save()
    print(f"Created: {builder2.get_stats()}\n")
    
    print("✓ Examples complete")
