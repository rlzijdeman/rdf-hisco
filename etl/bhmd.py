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
# pid = 'hdl:10622/SDZPFE' # for source purposes

response = requests.get(
    #server + '/api/access/datafile/1632/metadata/ddi' #-> gets you var ids
    # vars: rawOcc(854), NormOcc1(845), StdOcc1(846), StdOcc2(839),Hisco1(844), 
    #       Hisco2(843), Hisco3(840), Stat1(841),Stat2(850),Rel1(849),Rel2(847),Prd1(855),Prd2(848)
    server + '/api/access/datafile/1632?format=subset'+
            '&variables=854,845,846,839,844,843,840,841,850,849,847,855,848'
)
#print(response.text)

if response.status_code == 200:
    print("Contacted server succesfully\n")
else: raise SystemExit("Server says:",response.status_code)

#df = pd.read_csv(io.StringIO(response.text), sep='\t')
df = pd.read_csv(io.StringIO(response.text), sep='\t', 
                 dtype={'RawOcupationalTitle':'str', 'NormalizedOccupationalTitle':'str',
       'StandardizedOccupationalTitle1':'str', 'StandardizedOccupationalTitle2':'str',
       'HiscoCode1':'str', 'HiscoCode2':'str', 'HiscoCode3':'str', 'StatusCode1':'str', 
       'StatusCode2':'str','RelationCode1':'str', 'RelationCode2':'str', 
       'ProductCode1':'str', 'ProductCode2':'str'})

#print(df)
#response.headers["content-type"]
#response.encoding="utf-8"
#t=response.text
#df=pd.read_csv(t)
#print(t)
print(df.columns)
#RawOcupationalTitle', 'NormalizedOccupationalTitle',
#       'StandardizedOccupationalTitle1', 'StandardizedOccupationalTitle2',
#       'HiscoCode1', 'HiscoCode2', 'HiscoCode3', 'StatusCode1', 'StatusCode2',
#       'RelationCode1', 'RelationCode2', 'ProductCode1', 'ProductCode2']

### PART 2: Data wrangling
df=df.fillna('')
df['occupation']  = df['RawOcupationalTitle'].str.lower()
df['occupation2'] = df['NormalizedOccupationalTitle'].str.lower()
df['occupation3'] = df['StandardizedOccupationalTitle1'].str.lower()
df['occupation4'] = df['StandardizedOccupationalTitle2'].str.lower()

# leading zero in hisco digits is missing, resulting in 4 digit hisco's
#df['result'] = df['result'].str.replace(r'\D', '', regex=True)
df['HiscoCode1'] = df['HiscoCode1'].str.replace(r'\.0', '', regex=True)
# 7490 -> 07490
# -105 -> -105
df['HiscoCode1'] = df['HiscoCode1'].apply(lambda x: x.zfill(5) if (len(x)==4) & (x[0]!='-') else x)
df['hisco_id']=df['HiscoCode1']

# Fri Jan 17:
# hisco_id is now fine.
# for hisco_id2 and 3 -> we don't need .apply(str), because they are of type (str)
# if string is empty, we don't need to fill out (now we have 00000)
# this doesn't yet work:
# df['HiscoCode2'] = df['HiscoCode2'].apply(lambda x: x.zfill(5) if not pd.isnull(x)  else x)



#df['hisco_id']=df['hisco_id'].zfill(5)
#df.loc[df['hisco_id'].length() == 4, 'hisco_id3'] = zfill(5)
#df.loc[(df.ID == 'AA') & (df.Date >= 'Q121'), 'Used'] = ''
#df['c']=df['b'].apply(lambda x: 0 if x ==0 else math.log(x))



#df['hisco_id']=df['hisco_id'].apply('{:0>5}'.format)

df['hisco_id2']=df['HiscoCode2'].apply(str)
#df['hisco_id2']=df['hisco_id2'].apply('{:0>5}'.format)

df['hisco_id3']=df['HiscoCode3'].apply(str)
df['hisco_id3']=df['hisco_id3'].apply('{:0>5}'.format)

# errors 19429 'teixidor de indianas retirat del real servei' hisco 2 = 58340 - 20000
df.loc[df['RawOcupationalTitle'] == 'teixidor de indianas retirat del real servei', 'hisco_id2'] = '58340'
df.loc[df['RawOcupationalTitle'] == 'teixidor de indianas retirat del real servei', 'hisco_id3'] = '20000'


### PART 3: Creating triples
# create graph and namespace
sdo = Namespace('https://schema.org/')
bhmd = Namespace('https://iisg.amsterdam/resource/bhmd/')
hiscode = Namespace('https://iisg.amsterdam/resource/hisco/code/hisco/')
hiscostat = Namespace('https://iisg.amsterdam/resource/hisco/code/status/')
hiscorela = Namespace('https://iisg.amsterdam/resource/hisco/code/relation/')
hiscoprod = Namespace('https://iisg.amsterdam/resource/hisco/code/product/')

g = Graph()

# create triples
for index, row in df.iterrows():
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), RDF.type, SDO.Occupation ))
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/SDZPFE') ))
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), SDO.name, Literal(row['occupation'], lang = ('ca')) ))
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id2'])) ))
    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id3'])) ))

    if df.HiscoCode2.notna:
            g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), RDF._1, URIRef(hiscode+str(row['hisco_id'])) ))
            g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), RDF._2, URIRef(hiscode+str(row['hisco_id2'])) ))
    if df.HiscoCode3.notna:
            g.add((URIRef(iribaker.to_iri(bhmd+row['occupation'])), RDF._3, URIRef(hiscode+str(row['hisco_id3'])) ))
  

#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation2'])), RDF.type, SDO.Occupation ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation2'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/YK84PG') ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation2'])), SDO.name, Literal(row['occupation2'], lang = ('ca')) ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation2'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
#
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation3'])), RDF.type, SDO.Occupation ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation3'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/YK84PG') ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation3'])), SDO.name, Literal(row['occupation3'], lang = ('ca')) ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation3'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
#
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation4'])), RDF.type, SDO.Occupation ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation4'])), PROV.wasDerivedFrom, URIRef('https://hdl.handle.net/10622/YK84PG') ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation4'])), SDO.name, Literal(row['occupation4'], lang = ('ca')) ))
#    g.add((URIRef(iribaker.to_iri(bhmd+row['occupation4'])), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
  

    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.name, Literal(row['occupation'], lang = (str(row['en']))) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), PROV.wasDerivedFrom, Literal(str(row['provenance'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.occupationalCategory, URIRef(hiscode+str(row['hisco_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscostat+str(row['status_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscorela+str(row['relation_id'])) ))
    #g.add((URIRef(iribaker.to_iri(hisco+str(row['provenance'])+'/'+str(row['label']))), SDO.hasCategoryCode, URIRef(hiscoprod+str(row['product_id'])) ))
 
     
# write out results
g.serialize('../data/derived/bhmd.ttl',format='ttl')

