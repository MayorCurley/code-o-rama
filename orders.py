"""Prognos Orders module

This module reads an exchange log file into a dictionary for easy data 
retrieval.
"""

#import numpy as np
import pandas as pd
import os
from enum import Enum

class Orders:
    """Place __doc__ here"""

    def __init__(self, dirname):
        """Constructor for Orders object"""
        self.order_map = {}
        self.df = None
        
        self.load_dir(dirname)
        
    
    def load_dir(self, dirname):
        """Loads order log files found in containing directory"""
        print('load_dir()', dirname)
        if os.path.isdir(dirname):
            file_list = os.listdir(dirname)
            for i in range(len(file_list)):
                path_filename = os.path.join(dirname, file_list[i])
                print('processing ' + path_filename)
                self.load_file(path_filename)
            self.df = OrderMapUtils.order_map_to_dataframe(
                self.order_map)
        else:
            print(dirname + ' is not a directory')
            

    def load_file(self, filename, delimiter='\t'):
        """Loads order log file into maps for data access"""
        print('You rang load_file()?')
        
        filebase = os.path.basename(filename)
        dateStr = os.path.splitext(filebase)[0]
        print(dateStr)
        
        
        # setup order line position dictionary
        print('ol_pos')
        ol_pos = {}
        for i in range(len(OrderEvent.col_tokens)):
            ol_pos[OrderEvent.col_tokens[i]] = i
        
        with open(filename,'rt') as src:
            order_events = {}
            for line in src:
                fields = line.split(delimiter)
                event_primary_key = int(fields[ol_pos['event_primary_key']])
                #print('event_primary_key:',event_primary_key)
                if event_primary_key not in order_events:
                    order_events[event_primary_key] = list()
                order_event = OrderEvent.to_order_event(fields);
                order_events[event_primary_key].append(order_event)
                #print('order_events keys, values:',order_events.keys(),order_events.values())
            
            self.order_map[dateStr] = order_events
            
        # TODO how should we handle the dataframe df instance var here?
            
        print('load_file() complete')
        
        
    def query(self, query_str):
        """Performs a query on the dataset.
        
        Params
        ------
        query_str query string which retrieves the data
        
        Returns
        -------
        pandas dataframe containing query result
        
        """
        
        result = self.df
        
        select_cols = ""
        where_clause = ""
        
        query_str = str.strip(query_str)
        filter_idx = query_str.find("where")
        
        # if the keyword 'where' is not found in the query string,
        # assume the whole string is a where clause
        if filter_idx == -1:
            where_clause = str.strip(query_str)
        else:
            select_cols = query_str[:filter_idx]
            select_cols = str.strip(select_cols)
            select_cols = select_cols.replace(" ", "")
            where_clause = query_str[(filter_idx + 6):]
            where_clause = str.strip(where_clause)
            
        print("query()", select_cols)
        print("query()", where_clause)
            
        if len(where_clause) > 0:
            result = result.query(where_clause)
            
        if len(select_cols) > 0:
            result = result[:][select_cols.split(",")]
            
        return result
            
        
    def select(self, colnames_list, copy=False):
        """Retrieves a subset of the order events based on 
        the column list passed to this method.
        
        Params
        ------
        colnames_list list of column names to retrieve
        copy specifies if subset should be copied, 
             default value is False
        
        Returns
        -------
        pandas dataframe of subset values
        
        """
        
        df_sub = self.df[colnames_list]
        if copy == True:
            df_sub = df_sub.copy()
        
        return df_sub
        
        
    def where(self, filter, copy=False):
        """Retrieves a subset of the order events based on 
        the sql-like where clause filter.
        
        Params
        ------
        filter sql-like filter string
               example: "instrument_name == 6ju8 & ask_ticks > 18050" 
        copy specifies if subset should be copied, 
             default value is False
        
        Returns
        -------
        pandas dataframe of subset values
        
        """
        
        df_sub = self.df.query(filter)
        if copy == True:
            df_sub = df_sub.copy()
        
        return df_sub
        
    
    
    def find_by_datestr(self, datestr):
        """Retrieves order events by datestr
        
        Params
        ------
        
        datestr date string, for example 'YYYYMMDD'
        
        Returns
        -------
        dict of order events
        """
        
        omap = self.order_map[datestr]
        
        return omap
        
        
    def find_by_primary_key(self, datestr, event_primary_key):
        """Retrieves order events by event primary key
        
        Params
        ------
        
        datestr date string, for example 'YYYYMMDD'
        event_primary_key order event primary key long value
        
        Returns
        -------
        list of order events for event primary key
        """
        
        omap = self.find_by_datestr(datestr)
        order_events = omap[event_primary_key];
        
        return order_events
        
        
    def find_primkeys(self, datestr):
        """Retrieves event primary keys belonging to the datestr
        
        Params
        ------
        
        datestr date string, for example 'YYYYMMDD'
        
        Returns
        -------
        list of event primary keys
        """
        
        event_primary_keys = []
        
        omap = self.find_by_datestr(datestr)
        for key in omap.keys():
            event_primary_keys.append(key)
        
        return event_primary_keys
        

    def find_order_event(self, datestr, event_primary_key, event_id):
        """Retrieves an order event
        
        Params
        ------
        
        datestr date string, for example 'YYYYMMDD'
        event_primary_key order event primary key long value
        event_id order event id long value 
        
        Returns
        -------
        order event
        """
        
        order_event = None
        
        omap = self.find_by_datestr(datestr)
        event_pk_list = omap[event_primary_key]
        for i in range(len(event_pk_list)):
            pk_event = event_pk_list[i]
            print(pk_event)
            if getattr(pk_event, 'event_id') == event_id:
                order_event = pk_event
                break
        
        return order_event
        


class OrderEvent:
    """Place __doc__ here"""
    
    col_tokens = [
        'timestamp', 'event_id', 'event_primary_key', 'instrument_name', 
        'event_type', 'exchange_id', 'num_shares', 'price_hund_tick', 
        'trade_side', 'fill_liquid_type', 'gateway_id', 'alpha', 'ask_ticks', 
        'bid_ticks', 'ioc', 'tick_size', 'tick_value', 'currency_factor', 
        'parent_spread_primary_key', 'strategy', 'time_milestoneA', 
        'time_milestoneB', 'time_milestoneC', 'time_milestoneD', 'time_milestoneE', 
        'packet_seq_num', 'source_exchange_id', 'exchange_order_id'
    ]
    
    type_map = {
        'timestamp': 'long', 'event_id': 'int', 'event_primary_key': 'int', 
        'instrument_name': 'str', 'event_type': 'enum', 'exchange_id': 'str', 
        'num_shares': 'int', 'price_hund_tick': 'int', 'trade_side': 'enum', 
        'fill_liquid_type': 'enum', 'gateway_id': 'str', 'alpha': 'double', 
        'ask_ticks': 'long', 'bid_ticks': 'long', 'ioc': 'enum', 
        'tick_size': 'double', 'tick_value': 'double', 
        'currency_factor': 'double', 'parent_spread_primary_key': 'int', 
        'strategy': 'str', 'time_milestoneA': 'long', 
        'time_milestoneB': 'long', 'time_milestoneC': 'long', 
        'time_milestoneD': 'long', 'time_milestoneE': 'long', 
        'packet_seq_num': 'long', 'source_exchange_id': 'str', 
        'exchange_order_id': 'str'
    }
    
    
    
    full_column_len = 28
    
    
    def __init__(self):
        print('OrderEvent() default contructor')
    
    """
    def __init__(self, order_event_id):
        self.order_event_id = order_event_id
    """
        
    @classmethod
    def to_dict(cls, order_event):
        """Returns a copy of the order event as a dictionary
        
        Params
        ------
        
        cls class object
        order_event order event
        """
        
        order_event_dict = {}
        
        for k, v in order_event.__dict__.items():
            order_event_dict[k] = v
            
        return order_event_dict
        
    @classmethod
    def to_order_event(cls, raw_data):
        """Returns raw data as OrderEvent object
        
        Params
        ------
        
        cls class object
        raw_data raw data list representing order event
        colnames column names column-delimited string
        """
        #col_tokens = colnames.split(',');
        
        print('to_order_event()', len(raw_data), len(cls.col_tokens), 
            len(cls.type_map))
        
        order_event = cls()
        order_event_attrs = []
        
        # col_tokens = colnames.split(',');
        for i in range(len(raw_data)):
            # TODO field_name
            event_element = cls.__astype(raw_data[i], 
                cls.type_map[cls.col_tokens[i]])
            # strip the last data element of any whitespace
            if i == (len(raw_data) - 1) and isinstance(raw_data[i], str):
                event_element = event_element.strip()
            setattr(order_event, cls.col_tokens[i], event_element)
            order_event_attrs.append(event_element)
            
        return order_event
        
    @classmethod
    def __astype(cls, data, type):
        """Returns data as specified data type
        
        Params
        ------
        
        cls class object
        data data being type cast
        """
        #print('__asType()', data, type)
        
        result = data
        
        if type == 'int' or type == 'long':
            result = int(data)
        elif type == 'float' or type == 'double':
            result = float(data)
        elif type == 'str' or type == 'enum':
            result = str(data)
        else:
            print("type not handled by method:", type)
            
        return result
        
        
    def __str__(self):
        return self._display_str()
        
            
    def __repr__(self):
        return self._display_str()
        
        
    def _display_str(self):
        display = ""

        str_display_template = ("OrderEvent "
            "'timestamp': {timestamp}, 'event_id': {event_id}, "
            "'event_primary_key': {event_primary_key}, "
            "'instrument_name': {instrument_name}, "
            "'event_type': {event_type}, "
            "'exchange_id': {exchange_id}, 'num_shares': {num_shares}, "
            "'price_hund_tick': {price_hund_tick}, "
            "'trade_side': {trade_side}, "
            "'fill_liquid_type': {fill_liquid_type}, "
            "'gateway_id': {gateway_id}, 'alpha': {alpha}, "
            "'ask_ticks': {ask_ticks}, 'bid_ticks': {bid_ticks}, "
            "'ioc': {ioc}, 'tick_size': {tick_size}, "
            "'tick_value': {tick_value}, "
            "'currency_factor': {currency_factor}, "
            "'parent_spread_primary_key': {parent_spread_primary_key}, "
            "'strategy': {strategy}, 'time_milestoneA': {time_milestoneA}, "
            "'time_milestoneB': {time_milestoneB}, "
            "'time_milestoneC': {time_milestoneC}, "
            "'time_milestoneD': {time_milestoneD}, "
            "'time_milestoneE': {time_milestoneE}, "
            "'packet_seq_num': {packet_seq_num}, "
            "'source_exchange_id': {source_exchange_id}, "
            "'exchange_order_id': {exchange_order_id}")
            
        full_column_len = 28
        
        if len(self.__dict__) == full_column_len:
            display = str_display_template.format(**self.__dict__)
        else:
            i = 0
            dict_len = len(self.__dict__)
            display += "OrderEvent "
            for key, val in self.__dict__.items():
                display += ("\'" + key + "\': ")
                display += str(val)
                if i < (dict_len - 1):
                    display += ", "
                    i += 1
            
        return display


class EventType(Enum):
    """Represents the event type"""
    
    NEW_OUT = 'n'
    MODIFY_OUT = 'm'
    CANCEL_OUT = 'c'
    MODIFY_IN = 'M'
    QTY_MODIFY_IN = 'Q'
    CANCEL_IN = 'C'
    CANCEL_REJ_IN = 'X'
    ACK_IN = 'a'
    ACK_TIMEOUT_IN = 'A'
    PARTIAL_FILL_IN = 'P'
    FILL_IN = 'F'
    NEW_ORDER_REJ_IN = 'D'
    MODIFY_REJ_IN = 'Y'
    CANCEL_TIMEOUT_IN = 'K'
    MODIFY_TIMEOUT_IN = 'J'
    

class TradeSide(Enum):
    """Represents what side of the trade the event is on (buy or sell)"""
    
    BUY = 'B'
    SELL = 'S'
    
    
class FillLiquidType(Enum):
    """Event liquidity in respect to market"""
    
    ADD = 'A'
    REMOVE = 'R'
    UNKNOWN = 'U'
    
    
class OrderMapUtils:
    """Utilities for order map"""

    @classmethod
    def order_map_to_dataframe(cls, order_map):
        """Order map to DataFrame"""
        
        order_map_index = cls.build_order_map_index(order_map)
        multi_index = pd.MultiIndex.from_tuples(
            order_map_index, names=('datestr','event_pk','event_id'))
        
        dk = list(order_map.keys())[0];
        pk = list(order_map[dk].keys())[0]
        colnames = order_map[dk][pk][0].__dict__.keys()
        
        order_map_list = cls.order_map_list(order_map)
            
        return pd.DataFrame(
            order_map_list, index=multi_index, columns=colnames).sort_index()
        
        
    @classmethod
    def dataframe_to_order_map(cls, df):
        """DataFrame to order map"""
        
        order_map = {}
        
        idx_dict = df.to_dict(orient='index')
        for key, val in idx_dict.items():
            if isinstance(key, str):
                idx_split = key.split(",")
                dk = idx_split[0]
                pk = int(idx_split[1])
            elif isinstance(key, tuple):
                dk = key[0]
                pk = key[1]
            if dk not in order_map:
                order_map[dk] = dict()
            if pk not in order_map[dk]:
                order_map[dk][pk] = list()
            order_event = OrderEvent();
            for attr_name in val.keys():
                setattr(order_event, attr_name, val[attr_name])
            order_map[dk][pk].append(order_event)
        
        return order_map
        
        
    @classmethod
    def order_events_to_dataframe(cls, event_list):
        """Order events list to DataFrame"""
        
        # TODO consider indexing this dataframe
        
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
                    order_map_index.append((dk, pk, event_id))
        
        return order_map_index
    
    
    @classmethod
    def _order_map_colnames(cls, order_map):
        dk = list(order_map.keys())[0];
        pk = list(order_map[dk].keys())[0]
        
        return order_map[dk][pk][0].__dict__.keys()
        
        

    
    
    
    

    

