// Define the geographical range of the svg and its aspect ratio.
// NOTE: by using "let" these variables are available anywhere throughout
// all the js scripts (for this div only?). They cannot be redeclared.
// The functions defined below are also available throughout the scripts.
let lon0 = -130,
    lon1 = -122,
    lat0 = 42,
    lat1 = 52;
let dlon = lon1 - lon0;
let dlat = lat1 - lat0;
let clat = Math.cos(Math.PI * (lat0 + lat1) / (2 * 180));
let hfac = dlat / (dlon * clat);

// Define the size of the map svg.
let m = 10,
    w0 = 350,
    h0 = w0 * hfac;

let margin = { top: m, right: m, bottom: m, left: m },
    width = w0 + margin.left + margin.right,
    height = h0 + margin.top + margin.bottom;

function start_map() {

    // Declare the x (horizontal position) scale.
    const x = d3.scaleLinear()
        .domain([lon0, lon1])
        .range([margin.left, width - margin.right]);

    // Declare the y (vertical position) scale.
    const y = d3.scaleLinear()
        .domain([lat0, lat1])
        .range([height - margin.bottom, margin.top]);

    // Create the SVG container.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr('id', 'ax0');

    // make the container visible
    svg.append("g")
        .append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 2 * m)
        .attr("opacity", .3)
        .attr("id", "my_thing");

    // Add the x-axis.
    svg.append("g") // NOTE: the svg "g" element groups things together.
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisTop(x).ticks(3));

    // Add the y-axis.
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisRight(y).ticks(5));

    return svg

}

// Function to convert from lon and lat to svg coordinates.
let sx, sy;
function scaleMap(x, y) {
    var xscl = w0 / dlon;
    var yscl = h0 / dlat;
    sx = margin.left + xscl * (x - lon0);
    sy = height - margin.top - yscl * (y - lat0);
}
