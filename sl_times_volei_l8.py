# =======================================================================================================================================
# Packages

import streamlit as st
import pandas as pd
import math
import os
# import plotly.graph_objects as go
import random

# =======================================================================================================================================
# Setup streamlit (needs to be the first command)

st.set_page_config(layout = "wide")
st.title('Times L8 🏐')
st.set_page_config(page_title='Times L8 🏐')
st.markdown('---')

# =======================================================================================================================================
# Load raw CSV only once per session

if 'df_players' not in st.session_state:

    # Read raw CSV file with known players
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'known_players.csv')
    df_players = pd.read_csv(csv_path)

    # Add a "presence column"
    df_players['Presente'] = False

    # Sort by name
    df_players = df_players.sort_values(by='Nome').reset_index(drop=True)
 
    # Reorder columns
    df_players = df_players[['Presente','Nome','Genero','Score']]
    
    # Save to session_state
    st.session_state['df_players'] = df_players

# =======================================================================================================================================
# Add/Edit/Present players

with st.expander('Lista de Presença', expanded = False):
    df_edited = st.data_editor(st.session_state['df_players'],
                               num_rows='dynamic',
                               key='editable_table',
                               use_container_width=True,
                               hide_index=True)

    # Button to save changed to session_state
    if st.button('Salvar alterações'):
        st.session_state['df_players'] = df_edited.copy()
        st.success('Alterações salvas na memória temporária')

# =======================================================================================================================================
# Get dataframe from session_state (either raw on edited by user)

df_players = st.session_state['df_players']

# =======================================================================================================================================
# Create dictionary of present players

df_present = df_players[df_players['Presente'] == True]

present_players = {row['Nome']:
                   {'gender': row['Genero'],
                    'score': row['Score'],
                    'mvp': row['Score'] >= 9.0,  # Assuming MVPs are players with score >= 9.0
                    } for _, row in df_present.iterrows()}


# =======================================================================================================================================
# Print number of present players
n_players = len(present_players)
n_male = sum(1 for p in present_players.values() if p['gender'] == 'M')
n_female = sum(1 for p in present_players.values() if p['gender'] == 'F')

st.markdown(f"<div style='text-align: left; font-weight: bold;'>Total de jogadores: {n_players} ({n_male}M + {n_female}F)<br><br></div>", unsafe_allow_html=True)

if n_players > 36:
    st.error(f'🚨 Mais de 36 jogadores presentes ({n_players})')

# =======================================================================================================================================
# Tamanhos dos times

team_sizes = [0,0,0,0,0,0]
n_teams_recommended = math.ceil(n_players / 6)
if n_teams_recommended > 0:
    recommended_max = math.ceil(n_players / n_teams_recommended)
else:
    recommended_max = 0
filled = 0
for i in range(len(team_sizes)):
    if filled + recommended_max > n_players:
        fill_with = n_players - filled
    else:
        fill_with = recommended_max
    filled = filled + fill_with
    team_sizes[i] = fill_with

with st.expander('Tamanhos dos times', expanded = False):
    n_team_1 = st.number_input(label = 'Time A', min_value = 0, max_value = 6, step = 1, value = team_sizes[0], key = 'n_team_1')
    n_team_2 = st.number_input(label = 'Time B', min_value = 0, max_value = 6, step = 1, value = team_sizes[1], key = 'n_team_2')
    n_team_3 = st.number_input(label = 'Time C', min_value = 0, max_value = 6, step = 1, value = team_sizes[2], key = 'n_team_3')
    n_team_4 = st.number_input(label = 'Time D', min_value = 0, max_value = 6, step = 1, value = team_sizes[3], key = 'n_team_4')
    n_team_5 = st.number_input(label = 'Time E', min_value = 0, max_value = 6, step = 1, value = team_sizes[4], key = 'n_team_5')
    n_team_6 = st.number_input(label = 'Time F', min_value = 0, max_value = 6, step = 1, value = team_sizes[5], key = 'n_team_6')

    if n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5 != n_players:
        st.error(f'🚨 Jogadores por time ({n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5}) diferente do numero de jogadores ({n_players})')

team_sizes = [n_team_1,n_team_2,n_team_3,n_team_4,n_team_5,n_team_6]

# Print number of teams
n_teams = 0
if n_team_1 > 0: n_teams = n_teams + 1
if n_team_2 > 0: n_teams = n_teams + 1
if n_team_3 > 0: n_teams = n_teams + 1
if n_team_4 > 0: n_teams = n_teams + 1
if n_team_5 > 0: n_teams = n_teams + 1

st.markdown(f"<div style='text-align: left; font-weight: bold;'>Total de times: {n_teams}<br><br></div>", unsafe_allow_html=True)

# =======================================================================================================================================
# Definir Levantadores

setters = []

with st.expander('Definir levantadores', expanded = False):
    for name in present_players:
        if st.checkbox(name, key = f'setter_{name}') == True:
            setters.append(name)
    
    if len(setters) != n_teams:
        st.error(f'🚨 {len(setters)} levantadores para {n_teams} times')

# =======================================================================================================================================
# Função pra gerar times

def generate_teams(present_players, setters, team_sizes):
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Sanity checks

    n_players = len(present_players)
    n_setters = len(setters)
    n_teams = sum([1 for s in team_sizes if s > 0])
    sum_team_sizes = sum([s for s in team_sizes])

    if n_setters != n_teams or n_teams == 0:
        st.error(f'🚨 {n_setters} levantadores para {n_teams} times')
        return
    
    if n_players != sum_team_sizes or n_players ==0:
        st.error(f'🚨 Jogadores por time {sum_team_sizes} <> numero de jogadores {n_players}')
        return

    # ------------------------------------------------------------------------------------------------------------------------
    # Initialize teams with empty names

    teams = [[] for _ in range(n_teams)]
    
    allocated_per_team = n_teams * [0]

    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize setters and place them in the teams

    shuffled_setters = random.sample(setters, k = len(setters))
    
    for s,setter in enumerate(shuffled_setters):
        teams[s].append(setter)
        allocated_per_team[s] = allocated_per_team[s] + 1

    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize MVPs and place them in the teams

    mvps = [p for p in present_players if present_players[p]['mvp'] == True and p not in setters]
    random.shuffle(mvps)
    t_list = list(range(n_teams))
    random.shuffle(t_list)
    t_index = 0
    
    for mvp in mvps:
        allocated = False
        while allocated == False:
            t = t_list[t_index]
            if allocated_per_team[t] < team_sizes[t]:
                teams[t].append(mvp)
                allocated_per_team[t] = allocated_per_team[t] + 1
                allocated = True
            t_index = t_index + 1
            if t_index >= n_teams: t_index = 0
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize F and place them in the teams

    females = [p for p in present_players if present_players[p]['gender'] == 'F' and p not in setters]
    random.shuffle(females)
    t_list = list(range(n_teams))
    random.shuffle(t_list)
    t_index = 0
    
    for female in females:
        allocated = False
        while allocated == False:
            t = t_list[t_index]
            if allocated_per_team[t] < team_sizes[t]:
                teams[t].append(female)
                allocated_per_team[t] = allocated_per_team[t] + 1
                allocated = True
            t_index = t_index + 1
            if t_index >= n_teams: t_index = 0

    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize remaining players

    remaining = [p for p in present_players if p not in setters and p not in mvps and p not in females]
    random.shuffle(remaining)
    
    for player in remaining:
       for t,team in enumerate(teams):
            if allocated_per_team[t] < team_sizes[t]:
                team.append(player)
                allocated_per_team[t] = allocated_per_team[t] + 1
                break
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate team stats

    teams_stats = []

    for t, team in enumerate(teams):
        
        # Initialize
        score_sum = 0
        size = team_sizes[t]
        males = 0
        females = 0
        mvp_count = 0

        # Loop players
        for player in team:
            score_sum = score_sum + present_players[player]['score']
            if present_players[player]['gender'] == 'M':
                males = males + 1
            else:
                females = females + 1
            if present_players[player]['mvp'] == True: mvp_count = mvp_count + 1
        
        # Avg score
        score_avg = score_sum / size

        # Team stats dictionary
        teams_stats.append({'players': team,
                            'score_sum' : score_sum,
                            'size' : size,
                            'score_avg' : score_avg,
                            'males' : males,
                            'females' : females,
                            'mvps' : mvp_count})

    for p in present_players:
        allocated = False
        for team in teams:
            if p in team: allocated = True
        
    # ------------------------------------------------------------------------------------------------------------------------
    # Check if team split is fair

    # Check max and min # of females
    n_females = []
    n_mvps = []
    scores = []

    for team_stats in teams_stats:
        n_females.append(team_stats['females'])
        n_mvps.append(team_stats['mvps'])
        scores.append(team_stats['score_avg'])

    female_amplitude = max(n_females) - min(n_females) # max should be 1 (if a team has 2 and a team has 0, amplitude is 2, which means they could be 1-1 instead of 2-0)
    mvp_amplitude = max(n_mvps) - min(n_mvps) # max should be 1 (if a team has 2 and a team has 0, amplitude is 2, which means they could be 1-1 instead of 2-0)
    score_avg = sum(scores) / len(scores)
    score_sd = (sum((score - score_avg)**2 for score in scores) / len(scores)) ** 0.5
    
    output = {'teams' : teams_stats,
              'female_amplitude' : female_amplitude,
              'mvp_amplitude' : mvp_amplitude,
              'score_avg' : score_avg,
              'score_sd' : score_sd}

    return output

# =======================================================================================================================================
# Rodar a função gerar times 100x e pegar a de menor desvio padrão

st.markdown('---')
st.markdown('#### Gerar Times')

# Button to generate teams and checkbox to hide scores
button_generate = st.button('Gerar Times', key = 'button_generate')
hide_player_scores = st.checkbox('Esconder Scores', key = 'hide_scores', value = True)

# Check that best_generation is not on session_state, initialize if not
if 'best_generation' not in st.session_state:
    st.session_state['best_generation'] = {}

# If button is pressed, run the generation function
if button_generate == True:
    
    min_sd = 1000000
    best_generation = {}

    # Run code 100x to find a low standard deviation
    for _ in range(100):
        generation = generate_teams(present_players, setters, team_sizes)
        if generation['score_sd'] < min_sd and generation['female_amplitude'] <= 1 and generation['mvp_amplitude'] <= 1:
            best_generation = generation.copy()
            min_sd = generation['score_sd']
    
    # Save the best generation to session state
    st.session_state['best_generation'] = best_generation

# Fetch the best generation from session state
best_generation = st.session_state['best_generation']

# If the best_generation is not empty, display the teams
if best_generation:
    # Display result
    letters = ['A','B','C','D','E','F'] # max 6

    n_teams = len(best_generation['teams'])
    col_list = st.columns(n_teams*[1])

    for t,team in enumerate(best_generation['teams']):
        team_score = best_generation['teams'][t]['score_avg']
        team_size = best_generation['teams'][t]['size']
        with col_list[t]:
            html = f"""
            <div style="
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                background-color: #1e1e1e;
                color: white;
            ">
                <h4 style="margin-top: 0; color: white;">Time {letters[t]}</h4>
            """

            for p in team['players']:
                score = present_players[p]['score']
                player_string = f'🙌 {p}' if (p in setters) else f'{p}'
                if hide_player_scores == False: player_string = f'{player_string} ({score:.1f})'
                html += f"<p style='margin: 0px 0; color: white;'>{player_string}</p>"

            html += f"<p style='margin: 0px; color: #1f77b4;'><b>Score:</b> {team_score:.1f}</p>"
            html += f"<p style='margin: 0px; color: #1f77b4;'><b>Fixos:</b> {team_size}</p>"
            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)