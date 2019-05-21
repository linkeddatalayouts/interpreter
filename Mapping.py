from enum import Enum
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL

from Layout import LidlElement, get_element, create_element_with_type

from NamespaceDefinitions import *


class TermType(Enum):
    IRI = 1
    BLANKNODE = 2
    ERROR = 3


class LogicalSource(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.source = None
        self.layout = None
        self.layout_uri = None

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        self.source = graph.value(focus_node, RDFNS.RML.source)
        self.layout_uri = graph.value(focus_node, RDFNS.RML.referenceFormulation)
        self.layout = get_element(self.layout_uri)


class SubjectMap(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.term_type = None
        self.rdf_class = None

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        term_type_node = graph.value(focus_node, RDFNS.R2RML.termType)
        if term_type_node == RDFNS.R2RML.IRI:
            self.term_type = TermType.IRI
        elif term_type_node == RDFNS.R2RML.BlankNode:
            self.term_type = TermType.BLANKNODE

        self.rdf_class = graph.value(focus_node, RDFNS.R2RML.rrClass)


class PredicateObjectMap(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.predicate = None
        self.object_map = None

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        self.predicate = graph.value(focus_node, RDFNS.R2RML.predicate)
        object_map_node = graph.value(focus_node, RDFNS.R2RML.objectMap)
        self.object_map = create_element_with_type(ObjectMap, object_map_node, graph)


class ObjectMap(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.reference = None
        self.reference_attribute = None
        self.constant = None
        self.term_type = None

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        term_type_node = graph.value(focus_node, RDFNS.R2RML.termType)
        if term_type_node == RDFNS.R2RML.IRI:
            self.term_type = TermType.IRI
        elif term_type_node == RDFNS.R2RML.BlankNode:
            self.term_type = TermType.BLANKNODE

        reference_node = graph.value(focus_node, RDFNS.RML.reference)
        constant_node  = graph.value(focus_node, RDFNS.R2RML.constant)

        if reference_node is not None:
            self.reference = reference_node
            self.reference_attribute = get_element(self.reference)
        elif constant_node is not None:
            self.constant = constant_node
        else:
            raise Exception("object map without reference or constant: " + str(focus_node))


class Mapping(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.logical_source = None
        self.subject_map = None
        self.predicate_object_map = []

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        logical_source_node = graph.value(focus_node, RDFNS.RML.logicalSource)
        subject_map_node = graph.value(focus_node, RDFNS.R2RML.subjectMap)
        predicate_object_map_nodes = list(graph.objects(focus_node,RDFNS.R2RML.predicateObjectMap))

        self.check_rdf_constraints(focus_node, logical_source_node, predicate_object_map_nodes, subject_map_node)

        self.logical_source = create_element_with_type(LogicalSource, logical_source_node, graph)
        self.subject_map = create_element_with_type(SubjectMap, subject_map_node, graph)

        for po_map_node in predicate_object_map_nodes:
            self.predicate_object_map.append(create_element_with_type(PredicateObjectMap, po_map_node , graph))

    @staticmethod
    def check_rdf_constraints(focus_node, logical_source_node, predicate_object_map_nodes, subject_map_node):
        if logical_source_node is None:
            raise Exception("mapping without logical source: " + str(focus_node))
        if subject_map_node is None:
            raise Exception("mapping without subject map: " + str(focus_node))
        if len(predicate_object_map_nodes) == 0:
            raise Exception("mapping without predicate object map: " + str(focus_node))


def parse_mappings(graph):
    mapping_list = []
    for s, o, p in graph.triples((None, RDFNS.RML.logicalSource, None)):
        if (s, RDFNS.R2RML.subjectMap, None ) not in graph:
            continue
        if (s, RDFNS.R2RML.predicateObjectMap, None ) not in graph:
            continue

        mapping_list.append(create_element_with_type(Mapping,s,graph))

    return mapping_list

