// Code to make interactive plots of model-data comparisons.

// Define async function to load the data files.
// All other code is in the function create_vis() which is executed
// at the bottom of the script to run once the data have loaded.
async function loadFiles(year) {
    year = year;
    let coast = await d3.json("tracks2/coast_xy.json");
    let obs_info = await d3.json("obs/combined_bottle_" + year + "_cas7_t0_x4b_info.json")
    let obs_data = await d3.json("obs/combined_bottle_" + year + "_cas7_t0_x4b_obs.json")
    let mod_data = await d3.json("obs/combined_bottle_" + year + "_cas7_t0_x4b_mod.json")
    return [coast, obs_info, obs_data, mod_data];
};

// Code to make the plot and interact with it.
function create_vis(data) {

    // Name the data loaded by loadFiles():
    const coast = data[0];
    const obs_info = data[1];
    const obs_data = data[2];
    const mod_data = data[3];

    // Checking that these have the same length
    // console.log(Object.keys(obs_data.CT).length)
    // console.log(Object.keys(mod_data.CT).length)

    // console.log(mod_data.CT)

    make_map_info();
    //console.log(map_info);

    // Create the map svg
    svgMap = make_svg(map_info, 'ax0', 'Cast Locations');
    // Add the coastline.
    add_coastline(coast, svgMap, map_info);

    // PLOTTING

    let plot_fld_list = ['CT', 'SA', 'DO (uM)', 'NO3 (uM)', 'DIC (uM)', 'TA (uM)'];
    let plot_fld_axid = ['ax1', 'ax2', 'ax3', 'ax4', 'ax5', 'ax6'];
    let fld_axid_obj = {}
    // I think this object is not needed. I don't do anything with the axid's.
    for (let i = 0; i < plot_fld_list.length; i++) {
        fld_axid_obj[plot_fld_list[i]] = plot_fld_axid[i];
    }

    make_info(obs_info, map_info);

    let plotType = 'modobs';
    process_data(obs_data, mod_data, map_info, plotType);

    // Create the svg for the data
    let fld_svg = {};
    plot_fld_list.forEach(function (fld) {
        fld_svg[fld] = make_svg(data_info_all[fld], fld_axid_obj[fld], fld);
    });

    // Append the SVG element to an element in the html.
    var div1 = document.getElementById("div1");
    var div2 = document.getElementById("div2");

    div1.append(svgMap.node());
    plot_fld_list.forEach(function (fld) {
        div2.append(fld_svg[fld].node());
    });

    // SLIDER CODE
    var slider = document.getElementById("myRange");
    slider.setAttribute("min", 1) // adjust the slider range to months in a year
    slider.setAttribute("max", 12) // adjust the slider range to months in a year
    var output = document.getElementById("demo");
    let sliderMonths = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'Sepember', 'October', 'November', 'December'];
    slider.value = 6; // Initialize the slider value.
    output.innerHTML = sliderMonths[slider.value - 1] + " " + year; // Display the default slider value
    // Update the current slider value (each time you drag the slider handle)
    // and replot all the drifter locations to match the time from the slider.
    // Note: slider.oninput would update continuously, whereas .onchange
    // updates when you end the movement.
    slider.oninput = function () {
        update_cid_obj(brushExtent, slider);
        plot_fld_list.forEach(function (fld) {
            update_cast_colors3(fld, fld_svg[fld]);
            add_unity_line(fld, fld_svg[fld]);
        });
        output.innerHTML = sliderMonths[slider.value - 1] + " " + year;
    }
    // And this code does the same thing every time you push the left or right
    // arrow keys. Note that even though we keep incrementing or decrementing
    // slider.value it never goes below 1 or above 12.
    // document.addEventListener("keydown", (e) => {
    //     let slider = document.getElementById("myRange")
    //     if( e.key === "ArrowLeft" ) {
    //         slider.value -= 1
    //     }
    //     else if( e.key === "ArrowRight" ) {
    //         slider.value = Number(slider.value) + 1
    //     }

    //     update_cid_obj(brushExtent, slider);
    //     plot_fld_list.forEach(function (fld) {
    //         update_cast_colors(fld, fld_svg[fld]);
    //     });
    //     output.innerHTML = sliderMonths[slider.value - 1];
    // })
    // ISSUE: Using the code above worked fine when using the arrow buttons
    // after selecting a region with the brush, but if you selected the slider
    // then the arrow buttons would advance by 2 months instead of 1.

    // BRUSH CODE
    // Create a brush "behaviour".
    // A brush behaviour is a function that has methods such as .on defined on it.
    // The function itself adds event listeners to an element as well as
    // additional elements (mainly rect elements) for rendering the brush extent.
    let brushExtent = [[200, 250], [200, 250]];
    function handleBrush(e) {
        brushExtent = e.selection;
        // console.log(brushExtent)
        if (brushExtent != null) {
            update_cid_obj(brushExtent, slider);
            update_point_colors23(svgMap);
            plot_fld_list.forEach(function (fld) {
                update_cast_colors2(fld, fld_svg[fld]);
                update_cast_colors3(fld, fld_svg[fld]);
                add_unity_line(fld, fld_svg[fld]);
            });
        }
    }
    let brush = d3.brush()
        .on('end', handleBrush);
    function initBrush(whichSVG) {
        // I had to add the brush as a group otherwise it made the text label invisible.
        whichSVG.append('g')
            .call(brush);
    }
    // These lines execute at the start. The later execution is controlled by
    // interaction with the time slider or the brush.
    initBrush(svgMap);
    update_cid_obj(brushExtent, slider);
    update_point_colors1(svgMap);
    plot_fld_list.forEach(function (fld) {
        update_cast_colors1(fld, fld_svg[fld]);
        add_unity_line(fld, fld_svg[fld]);
    });

    // Create a dropdown menu
    const dropdown = d3.select("#myDropdown")
        .on("change", updateChart);

    // Add options to the dropdown
    dropdown.selectAll("option")
        .data([2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023])
        .enter()
        .append("option")
        .text(d => d)
        .attr("value", d => d);

    // Function to update the chart based on the selected value
    function updateChart() {
        year = d3.select(this).property("value");
        console.log(year);

        // Use the selectedValue to update your chart
        // ...
        d3.select("#ax0").remove();
        plot_fld_axid.forEach(function (axNum) {
            d3.select("#" + axNum).remove();
        })
        loadFiles(year).then(create_vis);
    }

}

// Line that executes the visualization code once the data have loaded.
loadFiles(2013).then(create_vis);