        function getLatLon() {
            var locationInput = document.getElementById('location').value;

            // Show loading spinner
            document.getElementById('loadingSpinner').style.display = 'block';

            // Use OpenCage Geocoding API
            fetch(`https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(locationInput)}&key=API_KEY_PLACEHOLDER`)
                .then(response => response.json())
                .then(data => {
                    var latitude = data.results[0].geometry.lat;
                    var longitude = data.results[0].geometry.lng;

                    document.getElementById('id_latitude').value = latitude;
                    document.getElementById('id_longitude').value = longitude;

                    // Hide loading spinner
                    document.getElementById('loadingSpinner').style.display = 'none';

                    // Display the second form with slide-down animation
                    var homeInfoSection = document.getElementById('home-info-section');
                    homeInfoSection.style.display = 'block';
                    homeInfoSection.style.height = homeInfoSection.scrollHeight + 'px';

                    // Remove the height style to allow for automatic height adjustment
                    setTimeout(() => {
                        homeInfoSection.style.height = '';
                    }, 500);
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