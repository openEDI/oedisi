"""Wiring Diagram utilities

Wiring diagrams can be hard to manage in their final list based form.
Some utilities plot, and future additions include nested wiring
diagram composition and a programmatic interface.
"""

from . import system_configuration
from .system_configuration import WiringDiagram


def get_graph(wiring_diagram: WiringDiagram):
    "Get networkx graph representation of wiring_diagram"
    import networkx as nx

    g = nx.MultiDiGraph()
    for c in wiring_diagram.components:
        g.add_node(c.name, type=c.type, parameters=c.parameters)
    for l in wiring_diagram.links:
        g.add_edge(
            l.source, l.target, source_port=l.source_port, target_port=l.target_port
        )
    return g


def plot_graph_matplotlib(wiring_diagram: WiringDiagram):
    import matplotlib.pyplot as plt
    import networkx as nx

    g = get_graph(wiring_diagram)
    pos = nx.spring_layout(g)
    nx.draw(
        g,
        pos,
        edge_color="black",
        width=1,
        linewidths=1,
        node_size=500,
        alpha=0.9,
        labels={node: node for node in g.nodes()},
    )

    edge_map = {
        (l.source, l.target): f"{l.source_port} -> {l.target_port}"
        for l in wiring_diagram.links
    }

    nx.draw_networkx_edge_labels(g, pos, edge_map, font_color="red")
    plt.axis("off")
    plt.show()


def get_graph_renderer(G):
    import networkx as nx
    from bokeh.plotting import from_networkx
    from bokeh.models import Circle, EdgesOnly, MultiLine
    from bokeh.palettes import Spectral4

    graph_renderer = from_networkx(G, nx.spectral_layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
    graph_renderer.node_renderer.selection_glyph = Circle(
        size=15, fill_color=Spectral4[2]
    )
    graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])

    graph_renderer.edge_renderer.glyph = MultiLine(
        line_color="#CCCCCC", line_alpha=0.8, line_width=5
    )
    graph_renderer.edge_renderer.selection_glyph = MultiLine(
        line_color=Spectral4[2], line_width=5
    )
    graph_renderer.edge_renderer.hover_glyph = MultiLine(
        line_color=Spectral4[1], line_width=5
    )

    # graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = EdgesOnly()
    return graph_renderer


def plot_graph_bokeh(wiring_diagram: WiringDiagram):
    from bokeh.models import (
        BoxSelectTool,
        HoverTool,
        Plot,
        Range1d,
        TapTool,
        PreText,
        CustomJS,
    )
    from bokeh.layouts import layout
    from bokeh.io import output_file, show

    G = get_graph(wiring_diagram)
    graph_renderer = get_graph_renderer(G)
    source = graph_renderer.node_renderer.data_source

    plot = Plot(
        width=800, height=800, x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1)
    )
    plot.title.text = f"{wiring_diagram.name} cosimulation"
    plot.renderers.append(graph_renderer)

    node_text = PreText(
        text="No node seleted",
        width=500,
        height=500,
    )
    edge_hover_tool = HoverTool(
        tooltips=[("source port", "@source_port"), ("target port", "@target_port")]
    )
    tap_tool = TapTool()
    tap_tool.callback = CustomJS(
        args={"nodes": source, "node_text": node_text},
        code="""
        var ind = cb_data.source.selected.indices[0];
        var name = nodes.data['index'][ind];
        var type = nodes.data['type'][ind];
        var parameters = nodes.data['parameters'][ind];
        var s = "Name: " + name + ". ";
        s += "Type: " + type + ". " ;
        s += "Parameters: " + JSON.stringify(parameters, null, 2);

        node_text.text = s;
        node_text.width = 500;
        style="white-space: pre-wrap;"
    """,
    )

    plot.add_tools(edge_hover_tool, tap_tool, BoxSelectTool())

    layout_ = layout([[plot, node_text]])
    show(layout_)
