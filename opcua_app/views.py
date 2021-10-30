from django.db.models.base import Model
from numpy.core.fromnumeric import sort
from django.shortcuts import redirect, render
from django.urls import reverse
import time,json
import websocket
import requests
import numpy as np, scipy.stats as st
import pandas as pd
from statistics import stdev,mean
from .models import FeedOverride, SpeedOverride, SpindleSpeed, CurrentPosition, FeedRate, Anomaly
from django.db.models import Count, Min, Max
from bokeh.plotting import figure
from bokeh.palettes import Category10, Plasma, Viridis
from bokeh.transform import cumsum
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource, ImageURL, Legend
from bokeh.models.tickers import FixedTicker
from bokeh.models import DatetimeTickFormatter,NumeralTickFormatter
from bokeh.models.renderers import GlyphRenderer
from bokeh.io import curdoc
from bokeh.themes import built_in_themes,theme
import bokeh.models as bkm
import bokeh.plotting as bkp
# import os 

def home(request):
    
    # os.system('python opcua_app/opcua_client.py')
    data = find_limits()
    feedRateOvr_min = round(FeedOverride.objects.all().aggregate(Min('feed_override_value'))['feed_override_value__min'],2)    
    feedRateOvr_max = round(FeedOverride.objects.all().aggregate(Max('feed_override_value'))['feed_override_value__max'],2)    
    speedOvr_min = round(SpeedOverride.objects.all().aggregate(Min('speed_override_value'))['speed_override_value__min'],2)    
    speedOvr_max = round(SpeedOverride.objects.all().aggregate(Max('speed_override_value'))['speed_override_value__max'],2)  
    actSpeed_min = round(SpindleSpeed.objects.all().aggregate(Min('spindle_speed_value'))['spindle_speed_value__min'],2)
    actSpeed_max = round(SpindleSpeed.objects.all().aggregate(Max('spindle_speed_value'))['spindle_speed_value__max'],2)
    
    args = {
        'feedRateOvr_min': feedRateOvr_min,
        'feedRateOvr_max': feedRateOvr_max,
        'feedRateOvr_mean': round(data['feedRateOvr_mean'],2),
        'speedOvr_min': speedOvr_min,
        'speedOvr_max': speedOvr_max,
        'speedOvr_mean': round(data['speedOvr_mean'],2),
        'actSpeed_min': actSpeed_min,
        'actSpeed_max': actSpeed_max,
        'actSpeed_mean': round(data['actSpeed_mean'],2),

    }
    return render(request,'opcua_app/home.html',args)

def anomaly_view(request):

    data = find_limits()

    #save Speed Override anomaly
    
    speedOvrs = SpeedOverride.objects.all()
    for speedOvr in speedOvrs:
        
        speedOvr_value = speedOvr.speed_override_value
        if speedOvr_value == 0.0:
            continue
        if speedOvr_value in range(data['speedOvr_intrvl'][0],data['speedOvr_intrvl'][1]):    
            pass        
        else:
            if not Anomaly.objects.filter(speedOvr_key=speedOvr).exists():

                speedOvr_anomaly = Anomaly.objects.create(param_type="s", speedOvr_key=speedOvr)
                speedOvr_anomaly.save()

    #save Feed Override anomaly
    
    feedRateOvrs = FeedOverride.objects.all()
    
    print(data['feedRateOvr_intrvl'][0],data['feedRateOvr_intrvl'][1])
    for feedRateOvr in feedRateOvrs:

        feedRateOvr_value = feedRateOvr.feed_override_value       
        if feedRateOvr_value == 0.0:
            continue
        if feedRateOvr_value in range(data['feedRateOvr_intrvl'][0],data['feedRateOvr_intrvl'][1]):
            pass
        else:
            if not Anomaly.objects.filter(feedRateOvr_key=feedRateOvr).exists():

                feedRateOvr_anomaly = Anomaly.objects.create(param_type="f", feedRateOvr_key=feedRateOvr)
                feedRateOvr_anomaly.save()

    
    #save Spindle Speed anomaly
    actSpeeds = SpindleSpeed.objects.all()
    for actSpeed in actSpeeds:

        actSpeed_value = actSpeed.spindle_speed_value
        
        if actSpeed_value == 0.0:
            continue
        if actSpeed_value in range(data['actSpeed_intrvl'][0],data['actSpeed_intrvl'][1]):
            pass
        else:
            if not Anomaly.objects.filter(actSpeed_key=actSpeed).exists():

                actSpeed_anomaly = Anomaly.objects.create(param_type="a", actSpeed_key=actSpeed)
                actSpeed_anomaly.save()

    #Retrieve the last five values of Speed Ovrride,Feed Override and Spindle Speed anomalies
    speedOvr_anomalies = Anomaly.objects.filter(param_type='s').order_by('-id')[:5]
    feedRateOvr_anomalies = Anomaly.objects.filter(param_type='f').order_by('-id')[:5]
    actSpeed_anomalies = Anomaly.objects.filter(param_type='a').order_by('-id')[:5]
    
    # anomalies = temp_anomalies | pres_anomalies
    # print(temp_anomalies[0])
    args = {
        'speedOvr_anomalies':speedOvr_anomalies,
        'feedRateOvr_anomalies' : feedRateOvr_anomalies,
        'actSpeed_anomalies' : actSpeed_anomalies,
        'feedRateOvr_intrvl': data['feedRateOvr_intrvl'],
        'speedOvr_intrvl':data['speedOvr_intrvl'],
        'actSpeed_intrvl':data['actSpeed_intrvl']

    }
    # print(data)
    return render(request,'opcua_app/anomaly.html',args)


def find_limits():

    #find speedOvr mean confidence interval
    speedOvrs = SpeedOverride.objects.all()
    speedOvr_data = []
    for speedOvr in speedOvrs:
        speedOvr_value = float(speedOvr.speed_override_value)
        if speedOvr_value == 0.0:
            continue
        speedOvr_data.append(speedOvr_value)
    speedOvr_intrvl = st.t.interval(0.95, len(speedOvr_data)-1, loc=np.mean(speedOvr_data), scale=st.sem(speedOvr_data))
    print(speedOvr_intrvl)
    
    #find feedRateOvr mean confidence interval
    feedRateOvrs = FeedOverride.objects.all()
    feedRateOvr_data = []
    for feedRateOvr in feedRateOvrs:
        feedRateOvr_value = float(feedRateOvr.feed_override_value)
        
        if feedRateOvr_value == 0.0:
            continue
        feedRateOvr_data.append(feedRateOvr_value)
    feedRateOvr_intrvl = st.t.interval(0.95, len(feedRateOvr_data)-1, loc=np.mean(feedRateOvr_data), scale=st.sem(feedRateOvr_data))

    #find actSpeed mean confidence interval
    actSpeeds = SpindleSpeed.objects.all()
    actSpeed_data = []
    for actSpeed in actSpeeds:
        actSpeed_value = float(actSpeed.spindle_speed_value)
        if actSpeed_value == 0.0:
            continue
        actSpeed_data.append(actSpeed_value)
    actSpeed_intrvl = st.t.interval(0.95, len(actSpeed_data)-1, loc=np.mean(actSpeed_data), scale=st.sem(actSpeed_data))

    #calculate the upper and lower bounds
    speedOvr_lower = round(speedOvr_intrvl[0])
    speedOvr_upper = round(speedOvr_intrvl[1])
    # print(feedRateOvr_intrvl)
    feedRateOvr_lower = round(feedRateOvr_intrvl[0])
    feedRateOvr_upper = round(feedRateOvr_intrvl[1])
    
    actSpeed_lower = round(actSpeed_intrvl[0])
    actSpeed_upper = round(actSpeed_intrvl[1])

    speedOvr_margin = round(stdev(speedOvr_data))
    feedRateOvr_margin = round(stdev(feedRateOvr_data))
    actSpeed_margin = round(stdev(actSpeed_data))

    args = {
        'feedRateOvr_intrvl': (feedRateOvr_lower-feedRateOvr_margin,feedRateOvr_upper+feedRateOvr_margin),
        'feedRateOvr_mean':mean(feedRateOvr_data),
        'speedOvr_intrvl':(speedOvr_lower-speedOvr_margin,speedOvr_upper+speedOvr_margin),
        'speedOvr_mean':mean(speedOvr_data),
        'actSpeed_intrvl': (actSpeed_lower-actSpeed_margin,actSpeed_upper+actSpeed_margin),
        'actSpeed_mean':mean(actSpeed_data),
    }
    
    
    return args

def graphs(request):

    #Create Speed Override graph
    curdoc().theme = 'dark_minimal'
    speedOvrs = SpeedOverride.objects.all().order_by('timestamp')
    speedOvr_data,speedOvr_timestamp = [],[]
    for speedOvr in speedOvrs:
        speedOvr_value = speedOvr.speed_override_value
        speedOvr_timestamp.append(speedOvr.timestamp)
        speedOvr_data.append(speedOvr_value)

    speedOvr_timestamp_data = pd.to_datetime(speedOvr_timestamp)
    title = "Speed Override"
    source = ColumnDataSource(data=dict(speedOvr_data = speedOvr_data, speedOvr_timestamp_data = speedOvr_timestamp_data ))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Speed %',
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    plot_case.add_tools(HoverTool(
    tooltips=[( 'Time',  '@speedOvr_timestamp_data{%T}'),('Speed','@speedOvr_data{‘0,0’}')],
    formatters={'@speedOvr_timestamp_data': 'datetime'}))
    
    # plot_case.vbar(x="speedOvr_timestamp_data", top="speedOvr_data", width=300,source = source,color='#78DEC7')
    plot_case.line(x="speedOvr_timestamp_data", y="speedOvr_data", source = source,line_color="#bd00ff",line_width = 1)
    plot_case.circle(x="speedOvr_timestamp_data", y="speedOvr_data", source = source, color="#bd00ff", size=4)
    script_speedOvr, div_speedOvr = components(plot_case)

    #Create feedRateOvr graph

    feedRateOvrs = FeedOverride.objects.all().order_by('timestamp')
    feedRateOvr_data,feedRateOvr_timestamp = [],[]
    for feedRateOvr in feedRateOvrs:
        feedRateOvr_value = feedRateOvr.feed_override_value
        feedRateOvr_timestamp.append(feedRateOvr.timestamp)
        feedRateOvr_data.append(feedRateOvr_value)

    feedRateOvr_timestamp_data = pd.to_datetime(feedRateOvr_timestamp)
    title = "Feed Rate Override"
    source = ColumnDataSource(data=dict(feedRateOvr_data = feedRateOvr_data, feedRateOvr_timestamp_data = feedRateOvr_timestamp_data ))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Speed %',
        # x_range = (0,20),
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'],days = ['%d-%m-%Y', '%F'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    plot_case.add_tools(HoverTool(
    tooltips=[( 'Time',  '@feedRateOvr_timestamp_data{%T}'),('Speed','@feedRateOvr_data{‘0,0’}')],
    formatters={'@feedRateOvr_timestamp_data': 'datetime'}))
    
    # plot_case.vbar(x="feedRateOvr_timestamp_data", top="feedRateOvr_data", width=300,source = source,color='#FF7600')
    plot_case.line(x="feedRateOvr_timestamp_data", y="feedRateOvr_data", source = source,line_color="#FF7600",line_width = 1)
    plot_case.circle(x="feedRateOvr_timestamp_data", y="feedRateOvr_data", source = source, color="#FF7600", size=2)
    script_feedRateOvr, div_feedRateOvr = components(plot_case)

    #Create actSpeed graph

    actSpeeds = SpindleSpeed.objects.all().order_by('timestamp')
    actSpeed_data,actSpeed_timestamp = [],[]
    for actSpeed in actSpeeds:
        actSpeed_value = actSpeed.spindle_speed_value
        actSpeed_timestamp.append(actSpeed.timestamp)
        actSpeed_data.append(actSpeed_value)

    actSpeed_timestamp_data = pd.to_datetime(actSpeed_timestamp)
    title = "Spindle Speed"
    source = ColumnDataSource(data=dict(actSpeed_data = actSpeed_data, actSpeed_timestamp_data = actSpeed_timestamp_data))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Speed RPM',
        # x_range = (0,20),
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'],days = ['%d-%m-%Y', '%F'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    plot_case.add_tools(HoverTool(
    tooltips=[( 'Time',  '@actSpeed_timestamp_data{%T}'),('Speed','@actSpeed_data{‘0,0’}')],
    formatters={'@actSpeed_timestamp_data': 'datetime'}))
    
    # plot_case.vbar(x="actSpeed_timestamp_data", top="actSpeed_data", width=300,source = source,color='#28FFBF')
    plot_case.line(x="actSpeed_timestamp_data", y="actSpeed_data", source = source,line_color="#28FFBF",line_width = 1)
    plot_case.circle(x="actSpeed_timestamp_data", y="actSpeed_data", source = source, color="#28FFBF", size=4)
    script_actSpeed, div_actSpeed = components(plot_case)
    

    #Create FeedRate graph

    frs = FeedRate.objects.all().order_by('timestamp')
    fr_x_data,fr_y_data,fr_z_data,fr_b_data,fr_timestamp = [],[],[],[],[],
    for fr in frs:
        fr_x_value = float(fr.x_axis)
        fr_y_value = float(fr.y_axis)
        fr_z_value = float(fr.z_axis)
        fr_b_value = float(fr.b_axis)
        fr_timestamp.append(fr.timestamp)
        fr_x_data.append(fr_x_value)
        fr_y_data.append(fr_y_value)
        fr_z_data.append(fr_z_value)
        fr_b_data.append(fr_b_value)

    fr_timestamp_data = pd.to_datetime(fr_timestamp)
    title = "Feed Rate"
    source = ColumnDataSource(data=dict(fr_x_data = fr_x_data, fr_y_data = fr_y_data,fr_z_data = fr_z_data,fr_b_data = fr_b_data,fr_timestamp_data = fr_timestamp_data))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Feed Rate (μm/min)',
        # x_range = (0,20),
        toolbar_location="below",
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'],days = ['%d-%m-%Y', '%F'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    # plot_case.add_tools(HoverTool(
    # tooltips=[( 'Time',  '@fr_timestamp_data{%T}'),('Position','@fr_y_data{‘0,0’}')],
    # formatters={'@fr_timestamp_data': 'datetime'}))
    
    # plot_case.vbar(x="fr_timestamp_data", top="fr_data", width=300,source = source,color='#28FFBF')
    x0 = plot_case.line(x="fr_timestamp_data", y="fr_x_data", source = source,line_color="#28FFBF",line_width = 1)
    x1 = plot_case.circle(x="fr_timestamp_data", y="fr_x_data", source = source, color="#28FFBF", size=4)
    y0 = plot_case.line(x="fr_timestamp_data", y="fr_y_data", source = source,line_color="#FF7600",line_width = 1)
    y1 = plot_case.circle(x="fr_timestamp_data", y="fr_y_data", source = source, color="#FF7600", size=4)
    z0 = plot_case.line(x="fr_timestamp_data", y="fr_z_data", source = source,line_color="#bd00ff",line_width = 1)
    z1 = plot_case.circle(x="fr_timestamp_data", y="fr_z_data", source = source, color="#bd00ff", size=4)
    b0 = plot_case.line(x="fr_timestamp_data", y="fr_b_data", source = source,line_color="#CE1F6A",line_width = 1)
    b1 = plot_case.circle(x="fr_timestamp_data", y="fr_b_data", source = source, color="#CE1F6A", size=4)

    # Add legend
    # plot_case.legend.location = "top_left"
    # plot_case.legend.title = "Axes"

    legend = Legend(items=[
    ("X axis"   , [x0,x1]),
    ("Y axis" , [y0,y1]),
    ("Z axis" , [z0,z1]),
    ("B axis" , [b0,b1])],
    location="top", title="Axes")

    plot_case.add_layout(legend, 'right')

    # Add hover tools seprately to each line
    g1 = bkm.Cross(x="fr_timestamp_data", y="fr_x_data",line_color="#28FFBF")
    g1_r = plot_case.add_glyph(source_or_glyph=source, glyph=g1)
    g1_hover = bkm.HoverTool(renderers=[g1_r], tooltips=[( 'Time',  '@fr_timestamp_data{%T}'),('X axis','@fr_x_data{‘0,0’}')],
    formatters={'@fr_timestamp_data': 'datetime'})
    plot_case.add_tools(g1_hover)

    g2 = bkm.Cross(x="fr_timestamp_data", y="fr_y_data",line_color="#FF7600")
    g2_r = plot_case.add_glyph(source_or_glyph=source, glyph=g2)
    g2_hover = bkm.HoverTool(renderers=[g2_r], tooltips=[( 'Time',  '@fr_timestamp_data{%T}'),('Y axis','@fr_y_data{‘0,0’}')],
    formatters={'@fr_timestamp_data': 'datetime'})
    plot_case.add_tools(g2_hover)

    g3 = bkm.Cross(x="fr_timestamp_data", y="fr_z_data",line_color="#bd00ff")
    g3_r = plot_case.add_glyph(source_or_glyph=source, glyph=g3)
    g3_hover = bkm.HoverTool(renderers=[g3_r], tooltips=[( 'Time',  '@fr_timestamp_data{%T}'),('Z axis','@fr_z_data{‘0,0’}')],
    formatters={'@fr_timestamp_data': 'datetime'})
    plot_case.add_tools(g3_hover)

    g4 = bkm.Cross(x="fr_timestamp_data", y="fr_b_data",line_color="#CE1F6A")
    g4_r = plot_case.add_glyph(source_or_glyph=source, glyph=g4)
    g4_hover = bkm.HoverTool(renderers=[g4_r], tooltips=[( 'Time',  '@fr_timestamp_data{%T}'),('B axis','@fr_b_data{‘0,0’}')],
    formatters={'@fr_timestamp_data': 'datetime'})
    plot_case.add_tools(g4_hover)

    script_fr, div_fr = components(plot_case)


    #Create CurrentPosition graph

    cps = CurrentPosition.objects.all().order_by('timestamp')
    cp_x_data,cp_y_data,cp_z_data,cp_b_data,cp_timestamp = [],[],[],[],[],
    for cp in cps:
        cp_x_value = float(cp.x_axis)
        cp_y_value = float(cp.y_axis)
        cp_z_value = float(cp.z_axis)
        cp_b_value = float(cp.b_axis)
        cp_timestamp.append(cp.timestamp)
        cp_x_data.append(cp_x_value)
        cp_y_data.append(cp_y_value)
        cp_z_data.append(cp_z_value)
        cp_b_data.append(cp_b_value)

    cp_timestamp_data = pd.to_datetime(cp_timestamp)
    title = "Current Position"
    source = ColumnDataSource(data=dict(cp_x_data = cp_x_data, cp_y_data = cp_y_data,cp_z_data = cp_z_data,cp_b_data = cp_b_data,cp_timestamp_data = cp_timestamp_data))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Current Position (μm)',
        # x_range = (0,20),
        toolbar_location="below",
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'],days = ['%d-%m-%Y', '%F'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    # plot_case.add_tools(HoverTool(
    # tooltips=[( 'Time',  '@cp_timestamp_data{%T}'),('Position','@cp_y_data{‘0,0’}')],
    # formatters={'@cp_timestamp_data': 'datetime'}))
    
    # plot_case.vbar(x="cp_timestamp_data", top="cp_data", width=300,source = source,color='#28FFBF')
    x0 = plot_case.line(x="cp_timestamp_data", y="cp_x_data", source = source,line_color="#28FFBF",line_width = 1)
    x1 = plot_case.circle(x="cp_timestamp_data", y="cp_x_data", source = source, color="#28FFBF", size=4)
    y0 = plot_case.line(x="cp_timestamp_data", y="cp_y_data", source = source,line_color="#FF7600",line_width = 1)
    y1 = plot_case.circle(x="cp_timestamp_data", y="cp_y_data", source = source, color="#FF7600", size=4)
    z0 = plot_case.line(x="cp_timestamp_data", y="cp_z_data", source = source,line_color="#bd00ff",line_width = 1)
    z1 = plot_case.circle(x="cp_timestamp_data", y="cp_z_data", source = source, color="#bd00ff", size=4)
    b0 = plot_case.line(x="cp_timestamp_data", y="cp_b_data", source = source,line_color="#CE1F6A",line_width = 1)
    b1 = plot_case.circle(x="cp_timestamp_data", y="cp_b_data", source = source, color="#CE1F6A", size=4)

    # Add legend
    # plot_case.legend.location = "top_left"
    # plot_case.legend.title = "Axes"

    legend = Legend(items=[
    ("X axis"   , [x0,x1]),
    ("Y axis" , [y0,y1]),
    ("Z axis" , [z0,z1]),
    ("B axis" , [b0,b1])],
    location="top", title="Axes")

    plot_case.add_layout(legend, 'right')

    # Add hover tools seprately to each line
    g1 = bkm.Cross(x="cp_timestamp_data", y="cp_x_data",line_color="#28FFBF")
    g1_r = plot_case.add_glyph(source_or_glyph=source, glyph=g1)
    g1_hover = bkm.HoverTool(renderers=[g1_r], tooltips=[( 'Time',  '@cp_timestamp_data{%T}'),('X axis','@cp_x_data{‘0,0’}')],
    formatters={'@cp_timestamp_data': 'datetime'})
    plot_case.add_tools(g1_hover)

    g2 = bkm.Cross(x="cp_timestamp_data", y="cp_y_data",line_color="#FF7600")
    g2_r = plot_case.add_glyph(source_or_glyph=source, glyph=g2)
    g2_hover = bkm.HoverTool(renderers=[g2_r], tooltips=[( 'Time',  '@cp_timestamp_data{%T}'),('Y axis','@cp_y_data{‘0,0’}')],
    formatters={'@cp_timestamp_data': 'datetime'})
    plot_case.add_tools(g2_hover)

    g3 = bkm.Cross(x="cp_timestamp_data", y="cp_z_data",line_color="#bd00ff")
    g3_r = plot_case.add_glyph(source_or_glyph=source, glyph=g3)
    g3_hover = bkm.HoverTool(renderers=[g3_r], tooltips=[( 'Time',  '@cp_timestamp_data{%T}'),('Z axis','@cp_z_data{‘0,0’}')],
    formatters={'@cp_timestamp_data': 'datetime'})
    plot_case.add_tools(g3_hover)

    g4 = bkm.Cross(x="cp_timestamp_data", y="cp_b_data",line_color="#CE1F6A")
    g4_r = plot_case.add_glyph(source_or_glyph=source, glyph=g4)
    g4_hover = bkm.HoverTool(renderers=[g4_r], tooltips=[( 'Time',  '@cp_timestamp_data{%T}'),('B axis','@cp_b_data{‘0,0’}')],
    formatters={'@cp_timestamp_data': 'datetime'})
    plot_case.add_tools(g4_hover)

    script_cp, div_cp = components(plot_case)

    args = {
        'script_speedOvr':script_speedOvr,
        'div_speedOvr':div_speedOvr,
        'script_feedRateOvr':script_feedRateOvr,
        'div_feedRateOvr':div_feedRateOvr,        
        'script_actSpeed':script_actSpeed,
        'div_actSpeed':div_actSpeed,      
        'script_cp':script_cp,
        'div_cp':div_cp,    
        'script_fr':script_fr,
        'div_fr':div_fr,
    }

    return render(request,'opcua_app/graphs.html',args)

def redirect_to_home(request):

    return redirect(reverse('home'))