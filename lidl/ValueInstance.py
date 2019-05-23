from rdflib import Literal


class ValueInstance(object):
    def __init__(self):
        self.rdf_literal = None
        self.python_value = None
        self.rdf_datatype = None


    def set_python_value(self,value):
        self.python_value = value
        self.rdf_literal = Literal(value)
        self.python_value = self.rdf_literal.datatype


    def set_rdf_literal(self, value):
        self.rdf_literal = value
        self.rdf_datatype = value.datatype
        self.python_value = value.python_value