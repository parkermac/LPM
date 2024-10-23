// Functions for obs.js.

let margin = 10;

function make_svg(this_info, axid) {
    // Create an svg with axes specific to a pair of variables, e.g.
    // lon,lat for the map or fld,z for a variable (in the object "this_info").
    // Assigns the svg to id=axid.
    let width = this_info.w0 + 2 * margin;
    let height = this_info.h0 + 2 * margin;
    // Declare the x (horizontal position) scale.
    const x = d3.scaleLinear()
        .domain([this_info.x0, this_info.x1])
        .range([margin, width - margin]);
    // Declare the y (vertical position) scale.
    const y = d3.scaleLinear()
        .domain([this_info.y0, this_info.y1])
        .range([height - margin, margin]);
    // Create the SVG container.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr('id', axid);
    // make the container visible
    svg.append("g")
        .append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("fill", "white")
        .attr("stroke", "red")
        .attr("stroke-width", 2 * margin)
        .attr("opacity", .3);
    // Add the x-axis.
    svg.append("g") // NOTE: the svg "g" element groups things together.
        .attr("transform", `translate(0,${height - margin})`)
        .call(d3.axisTop(x).ticks(3));
    // Add the y-axis.
    svg.append("g")
        .attr("transform", `translate(${margin},0)`)
        .call(d3.axisRight(y).ticks(5));
    return svg
}

// Function to convert from x and y to svg coordinates.
function scaleData(x, y, this_info) {
    var height = this_info.h0 + 2 * margin;
    var dx = this_info.x1 - this_info.x0;
    var dy = this_info.y1 - this_info.y0;
    var xscl = this_info.w0 / dx;
    var yscl = this_info.h0 / dy;
    // var sx, sy;
    sx = margin + xscl * (x - this_info.x0);
    sy = height - margin - yscl * (y - this_info.y0);

    return [sx, sy];
}

function add_coastline(coastfile, which_svg, map_info) {
    // Get the coast line segments. We need the Object.values() method here
    // because the floats in coast are packed as strings in the json.
    coastVal = Object.values(coastfile);
    let nCoast = coastVal.length;
    // Save the coastline as a list of lists in the format
    // [ [ [x,y], [x,y], ...], [], ...]
    // where each item in the list is one segment, packed as a list of [x,y] points.
    let cxy = [];
    for (let s = 0; s < nCoast; s++) {
        // pull out a single segment and scale
        var cx = coastVal[s].x;
        var cy = coastVal[s].y;
        var csxy = [];
        var sxy; // [sx, sy] from scaleData()
        for (let i = 0; i < cx.length; i++) {
            sxy = scaleData(cx[i], cy[i], map_info);
            csxy.push(sxy);
        }
        cxy.push(csxy);
    }
    // Loop over all the coast segments and plot them, one line per segment.
    for (let j = 0; j < nCoast; j++) {
        which_svg.append("path")
            .attr("d", d3.line()(cxy[j]))
            .attr("stroke", "black")
            .attr("fill", "none")
            .attr("opacity", 1.0);
    }
}