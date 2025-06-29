# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Packages

import streamlit as st
import pandas as pd
import math
import os
import random
import time


# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Setup streamlit (needs to be the first command)

st.set_page_config(layout = 'wide',page_title='Times L8 🏐')

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Initialize session_state variables

# Default page: page_home
if 'page' not in st.session_state:
    st.session_state['page'] = 'page_home'

# Load players data
if 'players_dictionary' not in st.session_state:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'known_players.csv')
    df_players = pd.read_csv(csv_path)
    df_players = df_players.sort_values(by='Name').reset_index(drop=True)
    players_dictionary = {row['Name']:
                   {'gender': row['Gender'],
                    'score': row['Score'],
                    'setter_score': row['Setter Score'],
                    } for _, row in df_players.iterrows()}
    st.session_state['players_dictionary'] = players_dictionary

# Player currently being edited
if 'player_being_edited' not in st.session_state:
    st.session_state['player_being_edited'] = ''

# Present players list
if 'present_names' not in st.session_state:
    st.session_state['present_names'] = []

# Team sizes
if 'team_sizes' not in st.session_state:
    st.session_state['team_sizes'] = [0, 0, 0, 0, 0, 0]

# Setters
if 'setter_names' not in st.session_state:
    st.session_state['setter_names'] = []

# Run optimization
if 'run_optimization' not in st.session_state:
    st.session_state['run_optimization'] = False

# Best result
if 'best_result' not in st.session_state:
    st.session_state['best_result'] = None

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Page navigation functions

# Page navigation function
def go_to_page(page_name):
    st.session_state['page'] = page_name

# Navigate to edit player page
def edit_player(player_name):
    st.session_state['player_being_edited'] = player_name
    go_to_page('page_editar_jogador')

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Team generation functions

# ---------------------------------------------------------------------------------------------------------------------------------------
# Generate random team function

def random_teams():
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Get input data

    present_names = st.session_state['present_names']
    setter_names = st.session_state['setter_names']
    players_dictionary = st.session_state['players_dictionary']
    team_sizes = st.session_state['team_sizes']
    n_teams = sum(1 for size in team_sizes if size > 0)

    # ------------------------------------------------------------------------------------------------------------------------
    # Initialize teams as empty lists
    
    teams = [[] for _ in range(n_teams)]
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Initialize allocated per team
    
    allocated_per_team = n_teams * [0]

    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize setters and place them in the teams

    random.shuffle(setter_names)

    for s,setter in enumerate(setter_names):
        teams[s].append(setter)
        allocated_per_team[s] = allocated_per_team[s] + 1

    # ------------------------------------------------------------------------------------------------------------------------
    # Randomize MVPs and place them in the teams

    mvp_names = [p for p in present_names if players_dictionary[p]['score'] >= 9.0 and p not in setter_names]
    random.shuffle(mvp_names)
    t_list = list(range(n_teams))
    random.shuffle(t_list)
    t_index = 0
    
    for mvp in mvp_names:
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
    # Randomize Females and place them in the teams

    female_names = [p for p in present_names if players_dictionary[p]['gender'] == 'F' and p not in mvp_names and p not in setter_names]
    random.shuffle(female_names)
    t_list = list(range(n_teams))
    random.shuffle(t_list)
    t_index = 0
    
    for female in female_names:
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

    remaining_names = [p for p in present_names if p not in setter_names and p not in mvp_names and p not in female_names]
    random.shuffle(remaining_names)
    
    for player in remaining_names:
       for t,team in enumerate(teams):
            if allocated_per_team[t] < team_sizes[t]:
                team.append(player)
                allocated_per_team[t] = allocated_per_team[t] + 1
                break # to next player
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate team stats

    teams_detailed = []
    setter_weight = 2 # weight for setters in the score calculation
    
    # Loop teams
    for t, team in enumerate(teams):
        
        # Initialize
        team_score_sum = 0
        team_weights_sum = 0
        team_size = team_sizes[t]
        team_males = 0
        team_females = 0
        team_mvps = 0

        # Loop players
        for player in team:
            # If player is a setter, multiply score by setter_weight
            if player in setter_names:
                team_score_sum = team_score_sum + players_dictionary[player]['setter_score'] * setter_weight
                team_weights_sum = team_weights_sum + setter_weight
            else:
                team_score_sum = team_score_sum + players_dictionary[player]['score']
                team_weights_sum = team_weights_sum + 1

            if players_dictionary[player]['gender'] == 'M':
                team_males = team_males + 1
            else:
                team_females = team_females + 1

            if players_dictionary[player]['score'] >= 9:
                team_mvps = team_mvps + 1
        
        # Avg score
        team_score_avg = team_score_sum / team_weights_sum

        # Team score standard deviation
        team_score_variance = 0
        for player in team:
            if player in setter_names:
                team_score_variance = team_score_variance + setter_weight * (players_dictionary[player]['setter_score'] - team_score_avg) ** 2
            else:
                team_score_variance = team_score_variance + 1 * (players_dictionary[player]['score'] - team_score_avg) ** 2
        team_score_variance = team_score_variance / team_weights_sum
        team_score_sd = team_score_variance ** 0.5

        # Team stats dictionary
        teams_detailed.append({'players': team,
                               'size' : team_size,
                               'score_avg' : team_score_avg,
                               'score_sd' : team_score_sd,
                               'males' : team_males,
                               'females' : team_females,
                               'mvps' : team_mvps})
        
    # ------------------------------------------------------------------------------------------------------------------------
    # Check if team split is fair

    # Check max and min # of females
    n_females = []
    n_mvps = []
    scores = []
    sds = []

    for team_stats in teams_detailed:
        n_females.append(team_stats['females'])
        n_mvps.append(team_stats['mvps'])
        scores.append(team_stats['score_avg'])
        sds.append(team_stats['score_sd'])

    female_amplitude = max(n_females) - min(n_females) # max should be 1 (if a team has 2 and a team has 0, amplitude is 2, which means they could be 1-1 instead of 2-0)
    mvp_amplitude = max(n_mvps) - min(n_mvps) # max should be 1 (if a team has 2 and a team has 0, amplitude is 2, which means they could be 1-1 instead of 2-0)
    score_avg = sum(scores) / len(scores)
    score_sd = (sum((score - score_avg)**2 for score in scores) / len(scores)) ** 0.5
    sd_avg = sum(sds) / len(sds)
    sd_sd = (sum((sd - sd_avg)**2 for sd in sds) / len(sds)) ** 0.5

    output = {'teams' : teams_detailed,
              'female_amplitude' : female_amplitude,
              'mvp_amplitude' : mvp_amplitude,
              'score_avg' : score_avg,
              'score_sd' : score_sd,
              'sd_avg' : sd_avg,
              'sd_sd' : sd_sd}

    
    return output


# ---------------------------------------------------------------------------------------------------------------------------------------
# Run random function N times and return the best team split

def optimize_teams():

    start_time = time.perf_counter()
    
    # Optimization parameters
    N = 1000 # Number of random teams to generate
    score_weight = 1 # weight on the actual score standard deviation (minimizing the difference between teams scores)
    sd_weight = 0.1 # weight on the standard deviation's standard deviation (ensuring the teams are equally granular)

    # Initialize variables
    output_list = []
    best_result = None
    lowest_cost = float('inf')

    # Init min/max with opposite extremes
    min_score_sd = float('inf')
    max_score_sd = float('-inf')
    min_sd_sd = float('inf')
    max_sd_sd = float('-inf')

    # Run the optimization
    with st.spinner('🔄 Otimizando combinação de times...'):
        # First pass: collect results and track min/max
        for _ in range(N):
            # Run random_teams()
            output = random_teams()

            # Append on all_results
            output_list.append(output)

            # Track min/max values for score_sd and sd_sd
            if output['score_sd'] < min_score_sd: min_score_sd = output['score_sd']
            if output['score_sd'] > max_score_sd: max_score_sd = output['score_sd']
            if output['sd_sd'] < min_sd_sd: min_sd_sd = output['sd_sd']
            if output['sd_sd'] > max_sd_sd: max_sd_sd = output['sd_sd']


        # Second pass: calculate normalized cost and get the best result
        for output in output_list:
            score_sd_norm = (output['score_sd'] - min_score_sd) / (max_score_sd - min_score_sd + 1e-8)
            sd_sd_norm = (output['sd_sd'] - min_sd_sd) / (max_sd_sd - min_sd_sd + 1e-8)
            cost = (score_weight * score_sd_norm + sd_weight * sd_sd_norm) / (score_weight + sd_weight)
            
            # If this is the best result so far, update the best_result and lowest_cost
            # Only update if female amplitude and mvp amplitude are lower than or equal to 1 (fair teams)
            if cost < lowest_cost and output['female_amplitude'] <= 1 and output['mvp_amplitude'] <= 1:
                lowest_cost = cost
                best_result = output

    # Output run time
    end_time = time.perf_counter()
    st.write(f"Execution time: {end_time - start_time:.2f} seconds")
    st.write(f"Avg Score: {best_result['score_avg']:.2f} (σ: {best_result['score_sd']:.2f})")
    st.write(f"Avg SD: {best_result['sd_avg']:.2f} (σ: {best_result['sd_sd']:.2f})")

    # Return the best result
    return best_result

# ---------------------------------------------------------------------------------------------------------------------------------------
# Show best result function

def show_best_result():

    # Get input data

    setter_names = st.session_state['setter_names']
    players_dictionary = st.session_state['players_dictionary']
    team_sizes = st.session_state['team_sizes']
    n_teams = sum(1 for size in team_sizes if size > 0)

    # Get the best result from session state
    best_result = st.session_state['best_result']
    
    # Display result
    letters = ['A','B','C','D','E'] # max 5

    n_teams = len(best_result['teams'])
    col_list = st.columns(n_teams*[1])


    # Build team cards
    for t,team in enumerate(best_result['teams']):
        team_score = best_result['teams'][t]['score_avg']
        team_sd = best_result['teams'][t]['score_sd']
        team_size = best_result['teams'][t]['size']
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
                score = players_dictionary[p]['score']
                player_string = f'🙌 {p}' if (p in setter_names) else f'{p}'
                html += f"<p style='margin: 0px; color: white;'>{player_string}</p>"

            html += f"<p style='margin: 0px; color: #1f77b4;'><b>Score:</b> {team_score:.1f} ± {team_sd:.1f}</p>"
            html += f"<p style='margin: 0px; color: #1f77b4;'><b>Fixos:</b> {team_size}</p>"
            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)


# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Home page and navigation buttons

if st.session_state['page'] == 'page_home':

    # Title
    st.title('🏐 Times L8')

    # Button to edit/add players
    st.button('✏️ Editar Jogadores', on_click=go_to_page, args=('page_editar_jogadores',))

    # Button to define present players
    st.button('📝 Lista de Presença', on_click=go_to_page, args=('page_presenca',))

    # Button to define team sizes (only if there are players present)
    if len(st.session_state['present_names']) > 0:
        st.button('📏 Tamanho dos Times', on_click=go_to_page, args=('page_tamanho_times',))
    else:
        st.markdown('<button disabled style="padding: 0.5rem 1rem;font-size: 1rem;background-color: #f0f2f6;color: #aaa;border: 1px solid #ccc;border-radius: 0.5rem;cursor: not-allowed;">📏 Tamanho dos Times</button>', unsafe_allow_html=True)

    # Button to define setters (only if there are players present and sum(team_sizes) = n_players)
    if len(st.session_state['present_names']) > 0 and sum(st.session_state['team_sizes']) == len(st.session_state['present_names']):
        st.button('🙌 Definir Levantadores', on_click=go_to_page, args=('page_levantadores',))
    else:
        st.markdown('<button disabled style="padding: 0.5rem 1rem;font-size: 1rem;background-color: #f0f2f6;color: #aaa;border: 1px solid #ccc;border-radius: 0.5rem;cursor: not-allowed;">🙌 Definir Levantadores</button>', unsafe_allow_html=True)
    
    # Button to generate teams (only if there are players present, sum(team_sizes) = n_players and len(setter_names) = n_teams)
    if len(st.session_state['present_names']) > 0 and sum(st.session_state['team_sizes']) == len(st.session_state['present_names']) and len(st.session_state['setter_names']) == sum(1 for size in st.session_state['team_sizes'] if size > 0):
        if st.button('🚀 Gerar Times'):
            st.session_state['run_optimization'] = True # order a new optimization run (i have to do this to ensure the results are shown below the button, not on top of the page)
    else:
        st.markdown('<button disabled style="padding: 0.5rem 1rem;font-size: 1rem;background-color: #f0f2f6;color: #aaa;border: 1px solid #ccc;border-radius: 0.5rem;cursor: not-allowed;">🚀 Gerar Times</button>', unsafe_allow_html=True)
    
    # If run_optimization is True, run the optimization and show the results
    if st.session_state['run_optimization'] == True:

        # Run the optimization
        best_result = optimize_teams()
        
        # save the best result to session state
        st.session_state['best_result'] = best_result 

        # Reset the flag
        st.session_state['run_optimization'] = False 

        # Show success
        st.success('✅ Times gerados com sucesso!')

        # Show the best result
        show_best_result()        


# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Edit player page and player management

# ---------------------------------------------------------------------------------------------------------------------------------------
# Main page for editing players

elif st.session_state['page'] == 'page_editar_jogadores':
    
    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',))
    st.markdown('---')
    st.markdown('### **Editar/Adicionar Jogadores**')
    
    # Read players data from session state
    players_dictionary = st.session_state['players_dictionary']

    # Add buttons to add/remove/edit players
    st.button('👤 Novo Jogador', on_click=go_to_page, args=('page_novo_jogador',))
    for player_name in players_dictionary.keys():
        player_score = players_dictionary[player_name]['score']
        player_setter_score = players_dictionary[player_name]['setter_score']
        player_gender = players_dictionary[player_name]['gender']
        player_string = f'✏️ {player_name} ({player_gender}, Score: {player_score:.1f}, Levant: {player_setter_score:.1f})'
        st.button(player_string, on_click=edit_player, args=(player_name,))

# ---------------------------------------------------------------------------------------------------------------------------------------
# Sub-page for adding new player

elif st.session_state['page'] == 'page_novo_jogador':
    
    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_editar_jogadores',))
    st.markdown('---')
    st.markdown('### **Novo Jogador**')
    
    # Inputs
    new_player_name = st.text_input('Nome', placeholder='Nome')
    new_player_score = st.number_input('Score', min_value=0.1, max_value=10.0, step=0.5, format="%.1f", value=5.0)
    new_player_setter_score = st.number_input('Levantamento', min_value=0.1, max_value=10.0, step=0.5, format="%.1f", value=5.0)
    new_player_gender = st.radio('Sexo', options=['M', 'F'], index=0)

    # Add new player to the dictionary
    if st.button('👤 Adicionar Jogador'):
        
        # Check if the player name is not empty
        if new_player_name:

            # Fetch the players dictionary from session state
            players_dictionary = st.session_state['players_dictionary']

            # Check if the player already exists
            if new_player_name in players_dictionary:
                st.error(f'🚨 Erro: {new_player_name} já existe.')
            else:
                # Add the new player to the dictionary
                players_dictionary[new_player_name] = {'gender' : new_player_gender,
                                                       'score' : new_player_score,
                                                       'setter_score' : new_player_setter_score}

                # Update the session state with the new players dictionary
                st.session_state['players_dictionary'] = players_dictionary

                # Show success response
                st.success(f'✅ Jogador {new_player_name} adicionado com sucesso.')

        else:
            st.error('🚨 Erro: insira um nome')

# ---------------------------------------------------------------------------------------------------------------------------------------
# Sub-page for editing/deleting an existing player

elif st.session_state['page'] == 'page_editar_jogador':
    
    # Player being edited
    player_being_edited = st.session_state['player_being_edited']
    players_dictionary = st.session_state['players_dictionary']

    # Current player data
    current_score = players_dictionary[player_being_edited]['score']
    current_setter_score = players_dictionary[player_being_edited]['setter_score']
    current_gender = players_dictionary[player_being_edited]['gender']
    
    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',), key='back_to_home_top')
    st.markdown('---')
    st.markdown(f'### **Editar {player_being_edited}**')
        
    # Inputs (can't change the name of the player)
    changed_score = st.number_input('Score', min_value=0.1, max_value=10.0, step=0.5, format="%.1f", value=current_score)
    changed_setter_score = st.number_input('Levantamento', min_value=0.1, max_value=10.0, step=0.5, format="%.1f", value=current_setter_score)
    changed_gender = st.radio('Sexo', options=['M', 'F'], index=['M', 'F'].index(current_gender))

    # Add new player to the dictionary
    if st.button('💾 Salvar Alterações'):
        
        if current_score != changed_score or current_gender != changed_gender or current_setter_score != changed_setter_score:
            # Update the player data
            players_dictionary[player_being_edited]['score'] = changed_score
            players_dictionary[player_being_edited]['setter_score'] = changed_setter_score
            players_dictionary[player_being_edited]['gender'] = changed_gender

            # Send the upated players dictionary to session state
            st.session_state['players_dictionary'] = players_dictionary
            
            # Show success response
            st.success(f'✅ Jogador {player_being_edited} alterado com sucesso.')
        
        else:
            st.warning('⚠️ Nenhuma alteração foi feita.')
    
    st.markdown('ou')

    # Button to remove the player
    if st.button('🗑️ Remover Jogador'):

        if player_being_edited in players_dictionary:
            # Remove the player from the dictionary
            del players_dictionary[player_being_edited]
            
            # Update the session state with the new players dictionary
            st.session_state['players_dictionary'] = players_dictionary
            
            # Show success response
            st.success(f'✅ Jogador {player_being_edited} removido com sucesso.')

            go_to_page('page_editar_jogadores')    
        
        else:
            st.error(f'🚨 Erro: {player_being_edited} não encontrado para remoção.')

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Presence list page

elif st.session_state['page'] == 'page_presenca':

    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',))
    st.markdown('---')
    st.markdown('### **Lista de Presença**')

    # Read players data from session state
    players_dictionary = st.session_state['players_dictionary']

    # Present players list
    present_names = st.session_state['present_names']
    
    # Generate a list of checkboxes for each player
    for player_name in players_dictionary.keys():
        player_checkbox = st.checkbox(player_name, key=f'{player_name} Presence', value = player_name in present_names)

        # If the checkbox is checked, add the player to the present list
        if player_checkbox ==True and player_name not in present_names:
            # Maximum of 30 players (5 teams of 6 players)
            if len(present_names) < 30:
                present_names.append(player_name)
            else:
                st.error('🚨 Erro: máximo de 30 jogadores presentes atingido.')

        # If the checkbox is unchecked, remove the player from the present list
        elif player_checkbox == False and player_name in present_names:
            present_names.remove(player_name)
    
    # Sort the present names alphabetically
    present_names = sorted(present_names)

    # Update the session state with the present names
    st.session_state['present_names'] = present_names

    # Success message with number of players present
    if len(present_names) > 0:
        st.success(f'✅ {len(present_names)} jogadores')
    else:
        st.warning('⚠️ Nenhum jogador presente.')

    # Back button on the bottom
    st.markdown('---')
    st.button('💾 Salvar Alterações', on_click=go_to_page, args=('page_home',), key='back_to_home_bottom')

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Team sizes page

elif st.session_state['page'] == 'page_tamanho_times':

    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',))
    st.markdown('---')
    st.markdown('### **Tamanho dos times**')

    # Get number of players present from session state
    n_players = len(st.session_state['present_names'])

    # Get team sizes from session state
    team_sizes = st.session_state['team_sizes']

    # Check if sum(team_sizes) is different than n_players. If so, make a new recommendation
    if sum(team_sizes) != n_players:
        # Reset team sizes
        team_sizes = [0, 0, 0, 0, 0]

        # Calculate recommended team sizes
        n_teams_recommended = math.ceil(n_players / 6) # this page is only accessible if there are players present (n_players > 0 always)

        # Max recommended size for each team
        recommended_max = math.ceil(n_players / n_teams_recommended) # again, n_teams_recommended > 0 always
    
        # Fill team sizes with recommended max size
        filled = 0
        for i in range(len(team_sizes)):
            if filled + recommended_max > n_players:
                fill_with = n_players - filled
            else:
                fill_with = recommended_max
            filled = filled + fill_with
            team_sizes[i] = fill_with
        
        # Save the recommended team sizes to session state (because the user might not click on save and we need a consistent state)
        st.session_state['team_sizes'] = team_sizes
        

    # Create number inputs for each team size
    n_team_1 = st.number_input(label='Time A', min_value=0, max_value=6, step=1, value=team_sizes[0], key='n_team_1')
    n_team_2 = st.number_input(label='Time B', min_value=0, max_value=6, step=1, value=team_sizes[1], key='n_team_2')
    n_team_3 = st.number_input(label='Time C', min_value=0, max_value=6, step=1, value=team_sizes[2], key='n_team_3')
    n_team_4 = st.number_input(label='Time D', min_value=0, max_value=6, step=1, value=team_sizes[3], key='n_team_4')
    n_team_5 = st.number_input(label='Time E', min_value=0, max_value=6, step=1, value=team_sizes[4], key='n_team_5')
    
    # Return success or error message based on the team sizes
    if n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5 == n_players:
        st.success(f'✅ Total de jogadores distribuídos ({n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5}) igual ao número de jogadores ({n_players})')
    else:
        st.error(f'🚨 Jogadores por time ({n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5}) diferente do número de jogadores ({n_players})')

    # Save team sizes to session state
    if n_team_1 + n_team_2 + n_team_3 + n_team_4 + n_team_5 == n_players:
        if st.button('💾 Salvar'):
            st.session_state['team_sizes'] = [n_team_1, n_team_2, n_team_3, n_team_4, n_team_5]
            st.success('✅ Tamanhos dos times salvos com sucesso.')
    else: # fake button for UI consistency
        st.markdown('<button disabled style="padding: 0.5rem 1rem;font-size: 1rem;background-color: #f0f2f6;color: #aaa;border: 1px solid #ccc;border-radius: 0.5rem;cursor: not-allowed;">💾 Salvar</button>', unsafe_allow_html=True)

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Setters page

elif st.session_state['page'] == 'page_levantadores':

    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',))
    st.markdown('---')
    st.markdown('### **Definir Levantadores**')

    # Get number of teams (number of elements in team_sizes where value > 0)
    team_sizes = st.session_state['team_sizes']
    n_teams = sum(1 for size in team_sizes if size > 0)

    # Get present players
    present_names = st.session_state['present_names'] # to enter in this page, there are players present

    # Setter names
    setter_names = st.session_state['setter_names']

    # Generate a list of checkboxes for each player
    for player_name in present_names:
        player_checkbox = st.checkbox(player_name, key=f'{player_name} Setter', value = player_name in setter_names)

        # If the checkbox is checked, add the player to the setters list
        if player_checkbox == True and player_name not in setter_names:
            # Maximum of n_teams setters
            if len(setter_names) < n_teams:
                setter_names.append(player_name)
            else:
                st.error(f'🚨 Erro: máximo de {n_teams} levantadores atingido.')

        # If the checkbox is unchecked, remove the player from the setters list
        elif player_checkbox == False and player_name in setter_names:
            setter_names.remove(player_name)
    
    # Sort the setter names alphabetically
    setter_names = sorted(setter_names)

    # Update the session state with the setter names
    st.session_state['setter_names'] = setter_names

    # Success message with number of setters
    if len(setter_names) == n_teams:
        st.success(f'✅ {len(setter_names)} levantadores para {n_teams} times')
    else:
        st.error(f'🚨 {len(setter_names)} levantadores para {n_teams} times')

    # Back button on the bottom
    st.markdown('---')
    st.button('💾 Salvar Alterações', on_click=go_to_page, args=('page_home',), key='back_to_home_bottom')

# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# =======================================================================================================================================
# Generate teams page

elif st.session_state['page'] == 'page_gerar_time':
    
    # Back button and title
    st.button('↩️ Voltar', on_click=go_to_page, args=('page_home',))
    st.markdown('---')
    st.markdown('### **Gerar Times**')