$("document").ready(
    $.post("get_confusion_matrix", {},
        function (data) {
            var svg = d3.select("#confusion-matrix");

            var svg_size = 400;
            var rect_padding = 5;
            var rect_size = (svg_size - 4 * rect_padding) / 2;

            var colors = {
                "green": "#71ff87",
                "red": "#ff7c71"
            };

            var rectangles = [];
            rectangles.push(
                {
                    "center": [rect_padding + (rect_size / 2), rect_padding + (rect_size / 2)],
                    "text": ["Correctly Predicted", "Spam"],
                    "testVal": data["testingSet"]["truePositive"],
                    "trainVal": data["trainingSet"]["truePositive"],
                    "color": colors["green"]
                }
            );
            rectangles.push(
                {
                    "center": [3 * rect_padding + (3 * rect_size / 2), rect_padding + (rect_size / 2)],
                    "text": ["Incorrectly Predicted", "Spam"],
                    "testVal": data["testingSet"]["falsePositive"],
                    "trainVal": data["trainingSet"]["falsePositive"],
                    "color": colors["red"]
                }
            );
            rectangles.push(
                {
                    "center": [rect_padding + (rect_size / 2), 3 * rect_padding + (3 * rect_size / 2)],
                    "text": ["Incorrectly Predicted", "Normal"],
                    "testVal": data["testingSet"]["falseNegative"],
                    "trainVal": data["trainingSet"]["falseNegative"],
                    "color": colors["red"]
                }
            );
            rectangles.push(
                {
                    "center": [3 * rect_padding + (3 * rect_size / 2), 3 * rect_padding + (3 * rect_size / 2)],
                    "text": ["Correctly Predicted", "Normal"],
                    "testVal": data["testingSet"]["trueNegative"],
                    "trainVal": data["trainingSet"]["trueNegative"],
                    "color": colors["green"]
                }
            );

            var g = svg
                .selectAll("g")
                .data(rectangles)
                .enter()
                .append("g");
            g
                .attr("transform", (d) => "translate(" + d.center[0] + ", " + d.center[1] + ")");

            g.append("rect")
                .attr("x", - rect_size / 2)
                .attr("y", - rect_size / 2)
                .attr("width", rect_size)
                .attr("height", rect_size)
                .attr("rx", 5)
                .style("fill", (d) => d.color);
            g.append("text")
                .text((d) => d.text[0])
                .attr("text-anchor", "middle")
                .attr("dy", "-2.2em");
            g.append("text")
                .text((d) => d.text[1])
                .attr("text-anchor", "middle")
                .attr("dy", "-1.2em");
            g.append("text")
                .classed("value-text", true)
                .attr("text-anchor", "middle")
                .attr("font-size", "1.5em")
                .attr("dy", "1.2em");

            confusionText();
        }
    )
)

function confusionText() {
    var value = $("input[type='radio'][name='confusion']:checked").val();
    var svg = d3.select("#confusion-matrix");
    var text = svg
        .selectAll(".value-text");
    if (value == "test") {
        text
            .each(function (d) {
                d3.select(this).text(d.testVal)
            });
    } else {
        text
            .each(function (d) {
                d3.select(this).text(d.trainVal)
            });
    }
}

$("input[type='radio'][name='confusion']").change( function() {
        confusionText();
});