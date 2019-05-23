from lidl.Mapping import parse_mappings
from lidl.Layout import create_element, AttributeScope
from lidl.Interpreter import interprete
from rdflib import Graph, URIRef

if __name__ == '__main__':
    graph = Graph()
    graph.parse("test.ttl", format="turtle")
    focusNode = URIRef("http://ppm.example.com/ns#ImageLayout")
    testLayout = create_element(focusNode, graph)

    testLayout.compute_static()
    testLayout.build_attribute_scope(AttributeScope())
    mappings = parse_mappings(graph)
    blob = bytes(1792)
    interprete(blob, testLayout, mappings)
    print(testLayout)