var map = null;

function initialize() {

	var mapOptions = {
	center: new google.maps.LatLng(-33.957030 , 18.436089),
	zoom: 8,
	mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map-canvas"),
	mapOptions);

	google.maps.event.addListener(map, 'center_changed', function() {

		load_events_from_map();

	});


	load_events_from_map();

	var drawingManager = new google.maps.drawing.DrawingManager({
    drawingControl: true,
    drawingControlOptions: {
      position: google.maps.ControlPosition.TOP_CENTER,
      drawingModes: [
        google.maps.drawing.OverlayType.POLYGON
      ]
    }
});
  drawingManager.setMap(map);
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
