# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "

mysql -u *** -p*** romanic
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
	
cadsql ="select * from esglesia where osm_id is not null and municipi is null"
mycursor.execute(cadsql)
myresult = mycursor.fetchall()
print ("resultat de la consulta: " + str(mycursor.rowcount) + " files")
for esglesia in myresult:
	osm_id = esglesia['osm_id']
	osm_tipus = esglesia['osm_tipus']
	print
	print(esglesia['esglesia'] + " (" + osm_id + ")")
	if (osm_tipus=="node"):
		overpass_query = "(node(%s););out;foreach(is_in->.a;area.a[admin_level~'[8]']->.a;convert node::=::,::id = id(),municipi=a.set(t['name']);out;);" % (osm_id)
	else:
		overpass_query = "(way(%s););(._;>;);out;foreach(is_in->.a;area.a[admin_level~'[8]']->.a;convert area::=::,::id =id(),municipi=a.set(t['name']);(._;>;);out;);" % (osm_id)
	#print (overpass_query)
	response = requests.get(overpass_url, params={'data': overpass_query})
	#print response.content;
	num1 = response.content.find("municipi\" v=\"")
	num2 = response.content.find("\"/>",num1)
	municipi = mid(response.content, num1+14, num2-num1-14+1)
	print (municipi)

	print(u'Actualitzar municipi? (y/n)');
	tecla = press_key();
	if (tecla=='y'):
		cadsql ="UPDATE esglesia set municipi='%s' where osm_id='%s'" % (municipi.replace("'","''"),str(osm_id))
		#print(cadsql)
		mycursor.execute(cadsql)
		mydb.commit()