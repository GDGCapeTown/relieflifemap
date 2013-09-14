(function(){

	// Shown
	var event_objs_currently_shown = [];

	// The queue
	var request_queue = async.queue(function (task, callback) {

		get_events_by_filter(task.query, task.lat, task.lng, function(err, eventing_objs){

			event_objs_currently_shown = eventing_objs;
			callback();

		});

	}, 1);

	// Render the items
	request_queue.drain = function() {

		$(".events-hide").hide();

		if(event_objs_currently_shown && event_objs_currently_shown.length > 0) {

			var html = '';

			$(event_objs_currently_shown).each(function(){
				var event_obj = this;

				html = html + '<a href="#" class="event-list-block"> \
						<h4>' + event_obj.headline + '</h4> \
						<span class="reach"> \
							<img src="/img/reach.png" /> \
							<h6>4000 people</h6> \
						</span> \
					</a>';

			});

			$("#events-listing").html(html);
			$("#events-listing").show();

		} else $("#events-none").show();	

		// Listen for clicks on blocks
		$(".event-list-block").unbind();
		$(".event-list-block").on('click', function(){

			handle_extended_view_open('#events-view', function(){});

		});

	}

	// Variable for local reference to map.
	var main_map = null;
	var select_map = null;

	/**
	* Shows a header
	**/
	var header_show = function(block) {

		$(".overhead-header").hide();
		if(block) $(block).slideDown();

	};

	/**
	* Shows a header
	**/
	var header_hide = function(block) {

		$(".overhead-header").slideUp();

	};

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
		$("#btn_create_event").click(function(){

			// Force it open
			handle_extended_view_open('#events-create', function(){

				// Set

			});

			// Stop it here
			return false;

		});

		$("#btn_select_create_event_points").click(function(){

			$("#map-info-block").hide();
			$(".overlay").hide();
			header_show('#header-select-region');

		});

	};

	/**
	* Handle the when the center changes.
	**/
	var handle_center_change_of_map = function() {

		// Get the latlng
		var latlng = get_center_latlng();

		// Setup Loading
		$(".events-hide").hide();
		$("#events-loading").show();

		// Render !
		request_queue.push({

			lat: latlng.lat,
			lng: latlng.lng,
			query: ''

		}, function(err){

			// Bla !

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

		// select-point-map-canvas
		select_map = new google.maps.Map(document.getElementById('select-point-map-canvas'), mapOptions);

		var drawingManager = new google.maps.drawing.DrawingManager({
		drawingMode: google.maps.drawing.OverlayType.MARKER,
		drawingControl: true,
		drawingControlOptions: {
		position: google.maps.ControlPosition.TOP_CENTER,
		drawingModes: [
		google.maps.drawing.OverlayType.POLYGON
		]
		},
		markerOptions: {
		icon: 'images/beachflag.png'
		},
		circleOptions: {
		fillColor: '#ffff00',
		fillOpacity: 1,
		strokeWeight: 5,
		clickable: false,
		editable: true,
		zIndex: 1
		}
		});
		drawingManager.setMap(select_map);

		// Setup center
		handle_center_change_of_map();

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
