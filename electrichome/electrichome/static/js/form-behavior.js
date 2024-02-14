function getLatLon() {
    var cityInput = document.getElementById('city').value;
    var stateInput = document.getElementById('state').value;

    var locationInput = `${cityInput}/${stateInput}`;

    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';

    fetch(`/api/geocode/${encodeURIComponent(locationInput)}/`)
        .then(response => response.json())
        .then(data => {
            if ('error' in data) {
                throw new Error(data.error);
            }

            var latitude = data.latitude;
            var longitude = data.longitude;

            document.getElementById('id_latitude').value = latitude;
            document.getElementById('id_longitude').value = longitude;

            // Hide loading spinner
            document.getElementById('loadingSpinner').style.display = 'none';

            updateUrl(cityInput, stateInput, latitude, longitude);

            // // Display the second form with slide-down animation
            // var homeInfoSection = document.getElementById('home-info-section');
            // homeInfoSection.style.display = 'block';
            // homeInfoSection.style.height = homeInfoSection.scrollHeight + 'px';
            //
            // // Remove the height style to allow for automatic height adjustment
            // setTimeout(() => {
            //     homeInfoSection.style.height = '';
            // }, 500);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Error fetching data. Please try again.');
        });
}

function disappearSubmitBtn() {
    document.getElementById("submitBtn").classList.add("submitting");
    document.getElementById("loadingMessage").classList.add("submitting");
}

function onPageLoad() {
    var urlParams = new URLSearchParams(window.location.search);

    // Check if city, state, latitude, and longitude parameters are present
    var hasCity = populateDataFromURL(urlParams, 'city');
    var hasState = populateDataFromURL(urlParams, 'state');
    var hasLat = populateDataFromURL(urlParams, 'latitude');
    var hasLon = populateDataFromURL(urlParams, 'longitude');

    if ( (hasCity && hasState) && ((hasLat && hasLon) == false) ) {
        // Trigger getLatLon to get the coordinates and update the form without the user having to.
        getLatLon();
    }
}

function populateDataFromURL(urlParams, paramName) {
    var value = urlParams.get(paramName)
    if (value != null) {
        var element = document.getElementById(paramName);
        if (element == null) { return false; }
        element.value = value
        return true;
    }
    return false;
}

function updateUrl(city, state, latitude, longitude) {
    var urlParams = new URLSearchParams(window.location.search);

    // Update or add the URL parameters
    urlParams.set('city', city);
    urlParams.set('state', state);
    urlParams.set('latitude', latitude);
    urlParams.set('longitude', longitude);

    // Create a new URL with the updated parameters
    var newUrl = window.location.pathname + '?' + urlParams.toString();

    // Update the browser URL without triggering a page reload
    history.pushState({}, '', newUrl);
}

window.addEventListener('DOMContentLoaded', (event) => {
    onPageLoad();
});