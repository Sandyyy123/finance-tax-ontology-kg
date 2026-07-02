"""
Finance/Tax Knowledge Graph demo - end-to-end entry point.

Pipeline:
  1. build OWL ontology + SHACL shapes         (ontology.py)
  2. extract candidate individuals from text   (extract.py)
  3. query with SPARQL + project to NetworkX    (query.py)

Run:  python main.py
"""
from ontology import build_ontology, build_shapes
from extract import extract
from query import to_networkx, SPARQL_VAT_RATES


def main():
    print("=" * 60)
    print("FINANCE / TAX KNOWLEDGE GRAPH  -  demo pipeline")
    print("=" * 60)

    print("\n[1] Building OWL ontology + SHACL shapes ...")
    onto = build_ontology()
    shapes = build_shapes()
    onto.serialize("finance_tax.ttl", format="turtle")
    shapes.serialize("shapes.ttl", format="turtle")
    print(f"    ontology  = {len(onto)} triples")
    print(f"    shapes    = {len(shapes)} triples")

    print("\n[2] LLM/NLP concept extraction from regulatory text ...")
    text = ("Under the EU VAT Directive, Muster GmbH applied a reduced rate of "
            "7% to an invoice of €12,500, while IFRS 15 governed revenue.")
    for span, label, cls in extract(text):
        print(f"    {span:<18} [{label:<7}] -> ft:{cls}")

    print("\n[3] SPARQL over the graph ...")
    for row in onto.query(SPARQL_VAT_RATES):
        print(f"    {row.cat.split('#')[-1]:<18} {row.rate}%")

    G = to_networkx(onto)
    print(f"\n[4] NetworkX projection: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    print("\nDone.")


if __name__ == "__main__":
    main()
