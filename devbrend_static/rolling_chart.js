(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart2 = function(config) {
    // combine default configuration with user configuration
    var options = $.extend({
        memory: 100,
        series: {
            'default': {data: []}
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

        for(var k in data) {
            var series = data[k];
            var points = [];
            for(var i in series) {
                if(series[i] == null) {
                    points.push(null);
                } else {
                    points.push([i, series[i]]);
                }
            }
            result.push($.extend(options.series[k],{data: points}));
        }

        return result;
    };

    // initial setup of library state (also builds necessary HTML)
    var plot = $.plot(this.$element, prepare_data(), options.chart);


    // register actions for this block
    this.actions({
        'add': function(e, message) {
            // deliberately undocumented feature (explicit is better):
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

})(jQuery, block);
