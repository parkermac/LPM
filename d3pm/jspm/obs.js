// Test of plotting particle tracking lines.

// Define async function to load the data files.
// All other code is in the function create_vis() which is executed
// at the bottom of the script to run once the data have loaded.
async function loadFiles() {
    let coast = await d3.json("tracks2/coast_xy.json");
    let obs_info = await d3.json("obs/bottle_ecologync_2017_info.json")
    let obs_data = await d3.json("obs/bottle_ecologync_2017_data.json")
    return [coast, obs_info, obs_data];
};

// Code to make the plot and interact with it.
function create_vis(data) {

    // Create the svg for the map
    svgMap = start_map();

    //svgCast = start_cast();

    // Name the data loaded by loadFiles():
    const coast = data[0];
    const obs_info = data[1]
    const obs_data = data[2]

    // Get the coast line segments. We need the Object.values() method here
    // because the floats in coast are packed as strings in the json.
    coastVal = Object.values(coast);
    let nCoast = coastVal.length;

    // Get the obs info
    // # output looks like:
    // # {"lon":{"0":-122.917,"1":-122.708,...
    // Here we do not need the Object.values() method because the floats are
    // already numbers.
    let olon = obs_info.lon;

    let cid_list = [];
    let lon_list = [];
    let lat_list = [];
    for (const [key, value] of Object.entries(obs_info.lon)) {
        cid_list.push(key);
        lon_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_info.lat)) {
        lat_list.push(value);
    }

    ncid = cid_list.length;

    // Save the coastline as a list of lists in the format
    // [ [ [x,y], [x,y], ...], [], ...]
    // where each item in the list is one segment, packed as a list of [x,y] points.
    let cxy = [];
    for (let s = 0; s < nCoast; s++) {
        // pull out a single segment and scale
        var cx = coastVal[s].x;
        var cy = coastVal[s].y;
        var csxy = [];
        for (let i = 0; i < cx.length; i++) {
            scaleMap(cx[i], cy[i]);
            csxy.push([sx, sy]);
        }
        cxy.push(csxy);
    }

    // Save the cid's as a list and the station locations as a list in the format"
    // [ [x,y], [x,y], ...]
    // where each item in the list is one cast/
    let icxy = [];
    for (let s = 0; s < ncid; s++) {
        // pull out a single cast location and scale
        var cx = lon_list[s];
        var cy = lat_list[s];
        scaleMap(cx, cy);
        icxy.push([sx, sy]);
    }

    // Loop over all the coast segments and plot them, one line per segment.
    for (let j = 0; j < nCoast; j++) {
        svgMap.append("path")
            .attr("d", d3.line()(cxy[j]))
            .attr("stroke", "black")
            .attr("fill", "none")
            .attr("opacity", 1.0);
    }

    // Append the SVG element to an element in the html.
    dataPlots.append(svgMap.node());

    // SLIDER CODE

    var slider = document.getElementById("myRange");
    // slider.setAttribute("max", nTimes - 1) // adjust the slider range to match the track length
    var output = document.getElementById("demo");
    // output.innerHTML = tlist[slider.value]; // Display the default slider value
    output.innerHTML = slider.value; // Display the default slider value

    // Update the current slider value (each time you drag the slider handle)
    // and replot all the drifter locations to match the time from the slider.
    slider.oninput = function () {
        // output.innerHTML = tlist[this.value];
        // update_sxyNow(this.value);
        // update_point_locations();
        output.innerHTML = this.value
    }

    // Initialize a list to indicate if a particle is within the brushExtent
    let isin = [];
    for (let j = 0; j < ncid; j++) {
        isin.push(2.0);
    }

    // BRUSH CODE

    // Create a brush "behaviour".
    // A brush behaviour is a function that has methods such as .on defined on it.
    // The function itself adds event listeners to an element as well as
    // additional elements (mainly rect elements) for rendering the brush extent.

    let brushExtent = [[0, 0], [0, 0]];

    function handleBrush(e) {
        brushExtent = e.selection;
        if (brushExtent != null) {
            update_isin();
            update_point_colors('#ax0');
        }
    }

    let brush = d3.brush()
        .on('end', handleBrush);

    function initBrush(whichSVG) {
        whichSVG.call(brush);
    }

    // This function updates the "isin" list based on the brush extent.
    function update_isin() {
        isin = []
        for (let j = 0; j < ncid; j++) {
            // Using the brush rectangle
            if (icxy[j][0] >= brushExtent[0][0] &&
                icxy[j][0] <= brushExtent[1][0] &&
                icxy[j][1] >= brushExtent[0][1] &&
                icxy[j][1] <= brushExtent[1][1]) {
                isin.push(1.0);
            } else {
                isin.push(2.0);
            }
        }
    }

    // This function colors all the points based on the brush extent.
    function update_point_colors(whichAx) {
        d3.select(whichAx)
            .selectAll('circle')
            .data(isin)
            .join('circle')
            .style('fill', function (d) {
                if (d == 2.0) {
                    return 'cyan';
                }
                else if (d == 1.0) {
                    return 'red';
                }
            })
            .attr('opacity', function (d) {
                if (d == 2.0) {
                    return 0.3;
                }
                else if (d == 1.0) {
                    return 1.0;
                }
            });
    }

    // This function plots all cast locations.
    function plot_cast_locations(whichAx, whichData) {
        d3.select(whichAx)
            .selectAll('circle')
            .data(whichData)
            .join('circle')
            .attr('cx', function (d) {
                return d[0];
            })
            .attr('cy', function (d) {
                return d[1]
            })
            .attr('r', 3);
    }

    // These lines execute at the start. The later execution is controlled by
    // interaction with the time slider or the brush.
    initBrush(svgMap);
    update_isin();
    plot_cast_locations('#ax0',icxy);
    update_point_colors('#ax0');

}

// Line that executes the visualization code once the data have loaded.
loadFiles().then(create_vis);