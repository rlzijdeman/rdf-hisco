# import libraries
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD , SDO, OWL, DCTERMS, RDFS #most common namespaces
import urllib.parse #for parsing strings to URI's

# retrieve data
df = pd.read_csv("../data/source/hisco_45_full_03.csv", sep=";", quotechar='"')

# create one variable for 5 digit HISCO codes
df['hisco_12345_id'] = df['hisco_full_id'].astype(str).str.zfill(5)
# print(df['hisco_12345_id'])


# create graph and namespace
sdo = Namespace('https://schema.org/')
hisco = Namespace('https://iisg.amsterdam/resource/hisco/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
g = Graph()


# create triples from csv
for index, row in df.iterrows():
    # major groups
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDF.type, URIRef(hisco+'MajorGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), DCTERMS.isPartOf, URIRef(hisco+'MajorGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), RDF.type, SDO.CategoryCode))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), SDO.codeValue, Literal(row['hisco_1_id'], datatype=XSD.integer) ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), SDO.name, Literal(row['label1'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), SDO.description, Literal(row['description1'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])), SDO.inCodeSet, URIRef(hisco+'HISCO') ))

    # minor groups
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDF.type, URIRef(hisco+'MinorGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), DCTERMS.isPartOf, URIRef(hisco+'MinorGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), RDF.type, SDO.CategoryCode))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), RDFS.subClassOf, URIRef(hiscode+str(row['hisco_1_id'])) ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), SDO.codeValue, Literal(int(str(row['hisco_1_id'])+str(row['hisco_2_id'])), datatype=XSD.integer) ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), SDO.name, Literal(row['label2'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), SDO.description, Literal(row['description2'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])), SDO.inCodeSet, URIRef(hisco+'HISCO') ))

    # unit groups
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDF.type, URIRef(hisco+'UnitGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), DCTERMS.isPartOf, URIRef(hisco+'UnitGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), RDF.type, SDO.CategoryCode))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), RDFS.subClassOf, URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])) ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), SDO.codeValue, Literal(int(str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), datatype=XSD.integer) ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), SDO.name, Literal(row['label3'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), SDO.description, Literal(row['description3'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])), SDO.inCodeSet, URIRef(hisco+'HISCO') ))

    # micro groups
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDF.type, URIRef(hisco+'MicroGroup') ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDF.type, SDO.CategoryCode))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), RDFS.subClassOf, URIRef(hiscode+str(row['hisco_1_id'])+str(row['hisco_2_id'])+str(row['hisco_3_id'])) ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), SDO.codeValue, Literal(row['hisco_full_id'], datatype=XSD.integer) ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), SDO.codeValue, Literal(row['hisco_full_id_pretty'], datatype=XSD.string) ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), SDO.name, Literal(row['label45'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), SDO.description, Literal(row['description45'], lang='en') ))
    g.add((URIRef(hiscode+str(row['hisco_12345_id'])), SDO.inCodeSet, URIRef(hisco+'HISCO') ))

# adding triples for HISCO schema
g.add((URIRef(hisco+'HISCO'), RDF.type, SDO.CategoryCodeSet) )
g.add((URIRef(hisco+'MajorGroup'), RDF.type, OWL.Class))
g.add((URIRef(hisco+'MinorGroup'), RDF.type, OWL.Class))
g.add((URIRef(hisco+'UnitGroup'), RDF.type, OWL.Class))
g.add((URIRef(hisco+'MicroGroup'), RDF.type, OWL.Class))

# adding auxiliary variables (status, relation, product)




# uncomment below to test output    
# print(g.serialize(format='turtle'))

# write out results
g.serialize('../data/derived/hisco-schema.ttl',format='ttl')


