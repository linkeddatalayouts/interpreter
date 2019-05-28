from .AttributeInstance import *
from uuid import uuid4
from .NamespaceDefinitions import *

import struct

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
