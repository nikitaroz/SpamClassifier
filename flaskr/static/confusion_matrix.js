var startedAnimation = false;

$(window).scroll(function () {
    if (
        ($(window).scrollTop() + $(window).height() == $(document).height())
        && !startedAnimation) {
        $.post("get_confusion_matrix", {}, function (data) {
            var diameter = 700; // TODO: change var names
            var radius = 10;
            console.log(data);

            var svg = d3.select("#confusion");

            var sampleData = d3.range(200).map((d, i) => ({
                r: radius,
                category: i % 2
            }));

            var manyBody = d3.forceManyBody().strength(-0.2);
            var center = d3.forceCenter().x(diameter / 2).y(diameter / 2);
            var collide = d3.forceCollide().radius(radius);

            var startTime = Date.now();
            var simulation = d3.forceSimulation()
                .force("charge", manyBody)
                .force("center", center)
                .force('collision', collide)
                .nodes(sampleData)
                .on("tick", function () {
                    svg.selectAll("circle")
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                    if (Date.now() - 1500 > startTime) {
                        simulation.stop();
                        newSimulation();
                    }
                });

            var newSimulation = function () {
                var xCenter = [100, 600];
                simulation
                    .force("charge", d3.forceManyBody().strength(-0.2))
                    .force("center", center)
                    .force('collision', collide)
                    .force('x', d3.forceX().x(function(d) {
                        return xCenter[d.category];
                      }).strength(0.1))
                    .on("tick", function () {
                        svg.selectAll("circle")
                            .attr("cx", d => d.x)
                            .attr("cy", d => d.y);
                        if (Date.now() - 5000 > startTime) {
                            simulation.stop();
                        }
                    })
                    .restart();
            }

            svg
                .selectAll("circle")
                .data(sampleData)
                .enter()
                .append("circle")
                .attr("class", "node")
                .style("fill", "black")
                //.style("fill", (d, i) => roleScale(i))
                .attr("r", d => d.r);
        }
        )
        startedAnimation = true;
    }
})
