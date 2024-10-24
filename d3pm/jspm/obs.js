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

    // Name the data loaded by loadFiles():
    const coast = data[0];
    const obs_info = data[1]
    const obs_data = data[2]

    // Define the geographical range of the MAP and its aspect ratio.
    let lon0 = -130, lon1 = -122, lat0 = 42, lat1 = 52;
    let dlon = lon1 - lon0;
    let dlat = lat1 - lat0;
    let clat = Math.cos(Math.PI * (lat0 + lat1) / (2 * 180));
    let hfac = dlat / (dlon * clat);
    // Define the size of the map svg.
    let w0 = 350; // width for the map
    let h0 = w0 * hfac; // height for the map
    // Create the svg for the map
    let map_info = {
        x0: lon0, x1: lon1,
        y0: lat0, y1: lat1,
        w0: w0, h0: h0
    };
    // Create the map svg
    svgMap = make_svg(map_info, 'ax0');
    // Add the coastline.
    add_coastline(coast, svgMap, map_info);

    // PLOTTING

    fld = 'CT';

    make_info(obs_info, map_info);

    process_data(obs_data, map_info);

    // Create the svg for the data
    svgData = make_svg(data_info_all[fld], 'ax1');

    // Append the SVG element to an element in the html.
    dataPlots.append(svgMap.node());
    dataPlots.append(svgData.node());

    // SLIDER CODE
    var slider = document.getElementById("myRange");
    slider.setAttribute("min", 1) // adjust the slider range to months in a year
    slider.setAttribute("max", 12) // adjust the slider range to months in a year
    var output = document.getElementById("demo");
    output.innerHTML = slider.value; // Display the default slider value
    // Update the current slider value (each time you drag the slider handle)
    // and replot all the drifter locations to match the time from the slider.
    // Note: slider.oninput would update continuously, whereas .onchange
    // updates when you end the movement.
    slider.onchange = function () {
        update_cid_region_time(slider);
        update_cast_colors(fld, svgData, cid_region_time)
        output.innerHTML = this.value
    }

    // BRUSH CODE
    // Create a brush "behaviour".
    // A brush behaviour is a function that has methods such as .on defined on it.
    // The function itself adds event listeners to an element as well as
    // additional elements (mainly rect elements) for rendering the brush extent.
    let brushExtent = [[0, 10], [0, 10]];
    function handleBrush(e) {
        brushExtent = e.selection;
        if (brushExtent != null) {
            update_cid_region(brushExtent);
            update_point_colors(svgMap, cid_region);
            update_cast_colors(fld, svgData, cid_region)
        }
    }
    let brush = d3.brush()
        .on('end', handleBrush);
    function initBrush(whichSVG) {
        whichSVG.call(brush);
    }

    // These lines execute at the start. The later execution is controlled by
    // interaction with the time slider or the brush.
    initBrush(svgMap);
    update_cid_region(brushExtent);
    update_point_colors(svgMap, []);
    update_cast_colors(fld, svgData, []);

}

// Line that executes the visualization code once the data have loaded.
loadFiles().then(create_vis);