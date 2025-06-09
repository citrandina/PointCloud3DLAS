<template>
  <div ref="graphContainer" id="graphContainer"></div>
</template>

<script setup>
import {ref, onMounted, watch, onBeforeUnmount} from 'vue';
import * as d3 from 'd3';
const selectedPartyId = ref(null);

const emit = defineEmits(['su-clicked', 'party-clicked', 'bau-clicked']);


const graphContainer = ref(null);
let resizeObserver = null;
function formatDate(dateInput) {
  if (!dateInput) return '';
  const date = new Date(dateInput);
  return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0];
}

const props = defineProps({
  linkedData: Object, // expects { su, bau, right, party }
  highlightedSuId: String,
  highlightedBauId: String,
});


watch(() => props.linkedData, () => {
  drawGraph();
}, {deep: true, immediate: true});

onMounted(() => {
  drawGraph();
    resizeObserver = new ResizeObserver(() => {
    drawGraph();
  });
  resizeObserver.observe(graphContainer.value);
});

onBeforeUnmount(() => {
  if (resizeObserver && graphContainer.value) {
    resizeObserver.unobserve(graphContainer.value);
  }
});
function drawGraph() {
  const data = props.linkedData;

  const sus = data.sus || [];

  if (!data?.bau || !data?.sus?.length || !data?.parties || !data?.rights) return;


// Grouping nodes
const parties = data.parties;
const rights = data.rights;
const spatialUnits = data.sus;

// Determine max group size to calculate height

const maxGroupSize = Math.max(parties.length, rights.length, spatialUnits.length);
const panelWidth = graphContainer.value.clientWidth;
const panelHeight = graphContainer.value.clientHeight;
const scaleFactor = Math.min(panelWidth / 800, panelHeight / 500, 1);
const fontSize = 12 * scaleFactor;
const spacingX = 200 * scaleFactor;
const verticalSpacing = 100 * scaleFactor;

const baseY = 0;



const totalHeight = maxGroupSize * verticalSpacing;

// Helper to center group
function centerGroup(count, index, spacing) {
  const groupHeight = count * spacing;
  const offsetY = (totalHeight - groupHeight) / 2;
  return offsetY + index * spacing;
}


// Party nodes
const partyNodes = parties.map((p, i) => ({
  id: p.p_id,
  label: `LA_Party:|${p.p_id} \nName: |${p.party_name} `,
  group: 'party',
  x: 0,
  y: centerGroup(parties.length, i, verticalSpacing)
}));
const partyYMap = new Map(partyNodes.map(p => [p.id, p.y]));


// Right nodes
const rightNodes = rights.map((r, i) => ({
  id: r.r_id,
  label: `LA_RRR: |${r.r_id} \nType: |${r.la_righttype} Share: |${r.share}  \nDate: |${formatDate(r.begin_lifespan)}-${formatDate(r.end_lifespan)}`,
  group: 'right',
  x: spacingX,
  y: partyYMap.get(r.p_id) ?? centerGroup(rights.length, i, verticalSpacing) // fallback
}));


// BAUnit (always centered)
const bauNodeY = totalHeight / 3;

// Spatial Unit nodes
// Group SU by BAU


// Sort BAUnits by their numeric id
const uniqueBausMap = new Map();
data.bau_rows.forEach(b => {
  if (!uniqueBausMap.has(b.bau_id)) {
    uniqueBausMap.set(b.bau_id, b);
  }
});
const sortedBaus = [...uniqueBausMap.values()].sort((a, b) => {
  const getNumber = id => parseInt(id?.match(/\d+$/)?.[0]) || 0;
  return getNumber(a.bau_id) - getNumber(b.bau_id);
});

// Build a map to get vertical order of BAUnits
const bauIndexMap = new Map(sortedBaus.map((bau, idx) => [bau.bau_id, idx]));

const suNodes = [...spatialUnits]
  .sort((a, b) => {
    const bauCompare = a.bau_id.localeCompare(b.bau_id, undefined, { numeric: true });
    if (bauCompare !== 0) return bauCompare;
    return a.su_id.localeCompare(b.su_id, undefined, { numeric: true });
  })
  .map((su, i) => ({
    id: su.su_id,
    label: `LA_SU:${su.su_id} \nFloor: ${su.surfacerelation} Type:${su.label}  \nAddress:|${su.ext_adressid}  \narea:|${su.computed_area ? parseFloat(su.computed_area).toFixed(2) : 'N/A'} m²`,
    group: 'su',
    x: spacingX * 3 * 1.1,
    y: centerGroup(spatialUnits.length, i, verticalSpacing * 0.9)
  }));





// BAUnit node
// Sort bau_rows by bau_id for consistent layout

// Build BAUnit nodes
const bauNodes = sortedBaus.map((bau, i) => ({
  id: bau.bau_id,
  label: `LA_BAUnit: |${bau.bau_id} \nType: |${bau.la_bautype || ''} \nDate: |${formatDate(bau.begin_lifespan)} - ${formatDate(bau.end_lifespan)}`,
  group: 'bau',
  x: spacingX * 2.2,
  y: centerGroup(sortedBaus.length, i, verticalSpacing)
}));




const staticNodes = [...partyNodes, ...rightNodes, ...bauNodes, ...suNodes];


const links = [
  // Link party → rights
  ...data.rights.map(r => ({
    source: r.p_id,
    target: r.r_id
  })),

  // Link rights → their associated BAUnits
  ...data.bau_rows.map(bau => ({
    source: bau.r_id,
    target: bau.bau_id
  })),

  // Link BAUnits → their Spatial Units
  ...data.sus.map(su => ({
    source: su.bau_id,  // ✅ use actual SU → BAU linkage
    target: su.su_id
  }))
];



// Clear existing content
d3.select(graphContainer.value).selectAll("*").remove();

// Create SVG first
const svg = d3.select(graphContainer.value)
  .append("svg")
  .attr("width", "100%")
  .attr("height", "100%")
  .attr("viewBox", `0 0 ${panelWidth} ${panelHeight}`)
  .call(
    d3.zoom()
      .scaleExtent([0.1, 3]) // min and max zoom
      .on("zoom", (event) => {
        zoomGroup.attr("transform", event.transform);
      })
  );

const zoomGroup = svg.append("g"); // all content will be inside this


const color = d3.scaleOrdinal()
  .domain(['party', 'right', 'bau', 'su'])
  .range(['#5fcdab', '#f6dca1', '#f6dca1', '#94dae6']);

// Create links first
const link = zoomGroup.append("g")
  .selectAll("line")
  .data(links)
  .enter()
  .append("line")
  .attr("stroke", "#999")
  .attr("stroke-width", 2);

// Create nodes
const node = zoomGroup.append("g")
  .selectAll("g")
  .data(staticNodes)
  .enter()
  .append("g")
  .attr("transform", d => `translate(${d.x},${d.y})`);

// Render text and rectangles after node creation
node.each(function (d) {
  const g = d3.select(this);
  const lines = d.label.split("\n");

  const text = g.append("text")
    .attr("x", 8)
    .attr("y", fontSize)
    .style("font-size", `${fontSize}px`)
    .style("font-family", "sans-serif")
    .style("fill", "#000");

  lines.forEach((line, i) => {
    const [labelPart, valuePart] = line.split("|");
    const tspan = text.append("tspan")
      .attr("x", 8)
      .attr("dy", i === 0 ? 0 : fontSize + 4);

    if (valuePart) {
      // Add label normal, value italic
      tspan.text(labelPart);
      tspan.append("tspan")
        .style("font-style", "italic")
        .text(` ${valuePart}`);
    } else {
      // No separator found, just normal
      tspan.text(line);
    }
  });


  const bbox = text.node().getBBox();
  g.insert("rect", "text")
    .attr("x", bbox.x - 8)
    .attr("y", bbox.y - 4)
    .attr("width", bbox.width + 16)
    .attr("height", bbox.height + 8)
    .attr("rx", 10)
    .attr("fill", color(d.group));
});

// Enable SU node click
node.filter(d => d.group === 'su')
  .style("cursor", "pointer")
  .on("click", function (event, d) {
    emit("su-clicked", d.id);
  });
// Enable Party node click to highlight chain
node.filter(d => d.group === 'party')
  .style("cursor", "pointer")
  .on("click", function (event, d) {
    emit("party-clicked", d.id);
  });
// Enable BAUnit node click to highlight chain
node.filter(d => d.group === 'bau')
  .style("cursor", "pointer")
  .on("click", function (event, d) {
    emit("bau-clicked", d.id); // 🔸 emit the BAUnit ID
  });
const clickableNodes = node.filter(d => d.group === 'su' || d.group === 'party' || d.group === 'bau');

// Hover styles
clickableNodes
  .style("cursor", "pointer")
  .on("mouseover", function(event, d) {
    d3.select(this).classed("node-hover", true);
  })
  .on("mouseout", function(event, d) {
    d3.select(this).classed("node-hover", false);
  });



// Calculate bounding box and node centers
let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
const nodeCenters = {};

node.each(function (d) {
  const bbox = this.getBBox();
  const absX = d.x;
  const absY = d.y;

  nodeCenters[d.id] = {
    cx: absX + bbox.width / 2,
    cy: absY + bbox.height / 2
  };

  minX = Math.min(minX, absX + bbox.x);
  maxX = Math.max(maxX, absX + bbox.x + bbox.width);
  minY = Math.min(minY, absY + bbox.y);
  maxY = Math.max(maxY, absY + bbox.y + bbox.height);
});

// Add class for easier selection
node.classed("highlighted", d => {
  if (!selectedPartyId.value) return false;

  // party selected
  if (d.group === 'party') return d.id === selectedPartyId.value;

  // rights linked to selected party
  if (d.group === 'right') {
    return props.linkedData.rights.some(r => r.p_id === selectedPartyId.value && r.r_id === d.id);
  }

  // BAUnit and SU connected to selected rights
  const linkedRights = props.linkedData.rights.filter(r => r.p_id === selectedPartyId.value).map(r => r.r_id);
  if (d.group === 'bau') {
  return props.linkedData.bau_rows.some(b =>
    b.r_id && props.linkedData.rights.some(r => r.p_id === selectedPartyId.value && r.r_id === b.r_id)
  );
}

  if (d.group === 'su') {
    return props.linkedData.rights.some(r => r.p_id === selectedPartyId.value && props.linkedData.bau.r_id === r.r_id);
  }

  return false;
});
// Apply highlighting based on highlightedSuId
node.classed("highlighted-su", d => {
  return d.group === 'su' && d.id === props.highlightedSuId;
});
node.classed("highlighted-bau", d => {
  return d.group === 'bau' && d.id === props.highlightedBauId;
});



// Apply updated viewBox
const padding = 10;
const viewWidth = maxX - minX + 2 * padding;
const viewHeight = maxY - minY + 2 * padding;
svg.attr("viewBox", `${minX - padding} ${minY - padding} ${viewWidth} ${viewHeight}`);

// Update link positions based on center of boxes
link
  .attr("x1", d => nodeCenters[d.source]?.cx ?? 0)
  .attr("y1", d => nodeCenters[d.source]?.cy ?? 0)
  .attr("x2", d => nodeCenters[d.target]?.cx ?? 0)
  .attr("y2", d => nodeCenters[d.target]?.cy ?? 0);
// Apply highlighted-su and highlighted-bau classes
node.classed("highlighted-su", d => d.group === 'su' && d.id === props.highlightedSuId);
node.classed("highlighted-bau", d => d.group === 'bau' && d.id === props.highlightedBauId);

// Party highlight remains as chain highlight, no problem


}

</script>

<style>


svg {
  width: 100%;
  height: 100%;
  display: block;
  background: #f9f9f9;
}
#graphContainer {
  width: 100%;
  height: 100%;
}
.highlighted rect {
  stroke: #ff3333;
  stroke-width: 3;
}
.highlighted-su rect {
  stroke: #7fe7fb;
  stroke-width: 3;
  fill: #d1f0f6; /* Optional: subtle background highlight */
}

.highlighted-su text {
  font-weight: bold;
  fill: #d33;
}
.highlighted-bau rect {
  stroke: #f3c379; /* or any highlight color */
  stroke-width: 3;
  fill: #f8e9c1 /* subtle background highlight */
}

.highlighted-bau text {
  font-weight: bold;
  fill: #cc6600;
}
/* Hover effect for clickable nodes */
.node-hover rect {
  stroke-opacity: 0.7;
  filter: brightness(1.2); /* 1.0 is normal, 1.3 is 30% brighter */
}


.node-hover text {
  fill: #333;
  font-weight: bold;
}


</style>
