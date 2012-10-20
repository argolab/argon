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
    format_color = function(s){
        return s.replace(/\[%\d+(;\d+)*#\]/gm, function(s){
            return s.replace('[%', '<span class="ac').replace(/;/gm, ' ac').replace('#]', '">');
        }).replace(/\[#%\]/gm, '</span>');
    }
    $.fn.telnet = function(){
        $(this).each(function(){
            var self=$(this);
            var text=self.text();
            text = format_blank(text);
            text = format_cr(text);
            text = format_quote(text);
            text = format_color(text);
            self.html(text);
        })
    }
})($)
