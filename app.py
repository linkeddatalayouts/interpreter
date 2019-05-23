from flask import Flask

from lidl.Layout import *


from rdflib import Graph, URIRef
from rdflib.namespace import RDF, NamespaceManager




app = Flask(__name__)


layouts = dict()
layouts_graph = None
layouts_graph_serialized = None

def update_layouts_graph():
    global layouts_graph, layouts_graph_serialized
    layouts_graph = Graph()
    nsMg = NamespaceManager(layouts_graph)
    nsMg.bind('LDP', LDP)

    this = URIRef('/')
    layouts_graph.add((this, RDF.type, LDP.SimpleContainer))

    for layout_id, layout in layouts:
        layouts_graph.add((this, LDP.member, URIRef("/" + str(layout_id))))

    layouts_graph_serialized = layouts_graph.serialize('/')

@app.route('/',methods=['GET'])
def root():
    if not layouts_graph:
        update_layouts_graph()

    return layouts_graph_serialized

@app.route('/<layout_id>',methods=['GET'])
def getter_layout(layout_id):
    if layout_id in layouts:
        return layouts[layout_id].layout_string
    else:
        return "unknown layout", 404



@app.route('/',methods=['POST'])
def create_layout():
    new_layout = Layout()
    try:
        new_layout.init_with_rdf(str(request.data))
    except Exception as e:
        str(e)
        return str(e), 400

    layouts[new_layout.guid] = new_layout


if __name__ == '__main__':
    app.run()


