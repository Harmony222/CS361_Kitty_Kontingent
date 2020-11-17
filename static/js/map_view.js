// for map view of trails list

function initMap() {
    const location = { lat: {{ lat }}, lng: {{ lon }} };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 8,
        center: location,
    });
    setMarkers(map);
}

let LOCATIONS = {{ locations | safe }};
function setMarkers(map) {
    const icons = {
        red: { icon: "http://maps.google.com/mapfiles/kml/paddle/red-circle.png", },
        yellow: { icon: "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png", },
        green: { icon: "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png", },
    };
    for (let i = 0; i < LOCATIONS.length; i++) {
        let trail = LOCATIONS[i];
        let infoWindow = new google.maps.InfoWindow({
            content: `<h6>${trail[0]}</h6><div><p>${trail[3]}</p></div>`,
            maxWidth: 200,
        });
        let marker = new google.maps.Marker({
            position: { lat: parseFloat(trail[1]), lng: parseFloat(trail[2]) },
            map,
            // icon: icons['red'].icon,
            title: trail[0],
        });
        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });
    }
}