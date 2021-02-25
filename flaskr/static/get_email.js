$(function() {
    $(":button#get_email").bind("click", function() {
        $.post($SCRIPT_ROOT + "/get_email", {
                sliderMin: $("#slider-range").slider("values", 0),
                sliderMax: $("#slider-range").slider("values", 1),
                hasNormal: $("input[name='hasNormal']:checked").val(),
                hasSpam: $("input[name='hasSpam']:checked").val()
        }, function(data) {
            $("#results").empty();
            $.each(data, function(index, value) {
                if (value.label == 0) {
                    value.label = "Not Spam";
                } else {
                    value.label = "Spam";
                }
                var template = $("#simple-message-template").html();
                var rendered = Mustache.render(template, value);
                $("#results").append(rendered);
            });
            $("#no-emails-header").remove();
            /*$(".btn-get-by-id").click(function() {
                var id = $(this).data("id");
                $.get("/item", {id: id});
            });*/
            $("mark").each( function() {
                var value = $(this).data("value");
                var color = d3.interpolateRdYlGn((-value + 100) / 200);
                $(this).css('background-color', color);
                var tooltip = "Value: " + value;
                
                $(this).attr("data-toggle", "tooltip");
                $(this).attr("title", tooltip);
                $(this).tooltip();
                //$(this).click(function() {
                //    window.location.replace("/search?q=" + $(this).text().toLowerCase());
                //});
            });
        });
    return false;
    })
})