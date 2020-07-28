# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "

objectiu: ja tinc la bd acabada (totes les esglésies relacionades amb un osm_id).
Les esglésies que he detectat com a ruïnoses tenen en comú el tag ruins=yes, però això no fa que la icona en el ID es vegi amb el logo de ruïnes
El que vull és assegurar-me de què tinc també aquests dos tags:
building:condition=ruinous
historic=ruins
'''

import json #parsejar JSON
import mysql.connector
import termios, fcntl, sys, os #script interactiu
import requests #cercar node
from osmapi import OsmApi #create, update node

overpass_url = "http://overpass-api.de/api/interpreter"

pswd = file( "/home/joan/projectes/OSM/esglesies_romaniques/mysql/.passwd", "r" )
for aLine in pswd:
	fields= aLine.split( ":" )
	#print fields[0], fields[1]
pswd.close()

mydb = mysql.connector.connect(
  host="localhost",
  user=fields[0],
  passwd=fields[1],
  database="romanic"
)

                     
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

def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]
#---

# creem la sessió, doncs només vull fer un changeset per tots els canvis
MyApi = OsmApi(passwordfile="/home/joan/projectes/OSM/.password2")
changeset_comment = '{"comment": "actualitzar esglésies ruïnoses amb el tag historic=ruins #1"}'
changeset_comment_json = json.loads(changeset_comment)
MyApi.ChangesetCreate(changeset_comment_json)

# fem la consulta a la bd
mycursor = mydb.cursor(dictionary=True) #dictionary=True per tal de tenir array associatiu
	
cadsql ="select * from esglesia where osm_id is not null and ruines=1 and id>=648 order by id"
mycursor.execute(cadsql)
myresult = mycursor.fetchall()
print ("resultat de la consulta: " + str(mycursor.rowcount) + " files")
for esglesia in myresult:
	esglesia_id = esglesia['id']
	osm_id = esglesia['osm_id']
	osm_tipus = esglesia['osm_tipus']
	print
	print(esglesia['esglesia'] + " (" + str(esglesia_id) + ", " + osm_id + ")")

	if (osm_tipus=="node"):
		node = MyApi.NodeGet(osm_id)
		tags_osm = node["tag"]
		print(tags_osm)
		print(u'Actualitzar OSM? (y/n/s) (s:salvar i tancar)');
		tecla = press_key();
		if (tecla=='y'):
			print('actualitzem')
			tags_osm.update({'building:condition':'ruinous','historic':'ruins'})
			print(MyApi.NodeUpdate(node)) #actualitzem la via (aquí podem veure que la note ja no hi és) 
		elif (tecla=='s'):
			MyApi.ChangesetClose() #actualitzem tot el que tenim fins ara
			sys.exit(0)

	elif (osm_tipus=="way"):
		way = MyApi.WayGet(osm_id)
		tags_osm = way["tag"]
		print(tags_osm)
		print(u'Actualitzar OSM? (y/n/s) (s:salvar i tancar)');
		tecla = press_key();
		if (tecla=='y'):
			print('actualitzem')
			tags_osm.update({'building:condition':'ruinous','historic':'ruins'})
			print(MyApi.WayUpdate(way)) #actualitzem la via (aquí podem veure que la note ja no hi és) 
		elif (tecla=='s'):
			MyApi.ChangesetClose() #actualitzem tot el que tenim fins ara
			sys.exit(0)
	elif (osm_tipus=="node"):
		relation = MyApi.RelationGet(osm_id)
		tags_osm = relation["tag"]
		print(tags_osm)
		print(u'Actualitzar OSM? (y/n/s) (s:salvar i tancar)');
		tecla = press_key();
		if (tecla=='y'):
			print('actualitzem')
			tags_osm.update({'building:condition':'ruinous','historic':'ruins'})
			print(MyApi.RelationUpdate(relation)) #actualitzem la via (aquí podem veure que la note ja no hi és) 
		elif (tecla=='s'):
			MyApi.ChangesetClose() #actualitzem tot el que tenim fins ara
			sys.exit(0)

MyApi.ChangesetClose() #actualitzem tot el que tenim fins ara