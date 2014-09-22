(function($, block) {
    // a simple wordcloud example
    block.fn.wordcloud = function(config) {
        var options = $.extend({
			// weight=0 means word is not in cloud
			weight_function : function(val,max) { return val; },
        }, config);

        var $container = $(this.$element);
        // create empty wordcloud with parameter options

        var wordcloud_el = $container.jQCloud([{
            text: "TEXT",
            weight: 1
        }]);

        // dict containing the labels and values
        var worddata_dict = {};

        var addword = function(label, value) {
            if (worddata_dict.hasOwnProperty(label)) {
                worddata_dict[label] += value;
            } else {
                worddata_dict[label] = value;
            }
            redraw();
        }

        var setword = function(label, value) {
            worddata_dict[label] = value;
            redraw();
        }

        var redraw = function() {
            var result = [];
	    var max = 0;
	    // incomplete, determine max
            for (var k in worddata_dict) {
                if (worddata_dict.hasOwnProperty(k)) {
			max = Math.max(max, worddata_dict[k]);
	        }
	    }
            for (var k in worddata_dict) {
                if (worddata_dict.hasOwnProperty(k)) {
		    var w = options.weight_function(worddata_dict[k],max);
		    if ( w > 0 )
                        result.push({text: k, weight: w});
                }
            }
            $($container).empty().jQCloud(result);
        }

        var reset = function() {
            worddata_dict = {};
        }

        this.actions({
            'set': function(e, message) {
                setword(message.value[0], message.value[1]);
            },
            'add': function(e, message) {
                addword(message.value[0], message.value[1]);
            },
            'reset': function(e, message) {
                reset();
            }
        });
        // return element to allow further work
        return this.$element;
    }
})(jQuery, block);
