(function(){

	// Options
	var mapOptions = {

		center: new google.maps.LatLng(-34.397, 150.644),
		zoom: 10,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		maxZoom: 10,
		minZoom: 10,
		zoomControl: false,
		disableDefaultUI: true

	};

	var changing_center = 1;
	var changing_lat = null;
	var created_points = [];

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

				html = html + '<a data-id="' + event_obj.id + '" data-lng="' + event_obj.lng + '" data-lat="' + event_obj.lat + '" href="#" class="event-list-block"> \
						<h4>' + event_obj.headline + '</h4> \
						<span class="reach"> \
							<img src="/img/reach.png" /> \
							<h6>' + event_obj.reach + ' people</h6> \
						</span> \
					</a>';

			});

			$("#events-listing").html(html);
			$("#events-listing").show();

		} else $("#events-none").show();	

		// Listen for clicks on blocks
		$(".event-list-block").unbind();
		$(".event-list-block").on('mouseover', function(){

			changing_center = 0;

			var lat = $(this).attr('data-lat');
			var lng = $(this).attr('data-lng');

			if(changing_lat != lat) {

				changing_lat = lat;
				main_map.setCenter(new google.maps.LatLng( (1*lat) , (1*lng) + 0.4 ));

			}

			changing_center = changing_center + 1;

		});
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

	var center_to_current_location = function() {

		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(success, error);
		}

		function success(position) {
			main_map.setCenter(new google.maps.LatLng( (1*position.coords.latitude), 
                                     (1*position.coords.longitude) + 0.4));

		}

		function error(msg) {
		}

	};

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
		$("#delete-user").click(function(){
								var id = $(this).attr('data-user-id');

                                $.ajax({

                                    type: 'get',
                                    url: '/users/delete/' + id,
                                    data: {
                                    },
                                    'success': function() {

                                        // Done !
                                    },
                                    'error': function(){}


                                });
		});

	var handle_binding_setup = function() {

		// Setup our button to create
		$(".btn_center_map").click(function(){

			// Force it open
			if (navigator.geolocation) {
				navigator.geolocation.getCurrentPosition(success, error);
			}

			function success(position) {
				select_map.setCenter(new google.maps.LatLng( (1*position.coords.latitude), 
	                                     (1*position.coords.longitude) + 0.4));

			}

			function error(msg) {
			}

			// Stop it here
			return false;

		});

		$(".btn_extended_close").click(function(){

			handle_extended_view_close('#events-listing', function(){});
            request_queue.drain();

		});

		// Setup our button to create
		$("#btn_create_event").click(function(){

			// Force it open
			handle_extended_view_open('#events-create', function(){

				// Set

			});

			// Stop it here
			return false;

		});

		// Setup our button to create
		$("#btn_manage_users").click(function(){
           $(".extended_open").show();
           $(".extended_close").hide();
           $(".events-hide").hide();
           $('#manage_users').fadeIn();

			// Stop it here
			return false;

		});

        $("#btn_select_create_user").click(function(){
                                var username = $("#txt_create_user").val();
                                var email = $("#txt_create_useremail").val();

                                $.ajax({

                                    type: 'post',
                                    url: '/users/create',
                                    data: {
                                        name: username,
                                        email: email,
                                    },
                                    'success': function() {

                                        // Done !
                                        header_hide();
                                        $(".mapping-canvas").hide();
                                        $("#map-canvas,#map-info-block,.overlay").show();

                                        handle_extended_view_close('#events-listing', function(){

                                            // Update list
                                            handle_center_change_of_map();

                                        });

                                    },
                                    'error': function(){}


                                });

        });

		$("#btn_select_create_event_points").click(function(){

			$(".mapping-canvas, #map-info-block, .overlay").hide();
			$("#select-point-map-canvas").show();

			if(!select_map) {

				// select-point-map-canvas
				select_map = new google.maps.Map(document.getElementById('select-point-map-canvas'), mapOptions);

				var drawingManager = new google.maps.drawing.DrawingManager({
				
					drawingMode: google.maps.drawing.OverlayType.POLYGON,
					drawingControl: true,
					drawingControlOptions: {
					position: google.maps.ControlPosition.TOP_CENTER,
					drawingModes: [
					google.maps.drawing.OverlayType.MARKER,
					google.maps.drawing.OverlayType.CIRCLE,
					google.maps.drawing.OverlayType.POLYGON,
					google.maps.drawing.OverlayType.POLYLINE,
					google.maps.drawing.OverlayType.RECTANGLE
					]
					},

				});
				drawingManager.setMap(select_map);

				google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event) {

					// Listen for poly
					if (event.type == google.maps.drawing.OverlayType.POLYGON) {

						var headline = $("#txt_create_headline").val();
						var reach = $("#txt_create_reach").val();
						var date = $("#txt_create_date").val();
						var description = $("#txt_create_desc").val();
						var howtohelp_txt = $("#txt_create_howtohelp").val();

						var path_obj = event.overlay.getPaths().getArray();
						if(path_obj) {

							var paths = path_obj[0];
							if(paths) {

								paths = paths.getArray();
								var lats = [];
								var lngs = [];

								paths.forEach(function(path_obj){

									lats.push(path_obj.pb);
									lngs.push(path_obj.qb);

								});

								$.ajax({

									type: 'post',
									url: '/events/save',
									data: {

										headline: headline,
										lat: lats.join(','),
										lng: lngs.join(','),
										reach: reach,
										date: date,
										description: description,
										howtohelp: howtohelp_txt

									},
									'success': function() {

										// Done !
										header_hide();
										$(".mapping-canvas").hide();
										$("#map-canvas,#map-info-block,.overlay").show();

										handle_extended_view_close('#events-listing', function(){

											// Update list
											handle_center_change_of_map();

										});

									},
									'error': function(){}


								});

							}

						}

					}

				});

			}

			header_show('#header-select-region');

		});

	};

	/**
	* Handle the when the center changes.
	**/
	var handle_center_change_of_map = function() {

		if(changing_center > 0) {

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

		}

	};

	/**
	* Create the setup script to start google maps.
	**/
	var initialize = function() {

		// Options
		
		main_map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

		var drawingManager = new google.maps.drawing.DrawingManager({
			drawingControl: false
		});

		drawingManager.setMap(main_map);

		// Listen for the center change !
		google.maps.event.addListener(main_map, 'center_changed', handle_center_change_of_map);

		// Setup center
		handle_center_change_of_map();

		center_to_current_location();

		// Setup bindings
		handle_binding_setup();

		handle_render_markers();

	};

	/**
	* Handles closing the view
	**/
	var handle_extended_view_close = function(block_str, fn) {

		$(".extended_open").hide();
		$(".extended_close").show();

		
		$(".overlay").animate({

			opacity: 0.25
		
		}, 50, function() {

			$(".overlay").fadeOut();
		
			$( "#map-info-block" ).animate({

				width: "40%"

			}, 500, function() {
			
				// Done !
				$("#manage_users").hide();
				$("#events-create").hide();
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

		$(".extended_open").show();
		$(".extended_close").hide();

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

	var handle_render_mark = function(event_id, points) {

		var stuffToPlot = [
		new google.maps.LatLng(-33.904616, 18.416605),
		new google.maps.LatLng(-33.987210, 18.338585),
		new google.maps.LatLng(-34.112373, 18.829536),
		new google.maps.LatLng(-33.874976, 18.733063)
		];
		
		var new_plot = new google.maps.Polygon({
		paths: stuffToPlot,
		strokeColor: '#FF0000',
		strokeOpacity: 0.8,
		strokeWeight: 2,
		fillColor: '#FF0000',
		fillOpacity: 0.35
		});
		new_plot.setMap(main_map);

		google.maps.event.addListener(new_plot, 'mouseout', function(event) {

			$('.event-list-block').removeClass('active');

	    });

		google.maps.event.addListener(new_plot, 'mousemove', function(event) {

			$('.event-list-block').removeClass('active');
			$('.event-list-block[data-id="' + event_id + '"]').addClass('active');

	    });

		google.maps.event.addListener(new_plot, 'click', function(event) {
	     	$('.event-list-block[data-id="' + event_id + '"]').click();
	    });

	};

	var handle_render_markers = function() {

		handle_render_mark(5785905063264256, []);

	};

	// Setup to listen for google onload
	google.maps.event.addDomListener(window, 'load', initialize);

})();
