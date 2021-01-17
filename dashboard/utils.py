import dash_html_components as html


def generate_table_content(names, values):
    content = [
        html.Tr([
            html.Th(name),
            html.Td(value)
        ])
        for name, value in zip(names, values)]
    return content


def generate_nodes(nb_periods):
    positions = _generate_nodes_positions(nb_periods)
    ids = _generate_nodes_ids(positions)
    return [{'data': id_, 'position': position, 'locked': True}
            for id_, position in zip(ids, positions)]


def _generate_nodes_positions(nb_periods):
    positions = [{'x': 50 * x, 'y': 50 * y}
                 for x in range(nb_periods + 1)
                 for y in range(-x, x + 1, 2)]
    return positions


def _generate_nodes_ids(positions):
    return [{'id': _format_id(position)} for position in positions]


def _format_id(position):
    return str(position['x']) + '_' + str(position['y'])
