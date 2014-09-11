(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart = function(config) {
    var options = $.extend({
        memory: 100,
        series: { serie : {label:"serie", color:'black'} }
    }, config);

    var handle_data = function(values) {
        var result = [];

        for(var i in values) {
            result.push([i, values[i]]);
        }
        return result;
    };

    var xo = { series: {
            lines: { show: true },
            points: {
                radius: 3,
                show: true,
                fill: true
            }
        }};

    var plot = $.plot(this.$element, [] , {});

    var reset = function() {
        var result = options.series;
	for(var k in result) {
	    if (result.hasOwnProperty(k)) {
	        result[k].databuffer = [];
	    }
	}
	return result;
    }

    var plot_series = reset();

    var add_to_serie = function(skey,value) {
	var databuffer = plot_series[skey].databuffer;
        if(databuffer.length > options.memory) {
            plot_series[skey].databuffer = databuffer.slice(1);
        }
	databuffer.push(value);
    }

    var redraw = function(serie_value) {
    	    var plot_current = [];
	    var mykeys = Object.keys(plot_series);
	    for(var mykey in mykeys) {
		var skey = mykeys[mykey];
		var serie = plot_series[skey];
		// serie['databuffer'].push(serie_value[skey]);
		add_to_serie(skey,serie_value[skey]);
		serie['data'] = handle_data(serie['databuffer']);
		plot_current.push(serie);
	    }
            plot.setData(plot_current);
            plot.setupGrid();
            plot.draw();
        }

    this.actions({
        'add': function(e, message) {
	    redraw(message.value);
        },
        'reset': function(e, message) {
	    plot_series = reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
