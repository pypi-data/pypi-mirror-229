import json


def entanglement_chart(values):
    vega_json = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Prototype Entanglement",
        "data": {
            "values": values},
        "config": {
            "tick": {
                "thickness": 2}},
        "mark": "tick",

            "encoding": {
            "x": {
                "field": "target_class",
                "type": "nominal"},
            "y": {
                "field": "entanglement",
                "type": "quantitative"},
            "color": {
                "field": "output_class",
                "type": "nominal"},
            "tooltip": [{
                        "field": "target_class",
                        "type": "nominal"}, {
                        "field": "output_class",
                        "type": "nominal"}, {
                        "field": "entanglement",
                        "type": "quantitative"}]}}
    return json.dumps(vega_json)


def entanglement_matrix(values):
    vega_json = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Prototype Entanglement",

        "data": {
            "values": values},

        "encoding": {
            "y": {
                "field": "output_class",
                "type": "nominal"},
            "x": {
                "field": "target_class",
                "type": "nominal"}},
        "layer": [{
            "mark": "rect",
            "encoding": {
                    "color": {
                        "scale": {
                            "domainMid": 0,
                            "scheme": "viridis"},
                        "field": "entanglement",
                        "type": "quantitative",
                        "title": "Entanglement",
                        "legend": {
                            "direction": "vertical"}}}}, {
            "mark": "text",
            "encoding": {
                "text": {
                    "field": "entanglement",
                    "type": "quantitative",
                    "format": ".1f"},
                "color": {
                    "condition": {
                        "test": "datum['entanglement'] > 0",
                        "value": "black"},
                    "value": "white"}}}],
            "config": {
            "axis": {
                "grid": True,
                "tickBand": "extent"},
            "text": {
                "fontSize": 8}}}
    return json.dumps(vega_json)


def entanglement_chart_and_matrix(values):
    vega_json = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Prototype Entanglement",
        "data": {
            "values": values},
        "config": {
            "tick": {
                "thickness": 2},
            "axis": {
                "grid": True,
                "tickBand": "extent"},
            "text": {
                "fontSize": 8}},
        "concat": [{
            "mark": "tick",
            "encoding": {
                    "x": {
                        "field": "target_class",
                        "type": "nominal"},
                "y": {
                        "field": "entanglement",
                        "type": "quantitative"},
                "color": {
                        "field": "output_class",
                        "type": "nominal"},
                "tooltip": [{
                            "field": "target_class",
                            "type": "nominal"}, {
                            "field": "output_class",
                            "type": "nominal"}, {
                            "field": "entanglement",
                            "type": "quantitative"}]}}, {
            "encoding": {
                "y": {
                    "field": "output_class",
                    "type": "nominal"},
                "x": {
                    "field": "target_class",
                    "type": "nominal"}},
            "layer": [{
                "mark": "rect",
                "encoding": {
                    "tooltip": [{
                        "field": "target_class",
                        "type": "nominal"}, {
                        "field": "output_class",
                        "type": "nominal"}, {
                        "field": "entanglement",
                        "type": "quantitative"}],
                    "color": {
                        "scale": {
                            "domainMid": 0,
                            "scheme": "viridis"},
                        "field": "entanglement",
                        "type": "quantitative",
                        "title": "Entanglement",
                        "legend": {
                            "direction": "vertical"}, }}}, {
                "mark": "text",
                "encoding": {
                    "text": {
                        "field": "entanglement",
                        "type": "quantitative",
                        "format": ".1f"},
                    "color": {
                        "condition": {
                            "test": "datum['entanglement'] > 0",
                            "value": "black"},
                        "value": "white"}}}]}]}
    return json.dumps(vega_json)


def entanglement_graph(vega_json):
    for vv in vega_json:
        if vv['target_class'] == vv['output_class']:
            vv['target_class'] = ""
    root_row = {k: None for k in vega_json[0].keys()}
    vega_json.append(root_row)
    return json.dumps(vega_json)
