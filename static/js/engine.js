jQuery( document ).ready(function( $ ) {
    
    /* ajaxSetup - Setup csrf headers for all ajax requests */
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    
    $( ".case_summary" ).click(function() {
        
        if($(this).find('.rc-engine').length) {
            console.log("here")
            $(this).find('.rc-engine').delay(200).fadeToggle();
            
        } else {
        console.log($(this).attr('id'));
        case_id = $(this).attr('id');
        
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    var csrftoken = $.cookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $.ajax({
            type : 'POST',
            url : "/rengine",
            data: {"case_id":case_id},
            success:function (data) {
                //var data = JSON.parse(data);
                //console.log(data);
                $( "#"+case_id ).append( "<div id=r_"+case_id+" class='rc-engine'>"+data+"</div>" );
            },
            error:function(xhr, status, error) {
                console.log("Error");
            console.log(error.Message);
            }   
        });   
        
        }
    });
});