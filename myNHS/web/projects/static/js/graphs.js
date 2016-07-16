queue()
    .defer(d3.json, "/myNHS/hipReplacements")
    .await(makeGraphs);

function makeGraphs(error, projectsJson) {
	
	//Get projectsJson data
	var hipReplacements = projectsJson;
	console.log(hipReplacements)

    //Create a Crossfilter instance
	var ndx = crossfilter(hipReplacements);
	var all = ndx.groupAll();
	console.log("All Reduced Count:" + all.reduceCount().value())

	// Simple Output
	var n = ndx.size();
	console.log("Total Data:" + n)

	// Define Dimensions
	var Latitude = ndx.dimension(function(d) { return d.Latitude; });
	var Longitude = ndx.dimension(function(d) { return d.Longitude; });
	var OrganisationNameDim = ndx.dimension(function(d) { return d.OrganisationName; });
	var MetricNameDim = ndx.dimension(function(d) { return d.MetricName; });
	var ValueDim = ndx.dimension(function(d) { return +d.Value; });

    // Set up Groups
	var ValueGroup = ValueDim.group()
	var OrganisationNameGroup = OrganisationNameDim.group()
	var MetricNameGroup = MetricNameDim.group()

    // Compute Total Hips
	var TotalHips = OrganisationNameGroup.reduceSum(function(d) {return d.Value;})
	console.log(TotalHips.top(3))

    //Charts
	var Chart = dc.rowChart("#row-chart");
	var number = dc.numberDisplay("#number-projects-nd");

	//var dataTable = dc.dataTable("#data-table");

	Chart
        .width(650)
        .height(3000)
        .gap(2)
        .dimension(OrganisationNameDim)
        .group(TotalHips)
        .elasticX(true)
        .ordering(function(d) { return -d.value })
        .label(function (d) { return d.key })
        .title(function (d) { return d.value });

	number
        .formatNumber(d3.format("d"))
        .valueAccessor(function(d){return d; })
        .group(all);

    dc.renderAll();

};