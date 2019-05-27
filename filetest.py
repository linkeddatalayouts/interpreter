from lidl.Mapping import parse_mappings
from lidl.Layout import create_element
from lidl.Interpreter import interprete
from rdflib import Graph, URIRef

import struct

if __name__ == '__main__':
    graph = Graph()
    graph.parse("test.ttl", format="turtle")
    focusNode = URIRef("http://ppm.example.com/ns#ImageLayout")
    testLayout = create_element(focusNode, graph)

    testLayout.compute_static()
    testLayout.build_attribute_scope()
    testLayout.fill_scopes()
    mappings = parse_mappings(graph)
    blob = bytes(1792)

    imagesize = 4

    header = struct.pack('=ccIIB',b'P', b'6',4,4,255)
    blob = header
    pixel = struct.pack('=BBB',0,128,254)

    for i in range(imagesize*imagesize):
        blob += pixel

    result = interprete(blob, testLayout, mappings)
    print(result.serialize('output.ttl', format='turtle'))