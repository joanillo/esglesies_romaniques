# encoding: utf-8
'''
cd /home/joan/projectes/OSM/esglesies_romaniques/python
PS1="$ "

mysql -u alumne -pkeiL2lai romanic
'''

import mysql.connector
import codecs

mydb = mysql.connector.connect(
  host="localhost",
  user="alumne",
  passwd="keiL2lai",
  database="romanic"
)

f = codecs.open("../data/esglesies_que_falten.txt", "w", "utf-8")

# fem la consulta a la bd
mycursor = mydb.cursor(dictionary=True) #dictionary=True per tal de tenir array associatiu
	
cadsql ="select * from esglesia where osm_id is null"
mycursor.execute(cadsql)
myresult = mycursor.fetchall()
print ("resultat de la consulta: " + str(mycursor.rowcount) + " files")
for esglesia in myresult:
	print
	nom = esglesia['nom']

	print(nom)

	f.write("---------------------\n")
	f.write("amenity=place_of_worship\n")
	if nom.lower().find("catedral")>=0:
		f.write("building=catedral\n")
	elif nom.lower().find("ermita")>=0:
		f.write("building=chapel\n")
	else:
		f.write("building=church\n")
	f.write("name=" + nom + "\n")
	if (esglesia['wikipedia']):
		f.write("wikipedia=" + esglesia['wikipedia'] + "\n")
	else:
		f.write("wikipedia=\n")
	if (esglesia['wikidata']):
		f.write("wikidata=" + esglesia['wikidata'] + "\n")
	else:
		f.write("wikidata=\n")
	f.write("religion=christian\n")
	f.write("denomination=catholic\n")
	f.write("note=importacio_esglesies_romaniques_prov\n")
	
f.close()
