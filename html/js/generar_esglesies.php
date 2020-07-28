<?php
// cd /home/joan/projectes/OSM/esglesies_romaniques/html/js2/
// $ php generar_esglesies.php

$conn = new mysqli("localhost", "joan", "She4aiVa", "romanic");

$myfile = fopen("esglesies.js", "w") or die("Unable to open file!");

$cad = "var esglesies_complet = [\n";
fwrite($myfile, $txt);

if (mysqli_connect_errno()) {
    printf("ha fallat la connexió: %s\n", mysqli_connect_error());
    exit();
}



$conn->query("SET NAMES 'utf8'");
$q=$conn->query("select esglesia, e.municipi, comarca, lat, lon, wikipedia, wikidata, esglesia_alt, ruines from esglesia e, municipi m, comarca c where e.municipi=m.alt_municipi and m.id_comarca=c.id_comarca and e.municipi is not null and osm_id is not null");

while($r=$q->fetch_assoc()) {
    print_r($r);
    $cad .= "{";
    $cad .= "name:\"".$r["esglesia"]."\", ";
    if ($r["comarca"]!="") $cad .= "alt_name:\"".$r["esglesia_alt"]."\", ";
    if ($r["ruines"]=="1") $cad .= "ruins:\"yes\", ";
    $cad .= "lat:".$r["lat"].", ";
    $cad .= "lon:".$r["lon"].", ";
    $cad .= "municipi:\"".$r["municipi"]."\", ";
    $cad .= "comarca:\"".$r["comarca"]."\", ";
    $cad .= "wikipedia:\"".$r["wikipedia"]."\", ";
    $cad .= "wikidata:\"".$r["wikidata"]."\" ";
    $cad .= "},\n";
}


$cad .= "]\n";
$cad = str_replace("},\n]", "}\n]", $cad);
fwrite($myfile, $cad);

fclose($myfile);

$conn->close();
/*
var esglesies_complet = [
{name:"la Tomba del General",municipi:"Roses",lat:42.2642006,lon:3.2127323,hi_es:"SI",megalith_type:"dolmen",wikipedia:"ca:Cova d'en Daina",wikidata:"",source:"",alt_name:"Megàlit del Coll de Fitor", comarca:"Alt Empordà"},
{name:"Cova d'en Daina",municipi:"Romanyà de la Selva",lat:41.8571228,lon:2.9927000,hi_es:"SI",megalith_type:"dolmen",wikipedia:"ca:Cova d'en Daina",wikidata:"Q3780704",source:"",alt_name:"", comarca:"Alt Empordà"},
{name:"Dolmen Caigut II",municipi:"Vilajuïga",lat:42.3301402,lon:3.1302425,hi_es:"SI",megalith_type:"passage_grave",wikipedia:"ca:Cova d'en Daina",wikidata:"",source:"",alt_name:"", comarca:"Baix Empordà"},
{name:"Dolmen de Biscarbó",municipi:"Les Valls d’Aguilar",lat:42.3443274,lon:1.2246121,hi_es:"SI",megalith_type:"dolmen",wikipedia:"ca:Dolmen de Biscarbó",wikidata:"Q19367912",source:"",alt_name:"", comarca:"Baix Empordà"}
]
*/


?>