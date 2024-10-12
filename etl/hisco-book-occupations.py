# import libraries
import pandas as pd
import numpy as np
import iribaker #parses strings to IRI's.
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD , SDO, OWL, DCTERMS, RDFS, PROV #most common namespaces
import urllib.parse #for parsing strings to URL's

# retrieve data
df = pd.read_csv("../data/source/hisco_occupation_link_combined.csv", 
                 sep=";", quotechar='"', dtype={'comtxt': 'string'})
#print(df)

# all strings to lower case
df['label'] = df['label'].str.lower()

# create copy of hisco_id as filled out string 
# ('7130' -> '07130', but '-1' remains '-1')
# if string of hisco_id = length 4 -> fill it out to 5
df['hisco_id']=np.where(len(str(df['hisco_id']))==4, 'hisco_id'.zfill(5),df['hisco_id'])

# create graph and namespace
sdo = Namespace('https://schema.org/')
hisco = Namespace('https://iisg.amsterdam/resource/hisco/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/status/')
hiscorela = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
hiscoprod = Namespace('https://iisg.amsterdam/resource/hisco/code/product/')

g = Graph()

# create triples from csv
for index, row in df.iterrows():
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), RDF.type, SDO.Occupation ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.name, Literal(row['label'], lang = (str(row['lc']))) ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), PROV.wasDerivedFrom, Literal(str(row['provenance'])) ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscostat+str(row['status_id'])) ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscorela+str(row['relation_id'])) ))
    g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscoprod+str(row['product_id'])) ))
 
     
# write out results
g.serialize('../data/derived/hisco-occupation-link.ttl',format='ttl')

