$("document").ready(
    $.post("get_confusion_matrix", {}, function(data) {
        var svg = d3.select("#test-confusion");

        svg
        .append("rect")
        .style("fill", "black")
    }
    )
)

function confusion_animation(data, svg) {
    var canvasWidth = 700; // TODO: change var names
    // canvasWidth
    var radius = 10;
    // TODO: data needs to be done

    var numExamples = 0;
    for (let [e, k] of Object.entries(data)) {
        numExamples += k;
    }
    var fractionClassifiedPositive = (data["truePositive"] + data["falsePositive"]) / numExamples;
    //var fractionClassifiedNegative = (data["trueNegative"] + data["falseNegative"]) / numExamples;



}