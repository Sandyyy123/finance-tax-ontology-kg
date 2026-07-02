# finance-tax-ontology-kg

A compact, runnable demo of a **Finance / Tax knowledge-graph** pipeline built on
the semantic-web stack: **RDF / OWL / SPARQL / SHACL** with **rdflib**, **spaCy**
and **NetworkX**. Written as a working reference for an ontology-engineering
engagement in the Finance & Tax domain.

## What it shows

| Stage | File | Semantic-web concept |
|-------|------|----------------------|
| 1. Ontology + taxonomy | `ontology.py` | OWL classes/properties, RDFS subclass axioms, a tax-classification taxonomy |
| 1b. Data quality | `ontology.py` | **SHACL** node shapes (every `Transaction` needs an amount + tax classification) |
| 2. Concept extraction | `extract.py` | spaCy NER → candidate ontology individuals (LLM-assisted ontology generation hook) |
| 3. Query + analytics | `query.py` | **SPARQL** SELECT over RDF, plus a **NetworkX** projection for graph analytics / Neo4j-style traversal |
| End-to-end | `main.py` | runs all stages |

## Run

```bash
pip install -r requirements.txt
python main.py
```

The extraction step uses spaCy `en_core_web_sm` when present and falls back to a
regex tagger otherwise, so the demo runs with zero extra downloads.

## Architecture

```
   regulatory text
        │  spaCy NER  (extract.py)
        ▼
  candidate individuals ──►  OWL ontology + taxonomy  (ontology.py)
                                   │
                     ┌─────────────┼──────────────┐
                     ▼             ▼              ▼
                SHACL shapes   SPARQL queries   NetworkX / Neo4j
                (validation)   (query.py)       projection
```

## Notes

- OWL/SHACL are authored directly against the RDF graph (no GUI), the same
  discipline used with Protégé or GraphDB.
- The NetworkX projection is the bridge to a property-graph store (Neo4j) for
  analytics that are awkward in pure SPARQL.
- Extend `LABEL_TO_CLASS` in `extract.py` to grow the extraction vocabulary as
  the ontology evolves.

Dr. Sandeep Grover — knowledge graphs, Python semantic stack, LLM-assisted
ontology generation.
