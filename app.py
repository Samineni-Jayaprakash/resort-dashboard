#!/usr/bin/env python
# coding: utf-8

# In[86]:


from dash import Dash, html,dcc,dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import pandas as pd
import numpy as np

resorts=resorts = (pd.read_csv("resorts.csv", encoding = "ISO-8859-1")
                   .assign(
                       country_elevation_rank=lambda x:x.groupby("Country",as_index=False)["Highest point"].rank(ascending=False),
                       country_price_rank=lambda x:x.groupby("Country",as_index=False)["Price"].rank(ascending=False),
                       country_slope_rank=lambda x:x.groupby("Country",as_index=False)["Total slopes"].rank(ascending=False),
                       country_cannon_rank=lambda x:x.groupby("Country",as_index=False)["Snow cannons"].rank(ascending=False)))
resorts.rename(columns={'Highest point':'Highestpoint','Total slopes':'Totalslopes','Summer skiing':'Summerskiing'},inplace=True)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app=Dash(__name__,external_stylesheets=[dbc.themes.QUARTZ,dbc_css])
load_figure_template("QUARTZ")
app.layout=dbc.Container([
    dbc.Tabs(className="dbc",children=[ 
              
              #-------------------------------------Tab1-------------------------------------------------
              dbc.Tab(label="Resort-map",children=[
                          html.H1(id="title",style={"textAlighn":"center"}),
                          dbc.Row([
                              dbc.Col([
                                  dbc.Card([
                                  dcc.Markdown(" **price Limit:** "),
                                  dcc.Slider(id="price-pick",
                                             min=0,
                                             max=150,
                                             step=20,
                                             value=50,
                                             className="dbc"),
                                      html.Br(),
                                      dcc.Markdown("**Feature Performances**"),
                                      dcc.Checklist(id="summer-pick",
                                                  options=[{"label":"Has summer Skiing","value":"Yes"}],
                                                  value=[]),
                                      dcc.Checklist(id="night-pick",
                                                  options=[{"label":"Has night Skiing","value":"Yes"}],
                                                  value=[]),
                                      dcc.Checklist(id="snow-pick",
                                                  options=[{"label":"Has snow Skiing","value":"Yes"}],
                                                  value=[])
                                      
                                  ])
                              ],width=3),
                              dbc.Col([
                                  dbc.Card(dcc.Graph(id="resort-map"))],width=9)
                              
                          ])
                      ]),
        #---------------------------------------------------------------Tab2---------------------------------------
        dbc.Tab(label="Country Profiler",children=[
                    html.H1(id="country-title",style={"textAlign":"center"}),
                    dbc.Row([
                        dbc.Col([
                            dcc.Markdown("**Select a continent**"),
                            dcc.Dropdown(id="continent-dropdown",
                                         options=resorts["Continent"].unique(),
                                         value="Europe",
                                         className="dbc"
                                        ),
                            html.Br(),
                            dcc.Markdown("**Select a country**"),
                            dcc.Dropdown(id="country-dropdown",
                                         value="Norway",
                                         className="dbc"
                                        ),
                            html.Br(),
                            dcc.Markdown("**Select Matrics:**"),
                            dcc.Dropdown(id="column-picker",
                                         options=resorts.select_dtypes("number").columns[3:],
                                         value=[],
                                         className="dbc"
                                       )
                                
                            
                        ],width=3),
                        
                         dbc.Col([dcc.Graph(id="metric-bar",
                                             hoverData={'points': [{'customdata': ['Hemsedal']}]})],width=6),
                            dbc.Col([
                                dcc.Markdown("**Resort report card**"),
                                dbc.Card(id="resort-name", style={"text-align": "center", "fontSize":20}),
                                dbc.Row([
                                    dbc.Col([dbc.Card(id="elev-kpi"),dbc.Card(id="price-kpi")]),
                                    dbc.Col([dbc.Card(id="slope-kpi"),dbc.Card(id="cannon-kpi")])
                            ])
                        
                    ],width=3)
                            
                ])
            ])
            
    ])
],style={"width":"1300"})

@app.callback(Output("title","children"),
              Output("resort-map","figure"),
              Input("price-pick","value"),
              Input("summer-pick","value"),
              Input("night-pick","value"),
              Input("snow-pick","value"),
             )
def selection(price,summer,night,snow):
    if not price:
        raise PreventUpdate
    df=resorts.loc[resorts["Price"]<=price]
    title=f"Resorts with a ticket price less than ${price}."
    if "Yes" in summer:
        df=df.loc[df["Summerskiing"]=="Yes"]
    if "Yes" in night:
        df=df.loc[df["Nightskiing"]=="Yes"]
    if "Yes" in snow:
        df=df.loc[df["Snowparks"]=="Yes"]
    fig=px.density_map(df,
                       lat="Latitude",
                       lon="Longitude",
                       z="Totalslopes",
                       hover_name="Resort",
                       zoom=2.5,
                       center={"lat":45,"lon":-100},
                       map_style="open-street-map",
                       height=600,
                       width=800,
                       
     )

    return title,fig

@app.callback(
    Output("country-dropdown", "options"), 
    Input("continent-dropdown", "value"))
def country_select(continent):
    return np.sort(resorts.query("Continent == @continent").Country.unique())

@app.callback(
    Output("country-title", "children"),
    Output("metric-bar", "figure"),
    Input("country-dropdown", "value"),
    Input("column-picker", "value")
)
def plot_bar(country, metric): 
    if not country and metric:
        raise PreventUpdate
    title = f"Top Resorts in {country} by {metric}"
    
    df = resorts.query("Country == @country").sort_values(metric, ascending=False)
        
    figure = px.bar(df, x="Resort", y=metric, custom_data=["Resort"]).update_xaxes(showticklabels=False)
        
    return title, figure

@app.callback(Output("resort-name","children"),
              Output("elev-kpi","children"),
              Output("price-kpi","children"),
              Output("slope-kpi","children"),
              Output("cannon-kpi","children"),
              Input("metric-bar","hoverData")
             )
def defsni(hoverData):
    resort = hoverData["points"][0]["customdata"][0]
    df=resorts.query("Resort==@resort")
    elev_rank = f"Elev_Rank: {int(df['country_elevation_rank'])}"
    price_rank=f"price_rank:{int(df["country_price_rank"])}"
    slope_rank=f"slope_rank:{int(df["country_slope_rank"])}"
    cannon_rank=f"cannon_rank:{int(df["country_cannon_rank"])}"

    return resort, elev_rank, price_rank, slope_rank, cannon_rank

if __name__=="__main__":
    port = int(os.environ.get('PORT', 8080))  # Render will set this automatically
    app.run(host='0.0.0.0', port=port, debug=False)

                                  
                          
          



# In[ ]:




