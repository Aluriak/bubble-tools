"""Data and formats used by _js.py module
to render a graph using cytoscape.js API

"""

from itertools import count
_next_uid = count(1)
next_uid = lambda: next(_next_uid)

def _attrs_to_json(attrs:dict):
    return ', '.join(f"'{k}': " + (f"'{v}'" if isinstance(v, str) else str(v)) for k, v in attrs.items())


def JS_NODE_LINE(id:str, parent:str=None, clique:bool=False, falsedges:iter=()) -> str:
    attrs = {'id': id}
    if parent:
        attrs['parent'] = str(parent)
    if clique:
        attrs['type'] = 'clique'
    falsedges = tuple(falsedges)
    if falsedges:
        attrs['falsedges'] = list(map(list, falsedges))
    return ' '*8 + "{{ data: {{ {} }} }},".format(_attrs_to_json(attrs))

def JS_EDGE_LINE(source:str, target:str, ispoweredge:bool, isreflexive:bool=False,
                 id:str or int='', label:str='', attrs:dict={}) -> str:
    """

    >>> JS_EDGE_LINE('a', 'b', True)
    "        { data: { source: 'a', target: 'b', type: 'poweredge' } },"

    >>> JS_EDGE_LINE('a', 'b', False)
    "        { data: { source: 'a', target: 'b' } },"

    >>> JS_EDGE_LINE('PWRN-a-1-1', 'PWRN-a-1-2', True)
    "        { data: { source: 'PWRN-a-1-1', target: 'PWRN-a-1-2', type: 'poweredge' } },"

    """
    classes = []
    end = ''
    if ispoweredge: end += ", type: '{}poweredge'".format('reflexive-' if isreflexive else '')
    if label:
        end += f", label: '{label}'"
        classes.append('autorotate')
    if classes:
        end += " }, classes: '" + ' '.join(classes) + "' },"
    else:
        end += " } },"
    id = str(id if id else next_uid())
    if attrs:
        attrs = ', ' + _attrs_to_json(attrs)
    else:
        attrs = ''
    return ' '*8 + f"{{ data: {{ source: '{source}', target: '{target}'" + attrs + end

def JS_FALSEDGE_LINE(source:str, target:str, id:str or int='') -> str:
    """

    >>> JS_EDGE_LINE('a', 'b')
    "        { data: { source: 'a', target: 'b', type: 'falsedge' } },"

    """
    return ' '*8 + f"{{ data: {{ source: '{source}', target: '{target}', type: 'falsedge' }} }},"


JS_FOOTER = """
    ]
  },

  layout: {
    name: 'cose-bilkent',
    numIter: 4000,
    initialEnergyOnIncremental: 0.9,
    refresh: 30,  // FPS
    fit: true,  // fit at the end
    padding: 20,  // fit padding
    animate: false,  // 'during' or 'end' or false

    nodeDimensionsIncludeLabels: true, // Avoid label overlap
    randomize: true,
    nodeRepulsion: 8500,
    idealEdgeLength: 60,  // in compounds
    edgeElasticity: 0.40,
    nestingFactor: 0.2001,  // force for edges inter-compounds

    gravity: 0.20,
    gravityRange: 1.8,
    gravityCompound: 0.9,
    gravityRangeCompound: 1.3,

    tile: true,  // tile disconnected nodes
    tilingPaddingVertical: 10,
    tilingPaddingHorizontal: 10,
  }
});



""".strip().splitlines(False)

JS_MOUSEOVER_WIDTH_CALLBACKS = """
// Callbacks for showing and hiding the false edges
var callback_add_false_edges = function(evt) {
    evt.target.animate({ style: { 'width': 5 } });
    //var falsedges = evt.target.data('falsedges')
    //for (var idx=0, item; item = falsedges[idx]; idx++) {
    //    cy.$('node[id="' + item[0] + '"] -> node[id="' + item[1] + '"]').animate({ style: { 'width': 5 } });
    //}
};
var callback_remove_false_edges = function(evt) {
    evt.target.animate({ style: { 'width': 0.5 } });
    //var falsedges = evt.target.data('falsedges')
    //for (var idx=0, item; item = falsedges[idx]; idx++) {
    //    cy.$('node[id="' + item[0] + '"] -> node[id="' + item[1] + '"]').animate({ style: { 'width': 0.5 } });
    //}
};
// Apply the callbacks when hovering the objects
cy.on('mouseover', 'edge[type="falsedge"]', callback_add_false_edges);
cy.on('mouseout', 'edge[type="falsedge"]', callback_remove_false_edges);

""".strip().splitlines(False)

JS_MOUSEOVER_SHOW_CALLBACKS = """
// Callbacks for showing and hiding the false edges
var callback_add_false_edges = function(evt) {
    var falsedges = evt.target.data('falsedges')
    // var falsedges = evt.target.data('falsedges_by_id')
    for (var idx=0, item; item = falsedges[idx]; idx++) {
        // console.log("Looping: index ", idx, "	item" + item);
        // cy.$('#' + item).addClass('highlighted-falsedge')
        cy.add({ data: {source: item[0], target: item[1], type: 'falsedge'}})
        // cy.$('#' + item).animate({ style: { 'width': 5 } });
    }
};
var callback_remove_false_edges = function(evt) {
    var falsedges = evt.target.data('falsedges')
    for (var idx=0, item; item = falsedges[idx]; idx++) {
        // console.log("Looping: index ", idx, "\titem" + item);
        // cy.$('#' + item).addClass('highlighted-falsedge')
        cy.remove(cy.$('edge[type="falsedge"]'))
        // cy.$('#' + item).animate({ style: { 'width': 1 } });
    }
};
// Apply the callbacks when hovering the objects
cy.on('mouseover', 'edge[falsedges]', callback_add_false_edges);
cy.on('mouseover', 'node[falsedges]', callback_add_false_edges);
cy.on('mouseout', 'edge[falsedges]', callback_remove_false_edges);
cy.on('mouseout', 'node[falsedges]', callback_remove_false_edges);

""".strip().splitlines(False)


JS_MIDDLE = """
    ],
    edges: [
""".strip().splitlines(False)


JS_HEADER = """
var cy = window.cy = cytoscape({
  container: document.getElementById('cy'),

  boxSelectionEnabled: false,
  autounselectify: true,

  style: [
    {
        selector: 'node',
        css: {
            'content': 'data(id)',
            'text-valign': 'center',
            'text-halign': 'center'
        }
    },
    {
        selector: 'node[type="clique"]',
        css: {
            'border-color': 'green',
        }
    },
    {
        selector: '$node > node',
        css: {
            'padding': '30px',
            'text-valign': 'top',
            'text-halign': 'center',
            'background-color': '#eee'
        }
    },
    {
        // selector: 'edge[type="edge"]',
        selector: 'edge',
        css: {
            'label': 'data(label)',
            'width': '1',
            'target-arrow-shape': 'none',
            'source-arrow-shape': 'none',
            //'target-arrow-color': 'black',
        }
    },
    {
        selector: '.autorotate',
        css: { 'edge-text-rotation': 'autorotate' }
    },
    {
        selector: 'edge[type="poweredge"]',
        css: {
            // 'width': '8',
            'width': 'data(width)',
            'target-arrow-shape': 'none',
            'source-arrow-shape': 'none',
            'line-color': 'black',
            'source-endpoint': 'outside-to-line',
            'target-endpoint': 'outside-to-line',
        }
    },
    {
        selector: 'edge[type="incomplete-poweredge"]',
        css: {
            // 'width': '8',
            'width': 'data(width)',
            'target-arrow-shape': 'none',
            'source-arrow-shape': 'none',
            'line-color': 'red',
            'source-endpoint': 'outside-to-line',
            'target-endpoint': 'outside-to-line',
        }
    },
    {
        selector: 'edge[type="falsedge"]',
        css: {
            'line-color': 'red',
            'width': 0.5,
        }
    },
    {
        selector: 'edge[type="highlighted-falsedge"]',
        css: {
            'line-color': 'red',
            'width': 5,
        }
    },
    {
        selector: 'edge[type="reflexive-poweredge"]',
        css: {
            'width': '10',
            //'width': 'data(width)',
            'target-arrow-shape': 'none',
            'source-arrow-shape': 'none',
            'target-arrow-color': 'black',
            'curve-style': 'bezier',
            'control-point-step-size': '300px',
            'loop-sweep': '40deg',
            'loop-direction': '90deg',
            'source-endpoint': 'outside-to-line',
            'target-endpoint': 'outside-to-line',
            'source-distance-from-node': '50%',
        }
    },
    {
        selector: 'node:selected',
        css: {
            'background-color': 'white',
            'line-color': 'white',
            'target-arrow-color': 'white',
            'source-arrow-color': 'white'
        }
    },
    {
        selector: ':parent',
        style: {
            'background-opacity': 0.133,
            // 'shape': 'circle',
            'border-width': 5,
            'border-color': 'black',
        }
    },
    {
        selector: 'node[type="clique"]',
        css: {
            'border-color': 'green',
        }
    },
    {
        selector: 'node[type="quasi-clique"]',
        css: {
            'border-color': 'green',
        }
    },
    {
        selector: '.top-center',
        css: {
            'text-valign': 'top',
            'text-halign': 'center',
        }
    },
  ],

  elements: {
    nodes: [
""".strip().splitlines(False)
