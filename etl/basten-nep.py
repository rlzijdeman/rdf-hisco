import io
import numpy as np
import pandas as pd
import requests
import iribaker #parses strings to IRI's.
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD , SDO, OWL, DCTERMS, RDFS, PROV #most common namespaces
import urllib.parse #for parsing strings to URL's

### PART 1: Getting data from Dataverse and read as Pandas PD
# docs: https://guides.dataverse.org/en/5.12.1/api/dataaccess.html

server = 'https://datasets.iisg.amsterdam/'
# pid = 'hdl:10622/YK84PG' # for source purposes

response = requests.get(
    #server + '/api/access/datafile/377/metadata/ddi' # -> gets you var ids
    server + '/api/access/datafile/377?format=subset&variables=289,290'
)
if response.status_code == 200:
    print("Contacted server succesfully\n")
else: raise SystemExit("Server says:",response.status_code)

df = pd.read_csv(io.StringIO(response.text), sep='\t')
#print(df)
#response.headers["content-type"]
#response.encoding="utf-8"
#t=response.text
#df=pd.read_csv(t)
#print(t)



### PART 2: Data wrangling
df['occupation'] = df['occupation'].str.lower()
# leading zero in hisco digits is missing, resulting in 4 digit hisco's
df['hisco_id']=df['hisco'].apply(str)
df['hisco_id']=df['hisco_id'].apply('{:0>5}'.format)

### PART 3: Creating triples
# create graph and namespace
sdo = Namespace('https://schema.org/')
basten = Namespace('https://iisg.amsterdam/resource/basten/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
#hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/status/')
#hiscorela = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
#hiscoprod = Namespace('https://iisg.amsterdam/resource/hisco/code/product/')

g = Graph()

# create triples
for index, row in df.iterrows():
    g.add((URIRef(iribaker.to_iri(basten+row['occupation'])), RDF.type, SDO.Occupation ))
    g.add((URIRef(iribaker.to_iri(basten+row['occupation'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/YK84PG') ))
    g.add((URIRef(iribaker.to_iri(basten+row['occupation'])), SDO.name, Literal(row['occupation'], lang = ('en-gb')) ))
    g.add((URIRef(iribaker.to_iri(basten+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
 

    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.name, Literal(row['occupation'], lang = (str(row['en']))) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), PROV.wasDerivedFrom, Literal(str(row['provenance'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscostat+str(row['status_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscorela+str(row['relation_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscoprod+str(row['product_id'])) ))
 
     
# write out results
g.serialize('../data/derived/basten.ttl',format='ttl')

