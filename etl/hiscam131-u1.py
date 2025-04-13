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


### PART 1: Read in data (download from hiscam.org)
df = pd.read_csv("../data/source/hiscam_u1.csv", sep='\t',dtype={'hisco':'str','hiscam':'str','version':str})

print(df)
