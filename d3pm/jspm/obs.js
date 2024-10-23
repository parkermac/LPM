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

    // Get the obs INFO which looks like: {"lon":{"0":-122.917,"1":-122.708,...
    // Here we do not need the Object.values() method because the floats are
    // already numbers.
    // The resulting lists will have one entry per cast.
    let cid_list = [];
    let lon_list = [];
    let lat_list = [];
    let time_list = [];
    for (const [key, value] of Object.entries(obs_info.lon)) {
        cid_list.push(key);
        lon_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_info.lat)) {
        lat_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_info.time)) {
        time_list.push(new Date(value).getMonth() + 1);
        // time_list will be month (1-12)
    }
    let ncid = cid_list.length;
    // Save the scaled station locations as an object (dict) with format:
    // { cid0: [x,y], cid1: [x,y], ...}
    // where each item in the list is one station
    let icxy = {};
    for (let i = 0; i < ncid; i++) {
        var sxy; // [sx, sy] from scaleData()
        sxy = scaleData(lon_list[i], lat_list[i], map_info);
        icxy[cid_list[i]] = sxy;
    }

    // DATA Processing
    // Get the bottle data. It is packed like:
    // {"cid":{"11":0,"20":0,"23":1,"42":1, ...
    // In this case the the key is an oddly-numbered index (e.g. "11")
    // and the value is the cid (e.g. 0).
    // begin by forming lists of cid, z, and time. One list entry for each "bottle".
    // Later we will form trimmed versions of these that only have entries
    // where the associated data field is not null.
    let data_cid_list = [], data_z_list = [], data_time_list = [];
    for (const [key, value] of Object.entries(obs_data.cid)) {
        data_cid_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_data.z)) {
        data_z_list.push(value);
    }
    for (const [key, value] of Object.entries(obs_data.time)) {
        data_time_list.push(new Date(value).getMonth() + 1);
    }
    // Next get the data fields.
    let fld_list = ['CT', 'SA', 'DO (uM)', 'NO3 (uM)']
    let data_lists = {};
    let this_data;
    fld_list.forEach(function (fld) {
        this_data = [];
        for (const [key, value] of Object.entries(obs_data[fld])) {
            this_data.push(value);
        }
        data_lists[fld] = this_data;
    });
    // Create the "data_info" objects (dicts) used for scaling and plotting the data.
    let fld_ranges = { 'CT': [4, 20], 'SA': [0, 34], 'DO (uM)': [0, 400], 'NO3 (uM)': [0, 50] };
    let data_y0 = -200, data_y1 = 0; // z range (meters)
    // Define the size of the map svg.
    let data_w0 = w0, data_h0 = h0; // width and height (svg pixel sizes) for the data
    let data_info_all = {};
    let data_info = {};
    fld_list.forEach(function (fld) {
        data_info = {
            x0: fld_ranges[fld][0], x1: fld_ranges[fld][1],
            y0: data_y0, y1: data_y1,
            w0: data_w0, h0: data_h0
        };
        data_info_all[fld] = data_info;
    });
    // Save the scaled DATA as a list in the format:
    // [ [x,y], [x,y], ...]
    // where each item in the list is one observation.
    let sdata_lists = {};
    fld_list.forEach(function (fld) {
        var sdxy = [];
        for (let i = 0; i < data_cid_list.length; i++) {
            var sxy; // [sx, sy] from scaleData()
            sxy = scaleData(data_lists[fld][i], data_z_list[i], data_info_all[fld]);
            sdxy.push(sxy);
        }
        sdata_lists[fld] = sdxy;
    });
    // Repackage the data into an object (dict) packed as:
    // {cid0: [ [x,y], [x,y], ...], cid1: [ [x,y], [x,y], ...], ...}
    // where the list corresponding to each cid is the scaled value and depths
    // for one CAST.
    // Also, drop any values where the data is null.
    let casts_all = {};
    fld_list.forEach(function (fld) {
        var casts = {};
        for (let i = 0; i < cid_list.length; i++) {
            var cid = cid_list[i];
            var this_cast = [];
            for (let j = 0; j < data_cid_list.length; j++) {
                var dcid = data_cid_list[j];
                if ((dcid == cid) && (data_lists[fld][j] != null)) {
                    this_cast.push(sdata_lists[fld][j]);
                }
            }
            casts[cid] = this_cast;
        }
        casts_all[fld] = casts;
    });

    // PLOTTING

    fld = 'CT';

    // Create the svg for the data
    svgData = make_svg(data_info_all[fld], 'ax1');

    // Initialize a lists of cid's to indicate if a cast is within the brushExtent
    // and the time slider
    let cid_region = [];
    let cid_region_time = [];

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
        update_cid_region_time();
        update_cast_colors(svgData, cid_region_time)
    output.innerHTML = this.value
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
            update_cid_region();
            update_point_colors(svgMap, cid_region);
            update_cast_colors(svgData, cid_region)
        }
    }
    let brush = d3.brush()
        .on('end', handleBrush);
    function initBrush(whichSVG) {
        whichSVG.call(brush);
    }

    // This function updates the "cid_region" list based on the brush extent.
    function update_cid_region() {
        cid_region = []
        for (let j = 0; j < ncid; j++) {
            var this_cid = cid_list[j];
            // Using the brush rectangle
            if (icxy[this_cid][0] >= brushExtent[0][0] &&
                icxy[this_cid][0] <= brushExtent[1][0] &&
                icxy[this_cid][1] >= brushExtent[0][1] &&
                icxy[this_cid][1] <= brushExtent[1][1]) {
                cid_region.push(cid_list[j]);
            }
        }
    }

    // This function updates the "cid_region_time" list based on the brush extent
    // and the time slider. Each entry is a cid.
    function update_cid_region_time() {
        cid_region_time = [];
        for (let i = 0; i < ncid; i++) {
            if (time_list[i] == slider.value &&
                cid_region.includes(cid_list[i])) {
                cid_region_time.push(cid_list[i]);
            }
        }
    }

    function update_point_colors(whichSvg, which_cid_list) {
        whichSvg.selectAll("circle").remove();
        // Loop over all cid's and plot them, one circle per cast.
        cid_list.forEach(function (cid) {
            whichSvg.append('circle')
                .attr('cx', icxy[cid][0])
                .attr('cy', icxy[cid][1])
                .attr('r', 3)
                .style('fill', function () {
                    if (which_cid_list.includes(cid)) {
                        return 'red';
                    }
                    else {
                        return 'blue';
                    }
                });
        })
    }

    function update_cast_colors(whichSvg, which_cid_list) {
        // Loop over all cid and plot them, one line per cast.
        whichSvg.selectAll("path").remove();
        cid_list.forEach(function (cid) {
            whichSvg.append("path")
                .attr("d", d3.line()(casts_all[fld][cid]))
                .attr("fill", "none")
                .style('stroke', function () {
                    if (which_cid_list.includes(cid)) {
                        return 'red';
                    }
                    else {
                        return 'blue';
                    }
                })
                .style('stroke-width', function () {
                    if (which_cid_list.includes(cid)) {
                        return '3';
                    }
                    else {
                        return '1';
                    }
                })
                .style('opacity', function () {
                    if (which_cid_list.includes(cid)) {
                        return '1';
                    }
                    else {
                        return '.3';
                    }
                });
        });
    }

    // These lines execute at the start. The later execution is controlled by
    // interaction with the time slider or the brush.
    initBrush(svgMap);
    update_cid_region();
    update_point_colors(svgMap, []);
    update_cast_colors(svgData, []);

}

// Line that executes the visualization code once the data have loaded.
loadFiles().then(create_vis);