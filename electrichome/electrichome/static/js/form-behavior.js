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