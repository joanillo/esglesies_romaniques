var map;
var tipusMapa;

var esglesies;
var vectorLayerIcones = [];

//https://stackoverflow.com/questions/27658280/layer-switching-in-openlayers-3
var layersOSM = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			source: new ol.source.OSM()
		})
	]
});


var layersWatercolor = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			source: new ol.source.Stamen({
				layer: 'watercolor'
			})
		})
	]
});

var layersToner = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			source: new ol.source.Stamen({
				layer: 'toner'
			})
		})
	]
});

var layersTerrain = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			source: new ol.source.Stamen({
				layer: 'terrain'
			})
		})
	]
});

//var projection = ol.proj.get('EPSG:25831');
//projection.setExtent([257904,4484796,535907,4751795]);
//var extent = [257904,4484796,535907,4751795];
var layersICGC = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			//extent: extent,
			source: new ol.source.TileWMS({
				url: 'http://mapcache.icc.cat/map/bases/service?',
				params: {
					'LAYERS': 'topo'
				}
			})
		})
	]
});

var layersOrtoFoto = new ol.layer.Group({
	layers: [
		new ol.layer.Tile({
			//extent: extent,
			source: new ol.source.TileWMS({
				url: 'http://mapcache.icc.cat/map/bases/service?',
				params: {
					'LAYERS': 'orto'
				}
			})
		})
	]
});


function setMapType(newType, filt) {

	tipusMapa = newType;

	if(newType == 'OSM') {
		map.setLayerGroup(layersOSM);
	} else if (newType == 'watercolor') {
		map.setLayerGroup(layersWatercolor);
	} else if (newType == 'toner') {
		map.setLayerGroup(layersToner);
	} else if (newType == 'terrain') {
		map.setLayerGroup(layersTerrain);
	} else if (newType == 'ICGC') {
		map.setLayerGroup(layersICGC);
	} else if (newType == 'ortofoto') {
		map.setLayerGroup(layersOrtoFoto);
	}

	//finalment, aquesta és la línia per eliminar tota la capa d'icones
	//sempre que cridem setMapType ja havíem pintat les icones, i per tant, aquí és un bon lloc per fer-ho
	//així és com es fa amb OpenLayers 4
	//https://gis.stackexchange.com/questions/251770/how-can-i-clear-a-vector-layer-features-in-openlayers-4
	vectorLayericones.getSource().clear()

	vectorLayerIcones = [];
				init_layer(filt);

	tancar_popup();
}

function init_mapa() {

	var tipusMapa = 'terrain';

	var renderOSM = [
		new ol.layer.Tile({
			source: new ol.source.OSM()
		})
	]

	var renderTerrain = [
		new ol.layer.Tile({
			source: new ol.source.Stamen({
				layer: 'terrain'
			})
		})
	]

	map = new ol.Map({
		target: 'map',
		layers: renderTerrain,
		view: new ol.View({
			center: ol.proj.fromLonLat([2.2,41.7]),
			zoom: 9
		})
	});


	var renderICGC = [
		new ol.layer.Tile({
			source: new ol.source.TileWMS({
					url: 'http://mapcache.icc.cat/map/bases/service?',
					params: {
							'LAYERS': 'topo'
					}
			})
		})
	]

	init_layer('');

}


function init_layer(filt) {

	if (filt=="") {
		//d'entrada dibuixem totes les esglésies
		var esglesies = esglesies_complet
	} else {
		var esglesies = esglesies_complet.filter(function (el) {
			//puc cercar per nom de l'església, municipi o comarca
			return (el.name.toLowerCase().indexOf(filt.toLowerCase()) >=0 || el.municipi.toLowerCase().indexOf(filt.toLowerCase()) >=0 || el.comarca.toLowerCase().indexOf(filt.toLowerCase()) >=0 )? el.name : null;
		});
	}

	var icones = [];

	for (var i=0;i<esglesies.length;i++) {
		var iconPoint = new ol.Feature({
			geometry: new ol.geom.Point(ol.proj.fromLonLat([esglesies[i].lon,esglesies[i].lat]))
		});
		var txt = "";
		
		if (esglesies[i].ruins == "yes") {
			txt += "<img src='img/ruins-16.png' alt='ruins' />&nbsp;"
		} else {
			txt += "<img src='img/church2-16.png' alt='ruins' />&nbsp;"		
		}
		
		txt += "<b>" + esglesies[i].name + "</b><br />";
		if(typeof esglesies[i].alt_name !== 'undefined' && esglesies[i].alt_name != '') txt += esglesies[i].alt_name + "<br />";
		txt += esglesies[i].municipi + "<br />";
		if (esglesies[i].wikipedia != "") txt += "<a href=\"http://ca.wikipedia.org/wiki/" + esglesies[i].wikipedia.replace("ca:","") + "\" target=\"_blank\">+info</a>&nbsp;-&nbsp;";
		txt += "<a href=\"#\" onclick=\"veure_esglesia(" + esglesies[i].lat + "," + esglesies[i].lon + ");\">zoom</a>&nbsp;-&nbsp;";
		txt += "<a href=\"#\" onclick=\"tancar_popup()\">close</a>&nbsp;";
		var estil = new ol.style.Style({
			fill: new ol.style.Fill({
				color: 'rgba(255,255,255,1)'
			}),
			image: new ol.style.Icon(({
					anchor: [0.5, 1],
					src: "./img/" + "church2-16.png"
			})),
			stroke: new ol.style.Stroke({
					color: '#3399CC',
					width: 3.25
			}),
			text: new ol.style.Text({
					font: '14px Calibri,sans-serif',
					offsetY: '-15',
					textAlign: 'left',
					fill: new ol.style.Fill({ color: '#000' }),
					stroke: new ol.style.Stroke({
						color: '#fff', width: 2
					}),
			})
		});

		var estil_ruines = new ol.style.Style({
			fill: new ol.style.Fill({
				color: 'rgba(255,255,255,1)'
			}),
			image: new ol.style.Icon(({
				anchor: [0.5, 1],
				src: "./img/" + "ruins-16.png"
			})),
			stroke: new ol.style.Stroke({
				color: '#3399CC',
				width: 3.25
			}),
			text: new ol.style.Text({
				font: '14px Calibri,sans-serif',
				offsetY: '-15',
				textAlign: 'left',
				fill: new ol.style.Fill({ color: '#000' }),
				stroke: new ol.style.Stroke({
					color: '#fff', width: 2
				}),
			})
		});

		if (esglesies[i].ruins == "yes") {
			iconPoint.setStyle(estil_ruines);
		} else {
			iconPoint.setStyle(estil);			
		}

		iconPoint.set('description', txt);
		icones.push(iconPoint);
	}
	var vectorSourceicones = new ol.source.Vector({
		features: icones
	});

	vectorLayericones = new ol.layer.Vector({
		source: vectorSourceicones
	});
	vectorLayerIcones.push(vectorLayericones);

	map.addLayer(vectorLayericones);

	map.on("click", function(e) {
		map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
			if (feature.N.description != undefined) {
				//console.log(feature.N.description);
				var txt = feature.N.description;
				document.getElementById('popup').style.visibility="visible";
				//document.getElementById('popup').style.display="block";
				var content = document.getElementById('popup-content');
				content.innerHTML = txt;
			}
		})
	});
}


function styleFunction() {
	return [
		new ol.style.Style({
			fill: new ol.style.Fill({
				color: 'rgba(255,255,255,1)'
			}),
			image: new ol.style.Icon(({
				anchor: [0.5, 1],
				src: "./img/church2-16.png"
			})),
			stroke: new ol.style.Stroke({
				color: '#3399CC',
				width: 3.25
			}),
			text: new ol.style.Text({
				font: '14px Calibri,sans-serif',
				offsetY: '-15',
				textAlign: 'left',
				fill: new ol.style.Fill({ color: '#000' }),
				stroke: new ol.style.Stroke({
					color: '#fff', width: 2
				}),
			})
		})
	];
}

function compare(a, b) {
	// Use toUpperCase() to ignore character casing
	const municipiA = a.municipi.toUpperCase();
	const municipiB = b.municipi.toUpperCase();

	var comparison = 0;
	if (municipiA > municipiB) {
			comparison = 1;
	} else if (municipiA < municipiB) {
			comparison = -1;
	}
	return comparison;
}

function veure_esglesia(lat,lon) {
	var coordinate= [lon,lat];
	map.getView().setZoom(14);
	map.getView().setCenter(ol.proj.transform(coordinate, 'EPSG:4326', 'EPSG:3857'));
	map.render()
}

function tancar_popup() {
	document.getElementById('popup').style.visibility = "hidden";
}

function filtrar_esglesies() {
	var filt = document.forms[0].elements[0].value
	document.forms[0].elements[0].value = "";

	setMapType(tipusMapa, filt)
}