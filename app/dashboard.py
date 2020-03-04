import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
import datetime as dt
import pandas as pd
import plotly.express as px

import os
import pandas as pd



data_files = os.listdir('./data')
dates = [x[5:15] for x in data_files]

meta_data = pd.DataFrame()
for x in data_files:
        games = ['IW', 'WW2', 'Bo4', 'MW']
        temp1 = pd.read_csv('./data/{}'.format(x))
        date = pd.to_datetime(x[5:15])
        if date <= pd.to_datetime('2017-08-13'):
            temp1['game'] = games[0]
        elif date <= pd.to_datetime('2018-08-19'):
            temp1['game'] = games[1]
        elif date <= pd.to_datetime('2019-08-18'):
            temp1['game'] = games[2]
        else:
            temp1['game'] = games[3]
        event = x[16:-4]
        temp1['event'] = event
        meta_data = meta_data.append(temp1, ignore_index = True)

meta_data.to_csv('./outputs/meta_data.csv')

stat_rm_ls = ['game', 'match id', 'series id', 'end time', 
              'mode', 'map', 'team', 'player']

stat_ls = list(meta_data.columns[9:])

player_names = meta_data['player'].unique()
team_names = meta_data['team'].unique()
title_names = meta_data['game'].unique()
mode_names = ['All', 'Respawn'] + list(meta_data['mode'].unique())
map_names = meta_data['map'].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div([
    
    html.Div([
        html.H1('CWL Dashboard')
    ]),
    
    html.Div([
        html.Div([
            
            html.H2('Options'),
            html.H2(' '),
            
            html.H4('Select Title: '),
            dcc.Dropdown(id='title-drop',
                          options=[
                              {'label': x, 'value': x} for x in title_names
                          ],
                          multi=True),
            
            html.H4('Select Player: '),
            dcc.Dropdown(id='player-drop',
                         options=[
                             {'label': x, 'value':x} for x in player_names
                        ],
                         multi=True), 
            
            html.H4('Select Mode: '),
            dcc.Dropdown(id='mode-drop',
                         options=[
                             {'label': x, 'value': x} for x in mode_names
                         ]),
            
            html.H4('Select Statistic to View: '),
            dcc.Dropdown(id='stat-id',
                         options=[
                             {'label': x, 'value': x} for x in stat_ls
                         ])
            
        ], className='two columns'),
        
        html.Div([
            html.H2('Stats Figure'),
            dcc.Graph(id='stat-graph'),
            
            # TODO will add in at a later date
            #html.H2('Stats Table'),
            #dash_table.DataTable(id='stat-table')
        ])
    ])
]) 

@app.callback(
    Output('stat-graph', 'figure'),
    [Input('title-drop', 'value'),
     Input('player-drop', 'value'),
     Input('mode-drop', 'value'),
     Input('stat-id', 'value')]
)
def update_figure(title, player, modes, stat):
    df = meta_data
    df = df[df['game'].isin([title])]
    df = df[df['player'].isin([player])]
    if modes == 'Respawn':
        mode_list = mode_names[2:].remove('Search & Destroy')
    elif modes == 'ALL':
        mode_list = mode_names[2:]
    else:
        mode_list = modes
    df = df[df['mode'].isin([mode_list])]
    plot_df = df.groupby(['game', 'player', 'mode'])[str(stat)].mean().reset_index()
    fig = px.scatter(plot_df, x='game', y=str(stat), color='player', marginal_y='rug')
    return fig

# Main
if __name__ == "__main__":
    app.run_server(debug=True)