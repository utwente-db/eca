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
        var newItem = $('<li class="stream-item"></li>');

        var tweetDiv = $('<div class="tweet"></div>');
        var contentDiv = $('<div class="content"></div>');
        var headerDiv = $('<div class="stream-item-header"></div>');

        // Build a tag image and header:
        var aTag1 = $('<a class="account-group"></a>');
        aTag1.attr("href", "http://twitter.com/" + tweet.user.screen_name);

        var avatar = $("<img>").addClass("avatar");
        avatar.attr("src", tweet.user.profile_image_url);
        aTag1.append(avatar);
        aTag1.append($('<strong class="fullname">' + tweet.user.name + '</strong>'));
        aTag1.append($('<span>&rlm;&nbsp;</span>'));
        aTag1.append($('<span class="username"><s>@</s><b>' + tweet.user.screen_name + '</b></span>'));
        headerDiv.append(aTag1);

        // Build timestamp:
        var smallTag = $('<small class="time"></small>');
        var aTag2 = $('<a class="tweet-timestamp"></a>');
        aTag2.attr("href", "http://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id);
        aTag2.attr("title", tweet.created_at);
        aTag2.append($('<span>' + tweet.created_at + '</span>'));
        smallTag.append(aTag2);
        headerDiv.append(smallTag);
        contentDiv.append(headerDiv);

        // Build contents:
        var pTag = $('<p class="tweet-text">' + tweet.text + '</p>');
        contentDiv.append(pTag);

        // Build outer structure of containing divs:
        tweetDiv.append(contentDiv);
        newItem.append(tweetDiv);
        
        // place new tweet in front of list 
        $list.prepend(newItem);

        // remove stale tweets
        if ($list.children().size() > options.memory) {
            $list.children().last().remove();
        }
    });

    return this.$element;
};
})(jQuery, block);
