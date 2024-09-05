// Show an alert box when you click on any h1 element.
function handleClick() {
    alert('An h1 element was clicked');
}
d3.selectAll('h1')
    .on('click', handleClick);

// // find sizes
// let w = window.screen.width;
// console.log(w)
// let width = w / 2
// let height = w / 6
// // Create the SVG container.
// const svg = d3.create("svg")
//     .attr("width", width)
//     .attr("height", height);
// // make the container visible
// svg.append("g")
//     .append("rect")
//     .attr("width", width)
//     .attr("height", height)
//     .attr("fill", "none")
//     .attr("stroke", "red")
//     .attr("stroke-width", 10)
//     .attr("opacity", .3)
//     .attr("id", "my_thing");
// // Append the SVG element.
// myFig.append(svg.node());

// Make a responsive svn rectangle.
let width = 600
let height = 500
d3.select("div#myFig")
    // You need to put it in a div in order for the size specified in
    // the html element to be respected, apparently.
    .append("div")
    // Container class to make it responsive.
    .classed("svg-container", true)
    .append("svg")
    // Responsive SVG needs these 2 attributes and no width and height attr.
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 " + width + " " + height)
    // Class to make it responsive.
    .classed("svg-content-responsive", true)
    // Fill with a rectangle for visualization.
    .append("rect")
    .classed("rect", true)
    .attr("width", width)
    .attr("height", height);