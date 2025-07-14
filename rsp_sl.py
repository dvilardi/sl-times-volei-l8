# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Import packages

import streamlit as st
import pandas as pd
import math
# import numpy as np
import plotly.graph_objects as go
# from datetime import datetime
# import math
#import pickle
import json

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Constant parameters


const_formats = {'pacing_line_shape':'hv',
                 'pacing_line_mode':'lines',
                 'portfolio_gaps_line_shape':'spline',
                 'portfolio_gaps_line_mode':'lines+markers'}

const_colors = {'pacing_spend_actual':'#000080',
                'pacing_spend_target':'#7babc7',
                'pacing_rolling_bva':'#d60000',
                'pacing_base_trip_weight':'#636363',
                'pacing_actual_trip_weight':'#d60000',
                'portfolio_x':'#134dab',
                'portfolio_comfort':'#8a8a8a',
                'portfolio_black':'#1f1f1f',
                'portfolio_moto':'#ad1010'}

const_sizes = {'portfolio_gaps_linewidth' : 2.0,
               'legend_font_size' : 10,
               'chart_height_pacing' : 300,
               'chart_height_portfolio' : 250,
               'box_margin_top' : 15,
               'box_margin_bottom' : 5,
               'box_margin_left' : 5,
               'box_margin_right' : 5
              }

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Set up streamlit (this needs to be the first "st" command)

st.set_page_config(layout = "wide")

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Build Sidebar and include dashboard options

st.sidebar.header("RSP Deep Dives")

selected_view = st.sidebar.radio(
    'Select a view:',
    options = ['Online Pacing',
               'Portfolio Gaps',
               'Price Plans',
               'WIP'],
    index = 1)

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ONLINE PACING

if selected_view == 'Online Pacing':

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Read dataframe
    
    df_pacer = pd.read_csv('/home/vilardi/vilardi_nfs/RSP/RSP_Deep_Dive_Dashboard/df_pacer.csv')

    # Get city list
    city_list = df_pacer['city'].unique().tolist()

    # Get week list
    week_list = df_pacer['week'].unique().tolist()

    # Create city filter
    selected_city = st.sidebar.selectbox(label = 'City', options = city_list, index = city_list.index('458 - Sao Paulo'))

    # Create week filters
    selected_start_week = st.sidebar.selectbox(label = 'Start Week', options = week_list, index = len(week_list)-2) # current week minus 1
    selected_end_week = st.sidebar.selectbox(label = 'End Week', options = week_list, index = len(week_list)-1) # current week

    # Filter dataframe
    df_pacer = df_pacer[(df_pacer['city'] == selected_city) & (df_pacer['week'] >= selected_start_week) & (df_pacer['week'] <= selected_end_week)]


    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot online pacing

    st.markdown('### Online Pacing - Budget and Spend')
    
    # Create figure
    fig = go.Figure()
    
    # Horizontal line at y = 0
    fig.add_shape(
        type='line',
        x0=df_pacer['tuner_run_start_time'].min(),
        x1=df_pacer['tuner_run_start_time'].max(),
        y0=0,
        y1=0,
        line=dict(color='black', width=1),
        xref='x',
        yref='y'
    )
    
    # Plot spend targets
    fig.add_trace(
        go.Scatter(
            x = df_pacer['tuner_run_start_time'],
            y = df_pacer['spend_target_value'],
            name = 'Spend Target (%GB)',
            mode = const_formats['pacing_line_mode'],
            line = dict(shape = const_formats['pacing_line_shape'], width = 2, color = const_colors['pacing_spend_target']),
            marker = dict(size = 5),
            yaxis = 'y',
            hovertemplate = 'Spend Target: %{y:,.2%}<extra></extra>'
        )
    )

    # Plot actual spends
    fig.add_trace(
        go.Scatter(
            x = df_pacer['tuner_run_start_time'],
            y = df_pacer['actual_spend'],
            name = 'Actual Spend (%GB)',
            mode = const_formats['pacing_line_mode'],
            line = dict(shape = const_formats['pacing_line_shape'], width = 2, color = const_colors['pacing_spend_actual']),
            marker = dict(size = 5),
            yaxis = 'y',
            hovertemplate = 'Actual Spend: %{y:,.2%}<extra></extra>'
        )
    )

    # Plot rolling BvAs (Bar)
    fig.add_trace(
        go.Bar(
            x = df_pacer['tuner_run_start_time'], 
            y = df_pacer['actual_target_diff'],
            text = df_pacer['actual_target_diff'].apply(lambda x: f"{x:.2%}"),
            textposition = 'auto',
            textfont = dict(size = 10),
            textangle = 0, # always horizontal
            name = 'Rolling 7d BvA (%GB)',
            hovertemplate = 'Rolling BvA: %{y:,.2%}<extra></extra>',
            marker_color=const_colors['pacing_rolling_bva']
        )
    )
    
    # Get min and max values for axis scaling
    y_min = pd.concat([df_pacer['spend_target_value'], df_pacer['actual_spend'], df_pacer['actual_target_diff']]).min()
    y_max = pd.concat([df_pacer['spend_target_value'], df_pacer['actual_spend'], df_pacer['actual_target_diff']]).max()
    y_min = math.floor(100*y_min)/100
    y_max = math.ceil(100*y_max)/100
    if y_min > 0: y_min = 0
    if y_max < 0: y_max = 0

    # Layout
    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        xaxis = dict(tickangle=-45,tickformat='%Y-%m-%d',dtick='D1',hoverformat='%Y-%m-%d %H:%M:%S'),
        yaxis = dict(tickformat='0.0%', range = [y_min,y_max]),
        legend = dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
        margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
        height = const_sizes['chart_height_pacing'],
        hovermode = 'x unified'
    )

    st.plotly_chart(fig,use_container_width=True)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot trip weights

    st.markdown('### Online Pacing - Trip Weights')

    # Create figure
    fig = go.Figure()
        
    # Plot base trip weight
    fig.add_trace(
        go.Scatter(
            x = df_pacer['tuner_run_start_time'],
            y = df_pacer['tw_base'],
            name = 'Base Trip Weight',
            mode = const_formats['pacing_line_mode'],
            line = dict(shape = const_formats['pacing_line_shape'],width = 2, color = const_colors['pacing_base_trip_weight']),
            marker = dict(size = 5),
            yaxis = 'y',
            hovertemplate = 'Base Trip Weight: %{y:,.4f}<extra></extra>'
        )
    )

    # Plot actual trip weight
    fig.add_trace(
        go.Scatter(
            x = df_pacer['tuner_run_start_time'],
            y = df_pacer['tw'],
            name = 'Final Trip Weight',
            mode = const_formats['pacing_line_mode'],
            line = dict(shape = const_formats['pacing_line_shape'],width = 2, color = const_colors['pacing_actual_trip_weight']),
            marker = dict(size = 5),
            yaxis = 'y',
            hovertemplate = 'Actual Trip Weight: %{y:,.4f}<extra></extra>'
        )
    )

    # Get min and max values for axis scaling
    y_min = pd.concat([df_pacer['tw'], df_pacer['tw_base'], df_pacer['tw_base']]).min()
    y_max = pd.concat([df_pacer['tw'], df_pacer['tw_base'], df_pacer['tw_base']]).max()
    y_min = math.floor(100*y_min)/100
    y_max = math.ceil(100*y_max)/100
    #if y_min > 0: y_min = 0
    #if y_max < 0: y_max = 0

    # Layout
    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        xaxis = dict(tickangle=-45,tickformat='%Y-%m-%d',dtick='D1',hoverformat='%Y-%m-%d %H:%M:%S'),
        yaxis = dict(range = [y_min,y_max]),
        legend = dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
        margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
        height = const_sizes['chart_height_pacing'],
        hovermode = 'x unified'
    )

    st.plotly_chart(fig,use_container_width=True)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Show dataframe

    df_pacer_to_print = df_pacer.copy()
    
    for col_name in ['spend_target_value','actual_target_diff','actual_spend']:
        df_pacer_to_print[col_name] = df_pacer_to_print[col_name].map(lambda x: f'{x:.2%}')
    
    st.markdown('### Online Pacing - Detailed')
    st.dataframe(df_pacer_to_print.sort_values(by = 'tuner_run_start_time', ascending = False))

    

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# PORTFOLIO GAPS

if selected_view == 'Portfolio Gaps':

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Read dataframe
    
    df_portfolio_gaps = pd.read_csv('/home/vilardi/vilardi_nfs/RSP/RSP_Deep_Dive_Dashboard/df_portfolio_gaps.csv')

    # Get geo list
    geo_list = df_portfolio_gaps['geo'].unique().tolist()

    # Get week list
    week_list = df_portfolio_gaps['week'].unique().tolist()

    # Create city filter
    selected_geo = st.sidebar.selectbox(label = 'Geo', options = geo_list, index = geo_list.index('[Mega-Region] LatAm'))

    # Create week filters
    selected_start_week = st.sidebar.selectbox(label = 'Start Week', options = week_list, index = week_list.index('2025-01-06'))
    selected_end_week = st.sidebar.selectbox(label = 'End Week', options = week_list, index = len(week_list)-1)

    # Filter dataframe
    df_portfolio_gaps = df_portfolio_gaps[(df_portfolio_gaps['geo'] == selected_geo) & (df_portfolio_gaps['week'] >= selected_start_week) & (df_portfolio_gaps['week'] <= selected_end_week)]

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot RSP Multipliers

    # Header
    st.markdown('---')
    st.markdown('### Mean Session-Level RSP Multipliers')

    # Single legend (instead of one for each chart, removing redundancy and clutter)
    st.markdown("""
        <span style='color:{};'>▬ UberX</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Comfort</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Black</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Moto </span>
        """.format(const_colors['portfolio_x'],const_colors['portfolio_comfort'],const_colors['portfolio_black'],const_colors['portfolio_moto']), unsafe_allow_html = True)

    col_list = st.columns([1,1,1,1,1])
    km_bucket_list = ['All','(a) 0-3 km','(b) 3-6 km','(c) 6-10 km','(d) 10+ km']

    for i,col in enumerate(col_list):
        
        km_bucket = km_bucket_list[i]
        df_km_bucket = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]
        
        with col:

            fig = go.Figure()

            ycol_list = ['avg_rsp_multiplier_x','avg_rsp_multiplier_comfort','avg_rsp_multiplier_black','avg_rsp_multiplier_moto']
            yname_list = ['X','Comfort','Black','Moto']
            colorkey_list = ['portfolio_x','portfolio_comfort','portfolio_black','portfolio_moto']
            
            for (ycol, yname,colorkey) in zip(ycol_list, yname_list, colorkey_list):
                # Plot
                fig.add_trace(
                    go.Scatter(
                        x = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]['week'],
                        y = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket][ycol],
                        mode = const_formats['portfolio_gaps_line_mode'],
                        name = yname,
                        line = dict(shape = const_formats['portfolio_gaps_line_shape'], color=const_colors[colorkey], width=const_sizes['portfolio_gaps_linewidth']),
                        yaxis='y',
                        hovertemplate = yname + ': %{y:,.2f}<extra></extra>'
                    )
                )

    
                # Layout
                fig.update_layout(
                    title = dict(text = km_bucket, y = 1.0, font = dict(size=15)),
                    xaxis_title = None,
                    yaxis_title = None,
                    xaxis = dict(tickformat="%b %Y", hoverformat = '%Y-%m-%d',dtick='M1',tickangle=-45),
                    #yaxis = dict(range=[0,yaxis_max]),
                    #legend = dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
                    showlegend = False,
                    margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
                    height = const_sizes['chart_height_portfolio'],
                    hovermode = "x unified"
                )

            # Plot
            st.plotly_chart(fig, use_container_width = True)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot RSP Multiplier Gaps

    # Header
    st.markdown('---')
    st.markdown('### Mean Session-Level RSP Multiplier Gaps vs UberX')

    # Single legend (instead of one for each chart, removing redundancy and clutter)
    st.markdown("""
        <span style='color:{};'>▬ Comfort</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Black</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Moto </span>
        """.format(const_colors['portfolio_comfort'],const_colors['portfolio_black'],const_colors['portfolio_moto']), unsafe_allow_html = True)

    col_list = st.columns([1,1,1,1,1])
    km_bucket_list = ['All','(a) 0-3 km','(b) 3-6 km','(c) 6-10 km','(d) 10+ km']

    for i,col in enumerate(col_list):
        
        km_bucket = km_bucket_list[i]
        df_km_bucket = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]
        
        with col:

            fig = go.Figure()

            ycol_list = ['avg_rsp_gap_comfort','avg_rsp_gap_black','avg_rsp_gap_moto']
            yname_list = ['Comfort','Black','Moto']
            colorkey_list = ['portfolio_comfort','portfolio_black','portfolio_moto']
            
            for (ycol, yname,colorkey) in zip(ycol_list, yname_list, colorkey_list):
                # Plot
                fig.add_trace(
                    go.Scatter(
                        x = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]['week'],
                        y = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket][ycol],
                        mode = const_formats['portfolio_gaps_line_mode'],
                        name = yname,
                        line = dict(shape = const_formats['portfolio_gaps_line_shape'], color=const_colors[colorkey], width=const_sizes['portfolio_gaps_linewidth']),
                        yaxis='y',
                        hovertemplate = yname + ': %{y:,.2%}<extra></extra>'
                    )
                )

    
                # Layout
                fig.update_layout(
                    title = dict(text = km_bucket, y = 1.0, font = dict(size=15)),
                    xaxis_title = None,
                    yaxis_title = None,
                    xaxis = dict(tickformat="%b %Y",hoverformat = '%Y-%m-%d',dtick="M1",tickangle=-45),
                    yaxis = dict(tickformat='0.0%'),
                    #yaxis = dict(range=[0,yaxis_max]),
                    #legend = dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
                    showlegend = False,
                    margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
                    height = const_sizes['chart_height_portfolio'],
                    hovermode = "x unified"
                )

            # Plot
            st.plotly_chart(fig, use_container_width = True)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot UFP

    # Header
    st.markdown('---')
    st.markdown('### Mean Session-Level UFP (USD)')

    # Single legend (instead of one for each chart, removing redundancy and clutter)
    st.markdown("""
        <span style='color:{};'>▬ UberX</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Comfort</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Black</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Moto </span>
        """.format(const_colors['portfolio_x'],const_colors['portfolio_comfort'],const_colors['portfolio_black'],const_colors['portfolio_moto']), unsafe_allow_html = True)

    col_list = st.columns([1,1,1,1,1])
    km_bucket_list = ['All','(a) 0-3 km','(b) 3-6 km','(c) 6-10 km','(d) 10+ km']

    for i,col in enumerate(col_list):
        
        km_bucket = km_bucket_list[i]
        df_km_bucket = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]
        
        with col:

            fig = go.Figure()

            ycol_list = ['avg_ufp_fare_x','avg_ufp_fare_comfort','avg_ufp_fare_black','avg_ufp_fare_moto']
            yname_list = ['X','Comfort','Black','Moto']
            colorkey_list = ['portfolio_x','portfolio_comfort','portfolio_black','portfolio_moto']
            
            for (ycol, yname,colorkey) in zip(ycol_list, yname_list, colorkey_list):
                # Plot
                fig.add_trace(
                    go.Scatter(
                        x = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]['week'],
                        y = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket][ycol],
                        mode = const_formats['portfolio_gaps_line_mode'],
                        name = yname,
                        line = dict(shape = const_formats['portfolio_gaps_line_shape'], color=const_colors[colorkey], width=const_sizes['portfolio_gaps_linewidth']),
                        yaxis='y',
                        hovertemplate = yname + ': %{y:,.2f}<extra></extra>'
                    )
                )

    
                # Layout
                fig.update_layout(
                    title = dict(text = km_bucket, y = 1.0, font = dict(size=15)),
                    xaxis_title = None,
                    yaxis_title = None,
                    xaxis = dict(tickformat="%b %Y",hoverformat = '%Y-%m-%d',dtick="M1",tickangle=-45),
                    #yaxis=dict(range=[0,yaxis_max]),
                    #legend=dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
                    showlegend = False,
                    margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
                    height = const_sizes['chart_height_portfolio'],
                    hovermode = "x unified"
                )

            # Plot
            st.plotly_chart(fig, use_container_width = True)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Plot UFP Gaps

    # Header
    st.markdown('---')
    st.markdown('### Mean Session-Level UFP Gaps vs UberX')

    # Single legend (instead of one for each chart, removing redundancy and clutter)
    st.markdown("""
        <span style='color:{};'>▬ Comfort</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Black</span>&nbsp;&nbsp;&nbsp;&nbsp;
        <span style='color:{};'>▬ Moto </span>
        """.format(const_colors['portfolio_comfort'],const_colors['portfolio_black'],const_colors['portfolio_moto']), unsafe_allow_html = True)

    col_list = st.columns([1,1,1,1,1])
    km_bucket_list = ['All','(a) 0-3 km','(b) 3-6 km','(c) 6-10 km','(d) 10+ km']

    for i,col in enumerate(col_list):
        
        km_bucket = km_bucket_list[i]
        df_km_bucket = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]
        
        with col:

            fig = go.Figure()

            ycol_list = ['avg_ufp_gap_comfort','avg_ufp_gap_black','avg_ufp_gap_moto']
            yname_list = ['Comfort','Black','Moto']
            colorkey_list = ['portfolio_comfort','portfolio_black','portfolio_moto']
            
            for (ycol, yname,colorkey) in zip(ycol_list, yname_list, colorkey_list):
                # Plot
                fig.add_trace(
                    go.Scatter(
                        x = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket]['week'],
                        y = df_portfolio_gaps[df_portfolio_gaps['km_bucket'] == km_bucket][ycol],
                        mode = const_formats['portfolio_gaps_line_mode'],
                        name = yname,
                        line = dict(shape = const_formats['portfolio_gaps_line_shape'], color=const_colors[colorkey], width=const_sizes['portfolio_gaps_linewidth']),
                        yaxis='y',
                        hovertemplate = yname + ': %{y:,.2%}<extra></extra>'
                    )
                )

    
                # Layout
                fig.update_layout(
                    title = dict(text = km_bucket, y = 1.0, font = dict(size=15)),
                    xaxis_title = None,
                    yaxis_title = None,
                    xaxis = dict(tickformat="%b %Y",hoverformat = '%Y-%m-%d',dtick="M1",tickangle=-45),
                    yaxis = dict(tickformat='0.0%'),
                    #yaxis = dict(range=[0,yaxis_max]),
                    #legend = dict(orientation='h', yanchor='bottom', y=1.03, xanchor = 'right', x=1, font=dict(size=const_sizes['legend_font_size'])),
                    showlegend = False,
                    margin = dict(l = const_sizes['box_margin_left'], r = const_sizes['box_margin_right'], t = const_sizes['box_margin_top'], b = const_sizes['box_margin_bottom']),
                    height = const_sizes['chart_height_portfolio'],
                    hovermode = "x unified"
                )

            # Plot
            st.plotly_chart(fig, use_container_width = True)


    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Show dataframe

    df_portfolio_gaps_to_print = df_portfolio_gaps.copy()
    
    for col_name in ['avg_rsp_gap_comfort','avg_rsp_gap_black','avg_rsp_gap_moto','avg_ufp_gap_comfort','avg_ufp_gap_black','avg_ufp_gap_moto']:
        df_portfolio_gaps_to_print[col_name] = df_portfolio_gaps_to_print[col_name].map(lambda x: f'{x:.2%}')
    
    st.markdown('---')
    st.markdown('### Portfolio Gaps Detailed')
    
    st.dataframe(df_portfolio_gaps_to_print)


# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# PRICE PLANS

if selected_view == 'Price Plans':
    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Header
    
    st.markdown('---')
    st.markdown('### Price Plans')

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Read dataframe
    
    df_price_plans = pd.read_csv('/home/vilardi/vilardi_nfs/RSP/RSP_Deep_Dive_Dashboard/df_price_plans.csv')

    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Apply sidebar filters (country, city, min date, max date, dates)

    # Lists
    country_list = sorted(df_price_plans['country_name'].unique().tolist())
    city_list = sorted(df_price_plans['city_name'].unique().tolist())
    min_datestr_list = sorted(df_price_plans['min_datestr'].unique().tolist())
    max_datestr_list = sorted(df_price_plans['max_datestr'].unique().tolist())

    # Insert "All" options
    country_list.insert(0, 'All')
    city_list.insert(0, 'All')
    min_datestr_list.insert(0, 'All')
    max_datestr_list.insert(0, 'All')

    # Sidebar Select-boxes (country, city, min date, max date)
    selected_country = st.sidebar.selectbox(label = 'Country', options = country_list, index = 0)
    selected_city = st.sidebar.selectbox(label = 'City', options = city_list, index = 0)
    selected_min_datestr = st.sidebar.selectbox(label = 'Min Datestr', options = min_datestr_list, index = 0)
    selected_max_datestr = st.sidebar.selectbox(label = 'Max Datestr', options = max_datestr_list, index = len(max_datestr_list)-1) # default live pps

    # Filter dataframe
    mask = pd.Series(True, index = df_price_plans.index)
    if selected_country != 'All': mask &= df_price_plans['country_name'] == selected_country
    if selected_city != 'All': mask &= df_price_plans['city_name'] == selected_city
    if selected_min_datestr != 'All': mask &= df_price_plans['min_datestr'] == selected_min_datestr
    if selected_max_datestr != 'All': mask &= df_price_plans['max_datestr'] == selected_max_datestr
    df_price_plans = df_price_plans[mask]
    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Apply pp multiselect filters (objective function, bounds). Already pre-filtered by country, city and min/max datestr

    # Lists
    of_list = sorted(df_price_plans['objective_function'].unique().tolist())
    xbounds_list = sorted(df_price_plans['bounds_x'].unique().tolist())

    # Multiselect objects (in main page) (of and bounds)
    selected_xbounds = st.multiselect('UberX Bounds', options = xbounds_list, default = xbounds_list)
    selected_of = st.multiselect('Objective Function', options = of_list, default = of_list)
    
    # Filter dataframe
    mask = pd.Series(True, index = df_price_plans.index)

    if selected_xbounds: mask &= df_price_plans['bounds_x'].isin(selected_xbounds)
    if selected_of: mask &= df_price_plans['objective_function'].isin(selected_of)
    
    df_price_plans = df_price_plans[mask]
    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Show dataframe

    st.dataframe(df_price_plans)

    




    
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Sidebar footer

st.sidebar.markdown('\nData sources, pipelines and queries used for this dash are all detailed in the [LatAm RSP Management doc](https://docs.google.com/document/d/1CVu5mwV7O1uESbBg80oYM65-DyKNPACMYbYi_v43AIk/edit?tab=t.0)\n')
st.sidebar.markdown('\nContact: [Danilo](https://whober.uberinternal.com/159113) | [Matheus](https://whober.uberinternal.com/191122)')
st.sidebar.markdown('\n[Datasets](https://docs.google.com/spreadsheets/d/1xjcjmiAIrgDUsNKaRvUPdU6UHzivZLK81oE2oTe42h8)')

