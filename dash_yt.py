import cleaning_yt
import pandas as pd

from dash import Dash ,html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objs as go


# chargement des dataframes, on prend les 100 premiers de chaque dataframe car l'opération peut prendre plusiseurs minutes environ 4-6 min en moyenne
actif_df = pd.read_excel('actif.xlsx').head(100)
inactif_df = pd.read_excel('inactif.xlsx').head(100)
df_filter_df = pd.read_excel('df_filter.xlsx').head(100)
top_channel_df = pd.read_excel('top_channel.xlsx').head(100)

# Graphiques df_filter_df 

fig_subscribers = px.bar(df_filter_df, x='category', y='subscribers', title='Nombre d\'abonnés par catégorie')
fig_views = px.scatter(df_filter_df, x='display_name', y='videos_views', size='subscribers', color='category',
                       title='Répartition des vues par chaîne', hover_name='display_name')
df_filter_df['like_dislike_ratio'] = df_filter_df['likes'] / (df_filter_df['dislikes'] + 1)  # +1 pour éviter la division par zéro
fig_ratio = px.bar(df_filter_df, x='display_name', y='like_dislike_ratio', title='Rapport likes/dislikes par chaîne')


# Graphiques top_channel_df
fig_subscribers_evolution = px.line(top_channel_df, x='created', y='subscribers', title='Évolution du nombre d\'abonnés dans le temps', color='display_name')

# Graphiques actif_df
fig_active_videos = px.histogram(actif_df, x='nbVidSince_2021-06-30', title='Nombre de vidéos publiées par les chaînes actives depuis 2021-06-30')
fig_correlation_active = px.scatter(actif_df, x='nbVidSince_2021-06-30', y='subscribers', title='Corrélation entre le nombre de vidéos et les abonnés pour les chaînes actives')

# Graphiques inactif_df
fig_inactive_videos = px.histogram(inactif_df, x='nbVidSince_2021-06-30', title='Nombre de vidéos publiées par les chaînes inactives depuis 2021-06-30')
fig_correlation_inactive = px.scatter(inactif_df, x='nbVidSince_2021-06-30', y='subscribers', title='Corrélation entre le nombre de vidéos et les abonnés pour les chaînes inactives')




# Style pour les cartes (Card) pour assurer la cohérence avec le fond noir
card_style = {
    'backgroundColor': '#343a40',
    'color': '#fff',
    'marginBottom': '10px',
    'borderRadius': '5px',
    'padding': '10px'
}


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = html.Div(children=[
    dbc.Container([
        dbc.Row(dbc.Col(html.H1("Dashboard YouTube", style={'color': '#fff'}), width=12)),
        
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_subscribers), style=card_style, width=6),
            dbc.Col(dcc.Graph(figure=fig_views), style=card_style, width=6)
        ]),
        
        dbc.Row(dbc.Col(dcc.Graph(figure=fig_ratio), style=card_style, width=12)),
        
        dbc.Row(dbc.Col(dcc.Graph(figure=fig_subscribers_evolution), style=card_style, width=12)),
        
        # Graphiques pour les chaînes actives
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_active_videos), width=6),
            dbc.Col(dcc.Graph(figure=fig_correlation_active), width=6)
        ]),
        # Graphiques pour les chaînes inactives
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_inactive_videos), width=6),
            dbc.Col(dcc.Graph(figure=fig_correlation_inactive), width=6)
        ]),
    ], fluid=True, style={'backgroundColor': '#343a40', 'color': '#fff'})
])


if __name__ == '__main__':
    app.run_server(debug=True)