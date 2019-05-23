from rdflib import URIRef, Namespace, Literal


class RDFNS:
    class LIDL:
        NS = "https://linkeddatalayouts.github.io/vocabularies/lidl.ttl#"

        endianness      = URIRef(NS + "endianness")
        LittleEndian    = URIRef(NS + "LittleEndian")
        BigEndian       = URIRef(NS + "BigEndian")
        MiddleEndian    = URIRef(NS + "MiddleEndian")

        Layout          = URIRef(NS + "Layout")

        Composite       = URIRef(NS + "Composite")
        attribute       = URIRef(NS + "attribute")
        distributable   = URIRef(NS + "distributable")

        Atomic          = URIRef(NS + "Atomic")
        datatype        = URIRef(NS + "datatype")
        bitSize         = URIRef(NS + "bitSize")
        byteSize        = URIRef(NS + "byteSize")

        Attribute       = URIRef(NS + "Attribute")
        order           = URIRef(NS + "order")
        predicate       = URIRef(NS + "predicate")
        layout          = URIRef(NS + "layout")
        count           = URIRef(NS + "count")
        value           = URIRef(NS + "value")

        Expression      = URIRef(NS + "Expression")
        ArgumentList    = URIRef(NS + "ArgumentList")
        Argument        = URIRef(NS + "Argument")
        operator        = URIRef(NS + "operator")

        # eval
        eval            = URIRef(NS + "eval")

        # basic algebra
        add             = URIRef(NS + "add")
        minus           = URIRef(NS + "minus")
        mul             = URIRef(NS + "mul")
        div             = URIRef(NS + "div")
        mod             = URIRef(NS + "mod")
        exp             = URIRef(NS + "exp")

        # compare
        le              = URIRef(NS + "le")
        leq             = URIRef(NS + "leq")
        eq              = URIRef(NS + "eq")
        neq             = URIRef(NS + "neq")
        geq             = URIRef(NS + "geq")
        gr              = URIRef(NS + "gr")

        # shift
        leftBitShift    = URIRef(NS + "leftBitShift")
        rightBitShift   = URIRef(NS + "rightBitShift")

        # bitwise operators
        bitwiseAND      = URIRef(NS + "bitwiseAND")
        bitwiseOR       = URIRef(NS + "bitwiseOR")
        bitwiseXOR      = URIRef(NS + "bitwiseXOR")

        # boolean operators
        AND             = URIRef(NS + "AND")
        OR              = URIRef(NS + "OR")
        NOT             = URIRef(NS + "NOT")


        # predefined atomic
        Bit         = URIRef(NS + "Bit")
        Byte        = URIRef(NS + "Byte")
        ByteBoolean = URIRef(NS + "ByteBoolean")
        UInt8       = URIRef(NS + "UInt8")
        Int8        = URIRef(NS + "Int8")
        UInt16      = URIRef(NS + "UInt16")
        Int16       = URIRef(NS + "Int16")
        UInt32      = URIRef(NS + "UInt32")
        Int32       = URIRef(NS + "Int32")
        UInt64      = URIRef(NS + "UInt64")
        Int64       = URIRef(NS + "Int64")

        Float32 = URIRef(NS + "Float32")
        Float64 = URIRef(NS + "Float64")

        ASCII   = URIRef(NS + "ASCII")

    class DCAT:
        NS = "http://www.w3.org/ns/dcat#"

        downloadURL = URIRef(NS + "downloadURL")
        byteSize = URIRef(NS + "byteSize")

    class DCT:
        NS = "http://purl.org/dc/terms/"

        format          = URIRef(NS + "format")
        octet_stream    = Literal("application/octet-stream")

    class R2RML:
        NS = "http://www.w3.org/ns/r2rml#"

        subjectMap = URIRef(NS + "subjectMap")
        termType = URIRef(NS + "termType")
        IRI = URIRef(NS + "IRI")
        BlankNode = URIRef(NS + "BlankNode")
        rrClass = URIRef(NS + "class")

        predicateObjectMap = URIRef(NS + "predicateObjectMap")
        predicate = URIRef(NS + "predicate")
        objectMap = URIRef(NS + "objectMap")


        constant = URIRef(NS + "constant")

    class RML:
        NS = "http://semweb.mmlab.be/ns/rml#"

        logicalSource = URIRef(NS + "logicalSource")
        source = URIRef(NS + "source")
        referenceFormulation = URIRef(NS + "referenceFormulation")
        reference = URIRef(NS + "reference")

