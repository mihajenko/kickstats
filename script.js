$(document).ready(function() {
    // get data
    d3.json('d3data.json', function(err, json) {
        // visualize data
        visualizeMe(json);
    });
});


function visualizeMe(project_data) {
    // Returns an event handler for fading a given chord group.
    function fade(opacity) {
        return function (g, i) {
            svg.selectAll(".chord path")
                .filter(function (d) {
                    return d.source.index != i && d.target.index != i;
                })
                .transition()
                .style("opacity", opacity);
        };
    }

    // SVG init
    var chord = d3.layout.chord()
        .padding(.05)
        .sortSubgroups(d3.descending)
        .matrix(project_data['relation_matrix']);


    var fill = d3.scale.ordinal()
        .domain(d3.range(project_data['relation_matrix'].length))
        // Colors
        .range(["#ee763c", "#f7e0c2", "#0b59d1", "#f8b2bc", "#cb1a62", "#59a5b7"]);


    // Browser constants
    var container = $('.main-container'),
        height = $(window).height(),
        width = container.width(),
        innerRadius = Math.min(width, height) * .41,
        outerRadius = innerRadius * 1.15;

    console.log(width);
    console.log(height);

    // SVG building
    var svg = d3.select("div.d3body").append("svg:svg")
        // Two attributes that are required to make it responsive
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 " + width + " " + height)
        // Class to make it responsive
        .classed("d3-content-responsive", true)
        // Global container g (instead of circle)
      .append("svg:g")
        .classed("circle", true)
        // sets position
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    // groups
    var g = svg.selectAll("g.group")
        .data(chord.groups())
      // inner containers
      .enter().append("svg:g")
        .classed("group", true)
        .on("mouseover", fade(0.15))
        .on("mouseout", fade(1));

    // colors and strokes
    g.append("svg:path")
        .style("fill", function(d) { return fill(d.index); })
        .style("stroke", function(d) { return fill(d.index); })
        .attr("d", d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius))
        .attr("id", function(d) { return "path-" + d.index });

    // texts
    g.append("svg:text")
        .attr("dx", 4)
        .attr("dy", 14)
        .attr("font-size", 11)
      .append("textPath")
        .classed("textpath", true)
        // xlink:href references a path to which the text will bind (and curve)
        .attr("xlink:href", function(d) { return "#path-" + d.index })
        .text( function(d) {
            return project_data['project_names'][d.index];
        });

    // chords
    svg.append("g")
        .classed("chord", true)
      .selectAll("path")
        .data(chord.chords)
      .enter().append("path")
        .attr("d", d3.svg.chord().radius(innerRadius))
        .style("fill", function(d) { return fill(d.target.index); })
        .style("opacity", 1);
}

