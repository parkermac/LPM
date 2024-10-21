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

    // Define the geographical range of the MAP and its aspect ratio.
    let lon0 = -130, lon1 = -122, lat0 = 42, lat1 = 52;
    let dlon = lon1 - lon0;
    let dlat = lat1 - lat0;
    let clat = Math.cos(Math.PI * (lat0 + lat1) / (2 * 180));
    let hfac = dlat / (dlon * clat);
    // Define the size of the map svg.
    let w0 = 350; // width for the map
    let h0 = w0 * hfac; // height for the map

    let map_info = {
        x0: lon0, x1: lon1,
        y0: lat0, y1: lat1,
        w0: w0, h0: h0
    };

    // Create the svg for the map
    svgMap = make_svg(map_info, 'ax0');

    // Define the ranges of the DATA (CT) and its aspect ratio.
    let data_x0 = 4, data_x1 = 20, data_y0 = -200, data_y1 = 0;
    // Define the size of the map svg.
    let data_w0 = w0; // width for the data
    let data_h0 = h0; // height for the data

    // Create the svg for the data
    let data_info = {
        x0: data_x0, x1: data_x1,
        y0: data_y0, y1: data_y1,
        w0: data_w0, h0: data_h0
    };
    svgData = make_svg(data_info, 'ax1');

    // Name the data loaded by loadFiles():
    const coast = data[0];
    const obs_info = data[1]
    const obs_data = data[2]

    // Get the coast line segments. We need the Object.values() method here
    // because the floats in coast are packed as strings in the json.
    coastVal = Object.values(coast);
    let nCoast = coastVal.length;

    // Get the obs info which looks like: {"lon":{"0":-122.917,"1":-122.708,...
    // Here we do not need the Object.values() method because the floats are
    // already numbers.
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

    // Get the obs data. It is packed like:
    // {"cid":{"11":0,"20":0,"23":1,"42":1, ...
    // In this case the  value is the cid and the key is an oddly-numbered index.
    let data_cid_list = [];
    let data_z_list = [];
    let data_CT_list = [];
    for (const [key, value] of Object.entries(obs_data.cid)) {
        data_cid_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_data.z)) {
        data_z_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_data.CT)) {
        data_CT_list.push(value);
    }
    ndcid = data_cid_list.length;

    // console.log(cid_list);
    // console.log(data_cid_list);

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

    // Save the scaled station locations as a list in the format:
    // [ [x,y], [x,y], ...]
    // where each item in the list is one station
    let icxy = [];
    for (let s = 0; s < ncid; s++) {
        // pull out a single cast location and scale
        var sxy; // [sx, sy] from scaleData()
        sxy = scaleData(lon_list[s], lat_list[s], map_info);
        icxy.push(sxy);
    }

    // Save the scaled DATA as a list in the format:
    // [ [x,y], [x,y], ...]
    // where each item in the list is one observation
    let sdxy = [];
    for (let s = 0; s < ndcid; s++) {
        // pull out a single cast location and scale
        var sxy; // [sx, sy] from scaleData()
        sxy = scaleData(data_CT_list[s], data_z_list[s], data_info);
        sdxy.push(sxy);
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
    dataPlots.append(svgData.node());

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

    // Initialize a list to indicate if a cast is within the brushExtent
    let isin = [];
    for (let j = 0; j < ncid; j++) {
        isin.push(2.0);
    }

    // Initialize a list to indicate if an observation is within the brushExtent
    let disin = [];
    for (let j = 0; j < ndcid; j++) {
        disin.push(2.0);
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
            update_disin();
            // console.log(isin);
            // console.log(disin);
            update_point_colors('#ax0', isin);
            update_point_colors('#ax1', disin);
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

    // This function updates the "disin" list based on the brush extent.
    function update_disin() {
        disin = [];
        for (let j = 0; j < ndcid; j++) {
            disin.push(2.0);
        }
        for (let i = 0; i < ncid; i++) {
            for (let j = 0; j < ndcid; j++) {
                if (data_cid_list[j] == cid_list[i] &&
                    isin[i] == 1.0) {
                    disin[j] = 1.0;
                }
            }
        }
    }

    // This function colors all the points based on the brush extent.
    function update_point_colors(whichAx, which_isin) {
        d3.select(whichAx)
            .selectAll('circle')
            .data(which_isin)
            .join('circle')
            .style('fill', function (d) {
                if (d == 2.0) {
                    return 'blue';
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
    function plot_locations(whichAx, whichData) {
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
    update_disin();
    plot_locations('#ax0', icxy);
    update_point_colors('#ax0', isin);
    plot_locations('#ax1', sdxy);
    update_point_colors('#ax1', disin);

}

// Line that executes the visualization code once the data have loaded.
loadFiles().then(create_vis);