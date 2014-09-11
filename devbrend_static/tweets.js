(function($, block) {
block.fn.tweets = function(config) {
    var options = $.extend({
        memory: 20
    }, config);

    // create the necessary HTML in the block container
    this.$element.append('<ol class="tweets stream-items"></ol>');

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
        $account.append($('<span>&rlm;&nbsp;</span>'));
        $account.append($('<span class="username"><s>@</s><b>' + tweet.user.screen_name + '</b></span>'));
        $header.append($account);

        // Build timestamp:
        var $time = $('<small class="time"></small>');
        $time.append($('<span>' + tweet.created_at + '</span>'));

        $header.append($time);
        $content.append($header);

        // Build contents:
        var $text = $('<p class="tweet-text">' + tweet.text + '</p>');
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
