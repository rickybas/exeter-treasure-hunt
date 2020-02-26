mapboxgl.accessToken = "pk.eyJ1IjoibGNyZXNkZWUiLCJhIjoiY2s3MTNnbXU3MDJycjNkczF1OHR2YjdmNCJ9.6eD1kNQOyOGLeiGr6udiZw";

var bounds = [
    [-3.540540, 50.730483],     //SW coords
    [-3.528915, 50.742147]      //NE coords
];

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



map.addControl(new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    },
    trackUserLocation: true
}))

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
});

map.flyTo({
    center: playerpos
});

