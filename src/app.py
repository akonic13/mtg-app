# Import required libraries
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.figure_factory as ff

# Read the card data data into pandas dataframe

card_data = pd.read_csv('https://raw.githubusercontent.com/akonic13/mtg-app/main/card_data_test.csv')
df = card_data.dropna(subset=['Price'], axis=0)

dfall = df.dropna(subset=['Price'], axis=0)

# drop cards over $30
# df2 = df[df['Price']<=30.00]
# df2 = df2[df2['Rarity']!='S']

# df for rarities
dfC = dfall[dfall['Rarity'] == 'C']
dfU = dfall[dfall['Rarity'] == 'U']
dfR = dfall[dfall['Rarity'] == 'R']
dfM = dfall[dfall['Rarity'] == 'M']
'''
Count occurences of the 7 card types
'''


def get_types(df):
    def typer(cardtype):
        if cardtype in [np.nan]:
            return 0

        elif cardtype.find(_) != -1:
            return 1
        else:
            return 0

    types = ['Land', 'Creature', 'Artifact', 'Enchantment', 'Instant', 'Sorcery', 'Planeswalker']
    typecount = []
    for i, _ in enumerate(types):
        typecount.append(float(df['Card_type1'].apply(typer).sum()) + float(df['Card_type2'].apply(typer).sum()))
        df[_] = df['Card_type1'].apply(typer) + df['Card_type2'].apply(typer)

    dftypes = pd.DataFrame(data={'Type': types, 'Count': np.array(typecount)})
    dftypes = dftypes.sort_values(by='Count')
    dfcolor = df['Color'].value_counts().reset_index()
    dfcolor = dfcolor.rename(columns={'Color': 'Count', 'index': 'Color'})

    return df,dftypes,dfcolor


# Create a dash application
app = dash.Dash(__name__)
server = app.server

# Build dash app layout
app.layout = html.Div(children=[ html.H1('Magic the Gathering Card Analysis',
                                style={'textAlign': 'center', 'color': '#503D36',
                                'font-size': 30}),
                                dcc.Dropdown(id='input-rarity',options=[
                                    {'label': 'Common','value': 'C'},
                                    {'label':'Uncommon','value': 'U'},
                                    {'label':'Rare','value':'R'},
                                    {'label': 'Mythic Rare','value':'M'},
                                    {'label':'All rarities','value':'all'}],placeholder='Select a card rarity',style={'text-align-last':'center'}),
                                # Segment 1
                                # Segment 2
                                html.Div([ ],id='color-plot', style={'width':'65%'}),
                                # Segment 3
                                html.Div([ ],id='type-plot', style={'width':'65%'})
                                ])

""" Compute_info function description

This function takes in airline data and selected year as an input and performs computation for creating charts and plots.

Arguments:
    airline_data: Input airline data.
    entered_year: Input year for which computation needs to be performed.

Returns:
    Computed average dataframes for carrier delay, weather delay, NAS delay, security delay, and late aircraft delay.

"""

"""Callback Function

Function that returns fugures using the provided input year.

Arguments:

    entered_year: Input year provided by the user.

Returns:

    List of figures computed using the provided helper function `compute_info`.
"""
# Callback decorator
@app.callback([Output(component_id='type-plot', component_property='children'),
               Output(component_id='color-plot', component_property='children')],Input(component_id='input-rarity', component_property='value'))
# Computation to callback function and return graph
def get_graph(rarity):
    if rarity == 'all':
        df,types,color = get_types(dfall)
        type_fig = px.histogram(types.sort_values('Count'),x='Type',y='Count',title='Type Distribution')
        color_fig = px.histogram(color.sort_values('Count'), x='Color', y='Count', title='Type Distribution')
        #type_fig = px.histogram(dfall, x='Color', y=dfall['Color'].value_counts().tolist(), title='Type Distribution')
        return[dcc.Graph(figure=type_fig),dcc.Graph(figure=color_fig)]
    if rarity == 'C':
        df, types,color = get_types(dfC)
        type_fig = px.histogram(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution')
        color_fig = px.histogram(color.sort_values('Count'), x='Color', y='Count', title='Type Distribution')
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig)]
    if rarity == 'U':
        df, types,color = get_types(dfU)
        type_fig = px.histogram(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution')
        color_fig = px.histogram(color.sort_values('Count'), x='Color', y='Count', title='Type Distribution')
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig)]
    if rarity == 'R':
        df, types,color = get_types(dR)
        type_fig = px.histogram(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution')
        color_fig = px.histogram(color.sort_values('Count'), x='Color', y='Count', title='Type Distribution')
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig)]
    if rarity == 'M':
        df, types,color = get_types(dfM)
        type_fig = px.histogram(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution')
        color_fig = px.histogram(color.sort_values('Count'), x='Color', y='Count', title='Type Distribution')
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig)]

    else:
        return []


# Run the app
if __name__ == '__main__':
    app.run_server()