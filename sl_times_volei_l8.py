# =======================================================================================================================================
# Packages

import streamlit as st
# import pandas as pd
import math
# import plotly.graph_objects as go
import random

all_known_players = {'Ricardo B' : {'gender' : 'M', 'score' : 10, 'mvp' : True},
                    'Fabio' : {'gender' : 'M', 'score' : 10, 'mvp' : True},
                    'Tonico' : {'gender' : 'M', 'score' : 10, 'mvp' : True},
                    'Christian' : {'gender' : 'M', 'score' : 10, 'mvp' : True},
                    'Brilhante' : {'gender' : 'M', 'score' : 9, 'mvp' : True},
                    'Marcao' : {'gender' : 'M', 'score' : 9, 'mvp' : True},
                    'Ricardo P' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Felipe L' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Adriano' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Pedro' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Leo' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Vitor' : {'gender' : 'M', 'score' : 8.5, 'mvp' : False},
                    'Carol' : {'gender' : 'F', 'score' : 8, 'mvp' : False},
                    'Marcelo' : {'gender' : 'M', 'score' : 7.5, 'mvp' : False},
                    'Hideki' : {'gender' : 'M', 'score' : 7.5, 'mvp' : False},
                    'Marreta' : {'gender' : 'M', 'score' : 7, 'mvp' : False},
                    'Taynara' : {'gender' : 'F', 'score' : 7, 'mvp' : False},
                    'Otacilio' : {'gender' : 'M', 'score' : 7, 'mvp' : False},
                    'Samira' : {'gender' : 'F', 'score' : 7, 'mvp' : False},
                    'Gabriel' : {'gender' : 'M', 'score' : 7, 'mvp' : False},
                    'Rhenan' : {'gender' : 'M', 'score' : 7, 'mvp' : False},
                    'Jorge' : {'gender' : 'M', 'score' : 6.5, 'mvp' : False},
                    'Danilo' : {'gender' : 'M', 'score' : 6.5, 'mvp' : False},
                    'Edson' : {'gender' : 'M', 'score' : 6.5, 'mvp' : False},
                    'Will' : {'gender' : 'M', 'score' : 6.5, 'mvp' : False},
                    'Marquinhos' : {'gender' : 'M', 'score' : 6.5, 'mvp' : False},
                    'Valdney' : {'gender' : 'M', 'score' : 6, 'mvp' : False},
                    'Matheus' : {'gender' : 'M', 'score' : 6, 'mvp' : False},
                    'Silvana' : {'gender' : 'F', 'score' : 6, 'mvp' : False},
                    'Mel' : {'gender' : 'F', 'score' : 5, 'mvp' : False},
                    'Chico' : {'gender' : 'M', 'score' : 5, 'mvp' : False},
                    'Mary' : {'gender' : 'F', 'score' : 5, 'mvp' : False},
                    'Rodrigo' : {'gender' : 'M', 'score' : 5, 'mvp' : False},
                    'Jessica' : {'gender' : 'F', 'score' : 5, 'mvp' : False},
                    'Dri' : {'gender' : 'F', 'score' : 4, 'mvp' : False},
                    'Cris N' : {'gender' : 'F', 'score' : 4, 'mvp' : False}}

# =======================================================================================================================================
# Setup streamlit (needs to be the first command)

st.set_page_config(layout = "wide")
st.title('Times L8 🏐')

# =======================================================================================================================================
# Present players

st.markdown('---')
st.markdown('#### Configurar')

# Known players: checkbox
all_known_names = sorted(all_known_players.keys()) # alphabetically sorted
present_known_players = []
with st.expander('Dos conhecidos, quem veio hoje?', expanded = False):
    for name in all_known_names:
        if st.checkbox(name, key = f'checkbox_{name}') == True:
            present_known_players.append(name)

# New players (up to 12)
present_new_players = []

with st.expander('Algum jogador novo? (max = 12)', expanded = False):
    for i in range(12):

        with st.expander(f'Jogador extra #{i+1}', expanded = False):
            name = st.text_input(label = '', key = f'extra_name_{i}', label_visibility = 'collapsed')
            gender = st.radio(label = '',options=['M', 'F'],horizontal=True,key=f'gender_{i}', label_visibility='collapsed')
            score = st.number_input(label = '',min_value=0.0,max_value=10.0,step=0.5,key=f'score_{i}', label_visibility='collapsed')
            mvp = st.checkbox(label = 'MVP',value=False,key=f'mvp_{i}')
            if name and gender and score:
                present_new_players.append({'name':name,'gender':gender,'score':score,'mvp':mvp})

# Merge both known and new players
present_players = {}

for p in present_known_players:
    present_players[p] = {'gender':all_known_players[p]['gender'],'score':all_known_players[p]['score'], 'mvp':all_known_players[p]['mvp']}

for p in present_new_players:
    present_players[p['name']] = {'gender':p['gender'],'score':p['score'],'mvp' : p['mvp']}

# Warn repeated names
np_names = [p['name'] for p in present_new_players]
for np in np_names:
    n = 0
    for kp in present_known_players:
        if np == kp:
            st.warning(f'⚠️ Alerta: jogador repetido ({np})')
            break

# Print number of present players
n_players = len(present_players)
n_male = sum(1 for p in present_players.values() if p['gender'] == 'M')
n_female = sum(1 for p in present_players.values() if p['gender'] == 'F')

st.markdown(f"<div style='text-align: center; font-weight: bold;'>Total de jogadores: {n_players} ({n_male}M + {n_female}F)</div>", unsafe_allow_html=True)

if n_players > 30:
    st.error(f'🚨 Mais de 36 jogadores presentes ({n_players})')

# =======================================================================================================================================
# Jogadores por time

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

with st.expander('Definir # de jogadores por time', expanded = False):
    n_team_1 = st.number_input(label = 'Time 1', min_value = 0, max_value = 6, step = 1, value = team_sizes[0], key = 'n_team_1')
    n_team_2 = st.number_input(label = 'Time 2', min_value = 0, max_value = 6, step = 1, value = team_sizes[1], key = 'n_team_2')
    n_team_3 = st.number_input(label = 'Time 3', min_value = 0, max_value = 6, step = 1, value = team_sizes[2], key = 'n_team_3')
    n_team_4 = st.number_input(label = 'Time 4', min_value = 0, max_value = 6, step = 1, value = team_sizes[3], key = 'n_team_4')
    n_team_5 = st.number_input(label = 'Time 5', min_value = 0, max_value = 6, step = 1, value = team_sizes[4], key = 'n_team_5')
    n_team_6 = st.number_input(label = 'Time 6', min_value = 0, max_value = 6, step = 1, value = team_sizes[5], key = 'n_team_6')

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

st.markdown(f"<div style='text-align: center; font-weight: bold;'>Total de times: {n_teams}</div>", unsafe_allow_html=True)

# =======================================================================================================================================
# Levantadores

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

# If the best_generation is found, display the teams
if best_generation:
    # Display result
    letters = ['A','B','C','D','E','F'] # max 6

    for t,team in enumerate(best_generation['teams']):
        team_score = best_generation['teams'][t]['score_avg']
        team_size = best_generation['teams'][t]['size']
        with st.expander(f'Time {letters[t]} (Score: {team_score:.1f}) (Fixos: {team_size})', expanded = True):
            for p in team['players']:
                player_score = present_players[p]['score']
                player_mvp = present_players[p]['mvp']
                if hide_player_scores == True:
                    player_string = f'{p}'
                else:
                    player_string = f'{p} ({player_score:.1f})'
                player_setter = p in setters
                #if player_mvp == True: player_string = f'{player_string} ⭐️'
                if player_setter == True: player_string = f'{player_string} 🙌'
                st.markdown(f"<p style='margin-bottom: 0.1rem;'>{player_string}</p>",unsafe_allow_html=True)


