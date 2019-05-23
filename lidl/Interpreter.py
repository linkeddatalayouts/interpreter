from .Mapping import Mapping, SubjectMap, PredicateObjectMap, ObjectMap
from .Layout import CompositeLayout, AtomicLayout, Attribute
from rdflib import Literal

from enum import Enum


class Evaluable(Enum):
    EVALUABLE = 1
    NOT_EVALUABLE = 2
    UNKNOWN = 3


def evaluate_atomic(atomicInstance, blob):
    # todo endianess
    endianness_fb = 'little'
    endianness_st = '<'
    # todo all types
    if atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Bit:
        pass
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Byte:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.ByteBoolean:
        return 0 == int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.UInt8:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Int8:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.UInt16:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Int16:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.UInt32:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Int32:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=True)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.UInt64:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Float32:
        return struct.unpack(endianness_st + 'f', blob)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.Float64:
        return struct.unpack(endianness_st + 'd', blob)
    elif atomicInstance.instanceOf.rdf_node == RDFNS.LIDL.ASCII:
        return int.from_bytes(blob, byteorder=endianness_fb, signed=False)

    raise Exception('unsupported datatype')


class ExpressionInstance(object):
    def __init__(self):
        self.expression = None
        self.argument_instances = []
        self.result_value = None
        self.evaluable = None

    def check_computable(self):
        computable = True

        for arg_instance in self.argument_instances:
            computable &= type(arg_instance) is Value | \
                          (type(arg_instance) is AttributeInstance and arg_instance.is_interpretable)

    def compute(self):
        if not self.evaluable:
            return False
        if self.result_value is not None:
            return True

        arguments = []
        for arg_instance in self.argument_instances:

            if type(arg_instance) is Value:
                value = arg_instance.python_value
            elif type(arg_instance) is Value:
                value = arg_instance.value.python_value
            else:
                raise Exception("only literals and atomics are supported as arguments in expressions")

            if value is None:
                raise Exception("internal error! argument evaluated to None!")

            arguments.append(value)
        self.result_value = self.expression.compute(arguments)


class Offset(object):
    def __init__(self, bit_offset = None, byte_offset=None):
        self.bit_offset_relative = bit_offset
        self.byte_offset_relative = byte_offset


class AttributeInstance(object):
    def __init__(self, attribute):
        self.instance_of = attribute
        self.offset2parent = Offset()
        self.bit_size = None
        self.byte_size = None
        self.is_evaluated = False
        self.count = None
        self.evaluable = None
        self.layout_instances = []

        self.count = self.instance_of.count

    def evaluate(self, blob):
        if self.evaluable is None or self.evaluable == False or self.offset2parent.bit_offset_relative is None:
            raise Exception("trying to evaluate an unevaluable attribute")
        # todo check multiple layouts

    def build_tree(self):
        for layout in self.instance_of.layouts:
            instance = AtomicInstance(layout) if type(layout) is AtomicLayout else CompositeInstance(layout)
            self.layout_instances.append(instance)

        for layout_instance in self.layout_instances:
            layout_instance.build_tree()

    def build_sizes(self):
        if self.bit_size or self.byte_size:
            return True

        finished = True
        for layout_instance in self.layout_instances:
            finished &= layout_instance.build_sizes()

        if finished:
            self.bit_size  = self.count * self.layout_instances[0].bit_size
            self.byte_size = self.count * self.layout_instances[0].byte_size

        return finished

    def build_offsets(self):
        finished = True
        for layout_instance in self.layout_instances:
            finished &= layout_instance.build_offsets()
        return finished

    def evaluate(self):
        finished = True
        for layout_instance in self.layout_instances:
            finished &= layout_instance.evaluate()

        return finished


class LayoutInstance(object):
    def __init__(self, layout):
        self.instanceOf = layout
        self.bit_size = None
        self.byte_size = None
        self.is_array = None
        self.value = None

        #if layout.static:
        #    self.bit_size = layout.staticBitSize
        #    self.byte_size = layout.staticByteSize


class AtomicInstance(LayoutInstance):
    def __init__(self, layout):
        LayoutInstance.__init__(self, layout)

        if layout.static:
            self.bit_size = layout.staticBitSize
            self.byte_size = layout.staticByteSize

    def build_tree(self):
        return

    def evaluate(self, blob):
        slice = blob[0:self.byteSize]
        value = evaluate_atomic(self, slice)
        self.value.set_python_value(value)

    def build_sizes(self):
        return True

    def build_offsets(self):
        return True



class CompositeInstance(LayoutInstance):
    def __init__(self, layout):
        LayoutInstance.__init__(self, layout)
        self.ordered_attribute_lists = []
        self.attribute_instances = []

    def build_ordered_attribute_list(self):
        current_order = -1
        current_attribute_list = None
        for attrib in self.instanceOf.ordered_attributes:
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
        for attr_instance_list  in self.attribute_instances:
            for attribute_instance in attr_instance_list :
                all_children_known  &= attribute_instance.build_sizes()

        if all_children_known:
            self.byte_size = 0
            self.bit_size = 0
            for attr_instance_list in self.attribute_instances:
                self.byte_size += attr_instance_list [0].byte_size
                self.bit_size += attr_instance_list [0].bit_size

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




    def build_tree(self):
        self.build_ordered_attribute_list()
        # todo do not ignore attributes with same order
        for attrib_list in self.ordered_attribute_lists:
            attribute_instance_list = []
            for attrib in attrib_list:
                attribute_instance_list.append(AttributeInstance(attrib))

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

def interprete(blob, layout, mappings):
    if type(layout) is AtomicLayout:
        layout_instance = AtomicInstance(layout)
    elif type(layout) is CompositeLayout:
        layout_instance = CompositeInstance(layout)
    else:
        return False

    layout_instance.build_tree()

    completed = False
    reached_fixpoint = False
    while not reached_fixpoint:
        reached_fixpoint = True
        reached_fixpoint &= layout_instance.build_sizes()
        reached_fixpoint &= layout_instance.build_offsets()
        #reached_fixpoint &= layout_instance.evaluate()

    return None
