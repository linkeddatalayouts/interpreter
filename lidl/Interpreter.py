from .Mapping import Mapping, SubjectMap, PredicateObjectMap, ObjectMap, TermType
from .Layout import CompositeLayout, AtomicLayout, Attribute, Expression
from rdflib import URIRef, Literal, Graph, Namespace, BNode
from rdflib.namespace import RDF, RDFS
from .NamespaceDefinitions import *
from uuid import uuid4

from enum import Enum
import struct
from .ValueInstance import *


class Evaluable(Enum):
    EVALUABLE = 1
    NOT_EVALUABLE = 2
    UNKNOWN = 3



def find_attribute_instance(layout_instance, attribute):
    attribute_scope = layout_instance.instance_of.attribute_scope
    attribute_paths = attribute_scope.get_paths_to_attribute(attribute)

    for path in attribute_paths:
        up_count = path.count(None)
        sub_path = path[up_count:]
        attr_inst_root = layout_instance
        while up_count > 0:
            attr_inst_root = attr_inst_root.parent_attribute_instance\
                                           .parent_layout_instance
            up_count -= 1

        while len(sub_path) > 0:
            for attrib_lists in attr_inst_root.attribute_instances:
                if len(sub_path) == 0:
                    break;
                for attrib_inst in attrib_lists:
                    if attrib_inst.instance_of == sub_path[0]:
                        sub_path = sub_path[1:]
                        attr_inst_root = attrib_inst.layout_instances[0]

                    if len(sub_path) == 0:
                        break;




        for attrib_lists in attr_inst_root.attribute_instances:
            for attrib_inst in attrib_lists:
                if attrib_inst.instance_of == attribute:
                    return attrib_inst

        return None

def evaluate_atomic(atomicInstance, blob):
    # todo endianess
    endianness_fb = 'little'
    endianness_st = '<'
    # todo all types
    if atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Bit:
        pass
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Byte:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.ByteBoolean:
        return 0 == int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.UInt8:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Int8:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.UInt16:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Int16:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.UInt32:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Int32:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.UInt64:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Float32:
        return struct.unpack(endianness_st + 'f', blob)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.Float64:
        return struct.unpack(endianness_st + 'd', blob)
    elif atomicInstance.instance_of.rdf_node == RDFNS.LIDL.ASCII:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)

    raise Exception('unsupported datatype')


class ExpressionInstance(object):
    def build(self, expression):
        for arg in expression.arguments:
            if type(arg) is Attribute:
                self.referenced_attributes.append(arg)
            elif type(arg) is Expression:
                self.build(arg)



    def __init__(self, expression):
        self.expression = expression
        self.referenced_attributes = []
        self.evaluable = None

        self.build(self.expression)


    def evaluate(self, layout_instance):

        arguments = dict()
        for arg in self.referenced_attributes:
            arg_instance = find_attribute_instance(layout_instance, arg)
            if arg_instance is None:
                return None
            if type(arg_instance) is ValueInstance:
                value = arg_instance
            elif type(arg_instance) is AttributeInstance:
                value = arg_instance.layout_instances[0].value
            else:
                raise Exception("only literals and atomics are supported as arguments in expressions")

            if value is None:
                raise Exception("internal error! argument evaluated to None!")

            arguments[arg] = value
        return self.expression.compute(arguments)



class Offset(object):
    def __init__(self, bit_offset = None, byte_offset=None):
        self.bit_offset_relative = bit_offset
        self.byte_offset_relative = byte_offset
        self.absolute_bit_offset = None
        self.absolute_byte_offset = None

class AttributeInstance(object):
    def __init__(self, attribute, parent_layout_instance):
        self.instance_of = attribute
        self.offset2parent = Offset()
        self.bit_size = None
        self.byte_size = None
        self.is_evaluated = False
        self.count = None
        self.evaluable = None
        self.layout_instances = []
        self.parent_layout_instance = parent_layout_instance

    #def evaluate(self, blob):
    #    if self.evaluable is None or self.evaluable == False or self.offset2parent.bit_offset_relative is None:
    #        raise Exception("trying to evaluate an unevaluable attribute")
    #    # todo check multiple layouts

    def build_tree(self):
        if isinstance(self.instance_of.count, Expression):
            self.count = ExpressionInstance(self.instance_of.count)
        else:
            self.count = self.instance_of.count

        for layout in self.instance_of.layouts:
            instance = AtomicInstance(layout, self) if type(layout) is AtomicLayout else CompositeInstance(layout, self)
            self.layout_instances.append(instance)

        for layout_instance in self.layout_instances:
            layout_instance.build_tree()

    def build_sizes(self):
        if self.bit_size or self.byte_size:
            return True

        finished = True
        for layout_instance in self.layout_instances:
            finished &= layout_instance.build_sizes()

        if isinstance(self.count, ExpressionInstance):
            return False


        if finished:
            self.bit_size  = self.count * self.layout_instances[0].bit_size
            self.byte_size = self.count * self.layout_instances[0].byte_size

        return finished

    def build_offsets(self):
        finished = True
        for layout_instance in self.layout_instances:
            finished &= layout_instance.build_offsets()
        return finished

    def compute_absolute_addresses(self, parent_offset):
        self.offset2parent.absolute_byte_offset = parent_offset.absolute_byte_offset \
                                                + self.offset2parent.byte_offset_relative

        for layout in self.layout_instances:
            layout.compute_absolute_addresses(self.offset2parent)

    def evaluate(self, blob):
        if self.offset2parent.byte_offset_relative is None:
            return False


        if type(self.count) is ExpressionInstance:
            result = self.count.evaluate(self.parent_layout_instance)
            if result is None:
                return False

            self.count = result.python_value



        finished = True
        for layout_instance in self.layout_instances:
            start = self.offset2parent.byte_offset_relative
            finished &= layout_instance.evaluate(blob[start:])

        return finished


class LayoutInstance(object):
    def __init__(self, layout, parent_attribute_instance):
        self.uuid = uuid4()
        self.instance_of = layout
        self.bit_size = None
        self.byte_size = None
        self.is_array = None
        self.value = None
        self.parent_attribute_instance = parent_attribute_instance



class AtomicInstance(LayoutInstance):
    def __init__(self, layout, parent_attribute_instance):
        LayoutInstance.__init__(self, layout, parent_attribute_instance)

        if layout.static:
            self.bit_size = layout.staticBitSize
            self.byte_size = layout.staticByteSize

    def build_tree(self):
        return

    def evaluate(self, blob):
        if self.value:
            return True
        slice = blob[0:self.byte_size]
        value = evaluate_atomic(self, slice)
        self.value = ValueInstance()
        self.value.set_python_value(value, self.instance_of.xsdType)

        return True


    def build_sizes(self):
        return True

    def build_offsets(self):
        return True

    def compute_absolute_addresses(self, parent_offset):
        pass


class CompositeInstance(LayoutInstance):
    def __init__(self, layout, parent_attribute_instance):
        LayoutInstance.__init__(self, layout, parent_attribute_instance)
        self.ordered_attribute_lists = []
        self.attribute_instances = []

    def build_ordered_attribute_list(self):
        current_order = -1
        current_attribute_list = None
        for attrib in self.instance_of.ordered_attributes:
            if attrib.order == current_order:
                current_attribute_list.append(attrib)
            elif attrib.order > current_order:
                if current_attribute_list is not None:
                    self.ordered_attribute_lists.append(current_attribute_list)

                current_order = attrib.order
                current_attribute_list = [attrib]

        if current_attribute_list is not None:
            self.ordered_attribute_lists.append(current_attribute_list)

    def build_sizes(self):
        if self.bit_size or self.byte_size:
            return True

        all_children_known = True
        for attr_instance_list in self.attribute_instances:
            for attribute_instance in attr_instance_list:
                all_children_known  &= attribute_instance.build_sizes()

        if all_children_known:
            self.byte_size = 0
            self.bit_size = 0
            for attr_instance_list in self.attribute_instances:
                self.byte_size += attr_instance_list[0].byte_size
                self.bit_size += attr_instance_list[0].bit_size

        return all_children_known

    def get_consistant_size(self,attr_instance_list):
        last_size = attr_instance_list[0].byte_size
        if last_size is None:
            return None

        for attr_inst in attr_instance_list:
            if attr_inst.byte_size is None:
                return None
            elif attr_inst.byte_size != last_size:
                raise Exception("inconsistant size of attributes with same order!")

        return last_size

    def build_offsets(self):
        for attr_instance_list in self.attribute_instances:
            for attr_inst in attr_instance_list:
                attr_inst.build_offsets()

        current_offset = Offset(0,0)

        for attr_instance_list in self.attribute_instances:
            for attr_inst in attr_instance_list:
                attr_inst.offset2parent = current_offset

                byte_size = self.get_consistant_size(attr_instance_list)
                if byte_size is None:
                    return False #we are missing something

                #new offset
                current_offset = Offset(0, current_offset.byte_offset_relative + byte_size)

        return True

    def compute_absolute_addresses(self, parent_offset):
        for attr_instance_list in self.attribute_instances:
            for attr_inst in attr_instance_list:
                attr_inst.compute_absolute_addresses(parent_offset)

    def evaluate(self, blob):
        finished = True
        for attr_instance_list in self.attribute_instances:
            for attrib in attr_instance_list:
                finished &= attrib.evaluate(blob)

        return finished


    def build_tree(self):
        self.build_ordered_attribute_list()
        # todo do not ignore attributes with same order
        for attrib_list in self.ordered_attribute_lists:
            attribute_instance_list = []
            for attrib in attrib_list:
                attribute_instance_list.append(AttributeInstance(attrib,self))

            self.attribute_instances.append(attribute_instance_list)

        for attribute_instance_list in self.attribute_instances:
            for attribute_instance in attribute_instance_list:
                attribute_instance.build_tree()

        def build_sizes(self):
            finished = True
            for attr_instance_list in self.attribute_instances:
                for attr_instance in attr_instance_list:
                    finished |= attr_instance.build_sizes()

            return finished

        def build_offsets(self):
            finished = True
            for attr_instance_list in self.attribute_instances:
                for attr_instance in attr_instance_list:
                    finished |= attr_instance.build_offsets()

            return finished

        def evaluate(self):
            finished = True
            for attr_instance_list in self.attribute_instances:
                for attr_instance in attr_instance_list:
                    finished |= attr_instance.evaluate()

            return finished



def map2rdf(layout_instance, mappings, graph, layout_uri, term_type = None):
    if type(layout_instance) is AtomicInstance:
        return layout_instance.value.rdf_literal

    if layout_instance.instance_of not in mappings:
        return None

    mapping = mappings[layout_instance.instance_of]


    if term_type is None:
        term_type = mapping.subject_map.term_type

    if term_type == TermType.IRI:
        layout_node = URIRef(str(layout_instance.uuid))
    else:
        layout_node = BNode()

    if mapping.subject_map.rdf_class:
        graph.add((layout_node, RDF.type, mapping.subject_map.rdf_class))

    if mapping.raw_mapping:
        offset = 0 if not layout_instance.parent_attribute_instance \
                   else layout_instance.parent_attribute_instance.offset2parent.absolute_byte_offset

        graph.add((layout_node, RDFNS.DCAT.byteSize, Literal(layout_instance.byte_size)))
        slice_uri = layout_uri + "/slice?start=" + str(offset) + "&length=" + str(layout_instance.byte_size)
        graph.add((layout_node, RDFNS.DCAT.downloadURL, URIRef(slice_uri)))
        graph.add((layout_node, RDFNS.DCT.format, Literal("application/octet-stream")))

    for po_map in mapping.predicate_object_map:
        o_map  = po_map.object_map
        if o_map.reference_attribute:
            attribute_instance = find_attribute_instance(layout_instance, o_map.reference_attribute)
            if attribute_instance is None:
                continue

            new_node = map2rdf(attribute_instance.layout_instances[0], mappings, graph, layout_uri, o_map.term_type)
        elif o_map.constant:
            new_node = o_map.constant
        else:
            raise Exception('not yet supported')

        if new_node is not None:
            graph.add((layout_node, po_map.predicate, new_node))

    return layout_node

def interprete(blob, layout, mappings, service_uri = "http://localhost:8080"):
    if type(layout) is AtomicLayout:
        layout_instance = AtomicInstance(layout)
    elif type(layout) is CompositeLayout:
        layout_instance = CompositeInstance(layout,None)
    else:
        return False

    layout_instance.build_tree()

    completed = False
    counter = 0
    reached_fixpoint = False
    while not reached_fixpoint:
        reached_fixpoint = True
        reached_fixpoint &= layout_instance.build_sizes()
        reached_fixpoint &= layout_instance.build_offsets()
        reached_fixpoint &= layout_instance.evaluate(blob)

        print("finished: " + str(counter))
        counter += 1

    root_offset = Offset()
    root_offset.absolute_byte_offset = 0
    layout_instance.compute_absolute_addresses(root_offset)

    layout_uri = service_uri + "/" + str(layout_instance.uuid)
    graph = Graph()
    root_uri_ref = map2rdf(layout_instance, mappings, graph, layout_uri)


    return graph


