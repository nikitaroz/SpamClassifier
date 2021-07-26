$("document").ready(
    $.post("/get_top_features", {},
        function (data) {
            var svg_size = 700;
            var edge_padding = 50;
            var pack_size = svg_size - 2 * edge_padding;

            var dataset = { "children": data };

            var max_abs_coef = d3.max(data.map(d => Math.abs(d.coefficient)));
            var cScale = d3.scaleSequential(d3.interpolateRdYlGn)
                .domain([-max_abs_coef, max_abs_coef]);
            var bubble = d3.pack(dataset)
                .size([pack_size, pack_size])
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
                    return "translate(" + (d.x + edge_padding) + "," + (d.y + edge_padding) + ")";
                });


            node.append("circle")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", function (d) {
                    return d.r;
                })
                .style("fill", function (d) {
                    return cScale(- d.data.coefficient);
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
                    var isSelected = !d3.select(this.parentNode).classed("selected");
                    prevSelected = d3.select(".selected");

                    svg.selectAll("g").classed("selected", false);
                    if (isSelected) {
                        d3.select(this.parentNode).classed("selected", true);
                    };

                    if (isSelected) {
                        var sel_x = d3.select(".selected circle").datum().x;
                        var sel_y = d3.select(".selected circle").datum().y;
                        var sel_r = d3.select(".selected circle").datum().r;

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
                                return "translate(" + (new_x + edge_padding) + "," + (new_y + edge_padding) + ")";
                            })
                        svg.selectAll("circle")
                            .attr("r", function (d) {
                                if (d3.select(this.parentNode).classed("selected")) {
                                    return d.r + 50;
                                } else {
                                    return d.r;
                                }
                            });
                        svg.select(".selected text")
                            .transition()
                            .attr("font-size", function (d) {
                                return svg_size / 30;
                            })
                            .attr("y", "-45");

                        svg.select(".selected")
                            .append("text")
                            .attr("dy", "0em")
                            .text(function (d) {
                                return `Found in ${d.data.frequency} emails`;
                            })
                            .classed("expandText", true);

                        svg.select(".selected")
                            .append("text")
                            .attr("dy", "1.2em")
                            .text(function (d) {
                                return `Coefficient: ${d.data.coefficient}`
                            })
                            .classed("expandText", true);

                        svg.selectAll(".selected .expandText")
                            .style("text-anchor", "middle")
                            .style("alignment-baseline", "middle")
                            .attr("font-size", "12");


                        prevSelected.selectAll(".expandText").remove();
                        prevSelected.selectAll("text")
                            .transition()
                            .attr("font-size", function (d) {
                                return Math.floor(3 * d.r / (d.data.feature.length));
                            })
                            .attr("y", "0")

                    } else {
                        svg.selectAll("g")
                            .transition()
                            .attr("transform", function (d) {
                                return "translate(" + (d.x + edge_padding) + "," + (d.y + edge_padding) + ")";
                            });

                        svg.selectAll("circle")
                            .attr("r", function (d) {
                                if (d3.select(this.parentNode).classed("selected")) {
                                    return d.r + 50;
                                } else {
                                    return d.r;
                                }
                            });
                        svg.selectAll(".expandText").remove();
                        svg.selectAll("text")
                            .transition()
                            .attr("font-size", function (d) {
                                return Math.floor(3 * d.r / (d.data.feature.length));
                            })
                            .attr("y", "0");
                    }
                });

            node.append("text")
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