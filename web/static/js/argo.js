function show_alert(messsage, type){
    if($('#message').length)
        return;
    var tag = $('<div id="message">');
    tag.html(messsage);
    if(type){
        tag.addClass('message-' + type);
    }
    tag.appendTo('body');
    setTimeout(function(){
        tag.fadeIn(1200, function(){
            tag.remove();
        });
    }, 1000);              
}

// /********************** 插件和启动 ***********************/

// var basic_libs = [
//     "/js/lib/fallback.js",
//     "/js/lib/jquery-ui.js",
//     "/js/lib/jquery.corner.js",
//     "/js/lib/jquery.cookie.js",
//     "/js/lib/jquery.form.js",
//     "/js/lib/jquery.linkify.js",
//     "/js/lib/sammy.js",
//     "/js/lib/sammy.template.js",
//     "/js/common.js",
// ];

// require(basic_libs, function() {

//     if (window.location.pathname != "/") {
// 	    return;
//     }
//     initTopNav();
//     initSideNav();
//     initHashLink();
//     initOther();
    

//     // the hash url router
//     var app = $.sammy(function() {
// 	    this.debug = true;

// 	    // do nothing
// 	    this.get('#!/', function() {});
// 	    this.get('#!/sec/', function() {});

// 	    // other
// 	    this.get(/#!\/.*/, function() {
// 	        notifyObj = notify("加载中...", 6000);
//  	        this.load(window.location.hash.substring(2) + "?nocache=" + Math.random(), {cache:false})
// 		        .then(function(context) {
// 		            notifyObj.fadeOut();
// 		            $("#content-column").html(context);
// 		        });
// 	    });

//     });
    
//     // default page，默认为首页
//     app.run('#!/main/');
    
// });

// /*********************** 顶栏 *****************/

// function initTopNav() {
//     if ($("#top-nav").length <= 0) {
// 	    return;
//     }
//     $("#top-nav a[href='/login/']").click(function(event) {
// 	    event.preventDefault();
// 	    showWindow('fwin-login', "/login/", "用户登录", 440, 220);
//     });
//     $("#top-nav a[href='/profile/']").click(function(event) {
// 	    event.preventDefault();
//     });
//     //$("#top-nav a[href='/reg/']").click(function(event) {
// 	//    event.preventDefault();
//     //    alert("尚未开放哦～");
//     //});
// }

// /*********************** 侧边栏 *****************/

// function initSideNav() {

//     if ($("#side-nav").length <= 0) {
// 	    return;
//     }
//     var sec_list = ['BBS系统', '校园社团', '院系交流', '电脑科技',
// 		            '休闲娱乐', '文化艺术', '学术科学', '谈天说地',
// 		            '社会信息', '体育健身'];

//     var a_sec_list = sec_list.map(function(sec, idx, arr) {
// 	    return '<a class="subitem" href="/sec/' + idx + '/">' + sec + '</a>';
//     });

//     // 产生分类讨论区列表
//     $("#side-nav a[href='/sec/']").after($('<div id="side-sec">' + a_sec_list.join('') + '</div>').hide());

//     // 点击展开分类讨论区
//     $("#side-nav a[href='/sec/']").click(function(event) {
// 	    event.preventDefault();
// 	    var hidden = $.cookie("side-sec-hidden") || $("#side-sec").is(":hidden");
// 	    if (hidden) {
// 	        $("#side-sec").show('fast');
// 	        $.cookie("side-sec-hidden", null);
// 	    } else {
// 	        $("#side-sec").hide('fast');
// 	        $.cookie("side-sec-hidden", "true");
// 	    }
	    
//     });

//     $("#side-nav").delegate("a", "click", function(event) {
// 	    // prevent location jump
// 	    event.preventDefault();
// 	    // first change the selection
// 	    $("#side-nav .selected").removeClass("selected");
// 	    $(this).addClass("selected");
// 	    // change url :-)
// 	    window.location.hash = "#!" + $(this).attr('href');
//         /* 每次点击都会刷新content-column */
//         /*$.get($(this).attr('href'), function(resp){            
//             $('#content-column').html(resp);
//         }); */
        
//     });
    
    
//     // 设置hover效果
//     $('#side-nav').delegate('.item, .subitem', 'hover', function() {
// 	    $(this).toggleClass("hover");
//     });

//     // 初始化选择项
//     $("#side-nav a[href='" + window.location.pathname + "']").addClass("selected");
    
//     //定期检查所有未处理信息 ,30s一次      
//     setInterval('checkall()', 30000);
    
//     $("#mail-box").click(function(){
//         $("#has-new-mail").hide();
//     });
    
//     $("#message-box").click(function(){
//         $("#has-new-message").hide();
//     });
// }


// /************* 转换站内url动作 ***************/
// function initHashLink() {
//     $("#content-column").delegate("a", "click", function(event) {
//         if($(this).attr('class') == 'load-exclude') return ;
 
// 	    pat = /http:\/\/(.+?)[\/$]/;
// 	    var hosts = pat.exec(this.href);
// 	    if (!hosts || hosts.length < 2) return;
// 	    var host = hosts[1];
        
// 	    event.preventDefault();
// 	    if (host == window.location.host) { // 	站内url
// 	        // console.log("open url in page: " + this.href);
// 	        window.location.hash = "!" + $(this).attr("href");
//             //url跳转自动 scroll 到顶部
//             $('html, body').animate({scrollTop:0}, 0);
// 	    } else {		// 站外url，新窗口打开
// 	        window.open(this.href);
// 	    }
//     });
// }


// function initOther() {
//     $('.to-top').click(function(event) {
//         $('html, body').animate({scrollTop:0}, 'fast');
//         return false;
//     });

//     $("#content-column").delegate(".common-button", "hover", function(event) {
//         $(this).toggleClass("button-hover"); 
//     }); 
    
//     //用户注册
//     $('#top-reg').click(function(){
//         var win = $('#fwin-register');
// 	    if (win.is(":visible")) {
//             win.dialog('close');
// 	    } else {
//             showWindow("fwin-register", "/reg/", "用户注册", 700, 490);
// 	    } 
//     });

// }
