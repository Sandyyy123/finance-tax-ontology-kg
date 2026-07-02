"""
Build a small Finance/Tax ontology in OWL using rdflib, plus SHACL shapes.

Demonstrates the semantic-web core of the role:
  - RDF/OWL class + property modelling (rdflib.Namespace, OWL.Class, RDFS)
  - a business taxonomy for tax classifications / regulatory concepts
  - SHACL node shapes for data-quality / consistency validation

Run:  python ontology.py  ->  writes finance_tax.ttl and shapes.ttl
"""
from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD

FT = Namespace("https://example.org/fin-tax#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def build_ontology() -> Graph:
    """Model financial entities, tax classifications and regulatory concepts."""
    g = Graph()
    g.bind("ft", FT)
    g.bind("owl", OWL)

    g.add((FT.Ontology, RDF.type, OWL.Ontology))
    RDFS.label  # keep import used

    # --- Classes (the taxonomy) ---------------------------------------
    classes = {
        "FinancialEntity": "Any legal or natural entity with financial obligations.",
        "LegalEntity": "An incorporated organisation.",
        "NaturalPerson": "An individual taxpayer.",
        "TaxClassification": "A category under a tax code.",
        "VATCategory": "Value-added-tax rate class (standard/reduced/exempt).",
        "RegulatoryConcept": "A concept defined by a regulation (e.g. IFRS, MiFID II).",
        "Transaction": "A financial event with tax consequences.",
        "TaxObligation": "A duty to remit tax arising from a transaction.",
    }
    for name, comment in classes.items():
        c = FT[name]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.label, Literal(name)))
        g.add((c, RDFS.comment, Literal(comment)))

    # subclass axioms
    g.add((FT.LegalEntity, RDFS.subClassOf, FT.FinancialEntity))
    g.add((FT.NaturalPerson, RDFS.subClassOf, FT.FinancialEntity))
    g.add((FT.VATCategory, RDFS.subClassOf, FT.TaxClassification))

    # --- Object / datatype properties ---------------------------------
    g.add((FT.hasTaxClassification, RDF.type, OWL.ObjectProperty))
    g.add((FT.hasTaxClassification, RDFS.domain, FT.Transaction))
    g.add((FT.hasTaxClassification, RDFS.range, FT.TaxClassification))

    g.add((FT.governedBy, RDF.type, OWL.ObjectProperty))
    g.add((FT.governedBy, RDFS.domain, FT.TaxClassification))
    g.add((FT.governedBy, RDFS.range, FT.RegulatoryConcept))

    g.add((FT.incursObligation, RDF.type, OWL.ObjectProperty))
    g.add((FT.incursObligation, RDFS.domain, FT.Transaction))
    g.add((FT.incursObligation, RDFS.range, FT.TaxObligation))

    g.add((FT.amount, RDF.type, OWL.DatatypeProperty))
    g.add((FT.amount, RDFS.domain, FT.Transaction))
    g.add((FT.amount, RDFS.range, XSD.decimal))

    g.add((FT.ratePercent, RDF.type, OWL.DatatypeProperty))
    g.add((FT.ratePercent, RDFS.domain, FT.VATCategory))
    g.add((FT.ratePercent, RDFS.range, XSD.decimal))

    # --- A couple of individuals (the reference data) -----------------
    g.add((FT.VAT_Standard_DE, RDF.type, FT.VATCategory))
    g.add((FT.VAT_Standard_DE, FT.ratePercent, Literal("19.0", datatype=XSD.decimal)))
    g.add((FT.VAT_Reduced_DE, RDF.type, FT.VATCategory))
    g.add((FT.VAT_Reduced_DE, FT.ratePercent, Literal("7.0", datatype=XSD.decimal)))
    return g


def build_shapes() -> Graph:
    """SHACL shapes: every Transaction needs an amount and a tax classification."""
    g = Graph()
    g.bind("sh", SH)
    g.bind("ft", FT)

    shape = FT.TransactionShape
    g.add((shape, RDF.type, SH.NodeShape))
    g.add((shape, SH.targetClass, FT.Transaction))

    amt = FT._amountProp
    g.add((shape, SH.property, amt))
    g.add((amt, SH.path, FT.amount))
    g.add((amt, SH.datatype, XSD.decimal))
    g.add((amt, SH.minCount, Literal(1)))

    cls = FT._classProp
    g.add((shape, SH.property, cls))
    g.add((cls, SH.path, FT.hasTaxClassification))
    g.add((cls, SH.minCount, Literal(1)))
    g.add((cls, SH.message, Literal("Every transaction must carry a tax classification.")))
    return g


if __name__ == "__main__":
    onto = build_ontology()
    shapes = build_shapes()
    onto.serialize("finance_tax.ttl", format="turtle")
    shapes.serialize("shapes.ttl", format="turtle")
    print(f"Ontology: {len(onto)} triples -> finance_tax.ttl")
    print(f"SHACL shapes: {len(shapes)} triples -> shapes.ttl")
