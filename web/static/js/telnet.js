(function($){
    format_blank = function(s){
        return s.replace(/ /g, '&nbsp;');
    }
    format_cr = function(s){
        return s.replace(/\n/g, '<br/>\n');
    }
    format_quote = function(s){
        return s.replace(/^【 在.*的大作中提到: 】(\n:.*)*/gm, function(s){
            return '<div class="postquote">' + s.replace(/^:/gm, '') + '</div>';
            });
    }
    $.fn.telnet = function(){
        $(this).each(function(){
            var self=$(this);
            var text=self.text();
            // text = format_blank(text);
            // text = format_cr(text);
            text = format_quote(text);
            self.html(text);
        })
    }
})($)
