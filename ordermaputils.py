"""Prognos Orders module

Utils for manipulating dictionaries
"""

#import numpy as np
import pandas as pd


class OrderMapUtils:
    """Utilities for order map"""

    @classmethod
    def order_map_to_dataframe(cls, order_map):
        """Order map to DataFrame"""
        
        index = cls.build_order_map_index(order_map)
        dk = list(order_map.keys())[0];
        pk = list(order_map[dk].keys())[0]
        colnames = order_map[dk][pk][0].__dict__.keys()
        
        order_map_list = cls.order_map_list(order_map)
            
        return pd.DataFrame(order_map_list, index=index, columns=colnames)
        
        
    @classmethod
    def dataframe_to_order_map(cls, df, order_event_cls):
        """DataFrame to order map"""
        
        order_map = {}
        
        idx_dict = df.to_dict(orient='index')
        for key, val in idx_dict.items():
            idx_split = key.split(",")
            dk = idx_split[0]
            pk = int(idx_split[1])
            if dk not in order_map:
                order_map[dk] = dict()
            if pk not in order_map[dk]:
                order_map[dk][pk] = list()
            
            order_map[dk][pk].append(val)
        
        return order_map
        
        
    @classmethod
    def order_events_to_dataframe(cls, event_list):
        """Order events list to DataFrame"""
        
        colnames = event_list[0].__dict__.keys()
        
        order_events = list()
        for i in range(len(event_list)):
            order_events.append([getattr(event_list[i], j) for j in colnames])
            
        return pd.DataFrame(order_events, columns=colnames)
        
    
    @classmethod
    def order_map_list(cls, order_map):
        """Order events map to list"""
        
        order_map_list = list()
        
        colnames = cls._order_map_colnames(order_map)
        
        date_keys = order_map.keys()
        for dk in date_keys:
            primkeys = order_map[dk].keys()
            for pk in primkeys:
                for i in range(len(order_map[dk][pk])):
                    order_map_list.append(
                        [getattr(order_map[dk][pk][i], j) for j in colnames])

        return order_map_list
    
    
    @classmethod
    def build_order_map_index(cls, order_map):
        """Place doc here"""
        
        order_map_index = list()
        
        date_keys = order_map.keys()
        for dk in date_keys:
            primkeys = order_map[dk].keys()
            for pk in primkeys:
                for i in range(len(order_map[dk][pk])):
                    order_event = order_map[dk][pk][i]
                    event_id = getattr(order_event, 'event_id')
                    order_map_index.append("%s,%d,%d" % (dk, pk, event_id))

        return order_map_index
        
    
    @classmethod
    def _order_map_colnames(cls, order_map):
        dk = list(order_map.keys())[0];
        pk = list(order_map[dk].keys())[0]
        
        return order_map[dk][pk][0].__dict__.keys()
        
        
