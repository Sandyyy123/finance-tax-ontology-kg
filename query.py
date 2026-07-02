"""
SPARQL queries + NetworkX projection over the Finance/Tax graph.

Shows the two ways the client will consume the graph:
  1. SPARQL SELECT over the RDF (rdflib)
  2. a NetworkX projection for graph analytics / Neo4j-style traversal
"""
import networkx as nx
from rdflib import Graph, Namespace, RDF, RDFS

FT = Namespace("https://example.org/fin-tax#")

SPARQL_SUBCLASSES = """
PREFIX ft: <https://example.org/fin-tax#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?child ?parent WHERE { ?child rdfs:subClassOf ?parent . }
"""

SPARQL_VAT_RATES = """
PREFIX ft: <https://example.org/fin-tax#>
SELECT ?cat ?rate WHERE { ?cat ft:ratePercent ?rate . } ORDER BY DESC(?rate)
"""


def run_queries(ttl_path: str = "finance_tax.ttl"):
    g = Graph()
    g.parse(ttl_path, format="turtle")

    print("Taxonomy (subclass axioms):")
    for row in g.query(SPARQL_SUBCLASSES):
        print(f"  {row.child.split('#')[-1]} rdfs:subClassOf {row.parent.split('#')[-1]}")

    print("\nVAT categories by rate:")
    for row in g.query(SPARQL_VAT_RATES):
        print(f"  {row.cat.split('#')[-1]:<18} {row.rate}%")

    return g


def to_networkx(g: Graph) -> nx.DiGraph:
    """Project the RDF taxonomy into a NetworkX DiGraph for analytics."""
    G = nx.DiGraph()
    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        G.add_edge(child.split("#")[-1], parent.split("#")[-1], rel="subClassOf")
    return G


if __name__ == "__main__":
    g = run_queries()
    G = to_networkx(g)
    print(f"\nNetworkX projection: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    if G.number_of_nodes():
        root = [n for n in G if G.out_degree(n) == 0]
        print(f"  root class(es): {root}")
