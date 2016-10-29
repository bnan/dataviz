var map;

function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 10,
		center: {lat: 40.668809, lng: -73.876674},
		mapTypeId: 'terrain'
	});

	// Create a <script> tag and set the USGS URL as the source.
	var script = document.createElement('script');
}

function eqfeed_callback(results) {
	var p = results;

	var heatmapData = [];
	for (var i = 0; i < p.points.length; i++) {
		var coords = p.points[i].coordinates;
		var latLng = new google.maps.LatLng(coords[0], coords[1]);
		var magnitude = p.points[i].count;
		var weightedLoc = {
			location: latLng,
			weight: magnitude
		};
		heatmapData.push(weightedLoc);
	}
	var heatmap = new google.maps.visualization.HeatmapLayer({
		data: heatmapData,
		dissipating: true,
		map: map
	});
}

var type = 1;

document.getElementById("filterByDate").onclick = function() {
	var startDate = $('#startDate').val();
	var endDate = $('#endDate').val();
	var getString = "/api" + "?date_start=" + startDate + "&date_end=" + endDate;

	$.get(getString, function(data) {
		eqfeed_callback(data);
	}, "json")
		.fail(function() {
			alert( "error" );
		});
};

document.getElementById("sum").onclick = function(){
	console.log(type);
	if (type != 1) {
		type = 1;
	}
};
document.getElementById("average").onclick = function(){
	console.log(type);
	if (type != 2) {
		type = 2;
	}
}; 
