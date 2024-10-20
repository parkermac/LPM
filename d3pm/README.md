# README

## This folder is for development of javascript programs using D3.js.

To start a server, in the terminal do:

**cd3** (alias for navigation to Documents/LPM/d3pm)

**cdlow** (alias for navigation to Documents/PM_Web_8)

**lhost** (alias for python -m http.server 8000, ctrl-c to exit)

Then in a browser go to:

localhost:8000

and it opens index.html from this folder. Or to open a different page just go to something like localhost:8000/test0.html.

VS Code Notes:
- shift + opt + F: format document
- or just right-click to get the context menu

Chrome Notes:
- right click on the page to open "Inspect"
- to force Chrome to reload the js script do shift + reload, or shift + cmd + r

---

### Translating across html, css, js, and d3:

### HTML

This html code adds an svg element with a circle and a line
<svg width="800" height="100">
    <circle r="100"></circle>
    <line x1="10" y1="10" x2="100" y2="10"></line>
</svg>

---

### CSS

This css code defines a new class called "title" and sets some attributes:
```
.title {
  float: left;
  padding: 7px;
  width: 100%;
  background-color: lightgrey;
  text-align: center;
}
```
If I wanted to change the css styling of a "selector" like h1 I could do:
```
h1 {
  color: green;
  font-size: 20px;
}
```
In css you can sometimes specify more than one property to an attribute:
```
  border: 1px solid #aaa;
```
To apply a class I defined in an html element I would do something like:
```
    <p id="myThing" class="title">Some text for the title</p>
```
If I wanted to change the text in this item I could do it in javascript:
```
    var output = document.getElementById("myThing");
    output.innerHTML = "Some new text for the title";
```
To apply css styling based on id do this:
```
    #myThing {color: green;}
```

---

### D3

Now how do some things look in js using d3?
```
// Create the SVG container.
const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);
```
// make the container visible
```
svg.append("g")
    .append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "none")
    .attr("stroke", "red")
    .attr("stroke-width", 10) <= should I use 10px here??
    .attr("opacity", .3)
    .attr("id", "my_thing");
```

---

**SUMMARY Here is how the same idea is written in three ways:**
```
- html: <svg width="800" height="60"> </svg>
    "Element": <opening_tag> content </closing_tag>
    In general I think that there are only a few attributes that should be set in the opening tag, e.g. the source of an image, and sometimes width and height.

- css: svg {width: 800px; height: 600px}
    "Rule": selector {declaration;}
    This can be in the style section of the header in html.
    This is where all the styling really belongs. So pay most attention to how things are written here.

- d3:  const svg = d3.create("svg").attr("width",800).attr("height",600);
    "Declare a Variable and Assign its Value": let a = 10;
    This can be in a script section of the html.

```
**So no wonder I have trouble going back and forth!**

I wonder if, in the right context, a number is always interpreted as px?