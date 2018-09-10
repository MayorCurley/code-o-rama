"""Prognos Orders module

This module reads an exchange log file into a dictionary for easy data 
retrieval.
"""

#import numpy as np
import os
from enum import Enum

class Orders:
    """Place __doc__ here"""

    def __init__(self):
        """Constructor for Orders object"""
        self.order_map = {}
        #self.order_events = {}
        
    def load_dir(self, dirname):
        """Loads order log files found in containing directory"""
        print('load_dir()', dirname)
        if os.path.isdir(dirname):
            file_list = os.listdir(dirname)
            for i in range(len(file_list)):
                path_filename = os.path.join(dirname, file_list[i])
                print('processing ' + path_filename)
                self.load_file(path_filename)
                
        else:
            print(dirname + ' is not a directory')
            

    def load_file(self, filename, delimiter='\t'):
        """Loads order log file into maps for data access"""
        print('You rang load_file()?')
        
        # TODO parse date string key from filename 
        # dummyDateStr = "20180831"
        filebase = os.path.basename(filename)
        dateStr = os.path.splitext(filebase)[0]
        print(dateStr)
        
        
        # setup order line position dictionary
        print('ol_pos')
        ol_pos = {}
        # TODO
        #col_tokens = colnames.split(',');
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
            
        print('load_file() complete')
        
    
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
        return ("OrderEvent "
            "'timestamp': {timestamp}, 'event_id': {event_id}, "
            "'event_primary_key': {event_primary_key}, "
            "'instrument_name': {instrument_name}, 'event_type': {event_type}, "
            "'exchange_id': {exchange_id}, 'num_shares': {num_shares}, "
            "'price_hund_tick': {price_hund_tick}, 'trade_side': {trade_side}, "
            "'fill_liquid_type': {fill_liquid_type}, "
            "'gateway_id': {gateway_id}, 'alpha': {alpha}, "
            "'ask_ticks': {ask_ticks}, 'bid_ticks': {bid_ticks}, "
            "'ioc': {ioc}, 'tick_size': {tick_size}, "
            "'tick_value': {tick_value}, 'currency_factor': {currency_factor}, "
            "'parent_spread_primary_key': {parent_spread_primary_key}, "
            "'strategy': {strategy}, 'time_milestoneA': {time_milestoneA}, "
            "'time_milestoneB': {time_milestoneB}, "
            "'time_milestoneC': {time_milestoneC}, "
            "'time_milestoneD': {time_milestoneD}, "
            "'time_milestoneE': {time_milestoneE}, "
            "'packet_seq_num': {packet_seq_num}, "
            "'source_exchange_id': {source_exchange_id}, "
            "'exchange_order_id': {exchange_order_id}").format(**self.__dict__)
            
            
    def __repr__(self):
        return ("OrderEvent "
            "'timestamp': {timestamp}, 'event_id': {event_id}, "
            "'event_primary_key': {event_primary_key}, "
            "'instrument_name': {instrument_name}, 'event_type': {event_type}, "
            "'exchange_id': {exchange_id}, 'num_shares': {num_shares}, "
            "'price_hund_tick': {price_hund_tick}, 'trade_side': {trade_side}, "
            "'fill_liquid_type': {fill_liquid_type}, "
            "'gateway_id': {gateway_id}, 'alpha': {alpha}, "
            "'ask_ticks': {ask_ticks}, 'bid_ticks': {bid_ticks}, "
            "'ioc': {ioc}, 'tick_size': {tick_size}, "
            "'tick_value': {tick_value}, 'currency_factor': {currency_factor}, "
            "'parent_spread_primary_key': {parent_spread_primary_key}, "
            "'strategy': {strategy}, 'time_milestoneA': {time_milestoneA}, "
            "'time_milestoneB': {time_milestoneB}, "
            "'time_milestoneC': {time_milestoneC}, "
            "'time_milestoneD': {time_milestoneD}, "
            "'time_milestoneE': {time_milestoneE}, "
            "'packet_seq_num': {packet_seq_num}, "
            "'source_exchange_id': {source_exchange_id}, "
            "'exchange_order_id': {exchange_order_id}").format(**self.__dict__)


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
    
    
    
    

    

