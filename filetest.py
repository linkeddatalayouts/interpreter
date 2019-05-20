from Layout import *


from rdflib import Graph, URIRef

if __name__ == '__main__':
    graph = Graph()
    graph.parse("test.ttl", format="turtle")
    focusNode = URIRef("http://ppm.example.com/ns#ImageLayout")
    testLayout = create_element(focusNode, graph)

    testLayout.compute_static()
    print(testLayout)