/*jslint es60*/
//API key
mapboxgl.accessToken = "pk.eyJ1IjoibGNyZXNkZWUiLCJhIjoiY2s3MTNnbXU3MDJycjNkczF1OHR2YjdmNCJ9.6eD1kNQOyOGLeiGr6udiZw";


//Map bounds
var bounds = [
    [-3.540540, 50.730483],     //SW coords
    [-3.528044, 50.741516]//NE coords
];

//Initiates the map
var mapcontainer = document.getElementById("game-map");
var map = new mapboxgl.Map({
    container: "map",
    style: 'mapbox://styles/lcresdee/ck715gk1v03sm1ipi8yo2yu20',
    center: [-3.534516, 50.735770],
    zoom: 20,
    pitch: 20,
    maxBounds: bounds,
    minZoom: 17
});


//[longitude, latitude]
var playerpos = [0, 0];


function setPlayerPos(position){
    playerpos[1] = position.coords.latitude;
    playerpos[0] = position.coords.longitude;
}

function locationError(){
    console.log("ERROR: Cannot get location");
}

function updateGeoLocation(){
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(setPlayerPos, locationError, {timeout:10000});
    } else{
        console.log("ERROR: Geolocation is not supported by this device or browser!");
    }
}

updateGeoLocation();

var playerGeo = {
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: playerpos
    },
    'properties': {
        'icon': 'monument'
    }
};

//Adds player locater GUI element
map.addControl(new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    },
    trackUserLocation: true
}));

const metersToPixelAtMaxZoom = (meters, latitude) => meters / 0.075 / Math.cos(latitude * Math.PI / 180)

//Called when map loads
map.on('load', function(){
    map.addSource('player', {
        'type': 'geojson',
        'data': {
            'type' : 'FeatureCollection',
            'features': [playerGeo]
        }
    });
    map.addLayer({
        'id': 'player',
        'type': 'symbol',
        'source': 'player',
        'layout': {
            'icon-image': ['concat', ['get', 'icon'], '-15'],
            'icon-size': 2.0
        }
        
    });
    var jsonURL = "/static/scripts/playerlocations.geojson";
    map.addSource('others', {

        'type': 'geojson',
        'data': jsonURL
    });
    map.addLayer({
        'id': 'others',
        'type': 'circle',
        'source': 'others',
        'paint': {
            'circle-radius': {
                stops: [[0,6], [20, 20]],
                base: 2
            }, 
            'circle-color': '#0783ff'
        }
    });
    map.addSource('start-zone', {
        'type': 'geojson',
        'data': {
            'type': 'Feature',
            'geometry':{
                'type': 'Point',
                'coordinates': [-3.534516, 50.735770]
            }
        }
    });
    map.addLayer({
        'id': 'start-zone',
        'source': 'start-zone',
        'type': 'circle',
        'paint': {
            'circle-color': '#52d1ff',
            'circle-opacity': 0.4,
            'circle-stroke-color': '#0a7aa3',
            'circle-stroke-width': 2,
            'circle-radius': {
                stops: [[0,0],
                        [20, metersToPixelAtMaxZoom(30, -3.534516)]],
                base: 2
            }
        }
    });
});

var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};

var cardsjson;
getJSON("https://localhost:5000/loadcards", function(error, data){
        cardsjson = data;
        });

console.log(cardsjson);

for (var i = 0; i < cardsjson.length; i++){
    var cardobj = json[i];
    new mapboxgl.Marker().seLngLat([cardobj.coordinates[1], cardobj.coordinates[0]]).addTo(map);
}

map.flyTo({
    center: playerpos
});