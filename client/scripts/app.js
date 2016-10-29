var map, heatmap;

function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 10,
		center: {lat: 40.668809, lng: -73.876674},
		mapTypeId: 'terrain'
	});

	heatmap = new google.maps.visualization.HeatmapLayer({
		data: [],
		dissipating: true,
		map: map
	});
}

function eqfeed_callback(results) {
	heatmap.setMap(null);
	if(type == 1) heatmapData = sum_type(results);
	else if(type == 2) heatmapData = average_type(results);
	heatmap = new google.maps.visualization.HeatmapLayer({
		data: heatmapData,
		dissipating: true,
		radius: 20,
		map: map
	});
}

function sum_type(results) {
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
		var idx = heatmapData.map(function(x) { return x.location; }).indexOf(latLng);
		if(idx != -1){
			var temp = heatmapData[idx]
			heatmapData[idx].magnitude += magnitude
		}
		else heatmapData.push(weightedLoc);
	}
	return heatmapData;
}

function average_type(results) {
	var p = results;

	var heatmapData = [];
	for (var i = 0; i < p.points.length; i++) {
		var coords = p.points[i].coordinates;
		var latLng = new google.maps.LatLng(coords[0], coords[1]);
		var magnitude = p.points[i].count;
		var weightedLoc = {
			location: latLng,
			weight: magnitude,
			iteration: 1
		};

		var idx = heatmapData.map(function(x) { return x.location; }).indexOf(latLng);
		if(idx != -1){
			var temp = heatmapData[idx]
			heatmapData[idx].magnitude = (temp.weight*temp.iteration)/(temp.iteration+1) + magnitude/(temp.iteration+1)
			heatmpaData[idx].iteration += 1;
		}
		else heatmapData.push(weightedLoc);
	}
	return heatmapData;
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
	type = 1;
};
document.getElementById("average").onclick = function(){
	type = 2;
};
