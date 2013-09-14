var map = null;

function initialize() {

	var mapOptions = {
	center: new google.maps.LatLng(-33.987210, 18.558585),
	zoom: 8,
	mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map-canvas"),
	mapOptions);

	google.maps.event.addListener(map, 'center_changed', function() {

		load_events_from_map();

	});
	
	var stuffToPlot = [
                new google.maps.LatLng(-33.904616, 18.416605),
                new google.maps.LatLng(-33.987210, 18.338585),
                new google.maps.LatLng(-34.112373, 18.829536),
                new google.maps.LatLng(-33.874976, 18.733063)
        ];
    var drawingManager = new google.maps.drawing.DrawingManager({
		drawingMode: google.maps.drawing.OverlayType.MARKER,
		drawingControl: true,
		drawingControlOptions: {
		position: google.maps.ControlPosition.TOP_CENTER,
		drawingModes: [
        google.maps.drawing.OverlayType.POLYGON
      ]
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
   somePolygon = new google.maps.Polygon({
    paths: stuffToPlot,
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#FF0000',
    fillOpacity: 0.35
  });
  somePolygon.setMap(map);
  drawingManager.setMap(map);



	load_events_from_map();
}
google.maps.event.addDomListener(window, 'load', initialize);

var load_events_from_map = function() {

	$(".events-hide").hide();
	$("#events-loading").show();

	var center_block = map.getCenter();
	var lat = center_block.pb;
	var lng = center_block.qb;

	$.ajax({

		url: '/events.json',
		uri: '/events.json',
		'method': 'get',
		dataType: 'json',
		'success': function(data_obj) {

			$(".events-hide").hide();

			var html = '';

			if(data_obj.length > 0) {

				$(data_obj).each(function(){
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

				$(".overlay").show();
				$( ".overlay" ).animate({

					opacity: 0.75
				
				}, 50, function() {
				
					$( "#map-info-block" ).animate({

						width: "92%"

					}, 1000, function() {
					
						// Done !
						$(".events-hide").hide();
						$("#events-view").fadeIn();

					});

				});

			});

		}

	});

};

$(document).ready(function(){

	

});

