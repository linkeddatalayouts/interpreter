from rdflib import Literal, term
from rdflib.namespace import XSD
from .NamespaceDefinitions import *
import struct

class ValueInstance(object):
    def __init__(self):
        self.rdf_literal = None
        self.python_value = None
        self.rdf_datatype = None


    def set_python_value(self,value,datatype):
        self.python_value = value
        self.rdf_literal = Literal(value, datatype=datatype)
        self.rdf_datatype = datatype
        pass


    def set_rdf_literal(self, value,datatype):
        self.rdf_literal = value
        self.rdf_datatype = datatype
        self.python_value = term._castLexicalToPython(value,self.rdf_datatype)
        pass

    def get_bytes(self, target_datatype):
        if self.rdf_datatype is None:
           return None

       #todo support all datatypes
        if self.rdf_datatype == XSD.string:
            if target_datatype == RDFNS.LIDL.ASCII:
                return str(self.rdf_literal).encode(encoding="ascii")
            elif target_datatype == RDFNS.LIDL.UTF16:
                return str(self.rdf_literal).encode(encoding="utf_16")
            elif target_datatype == RDFNS.LIDL.UTF16:
                return str(self.rdf_literal).encode(encoding="utf_32")
            else:
                raise Exception("unsupported datatype: " + str(target_datatype))
        elif self.rdf_datatype == XSD.hexBinary:
            return bytes.fromhex(str(self.rdf_literal))
        elif self.rdf_datatype == XSD.integer or \
             self.rdf_datatype == XSD.int or \
             self.rdf_datatype == XSD.unsignedInt or \
             self.rdf_datatype == XSD.double or \
             self.rdf_datatype == XSD.float:

            pack_string = "="
            if target_datatype == RDFNS.LIDL.UInt8:
                pack_string += "B"
            elif target_datatype == RDFNS.LIDL.Int8:
                pack_string += "b"
            elif target_datatype == RDFNS.LIDL.UInt16:
                pack_string += "H"
            elif target_datatype == RDFNS.LIDL.Int16:
                pack_string += "h"
            elif target_datatype == RDFNS.LIDL.UInt32:
                pack_string += "I"
            elif target_datatype == RDFNS.LIDL.Int32:
                pack_string += "i"
            elif target_datatype == RDFNS.LIDL.UInt64:
                pack_string += "L"
            elif target_datatype == RDFNS.LIDL.Int64:
                pack_string += "l"
            elif target_datatype == RDFNS.LIDL.Float32:
                pack_string += "f"
            elif target_datatype == RDFNS.LIDL.Float64:
                pack_string += "d"
            else:
                raise Exception("unsupported datatype: " + str(target_datatype))

            return struct.pack(pack_string, self.python_value)
        elif self.rdf_datatype == XSD.boolean:
            if target_datatype == RDFNS.LIDL.Bit:
                raise Exception("bits are not yet supported")
            elif target_datatype == RDFNS.LIDL.ByteBoolean:
                return struct.pack("=?", self.python_value)
            else:
                raise Exception("unsupported datatype: " + str(target_datatype))
