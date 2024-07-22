'''
 # @ Create Time: 2024-07-11 15:35:49.557159
'''

import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash import Dash
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pathlib

app = Dash(__name__, title="TWstock dividend forecast")

server = app.server

data_file = '2023final_predicted_data_test_1.csv'

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df = pd.read_csv(DATA_PATH.joinpath(data_file))

df['預估年度殖利率(%)'] = df['預估年度殖利率(%)'].str.replace("%", '').astype(float)
df['預估年度殖利率(%)'] = df['預估年度殖利率(%)'].round(3)

df_1 = df.groupby(['所屬行業'],as_index=False)['預估配發股利總金額(百萬)'].sum()
df_1['現金股利總額佔比(%)']=0

for i in range(len(df_1)):
    df_1['現金股利總額佔比(%)'][i] = round(df_1['預估配發股利總金額(百萬)'][i]/df_1['預估配發股利總金額(百萬)'].sum()*100,2)
df_1 = df_1.sort_values(by='預估配發股利總金額(百萬)', ascending=False)


#create_treemap_figure
fig = px.treemap(df, path=['所屬行業', '證券代碼'], values='市值(百萬)',
                 color='預估年度殖利率(%)',
                 #color_continuous_scale='Tealrose',
                 color_continuous_scale='OrRd',
                 custom_data=['股票簡稱','最近收盤股價','預估年度殖利率(%)','預估配發股利總金額(百萬)'],
                 color_continuous_midpoint=0.1,
                 title = 'TW-Stock market cap and dividend forecast treemap',
                 #width=1800, 
                 height=1000,
                 range_color=[0,15]
                 )
fig.update_traces(textposition='middle center', 
                  textfont_size=12,
                  texttemplate= "%{label}<br>%{customdata[0]}<br>最近收盤：%{customdata[1]}<br>預估殖利率：%{customdata[2]}",
                  hovertemplate="%{label}<br>預估股利總額(百萬)：%{customdata[3]}<extra></extra>")
fig.update_layout(margin = dict(t=25, l=5, r=5, b=25),)

#create_bar_figure
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1.add_trace(
    go.Bar(x=df_1['所屬行業'], y=df_1['預估配發股利總金額(百萬)'],name="預估配發股利總金額(百萬)"),
    secondary_y=False,)

fig1.add_trace(
    go.Scatter(x=df_1['所屬行業'], y=df_1['現金股利總額佔比(%)'], name="現金股利總額佔比(%)"),
    secondary_y=True,)

fig1.update_layout(
    title_text="各行業別預估股利總額及佔比")

fig1.update_xaxes(title_text="所屬行業")

fig1.update_yaxes(title_text="預估配發股利總金額(百萬)", secondary_y=False)
fig1.update_yaxes(title_text="現金股利總額佔比(%)", secondary_y=True)

app.layout = html.Div([
    html.H2(children='TW stock '+data_file[:4]+'dividend treemap'),
    dcc.Graph(
        id='test',
        figure = fig),
    dcc.RangeSlider(
        id='dividend-slider',
        min=df['預估年度殖利率(%)'].min(),
        max=round(df['預估年度殖利率(%)'].max())+1,
        value=[round(df['預估年度殖利率(%)'].max())+1,df['預估年度殖利率(%)'].min()],
        step=1,
        #marks={str(year): str(year) for year in df['year'].unique()}
    ),
    dcc.Graph(
        figure = fig1)
])
@app.callback(
    dash.dependencies.Output("test", "figure"), 
    [dash.dependencies.Input("dividend-slider", "value")])
#往下放一個函數，當call back發生的時候，會更新output
def data_filter(dividend):
    fig = px.treemap(df[(df['預估年度殖利率(%)']>=min(dividend))&(df['預估年度殖利率(%)']<=max(dividend))], path=['所屬行業', '證券代碼'], values='市值(百萬)',
                 color='預估年度殖利率(%)',
                 #color_continuous_scale='Tealrose',
                 color_continuous_scale='OrRd',
                 custom_data=['股票簡稱','最近收盤股價','預估年度殖利率(%)','預估配發股利總金額(百萬)'],
                 color_continuous_midpoint=0.1,
                 title = 'TW-Stock market cap and dividend forecast treemap',
                 #width=1800, 
                 height=1000,
                 range_color=[0,15]
                )
    fig.update_traces(textposition='middle center', 
                  textfont_size=12,
                  texttemplate= "%{label}<br>%{customdata[0]}<br>最近收盤：%{customdata[1]}<br>預估殖利率：%{customdata[2]}",
                  hovertemplate="%{label}<br>預估股利總額(百萬)：%{customdata[3]}<extra></extra>")
    fig.update_layout(margin = dict(t=25, l=5, r=5, b=25))
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
