# Import required libraries
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.figure_factory as ff

# Read the card data data into pandas dataframe

card_data = pd.read_csv('https://raw.githubusercontent.com/akonic13/mtg-web-scraper/main/card_data.csv')
dftest = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
df = card_data.dropna(subset=['Price'], axis=0)

dfall = df.dropna(subset=['Price'], axis=0)

# drop cards over $30
# df2 = df[df['Price']<=30.00]
dfall = dfall[dfall['Rarity']!='S']
dfall = dfall[dfall['Rarity']!='B']

def remove_legend(card_type):
    if pd.isnull(card_type) != True:
        card_type = card_type.replace('Legendary','')
    return card_type

dfall['Card_type2'] = dfall['Card_type2'].apply(remove_legend)

# df for rarities
dfC = dfall[dfall['Rarity'] == 'C']
dfU = dfall[dfall['Rarity'] == 'U']
dfR = dfall[dfall['Rarity'] == 'R']
dfM = dfall[dfall['Rarity'] == 'M']
dflist = [dfall,dfC,dfU,dfR,dfM]
'''
Count occurences of the 7 card types
'''


def calc_values(df):
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

    dfprice_color = df.groupby('Color').mean()['Price'].reset_index().sort_values('Price')

    price_type = []
    for _ in types:
        price_type.append([_, df[df[_] != 0].mean()['Price']])

    dfprice_type = pd.DataFrame(data=price_type, columns=['Type', 'Price'])
    dfprice_type = dfprice_type.sort_values('Price')


    return df,dftypes,dfcolor,dfprice_color,dfprice_type


# Create a dash application
app = dash.Dash(__name__,meta_tags=[{'name':'viewport','content':'width=device-width,initial-scale=1'}])
server = app.server

# Build dash app layout
app.layout = html.Div(children=[ html.H1('Magic the Gathering Card Analysis: Commander Format',
                                style={'textAlign': 'center', 'color': '#503D36',
                                'font-size': 30}),
                                dcc.Dropdown(id='input-rarity',options=[
                                    {'label': 'Common','value': 'C'},
                                    {'label':'Uncommon','value': 'U'},
                                    {'label':'Rare','value':'R'},
                                    {'label': 'Mythic Rare','value':'M'},
                                    {'label':'All rarities','value':'all'}],placeholder='Select a card rarity',style={'text-align-last':'center'}),
                                # Segment 1
                                dash_table.DataTable(id='card-table',data=df.to_dict('records'),columns=[{'name':i,'id':i} for i in df.columns],style_cell={'textAlign':'center'},sort_action='native',page_size=10),
                                # Segment 2
                                html.Div([ ],id='color-plot'),
                                # Segment 3
                                html.Div([ ],id='type-plot'),
                                html.Div([ ],id='price-plot'),
                                html.Div([ ],id='price2-plot')
                                ])


"""Callback Function

Function that returns fugures using the provided input year.

Arguments:

    entered_year: Input year provided by the user.

Returns:

    List of figures computed using the provided helper function `compute_info`.
"""
# Callback decorator
@app.callback([Output(component_id='type-plot', component_property='children'),
               Output(component_id='color-plot', component_property='children'),
               Output(component_id='price-plot',component_property='children'),
               Output(component_id='price2-plot',component_property='children'),
               Output(component_id='card-table',component_property='data')],Input(component_id='input-rarity', component_property='value'))
# Computation to callback function and return graph
def get_graph(rarity):
    if rarity == 'all':
        df,types, color, price_color, price_types = calc_values(dfall)
        type_fig = px.bar(types.sort_values('Count'),x='Type',y='Count',title='Type Distribution',labels={'Type':'Card Type','Count': '# of Occurences'})
        color_fig = px.bar(color.sort_values('Count'), x='Color', y='Count', title='Color Identity Distribution',labels={'Color':'Color Identitiy','Count': '# of Occurences'})
        price_fig = px.bar(price_color, x='Color', y='Price', title='Distribution of Average Price Across Colors',labels={'Color':'Color Identity','Price':'Average Price (USD)'})
        price_fig2 = px.bar(price_types, x='Type', y='Price', title='Distribution of Average Price Across Card Types',labels={'Type':'Card Type','Price':'Average Price (USD)'})
        table = dash_table.DataTable(id='card-table',data=dfM.to_dict('records'),columns=[{'name':i,'id':i} for i in df.columns],page_size=10)
        return[dcc.Graph(figure=type_fig),dcc.Graph(figure=color_fig),dcc.Graph(figure=price_fig),dcc.Graph(figure=price_fig2),dfall.to_dict('records')]
    if rarity == 'C':
        df, types, color, price_color, price_types = calc_values(dfC)
        type_fig = px.bar(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution',
                          labels={'Type': 'Card Type', 'Count': '# of Occurences'})
        color_fig = px.bar(color.sort_values('Count'), x='Color', y='Count', title='Color Identity Distribution',
                           labels={'Color': 'Color Identitiy', 'Count': '# of Occurences'})
        price_fig = px.bar(price_color, x='Color', y='Price', title='Distribution of Average Price Across Colors',
                           labels={'Color': 'Color Identity', 'Price': 'Average Price (USD)'})
        price_fig2 = px.bar(price_types, x='Type', y='Price', title='Distribution of Average Price Across Card Types',
                            labels={'Type': 'Card Type', 'Price': 'Average Price (USD)'})
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig), dcc.Graph(figure=price_fig),
                dcc.Graph(figure=price_fig2),dfC.to_dict('records')]
    if rarity == 'U':
        df, types, color, price_color, price_types = calc_values(dfU)
        type_fig = px.bar(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution',
                          labels={'Type': 'Card Type', 'Count': '# of Occurences'})
        color_fig = px.bar(color.sort_values('Count'), x='Color', y='Count', title='Color Identity Distribution',
                           labels={'Color': 'Color Identitiy', 'Count': '# of Occurences'})
        price_fig = px.bar(price_color, x='Color', y='Price', title='Distribution of Average Price Across Colors',
                           labels={'Color': 'Color Identity', 'Price': 'Average Price (USD)'})
        price_fig2 = px.bar(price_types, x='Type', y='Price', title='Distribution of Average Price Across Card Types',
                            labels={'Type': 'Card Type', 'Price': 'Average Price (USD)'})
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig), dcc.Graph(figure=price_fig),
                dcc.Graph(figure=price_fig2),dfU.to_dict('records')]
    if rarity == 'R':
        df, types, color, price_color, price_types = calc_values(dfR)
        type_fig = px.bar(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution',
                          labels={'Type': 'Card Type', 'Count': '# of Occurences'})
        color_fig = px.bar(color.sort_values('Count'), x='Color', y='Count', title='Color Identity Distribution',
                           labels={'Color': 'Color Identitiy', 'Count': '# of Occurences'})
        price_fig = px.bar(price_color, x='Color', y='Price', title='Distribution of Average Price Across Colors',
                           labels={'Color': 'Color Identity', 'Price': 'Average Price (USD)'})
        price_fig2 = px.bar(price_types, x='Type', y='Price', title='Distribution of Average Price Across Card Types',
                            labels={'Type': 'Card Type', 'Price': 'Average Price (USD)'})
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig), dcc.Graph(figure=price_fig),
                dcc.Graph(figure=price_fig2),dfR.to_dict('records')]
    if rarity == 'M':
        df, types, color, price_color, price_types = calc_values(dfM)
        type_fig = px.bar(types.sort_values('Count'), x='Type', y='Count', title='Type Distribution',
                          labels={'Type': 'Card Type', 'Count': '# of Occurences'})
        color_fig = px.bar(color.sort_values('Count'), x='Color', y='Count', title='Color Identity Distribution',
                           labels={'Color': 'Color Identitiy', 'Count': '# of Occurences'})
        price_fig = px.bar(price_color, x='Color', y='Price', title='Distribution of Average Price Across Colors',
                           labels={'Color': 'Color Identity', 'Price': 'Average Price (USD)'})
        price_fig2 = px.bar(price_types, x='Type', y='Price', title='Distribution of Average Price Across Card Types',
                            labels={'Type': 'Card Type', 'Price': 'Average Price (USD)'})
        return [dcc.Graph(figure=type_fig), dcc.Graph(figure=color_fig), dcc.Graph(figure=price_fig),
                dcc.Graph(figure=price_fig2),dfM.to_dict('records')]
    else:
        return[dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update]


# Run the app
if __name__ == '__main__':
    app.run_server()