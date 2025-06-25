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

st.set_page_config(layout = 'wide',page_title='Times L8 🏐')

# =======================================================================================================================================
# Initialize session_state variables

if 'page' not in st.session_state:
    st.session_state['page'] = 'page_home'

# =======================================================================================================================================
# Define a helper function to navigate between pages

def go_to_page(page_name):
    st.session_state['page'] = page_name
    st.rerun()

# =======================================================================================================================================
# Home page

if st.session_state['page'] == 'page_home':
    st.title('🏐 Times L8')
    st.button('✏️ Editar Jogadores', on_click=go_to_page, args=('page_jogadores',))
    st.button('📝 Lista de Presença', on_click=go_to_page, args=('page_presenca',))
    st.button('🙌 Definir Levantadores', on_click=go_to_page, args=('page_levantadores',))
    st.button('Gerar Times', on_click=go_to_page, args=('gerar',))

st.title('Times L8 🏐')


