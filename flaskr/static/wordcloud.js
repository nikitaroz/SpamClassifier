$("document").ready(
    $.post("/get_top_features", {},
        function (data) {
            var diameter = 700;
            var dataset = { "children": data };

            var cScale = d3.scaleSequential(
                d3.extent(data, function (d) { return d.frequency; }),
                d3.interpolateRdYlGn
            );

            var bubble = d3.pack(dataset)
                .size([diameter - 100, diameter - 100])
                .padding(2);

            var svg = d3.select("#wordcloud");

            var nodes = d3.hierarchy(dataset)
                .sum(function (d) { return Math.floor(Math.abs(d.coefficient)); });
            var node = svg.selectAll("node")
                .data(bubble(nodes).descendants())
                .enter()
                .filter(function (d) {
                    return !d.children
                })
                .append("g")
                .attr("class", "node")
                .attr("transform", function (d) {
                    return "translate(" + d.x + 100 + "," + d.y + 100 + ")";
                });


            node.append("circle")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", function (d) {
                    return d.r;
                })
                .style("fill", function (d) {
                    return cScale(d.data.frequency);
                })
                .style("stroke", "black")
                .style("stroke-width", "0")
                .on("mouseover", function (d) {
                    d3.select(this).style("stroke-width", "2")
                })
                .on("mouseout", function (d) {
                    d3.select(this).style("stroke-width", "0")
                })
                .on("click", function (d) {
                    var isSelected = !d3.select(this).classed("selected");
                    svg.selectAll("circle").classed("selected", false);
                    if (isSelected) {
                        d3.select(this).classed("selected", true);
                    };

                    if (isSelected) {
                        var sel_x = d3.select(".selected").datum().x;
                        var sel_y = d3.select(".selected").datum().y;
                        var sel_r = d3.select(".selected").datum().r;

                        d3.selectAll("g")
                            .transition()
                            .attr("transform", function (d) {
                                var dist = Math.sqrt((d.x - sel_x) ** 2 + (d.y - sel_y) ** 2);
                                var x_dist = (d.x - sel_x) / dist;
                                var y_dist = (d.y - sel_y) / dist;

                                if (dist < sel_r) {
                                    var new_x = d.x;
                                    var new_y = d.y;
                                } else {
                                    var new_x = d.x + 50 * x_dist;
                                    var new_y = d.y + 50 * y_dist;
                                }
                                return "translate(" + new_x + "," + new_y + ")";
                            })
                        svg.selectAll("circle")
                            .attr("r", function (d) {
                                if (d3.select(this).classed("selected")) {
                                    return d.r + 50;
                                } else {
                                    return d.r;
                                }
                            });
                    } else {
                        svg.selectAll("g")
                            .transition()
                            .attr("transform", function (d) {
                                return "translate(" + d.x + "," + d.y + ")";
                            });
                        svg.selectAll("circle")
                            .attr("r", function (d) {
                                if (d3.select(this).classed("selected")) {
                                    return d.r + 50;
                                } else {
                                    return d.r;
                                }
                            });
                    }
                });

            var text = node.append("text")
                .text(function (d) {
                    return d.data.feature;
                })
                .attr("fill", "black")
                .style("text-anchor", "middle")
                .style("alignment-baseline", "middle")
                .attr("font-family", "sans-serif")
                .attr("font-size", function (d) {
                    return Math.floor(3 * d.r / (d.data.feature.length));
                });
        })
);