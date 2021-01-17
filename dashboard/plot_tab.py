import dash_html_components as html
import dash_cytoscape as cyto

import plot_tab_layout
import utils

example_nb_nodes = 3

content = html.Div([
    cyto.Cytoscape(
        id='tree-plot',
        elements=utils.generate_nodes(example_nb_nodes),
        **plot_tab_layout.tree_plot
    )
])
