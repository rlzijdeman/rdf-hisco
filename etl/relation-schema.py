# import libraries
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD , SDO, OWL, DCTERMS, RDFS #most common namespaces
import urllib.parse #for parsing strings to URI's

# retrieve data
df = pd.read_csv("../data/source/relation.csv", sep=",", quotechar='"')

# create graph and namespace
sdo = Namespace('https://schema.org/')
hisco = Namespace('https://iisg.amsterdam/resource/hisco/')
hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
g = Graph()

# create triples from csv
for index, row in df.iterrows():
    g.add((URIRef(hiscostat+str(row['relation_id'])), RDF.type, SDO.CategoryCode ))
    g.add((URIRef(hiscostat+str(row['relation_id'])), SDO.inCodeSet, URIRef(hisco+'RELATION') )) 
    g.add((URIRef(hiscostat+str(row['relation_id'])), SDO.codeValue, Literal(row['relation_id'], datatype=XSD.integer) ))
    g.add((URIRef(hiscostat+str(row['relation_id'])), SDO.name, Literal(row['label'], lang='en') ))

# creating the CategoryCodeSet
g.add((URIRef(hisco+'RELATION'), RDF.type, SDO.CategoryCodeSet) )


# write out results
g.serialize('../data/derived/relation-schema.ttl',format='ttl')
