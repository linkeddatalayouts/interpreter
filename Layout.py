from uuid import uuid4
from enum import Enum
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL

from NamespaceDefinitions import *


class Endianness(Enum):
    LITTLE_ENDIAN = 1
    MIDDLE_ENDIAN = 2
    BIG_ENDIAN = 3
    UNDEFINED_ENDIAN = 4


createdElements = dict()


def remove_literal(type, literal):
    if literal is None:
        return None
    return type(literal)


def get_expression_type(focus_node, graph):
    # hardcoded at the moment, but should be dynamic in the future with linked service calls
    for s, p, o in graph.triples((focus_node, None, None)):
        if p == RDFNS.LIDL.eval:
            pass  # return ExpressionEval
        elif p == RDFNS.LIDL.add:
            return ExpressionAdd
        elif p == RDFNS.LIDL.minus:
            return ExpressionMinus
        elif p == RDFNS.LIDL.mul:
            return ExpressionMul
        elif p == RDFNS.LIDL.div:
            pass  # return ExpressionDiv
        elif p == RDFNS.LIDL.mod:
            pass  # return ExpressionMod
        elif p == RDFNS.LIDL.exp:
            pass  # return ExpressionExp
        elif p == RDFNS.LIDL.le:
            pass  # return ExpressionLess
        elif p == RDFNS.LIDL.leq:
            pass  # return ExpressionLessOrEqual
        elif p == RDFNS.LIDL.eq:
            pass  # return ExpressionEqual
        elif p == RDFNS.LIDL.neq:
            pass  # return ExpressionNotEqual
        elif p == RDFNS.LIDL.gr:
            pass  # return ExpressionGreater
        elif p == RDFNS.LIDL.geq:
            pass  # return ExpressionGreaterOrEqual
        elif p == RDFNS.LIDL.leftBitShift:
            pass  # return ExpressionLeftBitShift
        elif p == RDFNS.LIDL.rightBitShift:
            pass  # return ExpressionRightBitShift
        elif p == RDFNS.LIDL.bitwiseAND:
            pass  # return ExpressionBitwiseAND
        elif p == RDFNS.LIDL.bitwiseOR:
            pass  # return ExpressionBitwiseOr
        elif p == RDFNS.LIDL.bitwiseXOR:
            pass  # return ExpressionBitwiseXOr
        elif p == RDFNS.LIDL.AND:
            pass  # return ExpressionAND
        elif p == RDFNS.LIDL.OR:
            pass  # return ExpressionNOT
        elif p == RDFNS.LIDL.OR:
            pass  # return ExpressionNOT

        return None


def create_element(focus_node, graph, assumed_types=None):
    types = list(graph.objects(focus_node, RDF.type))
    found_type = None

    if RDFNS.LIDL.Composite in types:
        found_type = CompositeLayout
    elif RDFNS.LIDL.Atomic in types:
        found_type = AtomicLayout
    elif RDFNS.LIDL.Attribute in types:
        found_type = Attribute
    else:
        found_type = get_expression_type(focus_node, graph)
        if found_type is None:
            print("unknown types: " + str(types))
            return
    # if assumed_types and found_type not in assumed_types:
    #    raise Exception('found type: {0} , but not in list of assumed types'.format(str(found_type)))

    return create_element_with_type(found_type, focus_node, graph)


def create_element_with_type(element_class, focus_node, graph):
    if str(focus_node) in createdElements:
        return createdElements[str(focus_node)]

    element = element_class(focus_node)
    createdElements[str(focus_node)] = element

    element.from_rdf(focus_node, graph)

    return element


all_lidl_elements = dict()


def get_element(uri_ref):
    if uri_ref in all_lidl_elements:
        return all_lidl_elements[uri_ref]

    return None

class LidlElement(object):
    def __init__(self, rdf_node):
        object.__init__(self)
        self.uuid = uuid4()
        self.rdf_node = rdf_node
        self.label = None
        all_lidl_elements[rdf_node] = self

    def from_rdf(self, focus_node, graph):
        self.label = graph.value(focus_node, RDFS.label)


class Layout(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.endianness = Endianness.UNDEFINED_ENDIAN
        self.uri = 0

        self.staticBitSize = None
        self.staticByteSize = None
        self.static = None

    def from_rdf(self, focus_node, graph):
        super(Layout, self).from_rdf(focus_node, graph)

        self.rdf_node = focus_node
        if (focus_node, RDFNS.LIDL.endianness, RDFNS.LIDL.LittleEndian) in graph:
            self.endianness = Endianness.LITTLE_ENDIAN
        elif (focus_node, RDFNS.LIDL.endianness, RDFNS.LIDL.BigEndian) in graph:
            self.endianness = Endianness.BIG_ENDIAN
        elif (focus_node, RDFNS.LIDL.endianness, RDFNS.LIDL.MiddleEndian) in graph:
            raise NotImplementedError("MiddleEndian is not supported")

    def compute_static(self):
        raise Exception("you cannot do a static check on an untyped layout")


class AtomicLayout(Layout):
    def __init__(self, rdf_node):
        Layout.__init__(self, rdf_node)
        self.bitSize = None
        self.byteSize = None
        self.xsdType = None

    def from_rdf(self, focus_node, graph):
        super(Layout, self).from_rdf(focus_node, graph)

        self.bitSize  = remove_literal(int, graph.value(focus_node, RDFNS.LIDL.bitSize))
        self.byteSize = remove_literal(int, graph.value(focus_node, RDFNS.LIDL.byteSize))
        self.xsdType  =                     graph.value(focus_node, RDFNS.LIDL.datatype)

        if self.bitSize is None and self.byteSize is None:
            raise Exception("Atomic without any size specification: " + self.label + " " + self.uri)

        if self.bitSize is None:
            self.bitSize = 8 * self.byteSize

        if self.bitSize == 0:
            raise Exception("Atomic with size ZERO: " + self.label + " " + self.uri)

        if self.byteSize is None:
            if (self.bitSize % 8) == 0:
                self.byteSize = self.bitSize / self.byteSize

        self.staticBitSize = self.bitSize
        self.staticByteSize = self.byteSize

    def compute_static(self):
        self.static = True
        return True


class Attribute(LidlElement):
    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.order = None
        self.predicate = None
        self.count_node = None
        self.count = None
        self.layout_nodes = []
        self.layouts = []
        self.value = None
        self.value_node = None
        self.static = None

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        self.order       = graph.value(focus_node, RDFNS.LIDL.order)
        self.predicate   = graph.value(focus_node, RDFNS.LIDL.predicate)
        self.count_node  = graph.value(focus_node, RDFNS.LIDL.count)
        self.value_node   = graph.value(focus_node, RDFNS.LIDL.value)
        self.layout_nodes = list(graph.objects(focus_node, RDFNS.LIDL.layout))

        if type(self.count_node) is Literal:
            self.count = remove_literal(int, self.count_node)
        else:
            self.count = create_element(self.count_node, graph)

        if type(self.value_node) is Literal:
            self.value = self.value_node #todo this is not correct...
        elif self.value_node is not None:
            self.value = create_element(self.value_node, graph)

        for layout_node in self.layout_nodes:
            self.layouts.append(create_element(layout_node, graph))

    def compute_static(self):
        if self.static is not None:
            return self.static

        self.static = self.count is not None and (type(self.count_node) is Literal or self.count.compute_static())

        for layout in self.layouts:
            self.static &=  layout.compute_static() and self.static \
                                                   and layout.staticBitSize == self.layouts[0].staticBitSize \
                                                   and layout.staticByteSize == self.layouts[0].staticByteSize

        return self.static


class CompositeLayout(Layout):
    def __init__(self, rdf_node):
        Layout.__init__(self, rdf_node)
        self.attributeNodes = []
        self.ordered_attributes = []
        self.unordered_attributes = []

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)

        self.attributeNodes = list(graph.objects(focus_node, RDFNS.LIDL.attribute))

        for attribute_node in self.attributeNodes:
            attribute = create_element(attribute_node, graph, [Attribute])
            if attribute.order is not None:
                self.ordered_attributes.append(attribute)
            else:
                self.unordered_attributes.append(attribute)

        self.ordered_attributes.sort(key=lambda attr: attr.order)

    def compute_static(self):
        if self.static is not None:
            return self.static

        self.static = True
        for attribute in self.ordered_attributes:
            self.static &= attribute.compute_static()

        if self.static:
            self.staticByteSize = 0
            self.staticBitSize = 0
            for attribute in self.ordered_attributes:
                attribute_layout = attribute.layouts[0]
                self.staticBitSize += attribute_layout.staticBitSize * attribute.count
                self.staticByteSize += attribute_layout.staticByteSize * attribute.count

        return self.static


class Expression(LidlElement):
    rdf_property = None
    min_args = 0
    max_args = 1000

    def __init__(self, rdf_node):
        LidlElement.__init__(self, rdf_node)
        self.argument_nodes = []
        self.arguments = []

    def from_rdf(self, focus_node, graph):
        LidlElement.from_rdf(self, focus_node, graph)
        self.parse_argument_list(focus_node, graph)
        self.check_argument_constraints()

    def check_argument_constraints(self):
        arg_count = len(self.arguments)
        min_args = type(self).min_args
        if arg_count < min_args:
            raise Exception("minus expression in: " + self.__class__.__name_ +
                            " violating min_args of: " + str(min_args) +
                            " with argument count of: " + str(arg_count))

        max_args = type(self).max_args
        if arg_count > max_args:
            raise Exception("minus expression in: " + self.__class__.__name_ +
                            " violating max_args of: " + str(max_args) +
                            " with argument count of: " + str(arg_count))

    def parse_argument_list(self, focus_node,graph):
        current_list_node = graph.value(focus_node, self.rdf_property)

        while current_list_node != RDF.nil:
            first_node = graph.value(current_list_node, RDF.first)
            rest_node = graph.value(current_list_node, RDF.rest)

            self.argument_nodes.append(first_node)
            current_list_node = rest_node

        for num, argument_node in enumerate(self.argument_nodes):
            if type(argument_node) is Literal:
                self.arguments.append(remove_literal(int, argument_node))
                self.argument_nodes[num] = None
            else:
                argument = create_element(argument_node, graph, [Expression, Attribute])
                if argument is None:
                    raise Exception("found invalid argument at position: " + num + " in:" + str(focus_node))
                self.arguments.append(argument)

    def compute_static(self):
        return False #todo think about that


class ExpressionAdd(Expression):
    rdf_property = RDFNS.LIDL.add
    min_args = 2

    def __init__(self, rdf_node):
        Expression.__init__(self, rdf_node)

    def from_rdf(self, focus_node, graph):
        Expression.from_rdf(self, focus_node, graph)

    def compute(self, instance):
        pass


class ExpressionMinus(Expression):
    rdf_property = RDFNS.LIDL.minus
    min_args = 2
    max_args = 2

    def __init__(self, rdf_node):
        Expression.__init__(self, rdf_node)

    def from_rdf(self, focus_node, graph):
        Expression.from_rdf(self, focus_node, graph)

        if self.arguments.len() > 2:
            raise Exception("Minus Expression takes only 2 arguments")

    def compute(self, instance):
        pass


class ExpressionMul(Expression):
    rdf_property = RDFNS.LIDL.mul
    min_args = 2

    def __init__(self, rdf_node):
        Expression.__init__(self, rdf_node)

    def compute(self, instance):
        pass
