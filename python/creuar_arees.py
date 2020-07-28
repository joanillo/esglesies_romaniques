# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "

mysql -u *** -p*** romanic
mysqldump -i --complete-insert -u *** -p*** -r /home/joan/projectes/OSM/esglesies_romaniques/mysql/romanic_200415.sql -v romanic
'''

import json #parsejar JSON
import mysql.connector

import termios, fcntl, sys, os #script interactiu
import codecs

import requests #cercar node
#import jxmlease

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

def distance(str1, str2):
	str1 = str1.lower().replace(u"església de ", "")
	str2 = str2.lower().replace(u"església de ", "")
	print "---dist ---"
	print("bd: " + str1)
	print("json: " + str2)
	d=dict()
	for i in range(len(str1)+1):
		d[i]=dict()
		d[i][0]=i
	for i in range(len(str2)+1):
		d[0][i] = i
	for i in range(1, len(str1)+1):
		for j in range(1, len(str2)+1):
			d[i][j] = min(d[i][j-1]+1, d[i-1][j]+1, d[i-1][j-1]+(not str1[i-1] == str2[j-1]))
	return d[len(str1)][len(str2)]

def preparar_consulta(str):
	str = str.lower()
	paraules = ['Mair de Diu ', 'dera ', 'santuari de ', 'capella de ',u'parròquia de ', u'església de ', u'esglèsia de ', u'monestir de ', 'sant ', 'santa ', ' de la ', ' dels ', ' de ', ' la ', ' del ', 'ermita ', 'st. ', 'sta. ','st ','sta ', ' d\'', ' l\'']
	for paraula in paraules:
		str = str.replace(paraula,' ')
	str = str.replace('  ',' ')
	str = str.strip()
	valors = str.split(" ")
	cadsql = " "
	i=0
	for valor in valors:
		if (i>0):
			cadsql = cadsql + " and "
		cadsql = cadsql + "esglesia like '%" + valor.replace("'","''") + "%'"
		#esglesia like '%fai%'"
		i = i+1

	return cadsql

def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]
#---

with open('../data/areas_C_church.json', 'r') as f:
    esglesies_dict = json.load(f)

# creem la sessió, doncs només vull fer un changeset per tots els canvis
MyApi = OsmApi(passwordfile="/home/joan/projectes/OSM/.password2")

num_item = 1;
for esglesia in esglesies_dict:
	sortir_bucle=0
	name = ""
	name_ca = "" #cas Vall d'Aran
	alt_name = ""
	wikipedia = ""
	wikidata = ""
	municipi = ""

	osm_id = esglesia['id'];
	#todo: del primer node, fer una consulta i cercar les coordenades. Després, cercar el municipi.
	#lat = float(esglesia['lat']);
	#lon = float(esglesia['lon']);

	#tags
	tags = esglesia["tags"]
	if ("name" in tags.keys()):
		name = esglesia['tags']['name'];
	if ("name:ca" in tags.keys()):
		name_ca = esglesia['tags']['name:ca'];
	if ("alt_name" in tags.keys()):
		alt_name = esglesia['tags']['alt_name'];
	if ("wikipedia" in tags.keys()):
		wikipedia = esglesia['tags']['wikipedia'];
	if ("wikidata" in tags.keys()):
		wikidata = esglesia['tags']['wikidata'];

	f = codecs.open("cas_esglesia.txt", "w", "utf-8")
	print("=================================")
	f.write("=================================\n")
	print(num_item)
	print("=================================")
	if (name==""):
		print(u"COMPTE!! Església sense nom")
		num_item += 1
		continue
	print("name: " + name)
	if (alt_name != ""):
		print("alt_name: " + alt_name)
	if (name_ca != ""):
		print("name_ca: " + name_ca)
	#print ("(" + str(lat) + "," + str(lon) + ")" + " (" + str(lat) + "/" + str(lon) + ")");
	print("wikipedia: " + wikipedia)
	print("wikidata: " + wikidata)
	print ("osm_id: " + str(osm_id))

	#nodes
	nodes = esglesia["nodes"]
	osm_id_node = nodes[0] #només m'interessa el primer node
	#cerquem el municipi de l'església
	#overpass_query = "node[name~Dolmen](around:80,%f,%f);node[name~menhir](around:80,%f,%f);node[name~cist](around:80,%f,%f);node[historic=archaeological_site](around:80,%f,%f); out;" % (lat,lon,lat,lon,lat,lon,lat,lon)
	overpass_query = "(node(%i););out;foreach(is_in->.a;area.a[admin_level~'[8]']->.a;convert node::=::,::id = id(),municipi=a.set(t['name']);out;);" % (osm_id_node)
	#print overpass_query;
	response = requests.get(overpass_url, params={'data': overpass_query})
	#print response.content;
	num1 = response.content.find("lat=\"")
	num2 = response.content.find("\"",num1+5)
	lat = mid(response.content, num1+6, num2-num1-5)
	print("lat: " + lat)
	num1 = response.content.find("lon=\"")
	num2 = response.content.find("\"",num1+5)
	lon = mid(response.content, num1+6, num2-num1-5)
	print("lon: " + lon)
	print(lat + "/" + lon)
	#NOTA: he tingut problemes per parsejar el json que em retorna la overpass_query. No hi ha manera d'accedir al tag de municipi
	num1 = response.content.find("municipi\" v=\"")
	num2 = response.content.find("\"/>",num1)
	municipi = mid(response.content, num1+14, num2-num1-14+1)
	print("municipi: " + municipi)
	print("name + municipi: " + name + " " + unicode(municipi, "utf-8") + "\n")
	f.write("name: " + name + " (" + str(osm_id) + ")\n")
	f.write("alt_name: " + alt_name + "\n")
	f.write("name_ca: " + name_ca + "\n")
	f.write("(" + str(lat) + "," + str(lon) + ")" + "\n");
	f.write("municipi: " + unicode(municipi, "utf-8") + "\n")
	f.write("---" + "\n")

	# fem la consulta a la bd
	mycursor = mydb.cursor(dictionary=True) #dictionary=True per tal de tenir array associatiu
	
	#print(preparar_consulta(name))
	if (name_ca!=""):
		cadsql ="SELECT id, esglesia, municipi, wikipedia FROM esglesia where ((" + preparar_consulta(name) + ") or (" + preparar_consulta(name_ca) + ")) and osm_id IS NULL order by id"
	elif (alt_name!=""):
		cadsql ="SELECT id, esglesia, municipi, wikipedia FROM esglesia where ((" + preparar_consulta(name) + ") or (" + preparar_consulta(alt_name) + ")) and osm_id IS NULL order by id"
	else:
		cadsql ="SELECT id, esglesia, municipi, wikipedia FROM esglesia where " + preparar_consulta(name) + " and osm_id IS NULL order by id"		
	#cadsql ="SELECT id, esglesia, municipi, wikipedia FROM esglesia where id=1150";
	#print cadsql
	mycursor.execute(cadsql)
	myresult = mycursor.fetchall()
	if (mycursor.rowcount==0):
		sortir_bucle=1
	print ("resultat de la consulta: " + str(mycursor.rowcount) + " files")
	for esglesia in myresult:
		id = esglesia['id']
		print("bd: " + esglesia['esglesia'] + " (" + str(esglesia['id']) + ")")
		f.write("bd: " + esglesia['esglesia'] + "\n")
		if (esglesia['municipi']):
			print("(mun: " + esglesia['municipi'] + ")")
			f.write("(mun: " + esglesia['municipi'] + ")" + "\n")
		if (esglesia['wikipedia']):
			print("(wik: " + esglesia['wikipedia'] + ")")
			f.write("wik: " + esglesia['wikipedia'] + u" (viquipèdia)\n")
		dist_mitjana = (len(esglesia['esglesia'])+len(name))/2
		coincidencia = u"coincidència: " + str(100*abs(dist_mitjana - distance(esglesia['esglesia'], name))/dist_mitjana) + " %"
		print coincidencia
		f.write(coincidencia + "\n")
		if (alt_name != ""):
			coincidencia = u"coincidència: " + str(100*abs(dist_mitjana - distance(esglesia['esglesia'], alt_name))/dist_mitjana) + " %"
			print coincidencia
			f.write(coincidencia + "\n")
		if (name_ca != ""):
			coincidencia = u"coincidència: " + str(100*abs(dist_mitjana - distance(esglesia['esglesia'], name_ca))/dist_mitjana) + " %"
			print coincidencia
			f.write(coincidencia + "\n")
		print("-----------")
		f.write("-----------" + "\n")
		print(u'És aquesta? (y/n)');
		tecla = press_key();
		#print(tecla)
		if (tecla=='y'):
			print(u"Anem a fer un update a la bd")
			cadsql ="UPDATE esglesia set osm_id='%s' where id=%s" % (str(osm_id),str(id))
			print(cadsql)
			mycursor.execute(cadsql)
			cadsql ="UPDATE esglesia set lat=%s where id=%s" % (str(lat),str(id))
			print(cadsql)
			mycursor.execute(cadsql)
			cadsql ="UPDATE esglesia set lon=%s where id=%s" % (str(lon),str(id))
			print(cadsql)
			mycursor.execute(cadsql)
			if (wikipedia != ""):
				cadsql ="UPDATE esglesia set wikipedia='%s' where id=%s" % (wikipedia.replace("'","''"),str(id))
				print(cadsql)
				mycursor.execute(cadsql)
			if (wikidata != ""):
				cadsql ="UPDATE esglesia set wikidata='%s' where id=%s" % (wikidata,str(id))
				print(cadsql)
				mycursor.execute(cadsql)
			cadsql ="UPDATE esglesia set municipi='%s' where id=%s" % (municipi.replace("'","''"),str(id))
			mycursor.execute(cadsql)
			print(cadsql)
			cadsql ="UPDATE esglesia set osm_tipus='way' where id=%s" % (str(id))
			print(cadsql)
			mycursor.execute(cadsql)
			mydb.commit()
			sortir_bucle=1
			break

		print("\n")

	f.close()
	num_item += 1

	# no em vull passar del final quan deixo la tecla 'n' apretada
	while (sortir_bucle==0):
		print(u'\nper sortir del bucle: y');
		tecla = press_key();
		if (tecla=='y'):
			sortir_bucle = 1	

	
	print(u'\nUna altra esglèsia? (y/n)');
	tecla = press_key();
	if (tecla=='n'):
		sys.exit(0)			

