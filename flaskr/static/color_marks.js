
function colorMarks() {
    $("mark").each( function() {
        var value = $(this).data("value");
        var color = d3.interpolateRdYlGn((-value + 5) / 10);
        $(this).css('background-color', color);
        var tooltip = "Coefficient: " + value.toFixed(1);
        
        $(this).attr("data-toggle", "tooltip");
        $(this).attr("title", tooltip);
        $(this).tooltip();
    });
    $(".label-badge").each( function() {
        if(this.innerText == "Normal") {
            $(this).addClass("bg-success");
        } else {
            $(this).addClass("bg-danger");
        }
    })

}