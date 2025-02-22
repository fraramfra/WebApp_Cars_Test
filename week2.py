import altair as alt
import dash_bootstrap_components as dbc
import dash_vega_components as dvc
from dash import Dash, dcc, callback, Input, Output, html
from vega_datasets import data

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

#python -m pip list --format freeze > requirements.txt

cars = data.cars()

chart_1 = alt.Chart(cars).mark_point().encode(
    x = "Horsepower",
    y = "Miles_per_Gallon",
    color = "Origin",
    tooltip = ["Miles_per_Gallon", "Horsepower"]
).interactive()

app.layout = dbc.Container([
    dbc.Row([
        #First plot
        #A checkbox to select wether or not to display plot
        dbc.Col(dcc.Checklist(id = "show_chart", options = ["Show chart"])),
        #Vega is an Altair display. dcc.Graph can be used for plotly.
        dbc.Col(dvc.Vega(id = "scatter_1", spec = {})),
    ]),

    #Second plot
    #A dropdown to select which variable will be plotted
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id = "y_col", options = cars.columns, value = "Horsepower"),
            dvc.Vega(id = "scatter_2", spec = {}, signalsToObserve=["selection"]),
        ]),
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(
                    dbc.Card(id = "card_avg"),
                    label = "Card"
                ),
                dbc.Tab([
                    dcc.Markdown("You selected the following points: "),
                    #This goes along "signalsToObserve" to interact with selected points
                    dcc.Markdown(id = "signal_data_output"),
                ],
                label = "Summary"
                ),
            ]),
        ]),
    ]),

    #Third plot
    dcc.RangeSlider(
        id = "x_range",
        min = cars["Horsepower"].min(),
        max = cars["Horsepower"].max(),
        value = [cars["Horsepower"].min(), cars["Horsepower"].max()],
        updatemode = "drag"
    ),
    dvc.Vega(id = "scatter_3", spec = {}),

])

#First Plot
@callback(
    Output("scatter_1", "spec"),
    Input("show_chart", "value")
)
def create_chart(show_chart):
    if show_chart:
        return chart_1.to_dict()
    else:
        return {}

#Second Plot
@callback(
    Output("scatter_2", "spec"),
    Output("signal_data_output", "children"),
    Output("card_avg", "children"),
    #This is for selected point interaction:
    Input("y_col", "value"),
    Input("scatter_2", "signalData")
)
def choosex(y_col, signal_data):
    brush = alt.selection_point(fields=["Miles_per_Gallon", y_col], name = "selection")
    chart = alt.Chart(cars).mark_point(size = 50).encode(
        x = "Cylinders",
        y = y_col,
        tooltip = "Name",
        color = "Origin",
    ).add_params(brush).to_dict()

    card_avg = [
        dbc.CardHeader(f'Average {y_col}'),
        dbc.CardBody(f'{cars[y_col].mean()}')
    ]
    
    if signal_data:
        return chart, f'{signal_data["selection"]}', card_avg
    else:
        return chart, f'{signal_data}', card_avg

#Third Plot
@callback(
    Output("scatter_3", "spec"),
    Input("x_range", "value")
)
def slidex(x_range):
    return(
        alt.Chart(
            cars[cars["Horsepower"].between(x_range[0], x_range[1])]
        ).mark_point().encode(
            x = "Horsepower",
            y = "Miles_per_Gallon",
            color = "Displacement",
            tooltip = "Origin"
        ).interactive().to_dict()
    )

if __name__ == "__main__":
    app.run(debug = False)