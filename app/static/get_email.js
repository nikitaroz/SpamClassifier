$(function() {
    $(":button#get_email").bind("click", function() {
        $.getJSON($SCRIPT_ROOT + "/get_email", {}, 
        function(data) {
            $("#body").html(data.body);
            $("#subject").html(data.subject);
            $("#tokens").html(data.tokens);
            $("mark").each( function() {
                var value = $(this).data("value");
                var color = d3.interpolateRdYlGn((value + 100) / 200);
                $(this).css('background-color', color);
            });
        });
    return false;
    })
})
        
