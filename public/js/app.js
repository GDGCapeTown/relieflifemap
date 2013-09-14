(function(){

	// Variable for local reference to map.
	var main_map = null;

	/**
	* Returns the current lat and lng
	**/
	var get_center_latlng = function() { 

		var center_block = main_map.getCenter();
		return {

			lat: center_block.pb,
			lng: center_block.qb

		};

	}

	/**
	* Returns the Events according to filter
	**/
	var get_events_by_filter = function(search, lat, lng, fn) {

		// Build up our parameters
		var uri_params = [];

		// Always params
		uri_params.push('lat=' + lat);
		uri_params.push('lng=' + lng);

		// Add search if present
		if(search) uri_params.push('q=' + search);

		// Contact the server
		$.ajax({

			url: '/events.json?' + uri_params.join('&'),
			uri: '/events.json?' + uri_params.join('&'),
			'method': 'get',
			'dataType': 'json',
			'success': function(data_obj) { fn(null, data_obj); },
			'error': function(data_obj) { fn(data_obj); },
			'failure': function(data_obj) { fn(data_obj); }

		});

	};

	/**
	* Setup the UI bindings
	**/
	var handle_binding_setup = function() {

		// Setup our button to create
		$("#btn_create_event").click(function(){});

	};

	/**
	* Handle the when the center changes.
	**/
	var handle_center_change_of_map = function() {

		// Get the latlng
		var latlng = get_center_latlng();

		// Get the events
		get_events_by_filter(null, latlng.lat, latlng.lng, function(err, event_objs){

			console.log(event_objs.length);

		});

	};

	/**
	* Create the setup script to start google maps.
	**/
	var initialize = function() {

		// Options
		var mapOptions = {

			center: new google.maps.LatLng(-34.397, 150.644),
			zoom: 8,
			mapTypeId: google.maps.MapTypeId.ROADMAP,
			maxZoom: 8,
			minZoom: 8,
			zoomControl: false,
			disableDefaultUI: true

		};
		main_map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

		// Listen for the center change !
		google.maps.event.addListener(main_map, 'center_changed', handle_center_change_of_map);

		// Setup bindings
		handle_binding_setup();

	};

	/**
	* Handles closing the view
	**/
	var handle_extended_view_close = function(block_str, fn) {

		
		$(".overlay").animate({

			opacity: 0.25
		
		}, 50, function() {

			$(".overlay").fadeOut();
		
			$( "#map-info-block" ).animate({

				width: "40%"

			}, 500, function() {
			
				// Done !
				$(".events-hide").hide();
				$(block_str).fadeIn();

				// Callback
				fn();

			});

		});

	};

	/**
	* Handles opening the view
	**/
	var handle_extended_view_open = function(block_str, fn) {

		$(".overlay").show();
		$(".overlay").animate({

			opacity: 0.75
		
		}, 50, function() {
		
			$( "#map-info-block" ).animate({

				width: "92%"

			}, 500, function() {
			
				// Done !
				$(".events-hide").hide();
				$(block_str).fadeIn();

				// Callback
				fn();

			});

		});

	};

	// Setup to listen for google onload
	google.maps.event.addDomListener(window, 'load', initialize);

})();
