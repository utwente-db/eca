(function($, block) {

// Entity formatters for use by tweet list
var entity_formatters = {
    'urls': function(e) {
        return '<a href="' + e.url + '">' + e.display_url + '</a>';
    },
    
    'user_mentions': function(e) {
        return '<a href="https://twitter.com/'+e.screen_name+'">@'+e.screen_name+'</a>';
    },

    'hashtags': function(e) {
        return '<a href="https://twitter.com/hashtag/'+e.text+'?src=hash">#' +e.text+'</a>';
    },

    'default': function(e) {
        return '{ENTITY}';
    }
};

// processes entities for the given message and entity object
var process_entities = function(message, entities) {
    // short-circuit failure mode
    if(typeof entities === 'undefined') {
        return message;
    }

    // build list of entities sorted on starting index
    var es = [];

    $.each(entities, function(t, ts) {
        $.each(ts, function(_, e) {
            e['type'] = t;
            es.push(e);
        });
    });

    es.sort(function(a,b) {
        return a['indices'][0] - b['indices'][0];
    });

    // process entities one-by-one in order of appearance
    var marker = 0;
    var result = "";
    for(var i in es) {
        var e = es[i];
        var start = e['indices'][0];
        var stop = e['indices'][1];

        //copy string content
        result += message.substring(marker, start);

        //process entity (through formatter or no-op function)
        var formatter = entity_formatters[e.type]
                        || function(e) { return message.substring(start,stop) };
        result += formatter(e);

        // update marker location
        marker = stop;
    }

    // append tail of message
    result += message.substring(marker, message.length);

    return result;
}

block.fn.tweets = function(config) {
    var options = $.extend({
        memory: 20
    }, config);

    // create the necessary HTML in the block container
    this.$element.append('<ol class="tweet-list stream-items"></ol>');

    // store list for later
    var $list = this.$element.find('ol');


    // register default handler for handling tweet data
    this.actions(function(e, tweet){
        var $item = $('<li class="stream-item"></li>');

        var $tweet = $('<div class="tweet"></div>');
        var $content = $('<div class="content"></div>');
        var $header = $('<div class="stream-item-header"></div>');

        // Build a tag image and header:
        var $account = $('<a class="account-group"></a>');
        $account.attr("href", "http://twitter.com/" + tweet.user.screen_name);

        var $avatar = $("<img>").addClass("avatar");
        $avatar.attr("src", tweet.user.profile_image_url);
        $account.append($avatar);
        $account.append($('<strong class="fullname">' + tweet.user.name + '</strong>'));
        $account.append($('<span>&nbsp;</span>'));
        $account.append($('<span class="username"><s>@</s><b>' + tweet.user.screen_name + '</b></span>'));
        $header.append($account);

        // Build timestamp:
        var $time = $('<small class="time"></small>');
        $time.append($('<span>' + tweet.created_at + '</span>'));

        $header.append($time);
        $content.append($header);

        // Build contents:
        var text = process_entities(tweet.text, tweet.entities);
        var $text = $('<p class="tweet-text">' + text + '</p>');
        $content.append($text);

        // Build outer structure of containing divs:
        $tweet.append($content);
        $item.append($tweet);
        
        // place new tweet in front of list 
        $list.prepend($item);

        // remove stale tweets
        if ($list.children().size() > options.memory) {
            $list.children().last().remove();
        }
    });

    return this.$element;
};
})(jQuery, block);
