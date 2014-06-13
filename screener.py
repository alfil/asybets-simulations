"""
This script will check if there are signals for different 
strategies in a group of securities
"""

#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt
import datetime as dt

import excel_management as excel

from strategy import Strategy 


#===============================================================================
# CLASS: INDIVIDUAL SCREENER (Only 1 security)
#===============================================================================
class Individual_screener():
    """
    This class will store the relevant information and functions for the 
    signal detection of entry points of one Strategy in one Security
    """
    def __init__(self, symbol, to_date=dt.datetime.today()):
        self.symbol = symbol
        self.to_date = to_date  
        self.from_date = self.to_date.replace(to_date.year - 1)
        self.signal = False
    
        self.get_prices_yahoo()
        
    def get_prices_yahoo(self):
        """
        It get prices data from yahoo (last year)
        """
        try:
            self.df_prices = DataReader(self.symbol, "yahoo", self.from_date,
                                              self.to_date)
            
            self.df_prices['pct Adj Close'] = self.df_prices.pct_change()['Adj Close'] 
            
            
        except Exception, e:
            print e
            raise 
    
    
    def check_signal(self, strategy):
        """"
        It will check if the conditions for this strategy are met in the specified
        date (by default the date in which is run) 
        """
        # 1. Check last returns to see how many downs in a row
        ndowns = 0
        for day in self.df_prices[-strategy.ndowns:].iterrows():
            ###### TODO: See ways of generalized for different strategies###################################################################
            ###### Depending on the strategy it should count ones or others ###############################################################
            
            # 2. If one of the returns is positive => No signal
            if day[1]['pct Adj Close'] < 0:
                ndowns += 1
            else:
                break
        
        if ndowns == strategy.ndowns:
            self.signal = True
        

#===============================================================================
# CLASS: COLLECTIVE SCREENER (List of securities)
#===============================================================================
class Collective_screener():
    """
    It will launch a collective checking of the signal of an strategy
    """
    def __init__(self, strategy, to_date=dt.datetime.today()):
        # 1. Parameters
        self.strategy = strategy
        self.to_date = to_date
        self.df_results = pd.DataFrame()
        
        # 2. Get Excel with Stocks to simulate
        self.filename = excel.select_excel_file()

        # 3. Save in Dataframe of the stocks to simulate
        xl = pd.ExcelFile(self.filename)
        self.symbols = xl.parse('input')
        
        # 4. Process Screeners
        self.process_screeners()
        
        # 5. Save the result
        self.save_result()
        
        
    def process_screeners(self):
        """
        This function will iterate over all the securities and check
        if a signal is triggered
        """
        s_result = pd.Series()
        for row in self.symbols.iterrows():
            symbol = row[1]['symbol']
            print 'processing: ' + str(symbol)
            ind_screener = Individual_screener(symbol)
            ind_screener.check_signal(self.strategy)
            s_result['symbol'] = symbol
            s_result['signal'] = ind_screener.signal
            self.df_results = self.df_results.append(s_result, ignore_index=True)

    def save_result(self):
        """
        It will save the result in a new tab of the same excel file
        called Signals
        """
        self.df_results = self.df_results[['symbol', 'signal']]
        excel.save_in_new_tab_of_excel(self.filename, self.df_results, 'Signals')
        
        





#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    
    #===========================================================================
    # STRATEGY (common for individual and collective)
    #===========================================================================
    strategy = Strategy()
    strategy.post_open_conditions(ndowns = 4)
    strategy.post_close_conditions(nups = 1)
    
    #===========================================================================
    # INDIVIDUAL unit test
    #===========================================================================
#     ind_screener = Individual_screener("RWX")
#     ind_screener.check_signal(strategy)
#     print ind_screener.signal 
    
    #===========================================================================
    # COLLECTIVE unit test
    #===========================================================================
    col = Collective_screener(strategy)
        









