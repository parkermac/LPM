//JAVASCRIPT VIS CODE STARTS HERE
// define async function to load the data files. all other code is in the function create_vis() which is executed at the bottom of the script to run once the data have loaded
async function loadFiles() {
  let tracks_PS_restructured = await d3.json("./tracks/tracks_PS_restructured.json");
  let tracks_PS = await d3.json("./tracks/tracks_PS.json");
  let coast_xy = await d3.json("./tracks/coast_xy.json");
  let tracks_full_restructured = await d3.json("./tracks/tracks_full_restructured.json");
  let tracks_full = await d3.json("./tracks/tracks_full.json");
  return [tracks_PS_restructured, tracks_PS, coast_xy, tracks_full_restructured, tracks_full];
};
//code to make the vis:
function create_vis(data) {
  //name the variables loaded by loadFiles():
  const PS_data = data[0];
  const tracks_PS = data[1];
  const coast_file = data[2];
  const full_data = data[3];
  const tracks_full = data[4];

  var xmin = -125;
  var xmax = -121.75;
  var ymin = 46.75;
  var ymax = 50;

  // d3.select("#selected-dropdown").text("first");


  // define dimensions for the svg in which the vis will go
  var margin = {
      top: 50,
      right: 100,
      bottom: 100,
      left: 100
    },
    height = 1200 - margin.top - margin.bottom,
    width = (height + margin.top + margin.bottom) * Math.cos(0.5 * (ymin + ymax) * Math.PI / 180) * (xmax - xmin) / (ymax - ymin) - margin.left - margin.right;


  // width in pixels of map svg:
  chartWidth = width + margin.left + margin.right;
  var svgCentre = {
    x: width / 2,
    y: height / 2
  };
  var rectDims = {
    w: width + margin.left + margin.right,
    h: height + margin.top + margin.bottom
  };

  // create svg element to contain the vis (including the slider too)
  var svg = d3.select("#vis")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);


  var rectangle = svg.append("rect")
    .attr("x", svgCentre.x - (rectDims.w / 2) + 10) // offset left by half rect width
    .attr("y", svgCentre.y - (rectDims.h / 2)) // offset up by half rect height
    .attr("width", rectDims.w + 100)
    .attr("height", rectDims.h - 250)
    .attr("fill", "white");

  // var scrubber = d3.select("#vis")
  //     .append("svg")
  //     .attr("width", width + margin.left + margin.right)
  //     .attr("height", 150);  

  // var svg = d3.create("svg")
  //     .attr("width", width)
  //     .attr("height", height)
  //     .attr("transform","translate("+margin.left+","+150+")");  

  // console.log(svg);
  ////////// slider //////////
  //initialise some variables required in the slider function:
  var moving = false;
  var currentValue = 0;
  var targetValue = width;
  // access the play button created in the CSS:
  var playButton = d3.select("#play-button");

  // set up d3 scale for the slider:
  var x = d3.scaleLinear()
    .domain([0, 168])
    .range([0, targetValue])
    .clamp(true);

  // create group to hold the slider:
  var slider = svg.append("g")
    .attr("class", "slider")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // draw the slider: 
  slider.append("line")
    .attr("class", "track")
    .attr("x1", x.range()[0])
    .attr("x2", x.range()[1])
    .select(function () {
      return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-inset")
    .select(function () {
      return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-overlay")
    // code that executes when user clicks and drags the slider:
    .call(d3.drag()
      .on("start.interrupt", function () {
        slider.interrupt();
      })
      .on("start drag", function (event) {
        currentValue = event.x;
        // update function is what redraws the plot and updates the slider position
        update(x.invert(currentValue));
      })
    );

  // draw the slider rail and add text above the button showing current value:
  slider.insert("g", ".track-overlay")
    .attr("class", "ticks")
    .attr("transform", "translate(0," + 18 + ")")
    .selectAll("text")
    .data(x.ticks(14))
    .enter()
    .append("text")
    .attr("x", x)
    .attr("y", 10)
    .attr("text-anchor", "middle")
    .text(function (d) {
      var day_no = (Math.floor(d / 10) - 13);
      return day_no
    });

  // create the circular button:
  var handle = slider.insert("circle", ".track-overlay")
    .attr("class", "handle")
    .attr("r", 9);

  // not really sure which label this bit adds:
  var label = slider.append("text")
    .attr("class", "label")
    .attr("text-anchor", "middle")
    .text("Day: " + -13 + " (Hindcast)")
    .attr("transform", "translate(0," + (-25) + ")")

  //code that executes when user interacts with play button:
  playButton.on("click", function () {
    var button = d3.select(this);
    // if statement runs when user presses pause:
    if (button.text() == "Pause") {
      moving = false;
      clearInterval(timer);
      timer = 0;
      button.text("Play");
    }
    // else statement runs when user presses play:
    else {
      moving = true;
      // wait 250ms then execute the step function, repeat until user presses pause:
      timer = setInterval(step, 400);
      button.text("Pause");
    }
    console.log("Slider moving: " + moving);
    //   })
  })

  // create svg for the drifter map (fiddle with this bit to move plot):
  var scatterPlot = svg.append("g")
    .attr("class", "scatterplot")
  // .attr("transform", "translate(" + margin.left +"," + 250 + ")");

  // function to restructure coast json file into format required to plot:
  function reorder_cf(d) {
    return coast_file[d].x.map(function (item, index) { // combine x and y so that each point is an individual object
      return {
        x: item,
        y: coast_file[d].y[index]
      };
    });
  };
  // map.selectAll("path.coast").remove();

  // indices of each coast path:
  coast_line_lines = d3.range(1, 4251);

  // d3 scales for drifter map:
    // PM Edit: Original version had clamp(true) but then the drifters
    // piled up on the westtern boundary.
  xScaleScatter = d3.scaleLinear().clamp(false)
    .domain([xmin, xmax])
    // .domain(d3.extent(PS_data, d => d.x))
    .range([margin.left, chartWidth - margin.right]);
  yScaleScatter = d3.scaleLinear().clamp(false)
    .domain([ymin, ymax])
    // .domain(d3.extent(PS_data, d => d.y))
    .range([height - margin.bottom - 100, 150]);

  svg.append('rect')
    .attr('x', xScaleScatter(xmin))
    .attr('y', yScaleScatter(ymax))
    .attr('width', (xScaleScatter(xmax) - xScaleScatter(xmin)))
    .attr('height', (yScaleScatter(ymin) - yScaleScatter(ymax)))
    .attr('stroke', 'black')
    .attr('fill', "none");


  // function to create smoothed curve from list of (x,y) coords:
  line = d3.line().curve(d3.curveCatmullRom).x(d => xScaleScatter(d.x)).y(d => yScaleScatter(d.y))

  // loop through the coast paths and plot to form map:
  for (var t in coast_line_lines) {
    scatterPlot.append("path") // plot the coastline
      .attr("d", line(reorder_cf(coast_line_lines[t])))
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("opacity", 1)
      .attr("class", "coast")
  };
  ///////// plot //////////

  // initialise variables required for selection and brushing interactions:  
  var brushedDrifters = [];
  var selectedDrifter = [];

  // function that executes on each new frame when play button is playing:  
  function step() {
    // clears track of selected drifter if user has clicked on one:
    // scatterPlot.selectAll("path.selected_float").remove();
    // update the chart:
    update(x.invert(currentValue));
    // iterate to next time step:
    currentValue = currentValue + (targetValue / 168);
    // condition to stop when slider reaches end:
    if (currentValue > targetValue) {
      moving = false;
      currentValue = 0;
      clearInterval(timer);
      timer = 0;
      playButton.text("Play");
      console.log("Slider moving: " + moving);
    }
  }

  // function that draws the drifter plot and hosts the brush/selection interactions:
  function drawPlot(scatterPlot) {


    // function to reorder tracks. given a drifter and a time, this returns a path for the last 10 time steps (we can change this to whatever value we like)
    function reorder(d, point) {
      if (point < 20) {
        return tracks_PS[d].x.slice(0, point).map(function (item, index) { // combine x and y so that each point is an individual object
          return {
            track: d,
            x: item,
            y: tracks_PS[d].y.slice(0, point)[index]
          };
        });
      } else {
        return tracks_PS[d].x.slice(point - 20, point).map(function (item, index) { // combine x and y so that each point is an individual object
          return {
            track: d,
            x: item,
            y: tracks_PS[d].y.slice(point - 20, point)[index]
          };
        });
      }
    };

    // same as above but for the drifter the user has clicked on, this will return the full path
    function reorder_selected(d) {
      return tracks_PS[d].x.map(function (item, index) { // combine x and y so that each point is an individual object
        return {
          x: item,
          y: tracks_PS[d].y[index]
        };
      });
    };

    // define variable to hold the current time step (i.e. point index)
    var point = Math.round(x.invert(currentValue));

    // define brush interaction:
    brush = d3.brush()
      .extent([
        // get area traced out by brush in x,y coords
        // [d3.min(xScaleScatter.range()), d3.min(yScaleScatter.range())],
        // [d3.max(xScaleScatter.range()), d3.max(yScaleScatter.range())]
        [xScaleScatter(xmin), yScaleScatter(ymax)],
        [chartWidth, height]
      ])
      // remove any selected tracks when user clicks on empty space:
      .on("brush start", event => {
        scatterPlot.selectAll("path.selected_float").remove();
        selectedDrifter = null;
        scatterPlot.selectAll("circle.dot")
          .data(scatterData, d => d.track)
          .attr("opacity", d => {
            if (brushedDrifters.includes(d.track)) {
              return 1;
            } else if (selectedDrifter === d.track) {
              return 1;
            } else {
              if (brushedDrifters.length == 0) {
                return 1
              } else {
                return 0.2;
              }
            }
          }) // make bubbles a bit transparent
          .attr("fill", d => {
            if (selectedDrifter === d.track) {
              return "black";
            } else if (brushedDrifters.includes(d.track)) {
              return "purple";
            } else {
              return "blue";
            }
          })
          .attr("r", d => {
            if (brushedDrifters.includes(d.track)) {
              return 3;
            } else if (selectedDrifter === d.track) {
              return 5;
            } else {
              return 1.5;

            }
          });
      })
      // code that executes once brush finished:
      .on("brush end", (event) => {
        // if loop for empty brush:
        if (event.selection === null) {
          brushedDrifters = [];
        }
        // else loop for non-empty brush:
        else { // remove any selected float trajectories (probably unnecessary given this happens on burhs start):
          scatterPlot.selectAll("path.selected_float").remove();

          const [
            [x0, y0],
            [x1, y1]
          ] = event.selection;
          // access drifter locations for relevant time step for all drifters within brush:
          brushedDrifters = PS_data.filter(d => d.point === point)
            .filter(d => {
              return x0 <= xScaleScatter(d.x)
                && x1 >= xScaleScatter(d.x)
                && y0 <= yScaleScatter(d.y)
                && y1 >= yScaleScatter(d.y);
            }).map(d => d.track);
        };
        // call the code to update the plot on any brush interaction:
        makeScatterPlot(scatterPlot);
      });

    // access drifter locations for current time step:
    const scatterData = PS_data.filter(d => d.point === point);

    // function to draw the plot on any interaction:
    function makeScatterPlot(scatterPlot) {
      // reveals trajectories for any brushed tracks:
      scatterPlot.selectAll(".brushContainer")
        .data([1])
        .join("g")
        .attr("class", "brushContainer")
        .call(brush)
        // .call(console.log('hello'))
        // most of the vis code lives inside this call():
        .call(function () {
          // function to show trajectories of brushed floats:
          function track_reveal() {
            scatterPlot.selectAll("path.float").remove();
            for (var t in brushedDrifters) {
              scatterPlot.append("path").attr("d", line(reorder(brushedDrifters[t], point))).attr("fill", "none").attr("stroke", "red").attr("class", "float").attr("opacity", 0.1)
            };
          };

          // console.log(scatterPlot.selectAll(".brushContainer"));
          // execute the code to reveal the float trajectories:
          scatterPlot.call(track_reveal);

          // set circle properties for brushed vs selected floats:
          scatterPlot.selectAll("circle.dot")
            .data(scatterData, d => d.track) // <-- provide a 🔑 key function for joining data to SVG elements
            //     this key function is needed for proper animation, see https://observablehq.com/@philippkoytek/d3-part-3-selection-join-explained
            .join("circle")
            .sort((a, b) => b.point - a.point) // sort the data so that big bubbles are in the background
            .attr("class", "dot")
            .on("click", (event, d) => {
              console.log(selectedDrifter);
              // if code clears trajectory when you reselect same drifter again (NOT SURE THIS IS ACTUALLY WORKING)
              if (d.track === selectedDrifter) {
                scatterPlot.selectAll("path.selected_float").remove();
                selectedDrifter = null;
                scatterPlot.selectAll("circle.dot")
                  .data(scatterData, d => d.track)
                  .attr("opacity", d => {
                    if (brushedDrifters.includes(d.track)) {
                      return 1;
                    } else if (selectedDrifter === d.track) {
                      return 1;
                    } else {
                      if (brushedDrifters.length == 0) {
                        return 1
                      } else {
                        return 0.2;
                      }
                    }
                  }) // make bubbles a bit transparent
                  .attr("fill", d => {
                    if (selectedDrifter === d.track) {
                      return "black"; // (NOT SURE THIS CONDITION IS WORKING)
                    } else if (brushedDrifters.includes(d.track)) {
                      return "purple";
                    } else {
                      return "blue";
                    }
                  })
                  .attr("r", d => {
                    if (brushedDrifters.includes(d.track)) {
                      return 3;
                    } else if (selectedDrifter === d.track) {
                      return 5;
                    } else {
                      return 1.5;

                    }
                  });
              }
              // else code plots full trajectory on selection, first clearing any previous selection:
              else {
                selectedDrifter = d.track;
                scatterPlot.selectAll("path.selected_float").remove();
                scatterPlot.append("path").attr("d", line(reorder_selected(selectedDrifter))).attr("fill", "none").attr("stroke", "green").attr("class", "selected_float").attr("opacity", 0.5).attr("stroke-width", 2);
                scatterPlot.selectAll("circle.dot")
                  .data(scatterData, d => d.track)
                  .attr("opacity", d => {
                    if (brushedDrifters.includes(d.track)) {
                      return 1;
                    } else {
                      if (brushedDrifters.length == 0) {
                        return 1
                      } else {
                        return 0.2;
                      }
                    }
                  }) // make bubbles a bit transparent
                  .attr("fill", d => {
                    if (selectedDrifter === d.track) {
                      return "black"; // (NOT SURE THIS CONDITION IS WORKING)
                    } else if (brushedDrifters.includes(d.track)) {
                      return "purple";
                    } else {
                      return "blue";
                    }
                  })
                  .attr("r", d => {
                    if (brushedDrifters.includes(d.track)) {
                      return 3;
                    } else if (selectedDrifter === d.track) {
                      return 5;
                    } else {
                      return 1.5;

                    }
                  });
              }
            })
            // set opacity and fill values for circles depending on whether they've been selected/brushed:
            .attr("opacity", d => {
              if (brushedDrifters.includes(d.track)) {
                return 1;
              } else if (selectedDrifter === d.track) {
                return 1;
              } else {
                if (brushedDrifters.length == 0) {
                  return 1
                } else {
                  return 0.2;
                }
              }
            }) // make bubbles a bit transparent
            .attr("fill", d => {
              if (selectedDrifter === d.track) {
                return "black"; // (NOT SURE THIS CONDITION IS WORKING)
              } else if (brushedDrifters.includes(d.track)) {
                return "purple";
              } else {
                return "blue";
              }
            })
            .transition().duration(400).ease(d3.easeLinear) // <-- animate the update of float location (the duration should be set to be the same as the delay in the step function for the slider)
            .attr("cx", d => xScaleScatter(d.x))
            .attr("cy", d => yScaleScatter(d.y))
            // set dot radius according to selection:
            .attr("r", d => {
              if (brushedDrifters.includes(d.track)) {
                return 3;
              } else if (selectedDrifter === d.track) {
                return 5;
              } else {
                return 1.5;

              }
            });
        });
    };
    // execute the above code to make the scatter plot:
    svg.select("g.scatterplot")
      .call(makeScatterPlot); //} );
  }

  // execute the draw plot code once at the beginning so that the drifters show up before the first interaction:
  drawPlot(scatterPlot);

  // function to update the vis whenever the timestep changes:
  function update(h) {
    // update position and text of label according to slider scale:
    handle.attr("cx", x(h));
    label
      .attr("x", x(h))
      .text(function () {
        var day_no = (Math.floor(h / 10) - 13);
        if (day_no < 0) {
          return " Day: " + day_no + " (Hindcast)"
        } else {
          return " Day: " + day_no + " (Forecast)"
        }
      });

    // redraw the plot for the new timestep:
    drawPlot(scatterPlot);
  }
};

// line that executes the visualisation code once the data have loaded.
loadFiles().then(create_vis);
