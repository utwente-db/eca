/*
** Blocks plugin allows for quick creation of new block types.
*/
(function($) {
    var ConstructionState = function($element) {
        this.$element = $element;

        // transfer all block constructors to scope
        for(var b in block.fn) {
            // prevent overrides
            if(!(b in this)) {
                // reference block type in this object
                this[b] = block.fn[b];
            }
        }
    };

    ConstructionState.prototype.actions = function(actions_or_def, def) {
        // handle function overloading
        if(typeof actions_or_def == 'function') {
            def = actions_or_def;
            actions = {};
        } else {
            actions = actions_or_def;
        }

        // default actionless handler
        if(typeof def == 'undefined') {
            def = function(e, message) {
                console.error("Received actionless server event." +
                              " Did you forget to set an action field?");
            }
        }

        // dispatch all incoming server events
        this.$element.on('server-event', function(e, message) {
            if(!('action' in message)) {
                $(this).trigger('_default.server-event', [message]);
            } else {
                $(this).trigger(message.action+'.server-event', [message]);
            }
        });

        // bind all actions
        this.$element.on('_default.server-event', def);

        for(var k in actions) {
            this.$element.on(k+'.server-event', actions[k]);
        }

    }

    block = function(elements) {
        // allow passing of selectors, jquery objects and DOM nodes
        var $element = $(elements);

        // actual work
        if($element.length != 1) {
            console.error("Must have one element to create block for." +
                          " Was given: '",elements,"'");
            return;
        } 

        return new ConstructionState($element);
    }

    block.fn = {};
})(jQuery);
