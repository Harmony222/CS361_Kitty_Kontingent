// MAP UI SCRIPT
// let LOCATIONS = {{ locations | safe }};
let map;
let markers = [];
let mapData = $('#map-data').data();

// TODO - figure out how to make the js work in this file so it can be moved from the html page
function initMap() {
    // const location = { lat: {{ lat }}, lng: {{ lon }} };
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 8,
        center: location,
    });
    setMarkers(map, LOCATIONS);
}
function addMarker(trail) {
    let marker = new google.maps.Marker({
        position: {
            lat: parseFloat(trail[1]),
            lng: parseFloat(trail[2])
        },
        map,
        // icon: icons['red'].icon,
        title: trail[0],
    });
    markers.push(marker);
}
function setMapOnAll(map) {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}
function setMarkers(map, locations) {
    const icons = {
        red: {
            icon: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        },
        yellow: {
            icon: "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
        },
        green: {
            icon: "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png",
        },
    };
    let infoWindow = new google.maps.InfoWindow({maxWidth: 400});
    for (let i = 0; i < locations.length; i++) {
        let trail = locations[i];
        let infoContent =
            `<h5>${trail[0]}</h5>` +
            `<img src="${trail[10]}" style="max-width: 300px; max-height: 300px;">` +
            `<div><p>${trail[3]}</p></div>` +
            `<div><p><strong>Length:</strong> ${trail[4]} miles</p></div>` +
            `<div><p><strong>Rating:</strong> ${trail[5]} stars</p></div>` +
            `<div><p><strong>Difficulty:</strong> ${trail[6]}</p></div>` +
            `<div><p><strong>${trail[7]}</strong></p></div>` +
            `<a href="${trail[8]}" target="_blank" role="button" class="btn btn-info btn-sm btn-marker" title="Click to open new Google Maps tab">Navigate to Trailhead</a>` +
            `<a href="${trail[9]}" target="_blank" role="button" class="btn btn-info btn-sm btn-marker" title="Click to get Customized Gear list">Gear for Trail</a>`;
        let marker = new google.maps.Marker({
            position: {
                lat: parseFloat(trail[1]),
                lng: parseFloat(trail[2])
            },
            map,
            // icon: icons['red'].icon,
            title: trail[0],
        });
        markers.push(marker);
        marker.setMap(map);
        marker.addListener("click", () => {
            infoWindow.setContent(infoContent);
            infoWindow.open(map, marker);
        });
    }
}
// changes map pins when filter slider is changed
function filterMap(difficulty) {
    // let fitness = {{ user_fitness }};
    let url = "/find_trails?difficulty=" + difficulty + "&fitness=" + fitness;
    let params = {"difficulty": difficulty, "fitness": fitness}
    const Http = new XMLHttpRequest();
    Http.open("GET", url, params);
    Http.send();
    Http.onreadystatechange = () => {
        let locations = JSON.parse(Http.response);
        // delete markers
        setMapOnAll(null);
        markers = [];
        setMarkers(map, locations);  // place new markers
    }
}
