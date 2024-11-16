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
# pid = 'hdl:10622/KNGX6B' # for source purposes

response = requests.get(
    #for fileid visit dataverse, click file and look for id in address bar
    #server + '/api/access/datafile/33670/'
    #server + '/api/access/datafile/33670/metadata/ddi' # -> gets you var ids
    server + '/api/access/datafile/33670?format=subset&variables=132473,132472'
    #print(response.text)
)
print(response.text)

if response.status_code == 200:
    print("Contacted server succesfully\n")
else: raise SystemExit("Server says:",response.status_code)

df = pd.read_csv(io.StringIO(response.text), sep='\t', dtype={'OCCUPATION':'str', 'HISCO':'str'})
df = df.dropna(axis=0) # removing 1 observation without hisco code
df = df.rename(columns={'OCCUPATION': 'occupation', 'HISCO':'hisco'})


### PART 2: Data wrangling
df['occupation'] = df['occupation'].str.lower()

# small function to fill out 4 digit codes to 5 digits
def fill_hisco(x):
 if len(x)==4:
    return x.zfill(5)
 else:
    return x

df['hisco_id'] = df['hisco'].apply(fill_hisco)


### PART 3: Creating triples
# create graph and namespace
sdo = Namespace('https://schema.org/')
basten = Namespace('https://iisg.amsterdam/resource/basten/')
mooney = Namespace('https://iisg.amsterdam/resource/mooney/')
seCedar = Namespace('https://iisg.amsterdam/resource/se-CEDAR/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
#hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/status/')
#hiscorela = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
#hiscoprod = Namespace('https://iisg.amsterdam/resource/hisco/code/product/')

g = Graph()

# create triples
for index, row in df.iterrows():
    g.add((URIRef(iribaker.to_iri(seCedar+row['occupation'])), RDF.type, SDO.Occupation ))
    g.add((URIRef(iribaker.to_iri(seCedar+row['occupation'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/KNGX6B') ))
    g.add((URIRef(iribaker.to_iri(seCedar+row['occupation'])), SDO.name, Literal(row['occupation'], lang = ('sv')) ))
    g.add((URIRef(iribaker.to_iri(seCedar+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
 

    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.name, Literal(row['occupation'], lang = (str(row['en']))) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), PROV.wasDerivedFrom, Literal(str(row['provenance'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscostat+str(row['status_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscorela+str(row['relation_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscoprod+str(row['product_id'])) ))
 
     
# write out results
g.serialize('../data/derived/se-cedar-hisco.ttl',format='ttl')