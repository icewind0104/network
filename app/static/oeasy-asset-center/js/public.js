'use strict'
$('document').ready(function(){
    function ajax_get(url, recall){
        var xhr = new XMLHttpRequest();
        xhr.open("get", url, true);
        xhr.timeout = 8000;
        xhr.onload = function(e){
            if(this.status == 200){
                recall(this.responseText);
            } else {
                alert("server error");
            }
        };
        xhr.send(null);
        xhr = null;
    }
    
    function mark_error(obj){
        $(obj).data('check', '');
        $(obj).next().html("<i class='uk-icon-exclamation-triangle motion'></i>该用户不存在");
    }
    
    function mark_correct(obj){
        $(obj).data('check', 'false');
        $(obj).next().html("<i class='uk-icon-check-square correct'></i>");
    }
    
    function mark_clear(obj){
        $(obj).data('check', '');
        $(obj).next().html("");
    }
    
    !function(){
        /* check user name */
        $("input#user").blur(function(e){
            var target = this
            if($(this).val().length > 0) {
                var name = encodeURI($(this).val());
                ajax_get(`/check_name/${name}/`, function(r){
                    if(r === 'OK'){
                        mark_correct(target);
                    } else {
                        mark_error(target);
                    }
                });
            } else {
                mark_clear(target);
            }
        })
        
    }()
})