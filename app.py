import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide")

df = pd.read_csv('data/data.csv')

st.write('## :rugby_football: 🤓 Six Nations Fantasy Rugby Analytics 🤓 :rugby_football: ')

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

df['flag'] = df['team'].map(lambda x: emoji_map[x])

tab1, tab2, tab3 = st.tabs(['Player Value Analysis', 'Summary Stats', 'Players Head to Head'])

# Filters


with tab1:
    st.markdown('## Player Value Analysis')
    st.markdown('`This tab looks at the relationship between the points a player earns and their price.\
                Price is on the x-axis and points on the y-axis. The dotted lines represent \
                different points per price ratios. The higher the points per price ratio the better \
                value that player represents.`')
    tab1_selected_round = st.radio(
        "Filter by round:",
        ['Round 1', 'Round 2', 'Round 3', 'Round 4', 'Round 5', 'All Rounds'],
        horizontal=True
        )
    t1col1, t1col2 = st.columns(2)

    with t1col1:
        selected_positions =  st.multiselect(
            'Filter by positions:',
            positions,
            default=positions)

    with t1col2:
        selected_teams =  st.multiselect(
            'Filter by teams:',
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
            custom_data=['name', 'position'],
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
                    text=r['flag'],
                    ax=0,
                    ay=0,
                    font_size=20
                    )
        

        fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Position: %{customdata[1]}<br>Price: %{x} <br>Points: %{y}"
    )
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_layout(xaxis_range=[min_x - 3, max_x + 3])
        fig.update_layout(yaxis_range=[min_y - 5, max_y + 7])
        fig.update_layout(showlegend=False, xaxis_title='Price', yaxis_title='Points per Round')
        return fig

    fig = plot_scatter(df, positions=selected_positions, teams=selected_teams, round_name=tab1_selected_round)

    st.write(fig)

with tab2:
    tab2_selected_round = st.radio(
        "",
        ['Round 1', 'Round 2', 'Round 3', 'Round 4', 'Round 5', 'All Rounds'],
        horizontal=True,
        key='tab2'
        )
    tab2_price_col = rounds[tab2_selected_round]['price_col']
    tab2_points_col = rounds[tab2_selected_round]['points_col']
    t2col1, t2col2 = st.columns(2)
    played = df[df[tab2_points_col]!=0].copy()

    with t2col1:
        by_team = played.groupby(['team', 'flag'], as_index=False)[[tab2_points_col]].mean().sort_values(by=tab2_points_col)
        by_team[tab2_points_col] = by_team[tab2_points_col].round(1)
        fig_team = px.bar(by_team, 
                     y='team',
                     x=tab2_points_col,
                     orientation='h',
                     text=by_team['flag'] + ' ' + by_team[tab2_points_col].astype(str))
        fig_team.update_layout(showlegend=False, 
                            title='Performance by team',
                            titlefont=dict(size=24),
                               yaxis = dict(
                                    title='Team',
                                    tickfont = dict(size=14),
                                    titlefont = dict(size=16))
                                    ,
        xaxis = dict(
                            title='Avg points per player',
                            tickfont = dict(size=14),
                            titlefont = dict(size=16))
        )

        fig_team.update_traces(textposition='inside')
        fig_team.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
        fig_team.update_traces(marker_color='rgb(255,255,255)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5)
        st.write(fig_team)
    with t2col2:
        # st.write('### Performance by position')
        by_position = (played.groupby(['position'], 
                                     as_index=False)[[tab2_points_col]]
                                     .mean()
                                     .sort_values(by=tab2_points_col, ascending=False)
        )
        by_position[tab2_points_col] = by_position[tab2_points_col].round(1)
        fig_position= px.bar(by_position, 
                     y='position',
                     x=tab2_points_col,
                     orientation='h',
                     text=tab2_points_col,
                     color='position')
        fig_position.update_layout(showlegend=False, 
                            title='Performance by position',
                            titlefont=dict(size=24),
                               yaxis = dict(
                                    title='Position',
                                    tickfont = dict(size=14),
                                    titlefont = dict(size=16))
                                    ,
        xaxis = dict(
                            title='Avg points per player',
                            tickfont = dict(size=14),
                            titlefont = dict(size=16))
        )

        fig_position.update_traces(textposition='inside')
        # fig_position.update_layout(uniformtext_minsize=20)
        st.write(fig_position)

with tab3:   
    played = df[df['num_matches']!=0]
    played['name_flag'] = played['name'] + ' ' + played['flag']
    players = played['name_flag'].unique()
    t3_players_selected =  st.multiselect(
            'Select players to compare:',
            players,
            default=['Marcus Smith 🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Hugo Keenan 🇮🇪'])
    
    t3col1, t3col2 = st.columns(2, gap='large')

    with t3col1:
        st.markdown("### Cumulative points by week")
        comp_by_round = played[played['name_flag'].isin(t3_players_selected)].set_index('name_flag')
        comp_by_round = comp_by_round.filter(like='points_round')
        comp_by_round[0] = 0
        for i in range(1,6):
            try:
                comp_by_round[i] = comp_by_round[f'points_round_{i}']
            except:
                comp_by_round[i] = None
        comp_by_round = comp_by_round[[0,1,2,3,4,5]].T.cumsum()
        fig_by_round = px.line(comp_by_round, markers=True, width=750, height=600)
        fig_by_round.update_layout(showlegend=True, 
                                yaxis = dict(
                                        title='Points',
                                        tickfont = dict(size=14),
                                        titlefont = dict(size=16))
                                        ,
            xaxis = dict(
                                title='Round',
                                tickfont = dict(size=14),
                                titlefont = dict(size=16))

        )
        st.write(fig_by_round)

    
    with t3col2:
        st.markdown("### Radar Chart Comparison")
        st.markdown("`Each point area (e.g. Kicking) is ranked from 0 to 1 with 0 being the worst of all players in the competition and 1 being the best.`""")
        radar_df = played.set_index('name_flag')
        radar_df['Kicking'] = (
            radar_df['Conversion'] * 2
            + radar_df['Penalty'] * 5
            + radar_df['Drop goal'] * 7
            + radar_df['Kick 50-22'] * 10
        )
        radar_df['Tackling'] = (
            radar_df['Tackles'] * 1
            + radar_df['Dominant tackles'] * 7
        )
        radar_df['Tries + Assists'] = (
            radar_df['Try'] * 15
            + radar_df['Assists'] * 7
        )
        radar_df['Carries + Linebreaks'] = (
            radar_df['Line-breaks'] * 7
            + radar_df['Metres carried'] * 0.2
        )
        radar_df['Breakdown + Lineout Steals'] = (
            radar_df['Breakdown steal'] * 7
            + radar_df['Lineout steal'] * 7
        )
        
        cols = ['Kicking', 'Tackling', 'Tries + Assists',
                'Carries + Linebreaks','Breakdown + Lineout Steals']
        
        for col in cols:
            radar_df[col] = radar_df[col] / radar_df[col].max()
        
        # fig_radar = px.line_polar(radar_to_plot, r='r', theta='theta', line_close=True)
        # st.write(fig_radar)
    
        fig_radar = go.Figure()
        for player in t3_players_selected:

            fig_radar.add_trace(go.Scatterpolar(
                r=radar_df.loc[player][cols].values,
                theta=cols,
                fill='toself',
                name=player
            ))

        fig_radar.update_layout(
            width=600,
            height=600,
            margin = dict(l = 75, r = 20),
        polar=dict(
            radialaxis=dict(
            visible=True,
            range=[0, 1]
            )),
        showlegend=True
        )
        st.write(fig_radar)
    

    st.write('### All player data')
    st.markdown("`Each point area (e.g. Kicking) is ranked from 0 to 1 with 0 being the worst of all players in the competition and 1 being the best.`""")

    all_player_df = radar_df[['position', 'team', 'num_matches', 
                              'latest_price', 'points_all_rounds',
                              ] + cols]
    st.dataframe(all_player_df, use_container_width=True)
