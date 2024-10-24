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

    make_map_info();

    // Create the map svg
    svgMap = make_svg(map_info, 'ax0');
    // Add the coastline.
    add_coastline(coast, svgMap, map_info);

    // PLOTTING

    let plot_fld_list = ['CT', 'SA'];
    let plot_fld_axid = ['ax1', 'ax2'];
    let fld_axid_obj = {}
    for (let i = 0; i < plot_fld_list.length; i++) {
        fld_axid_obj[plot_fld_list[i]] = plot_fld_axid[i];
    }


    make_info(obs_info, map_info);

    process_data(obs_data, map_info);

    // Create the svg for the data
    let fld_svg = {};
    plot_fld_list.forEach(function (fld) {
        fld_svg[fld] = make_svg(data_info_all[fld], fld_axid_obj[fld]);
    });

    // Append the SVG element to an element in the html.
    var div1 = document.getElementById("div1");
    var div2 = document.getElementById("div2");

    div1.append(svgMap.node());
    div2.append(svgData.node());

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