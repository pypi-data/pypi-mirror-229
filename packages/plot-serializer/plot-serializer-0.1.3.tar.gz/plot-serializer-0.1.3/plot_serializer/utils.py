from importlib import resources as impresources
from plot_serializer import ontologies
from rdflib import Graph


def unit_in_ontology(unit_name, ontology_path="default"):
    if ontology_path == "default":
        ontology_path = impresources.files(ontologies) / "om-2.0.rdf"
    g = Graph()

    g.parse(ontology_path, format="xml")

    query = (
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?unit
        WHERE{
        ?unit a om:Unit ;
                rdfs:label "%s"@en .
        }
        """
        % unit_name
    )

    results = g.query(query)

    return len(results)
