import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import time
import requests
from datetime import datetime, timedelta
from shapely.geometry import Point
from busSim import BusSim
from graph import Graph
from geopy.distance import geodesic
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics.pairwise import pairwise_distances
from constrained_kmedoids import KMedoids
import itertools

def list_route(group_number,group_table): # generate all possible routes for one day
    each_route=[]
    for i in range(len(group_table)):
        if group_table['label'].iloc[i]==group_number:
            each_route.append(i)
    possible_route=list(itertools.permutations(each_route))
    return possible_route


def best_route(group_number,group_table,distMatrix = dist): # generate the route with the smallest total distance for each day
    route_dictionary={}    
    distance = pd.DataFrame(distMatrix)
    for i in range(len(list_route(group_number,group_table))):
        route=list_route(group_number,group_table)[i]
        dist=0
        for j in range(len(route)):
            if j+1<len(route):
                dist+=distance.iloc[route[j],route[j+1]] 
        route_dictionary[route]=dist

    minimum_distance = min(route_dictionary.values())
    minimum_route = [key for key in route_dictionary if route_dictionary[key] == minimum_distance][0]
    return minimum_route

def totalroute_each_day(group_number,group_table): # generate the total route for each day with its total score
    score=0
    total_route=[]
    total_score=[]
    for i in range(len(best_route(group_number,group_table))):
        for j in range(len(df)):
            if best_route(group_number,group_table)[i]==j:
                score+=df['SCORE'].iloc[j]
                name=df['geoID'].iloc[j]
        total_route.append(name)
        total_score.append(score)
    return total_route, sum(total_score)

def sorted_route_by_score(group_table): # generate sorted dataframe of five days, and sorted dataframe for total circulation
    route_list=[]
    for i in range(5):
        route_list.append(totalroute_each_day(i+1,group_table)[0]) # collect five days' route together
    score_list=[]
    for i in range(5):
        score_list.append(totalroute_each_day(i+1,group_table)[1]) # collect five days' score together
    
    dict_ab={'schedule':route_list,'score':score_list}
    df_route_score=pd.DataFrame.from_dict(dict_ab, orient='index') # generate the dataframe of each route with its score for each day
    df_route_score=df_route_score.T
    df_route_score=df_route_score.sort_values(by=['score'],ascending=False) # sort the route of each day by score
    total_circluation = pd.read_csv("TotalCir.csv")
    circluation=total_circluation.sort_values(by=['Total Circulation'],ascending=False) # sort the circulation of each day 
    return df_route_score, circluation 

def match_weekdays(group_table): # Match the route from large to small with the weekdays by its score
    df_route_score=sorted_route_by_score(group_table)[0]
    circluation=sorted_route_by_score(group_table)[1]
    weekdays=['Mondays','Tuesdays','Wednesdays','Thursdays','Fridays']
    matched_route={}
    for i in range(len(circluation)):
        for j in range(len(weekdays)):
            if circluation['Unnamed: 0'].iloc[i]==weekdays[j]:
                matched_route[weekdays[j]]=df_route_score['schedule'].iloc[i]
    return matched_route

def createSchedule(Monday,Tuesday,Wednesday,Thursday,Friday): # create the framework of the schedule
    weekin = {'Monday':Monday, 'Tuesday':Tuesday, 'Wednesday':Wednesday, 'Thursday':Thursday, 'Friday':Friday}
    schedule_initial = pd.DataFrame.from_dict(weekin,orient='index',columns=['4pm','5pm','6pm','7pm']).T
    return schedule_initial

def Auto_schedule(group_table): # Automatcially generate the final schedule
    schedule=createSchedule(match_weekdays(group_table)['Mondays'],match_weekdays(group_table)['Tuesdays'],match_weekdays(group_table)['Wednesdays'],match_weekdays(group_table)['Thursdays'],match_weekdays(group_table)['Fridays'])
    return schedule