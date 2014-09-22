(function($, block) {
    // a simple wordcloud example
    block.fn.wordcloud = function(config) {
        var options = $.extend({
            // weight=0 means word is not in cloud
            weight_function : function(val,max) { return val; },
        }, config);

        var $container = $(this.$element);

        // dict containing the labels and values
        var worddata_dict = {};
        var dirty = false;

        var addword = function(label, value) {
            if (worddata_dict.hasOwnProperty(label)) {
                worddata_dict[label] += value;
            } else {
                worddata_dict[label] = value;
            }
            flag_dirty();
        }

        var setword = function(label, value) {
            worddata_dict[label] = value;
            flag_dirty();
        }

        var flag_dirty = function() {
            dirty = true;
        }

        var redraw = function() {
            if(!dirty) {
                window.setTimeout(redraw, 500);
                return;
            }

            var result = [];
            var max = 0;

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
            $($container).empty().jQCloud(result, {delayedMode: false});

            dirty = false;
            window.setTimeout(redraw, 500);
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

        // start redraw loop
        window.setTimeout(redraw, 500);

        // return element to allow further work
        return this.$element;
    }
})(jQuery, block);
