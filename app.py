import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

df = pd.read_csv('data/data.csv')

st.write('## :rugby_football: Guinness Fantasy Rugby Player Picker :rugby_football: ')

# Layout options
rounds = {
    'Round 1':{ 'points_col': 'points_round_1', 'price_col':'price_round_1'},
    'Round 2':{ 'points_col': 'points_round_2', 'price_col':'price_round_2'},
    'Round 3':{ 'points_col': 'points_round_3', 'price_col':'price_round_3'},
    'Round 4':{ 'points_col': 'points_round_4', 'price_col':'price_round_4'},
    'Round 5':{ 'points_col': 'points_round_5', 'price_col':'price_round_5'},
    'All Rounds':{ 'points_col': 'points_per_round_all_rounds', 'price_col':'latest_price'}
}
positions = df.position.unique()
teams = df.team.unique()

emoji_map = {
    'England':'🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'France':'🇫🇷',
    'Italy':'🇮🇹',
    'Wales':'🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'Scotland':'🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'Ireland':'🇮🇪'

}

# Filters
selected_round = st.radio(
    "",
    ['Round 1', 'Round 2', 'Round 3', 'Round 4', 'Round 5', 'All Rounds'],
    horizontal=True
    )

col1, col2 = st.columns(2)

with col1:
    selected_positions =  st.multiselect(
        'Positions:',
        positions,
        default=positions)

with col2:
    selected_teams =  st.multiselect(
        'Teams:',
        teams,
        default=teams)

## Scatter plot
def plot_scatter(df, positions=['back-row'], teams=['France'], round_name='All Rounds'):
    price_col = rounds[round_name]['price_col']
    points_col = rounds[round_name]['points_col']
    
    tp = df[
        (df['position'].isin(positions))
        & (df['team'].isin(teams))
        & (df[points_col] != 0)
            ]
    
    max_x = df[price_col].max()
    min_x = df[df[price_col]!=0][price_col].min()
    max_y = df[points_col].max()
    min_y = df[df[points_col]!=0][points_col].min()


    fig = px.scatter(tp,
           x=price_col, 
           y=points_col,
           hover_data=['name'],
           width=1200, height=600)
    
    ## Add 
    for value in [0, 1, 2, 3, 4, 5 ,6]:
        fig.add_shape(type="line",
                    x0=0, y0=0, x1=max_x, y1=value*max_x,
                    line=dict(
                    color="grey",
                    width=1,
                    dash="dot")
                    )
        fig.add_annotation(x=max_x+1, y=value*max_x,
            text=f"{value} points per price unit",
            showarrow=False,
            arrowhead=1)
        ## Add sub-lines
        for i in [0.25, 0.5 ,0.75]:
            fig.add_shape(type="line",
                    x0=0, y0=0, x1=max_x, y1=(value+i)*max_x,
                    line=dict(
                    color="grey",
                    width=0.5,
                    dash="dot")
                    )


    for i,r in tp.iterrows():
        fig.add_annotation(
                x=r[price_col], y=r[points_col],
                text=emoji_map[r['team']],
                ax=0,
                ay=0,
                font_size=20
                )
    
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.update_layout(xaxis_range=[min_x - 3, max_x + 3])
    fig.update_layout(yaxis_range=[min_y - 5, max_y + 7])
    fig.update_layout(showlegend=False)
    return fig

fig = plot_scatter(df, positions=selected_positions, teams=selected_teams, round_name=selected_round)

st.write(fig)