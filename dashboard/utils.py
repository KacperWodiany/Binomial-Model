import dash_html_components as html


def generate_table_content(names, states):
    content = [
        html.Tr([
            html.Th(name),
            html.Td(value)
        ])
        for name, value in zip(names, states)
    ]
    return content
