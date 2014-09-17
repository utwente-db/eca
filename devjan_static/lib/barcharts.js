(function($, block) {

// a simple barchart example
block.fn.barchart = function(config) {
    var options = $.extend({
        bar_series : ["default"],
        bar_options : {
		series: {	
			bars: {
                		show: true
        		}
    		}
    }}, config);

    // create empty barchart with parameter options
    var plot = $.plot(this.$element, [],options.bar_options);

    // dict containing the labels and values
    var bardata_dict = {};
    var bardata_series = {};

    var initbar = function(series) {
	for(var k in series) {
	   bardata_series[series[k]] = {order:k,data:[]};
	}
    }

    initbar(options.bar_series);

    var addbar = function(label, value) {
	if (bardata_dict.hasOwnProperty(label))
		bardata_dict[label] = (bardata_dict[label] + value);
	else
		bardata_dict[label] = value;
	redraw();
    }

    var setbar = function(label, value) {
	bardata_dict[label] = value;
	redraw();
    }

    var redraw = function() {
        var result = [];
	var bardata = [];
	var bardata2 = [];
	var cnt = 0;
	for(var k in bardata_dict) {
	    if (bardata_dict.hasOwnProperty(k)) {
 		bardata.push([cnt,bardata_dict[k]]);
 		bardata2.push([cnt,bardata_dict[k]+100]);
	    }
	    cnt++;
	}
	var xtra = { show : true };
 	result.push({label:'MYLABEL',data:bardata, bars: { fill:true, show : true}});
 	result.push({label:'MYLABEL2',data:bardata2, bars: {fill:true,  show : true }});
	// console.log(result);
        plot.setData(result);
	plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	bardata_dict = {};
    }

    this.actions({
        'set': function(e, message) {
	    setbar(message.value[0],message.value[1]);
        },
        'add': function(e, message) {
	    addbar(message.value[0],message.value[1]);
        },
        'reset': function(e, message) {
	    reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
