# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "

objectiu: ja tinc la bd acabada (totes les esglésies relacionades amb un osm_id).
Ara el que vull és actualitzar a la bd informació que està a OSM. Concretament, els camps esglesia_alt i ruines.
esglesia_alt (nom alternatiu de l'església): he de cercar a OSM per alt_name, i si existeix, posar a esglesia_alt el valor que em falta, que pot ser name o alt_name.
'''

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
MyApi = OsmApi(passwordfile="/home/joan/projectes/OSM/.password")

# fem la consulta a la bd
mycursor = mydb.cursor(dictionary=True) #dictionary=True per tal de tenir array associatiu
	
cadsql ="select * from esglesia where osm_id is not null and id>=1788 order by id"
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
		overpass_query = "(node(%s););out center;" % (osm_id)
	elif (osm_tipus=="way"):
		overpass_query = "(way(%s););out center;" % (osm_id)
	else: #relation
		overpass_query = "(relation(%s););out center;" % (osm_id)
	#print (overpass_query)
	response = requests.get(overpass_url, params={'data': overpass_query})
	#print response.content;

	num1 = response.content.find("\"name\" v=\"")
	num2 = response.content.find("\"/>",num1)
	name = mid(response.content, num1+11, num2-num1-11+1)
	print (name)
	if (len(name)>100): #no hem pogut esbrinar el name (problema de connexió). Aturem el script (Please check /api/status for the quota of your IP address)
		sys.exit(0)	
	
	num1 = response.content.find("\"alt_name\" v=\"")
	num2 = response.content.find("\"/>",num1)
	alt_name = ""
	if (num1>=0):
		alt_name = mid(response.content, num1+15, num2-num1-15+1)
		print (alt_name)

	num1 = response.content.find("\"ruins\" v=\"")
	num2 = response.content.find("\"/>",num1)
	ruins = ""
	if (num1>=0):
		ruins = mid(response.content, num1+12, num2-num1-12+1)
		print (ruins)

	if (ruins=='yes'):
		print 'ruins=1'
		#print(u'Actualitzar bd? (y/n)');
		#tecla = press_key();
		#if (tecla=='y'):
		cadsql ="UPDATE esglesia set ruines=1 where osm_id='%s'" % (str(osm_id))
		print(cadsql)
		mycursor.execute(cadsql)
		mydb.commit()

	if (alt_name!=''):
		print("bd: " + esglesia['esglesia'])
		print ("1-name: " + name)
		print ("2-alt_name: " + alt_name)

		print(u'Actualitzar bd? (1/2/n)');
		tecla = press_key();
		if (tecla=='1'):
			cadsql ="UPDATE esglesia set esglesia_alt='%s' where osm_id='%s'" % (name.replace("'","''"),str(osm_id))
			print(cadsql)
			mycursor.execute(cadsql)
			mydb.commit()
		elif (tecla=='2'):
			cadsql ="UPDATE esglesia set esglesia_alt='%s' where osm_id='%s'" % (alt_name.replace("'","''"),str(osm_id))
			print(cadsql)
			mycursor.execute(cadsql)
			mydb.commit()
		else:
			print ("no fem res")

