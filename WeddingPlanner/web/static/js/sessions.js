//WeddingPlanner Dashboard
//========================
//
//Simple set of graphs.
//
//
//Author
//------
//
//:author: Sami Niemi (sami.niemi@valtech.co.uk)
//
//
//Version
//-------
//
//:version: 0.1
//:date: 01-Aug-2016


queue()
    .defer(d3.json, "/WeddingPlanner/sessions")
    //.defer(d3.csv, "./static/data/waittime.csv")
    .await(makeGraphs);


function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

// create functions to generate averages for any attribute
function reduceAddAvg(attr) {
  return function(p,v) {
    if (isNumber(v[attr])) {
      ++p.count
      p.sums += v[attr];
      p.avg = (p.count === 0) ? 0 : p.sums/p.count; // guard against dividing by zero
    }
    return p;
  };
}

function reduceRemoveAvg(attr) {
  return function(p,v) {
    if (isNumber(v[attr]))  {
      --p.count
      p.sums -= v[attr];
      p.avg = (p.count === 0) ? 0 : p.sums/p.count;
    }
    return p;
  };
}

function reduceInitAvg() {
  return {count:0, sums:0, avg:0};
}


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y%m%d");

	//Get projectsJson data
	var data = projectsJson;

	//Modify
    data.forEach(function(d) {
        d.sessions = +d.sessions;
        d.bounces = +d.bounces;
        d.sessionDuration = +d.sessionDuration;
        d.bounceRate = +d.bounceRate;
        d.avgSessionDuration = +d.avgSessionDuration;
        d.date = dateFormat.parse(d.date);
    });

    //Create a Crossfilter instance
	var ndx = crossfilter(data);

	// Define Dimensions
	var timeDim = ndx.dimension(function(d) {return d.date;})
    console.log(timeDim.top(5))

    // Compute sums and counts
	var sessions = timeDim.group().reduceSum(function(d) {return +d.sessions});
	var bounces = timeDim.group().reduceSum(function(d) {return +d.bounces});
	var bounceRate = timeDim.group().reduceSum(function(d) {return +d.bounceRate});

    //Charts
	var rateChart = dc.lineChart("#rate-chart");
    var timeChart = dc.compositeChart('#time-chart');

    rateChart
        .width(1300)
        .height(300)
        .margins({top: 10, right: 10, bottom: 20, left: 40})
        .dimension(timeDim)
        .group(bounceRate)
        .transitionDuration(500)
        .elasticY(true)
        .elasticX(true)
        .brushOn(false)
        .x(d3.time.scale().domain(d3.extent(data, function(d) { return d.date; })))
        .mouseZoomable(true);

    timeChart
        .width(1300)
        .height(300)
        .margins({top: 10, right: 10, bottom: 20, left: 40})
        .dimension(timeDim)
        .group(sessions)
        .transitionDuration(500)
        .elasticY(true)
        .elasticX(true)
        .brushOn(false)
        .x(d3.time.scale().domain(d3.extent(data, function(d) { return d.date; })))
        .legend(dc.legend().gap(5))
        .renderHorizontalGridLines(true)
        .compose([dc.lineChart(timeChart)
                        .dimension(timeDim)
                        .colors('red')
                        .group(sessions, "Sessions")
                        .elasticY(true)
                        .elasticX(true),
                  dc.lineChart(timeChart)
                        .dimension(timeDim)
                        .colors('blue')
                        .group(bounces, "Bounces")
                        .elasticY(true)
                        .elasticX(true)]);

    function rangesEqual(range1, range2) {
        if (!range1 && !range2) {
            return true;
        }
        else if (!range1 || !range2) {
            return false;
        }
        else if (range1.length === 0 && range2.length === 0) {
            return true;
        }
        else if (range1[0].valueOf() === range2[0].valueOf() &&
            range1[1].valueOf() === range2[1].valueOf()) {
            return true;
        }
        return false;
    }
    // monkey-patch the first chart with a new function
    // technically we don't even need to do this, we could just change the 'filtered'
    // event externally, but this is a bit nicer and could be added to dc.js core someday
    timeChart.focusCharts = function (chartlist) {
        if (!arguments.length) {
            return this._focusCharts;
        }
        this._focusCharts = chartlist; // only needed to support the getter above
        this.on('filtered', function (range_chart) {
            if (!range_chart.filter()) {
                dc.events.trigger(function () {
                    chartlist.forEach(function(focus_chart) {
                        focus_chart.x().domain(focus_chart.xOriginalDomain());
                    });
                });
            } else chartlist.forEach(function(focus_chart) {
                if (!rangesEqual(range_chart.filter(), focus_chart.filter())) {
                    dc.events.trigger(function () {
                        focus_chart.focus(range_chart.filter());
                    });
                }
            });
        });
        return this;
    };

    timeChart.focusCharts([rateChart]);


    // register handlers
    d3.selectAll('a#all').on('click', function () {
        dc.filterAll();
        dc.renderAll();
    });

    d3.selectAll('a#time').on('click', function () {
        timeChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#rate').on('click', function () {
        rateChart.filterAll();
        dc.redrawAll();
    });


    dc.renderAll();

};