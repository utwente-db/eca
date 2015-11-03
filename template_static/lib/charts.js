(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart = function(config) {
    // combine default configuration with user configuration
    var options = $.extend({
        memory: 100,
	// required!!
        series: {
            'default': {data: []}
        },
	// flot initialization options
        options: {
            xaxis: {
                show: false
            }
        }
    }, config);

    // maintain state for this block
    var data = {};
    for(var k in options.series) {
        data[k] = (options.series[k].data || []).slice();
    }

    // function to project our state to something the library understands
    var prepare_data = function() {
        var result = [];

        // process each series
        for(var k in data) {
            var series = data[k];
            var points = [];

            // create point pairs and gap values
            for(var i in series) {
                if(series[i] == null) {
                    points.push(null);
                } else {
                    points.push([i, series[i]]);
                }
            }

            // combine state data with series configuration by user
            result.push($.extend(options.series[k], {data: points}));
        }

        return result;
    };

    // initial setup of library state (also builds necessary HTML)
    var plot = $.plot(this.$element, prepare_data(), options.options);


    // register actions for this block
    this.actions({
        'add': function(e, message) {
            // if the 'value' field is used, update all series (useful with a single series)
            if(typeof message.values == 'undefined' && typeof message.value != 'undefined') {
                message.values = {}
                for(var k in options.series) {
                    message.values[k] = message.value;
                }
            }

            // update all series
            for(var k in options.series) {
                // roll memory
                if(data[k].length > options.memory) {
                    data[k] = data[k].slice(1);
                }

                // insert value or gap
                data[k].push(message.values[k] || null);
            }

            // update HTML
            plot.setData(prepare_data());
            plot.setupGrid();
            plot.draw();
        }
    });

    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple linechart example
block.fn.linechart = function(config) {
    var options = $.extend({
	// required
        series : {default:{}},
	// flot initialization options
        options : {}
    }, config);

    // create empty linechart with parameter options
    var plot = $.plot(this.$element, [],options.options);

    // dict containing the labels and values
    var linedata_series = {};
    var linedata_first;

    var initline = function(series) {
	linedata_first = undefined;
	for(var k in series) {
	   var si = series[k];
	   si.data = [];
	   linedata_series[k] = si;
	   if ( linedata_first == undefined )
	       linedata_first = si;
	}
    }

    initline(options.series);

    var addline = function(label, values) {
    	var data;

	if (linedata_series.hasOwnProperty(label))
		data = linedata_series[label].data;
	else
		data = linedata_first.data;
	for(var v in values) {
		data.push(values[v]);
	}
	redraw();
    }

    var setline = function(label, values) {
	if (linedata_series.hasOwnProperty(label))
		linedata_series[label].data = values;
	else
		linedata_first.data = values;
	redraw();
    }

    var redraw = function() {
        var result = [];
    	for(var k in linedata_series) {
	    if (linedata_series.hasOwnProperty(k)) {
	    	var line_serie = linedata_series[k];

 		result.push({label:k,data:line_serie.data});
	    }
	}
        plot.setData(result);
	plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	initline(options.series);
    }

    this.actions({
        'set': function(e, message) {
	    setline(message.series, message.value);
        },
        'add': function(e, message) {
	    addline(message.series, message.value);
        },
        'reset': function(e, message) {
	    reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple barchart example
block.fn.barchart = function(config) {
    var options = $.extend({
        filter_function : function(category,val,max) { return true; },
	// required
    	series : { "default":{
        	data: {},
        	label: "default",
        	bars: {
                	show: true,
                	barWidth: 0.2,
                	align: "left"
            	}
       	 
    	} },
	// flot initialization options
	options: { xaxis: {
                mode: "categories",
                tickLength: 0
            }}

    }, config);

    var bardata_series = options.series;
    var bardata_first;

    for (bardata_first in bardata_series) break;

    var translate_bar = function() {
        var result = [];
	for(var k in bardata_series) {
	    if (bardata_series.hasOwnProperty(k)) {
		var newserie = jQuery.extend({}, bardata_series[k]);
        	var newdata = [];
		var data = newserie.data;
		var max = 0;

		for(var l in data) {
	    	    if (data.hasOwnProperty(l)) {
                        max = Math.max(max, data[l]);
		    }
		}

		for(var l in data) {
	    	    if (data.hasOwnProperty(l)) {
		        if ( options.filter_function(l,data[l],max) )
			    newdata.push([l,data[l]]);
		    }
		}
		newserie.data = newdata;
		result.push(newserie);
	    }
	}
	return result;
    }

    var plot = $.plot(this.$element, translate_bar(), options.options);

    var addbar = function(serie_label, category, value) {
    	var data;

    	if ( serie_label == undefined )
		data = bardata_series[bardata_first].data;
	else 
		data = bardata_series[serie_label].data;
	if (data.hasOwnProperty(category))
		data[category] = (data[category] + value);
	else
		data[category] = value;
	redraw();
    }

    var setbar = function(serie_label, category, value) {
    	var data;

    	if ( serie_label == undefined )
		data = bardata_series[bardata_first].data;
	else 
		data = bardata_series[serie_label].data;
	data[category] = value;
	redraw();
    }

    var redraw = function() {
        plot.setData(translate_bar());
	plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	for(var k in bardata_series) {
	    if (bardata_series.hasOwnProperty(k)) {
		bardata_series[k].data = {};
	    }
	}
    }

    this.actions({
        'set': function(e, message) {
		setbar(message.series,message.value[0],message.value[1]);
        },
        'add': function(e, message) {
		addbar(message.series,message.value[0],message.value[1]);
        },
        'reset': function(e, message) {
		reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple piechart example
block.fn.piechart = function(config) {
    var options = $.extend({
    	// see: http://www.flotcharts.org/flot/examples/series-pie/
        filter_function : function(category,val,max) { return true; },
        options : {
		series: {	
			pie: {
                		show: true
        		}
    		},
		// demo crashes with this option
		// legend: { show: false }
    }}, config);

    // create empty piechart with parameter options
    var plot = $.plot(this.$element, [],options.options);

    // dict containing the labels and values
    var piedata_dict = {};

    var addpie = function(label, value) {
	if (piedata_dict.hasOwnProperty(label))
		piedata_dict[label] = (piedata_dict[label] + value);
	else
		piedata_dict[label] = value;
	redraw();
    }

    var setpie = function(label, value) {
	piedata_dict[label] = value;
	redraw();
    }

    var redraw = function() {
        var result = [];
	var max = 0;

	for(var k in piedata_dict) {
	    if (piedata_dict.hasOwnProperty(k)) {
                max = Math.max(max, piedata_dict[k]);
	    }
	}
	for(var k in piedata_dict) {
	    if (piedata_dict.hasOwnProperty(k)) {
		if ( options.filter_function(k,piedata_dict[k],max) )
 		    result.push({label:k,data:piedata_dict[k]});
	    }
	}
        plot.setData(result);
        plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	piedata_dict = {};
    }

    this.actions({
        'set': function(e, message) {
	    setpie(message.value[0],message.value[1]);
        },
        'add': function(e, message) {
	    addpie(message.value[0],message.value[1]);
        },
        'reset': function(e, message) {
	    reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
