import io
import numpy as np
import pandas as pd
import requests
import iribaker #parses strings to IRI's.
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD , SDO, OWL, DCTERMS, RDFS, PROV #most common namespaces
from time import perf_counter
from time import ctime
import urllib.parse #for parsing strings to URL's


### PART 1: Getting data from Dataverse and read as Pandas PD
# docs: https://guides.dataverse.org/en/5.12.1/api/dataaccess.html

server = 'https://datasets.iisg.amsterdam/'
 #pid = 'hdl:10622/88ZXD8' # for source purposes

response = requests.get(
   #server + '/api/access/datafile/9824/metadata/ddi' # -> gets you var ids
     server + '/api/access/datafile/9824?format=subset&variables=20241,20238,20234,20244,20243,20229'
)
if response.status_code == 200:
    print("Contacted server succesfully\n")
else: raise SystemExit("Server says:",response.status_code)


#print(df)
#response.headers["content-type"]
#response.encoding="utf-8"
#df=pd.read_csv(t)

#t=response.text
#print(t)

# read data
df = pd.read_csv(io.StringIO(response.text), sep='\t',
                 dtype={'Original':'str', 'Standard':str, 'HISCO':'str','STATUS':str,
                        'RELATION':str, 'PRODUCT':str})


# slimming down for testing purposes
#df = df.tail(100)
#df = df[df['Original']=="beroepstitel niet vermeld"]

### PART 2: Data wrangling
df['occupation'] = df['Original'].str.lower()
df['standard'] = df['Standard'].str.lower()

# if string of hisco_id = length 4 -> fill it out to 5
df['hisco_id'] = df['HISCO'].apply(str)
df['hisco_id']=np.where(len(str(df['hisco_id']))==4, 'hisco_id'.zfill(5),df['hisco_id'])


df['status_id'] = df['STATUS']
df['relation_id'] = df['RELATION']
df['product_id'] = df['PRODUCT']

### PART 3: Creating triples
# create graph and namespace
sdo = Namespace('https://schema.org/')
hsndb = Namespace('https://iisg.amsterdam/resource/hsndb/occupation/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/status/')
hiscorela = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
hiscoprod = Namespace('https://iisg.amsterdam/resource/hisco/code/product/')

g = Graph()

# create triples
for index, row in df.iterrows():
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), RDF.type, SDO.Occupation ))
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.isPartOf, URIRef('https://hdl.handle.net/10622/88ZXD8') ))
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.name, Literal(row['occupation'], lang = ('nl')) ))
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.alternateName, Literal(row['standard'], lang = ('nl')) )) 

    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))

    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.hasCategoryCode, URIRef(hiscostat+str(row['status_id'])) ))
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.hasCategoryCode, URIRef(hiscorela+str(row['relation_id'])) ))
    g.add((URIRef(iribaker.to_iri(hsndb+row['occupation'])), SDO.hasCategoryCode, URIRef(hiscoprod+str(row['product_id'])) )) 
    
    print(URIRef(iribaker.to_iri(hsndb+row['occupation'])))


# write out results
start = perf_counter()
print("\nwriting results... go and have lunch... \nThe time is now:", ctime(), "\n")
g.serialize('../data/derived/hsndb.ttl',format='ttl')
end = perf_counter()
timediff = end - start
print("Time in seconds elapsed during g.serialize: ", timediff) # Time in seconds,ca 2000 on oldish macbook pro
