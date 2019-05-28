from rdflib import Literal


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
        self.python_value = value.python_value
        pass