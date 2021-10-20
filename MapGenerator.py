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


class MapGenerator:

    def __init__(self):
        pass


    # output the distribution of one specific factor in a map
    def single_map(self,factor):
        
        # load data from plot data from file
        try:
            street = gpd.read_file("./plot/background/street-shp")
        except:
            pass
        df_score = gpd.read_file("zip://plot/background/SCORE.zip")
        gdf = gpd.GeoDataFrame(df_score, geometry=df_score.geometry)
        
     
        ax=gdf.plot(column=factor, cmap='BuPu',figsize=(20,16),legend=False,alpha=0.35
                     ,legend_kwds={'orientation': "horizontal",
                        'shrink': 0.5,'alpha':0.45,'pad':0.01})
        fig = ax.figure

        street.plot(color="darkgray", alpha = .5, ax=ax, zorder=3)
        ax.set_axis_off()    
        ax.title.set_text(factor)
        
        return ax


    def combine_map(self,factorDic,number):
        
        ratioSum = sum(factorDic.values())
        
        # compute the percentage of each factor
        processDic = {}
        for key,value in factorDic.items():
            processDic[key] = value/ratioSum
            
        # load data from plot data from file
        try:
            street = gpd.read_file("./plot/background/street-shp")
        except:
            pass
        df_score = gpd.read_file("zip://plot/background/SCORE.zip")
        df_score['utility_map'] = 0
        
        # construct the utility function
        for key in processDic.keys():
            df_score['utility_map'] += processDic[key]*df_score[key]

        df_all = df_score.copy()
        df_score = df_score[df_score['utility_map']>0]
        df_score = df_score.sort_values('SCORE',ascending=False)
        gdf = gpd.GeoDataFrame(df_all, geometry=df_all.geometry)
        ax=gdf.plot(column='SCORE', cmap='BuPu',figsize=(20,16),legend=False,alpha=1
                     ,legend_kwds={'orientation': "horizontal",
                        'shrink': 0.5,'alpha':0.5,'pad':0.01})
        fig = ax.figure
        #cb_ax = fig.axes[1] 
        #cb_ax.tick_params(labelsize=20)   
        street.plot(color="darkgray", alpha = .5, ax=ax, zorder=3)
        ax.title.set_text(factorDic)
        ax.set_axis_off()
        return ax,df_score,df_all


    def utilityMap(self,factorDic,number):

        for each in factorDic.keys():
            self.single_map(each)
        ax,df_cen, df_all = self.combine_map(factorDic,number)
        df_cen = df_cen.head(number)

        df_all = df_all.reset_index().rename(columns={"index":"geoID"})
        df_cen = df_cen.reset_index().rename(columns={"index":"geoID"})
        return ax,df_cen,df_all
