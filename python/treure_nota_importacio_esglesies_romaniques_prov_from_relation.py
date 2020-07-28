# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "
'''
import json #parsejar JSON
import termios, fcntl, sys, os #script interactiu
import requests #cercar node
from osmapi import OsmApi #create, update node

overpass_url = "http://overpass-api.de/api/interpreter"

#---
def press_key():
	fd = sys.stdin.fileno()

	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)

	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

	try:
		while 1:
			try:
				c = sys.stdin.read(1)
				#print "Got character", repr(c)
				return c;
			except IOError: pass
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
#---

'''
Per obtenir el fitxer ../data/importacio_esglesies_romaniques_prov.json
fem la següent consulta a overpass-turbo:
[out:json];
area["name"="Catalunya"]->.boundaryarea;
(
nwr(area.boundaryarea)[note=importacio_esglesies_romaniques_prov];
);
out meta;
'''

with open('../data/importacio_esglesies_romaniques_prov.json', 'r') as f:
    esglesies_dict = json.load(f)

# creem la sessió, doncs només vull fer un changeset per tots els canvis
MyApi = OsmApi(passwordfile="/home/joan/projectes/OSM/.password2")
changeset_comment = '{"comment": "Eliminar nota provisional: esglesies_romaniques_prov"}'
changeset_comment_json = json.loads(changeset_comment)
MyApi.ChangesetCreate(changeset_comment_json)

num_item = 1;
for esglesia in esglesies_dict:
	print("===" + str(num_item) + "==============================")
	osm_id= esglesia['id'];
	print(osm_id)
	tags = esglesia["tags"]
	name = tags[u"name"]
	print(name)
	relation = MyApi.RelationGet(osm_id)
	tags_osm = relation["tag"]
	print(tags_osm[u"name"])
	#hem d'eliminar la nota note=importacio_esglesies_romaniques_prov
	#print(tags_osm)
	#eliminació d'un element dins d'un diccionari:
	del tags_osm[u"note"] #eliminem el tag
	print(MyApi.RelationUpdate(relation)) #actualitzem la via (aquí podem veure que la note ja no hi és)

	num_item = num_item + 1

	#break #sortim a la primera iteració per fer proves

# tanquem la sessió
MyApi.ChangesetClose()
