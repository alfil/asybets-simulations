"""
This script will launch simulations for different strategies
for different stocks/ETFs and will return an excel file
with their results in order to further analize them
"""
#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt

import excel_management as excel

from strategy import Strategy 
from simulation import Simulation

#===============================================================================
# CLASSES
#===============================================================================
class Collective_simulation():
    """
    This class will store the relevant information for a Collective Simulation
    and the functions that will operate it
    """
    def __init__(self, strategy, from_date='20000101', to_date='20140610'):
        # 1. Parameters
        self.strategy = strategy
        self.from_date = from_date
        self.to_date = to_date
        self.df_results = pd.DataFrame()
        
        # 2. Get Excel with Stocks to simulate
        self.filename = excel.select_excel_file()
        
        
        # 3. Save in Dataframe of the Stocks to simulate
        xl = pd.ExcelFile(self.filename)
        self.symbols = xl.parse('input')
        print self.symbols
        
    def process_simulations(self):
        """
        This function will iterate over all the symbols and simulate the 
        strategy.
        """
        for row in self.symbols.iterrows():
            
            symbol = row[1]['symbol']
            print 'processing ' + str(symbol)
            sim = Simulation(symbol, from_date=self.from_date, to_date=self.to_date)
            sim.get_prices_yahoo()
            sim.apply_strategy(self.strategy)
            s_result = sim.get_result()
            s_result['symbol']=symbol
            self.df_results = self.df_results.append(s_result, ignore_index=True)
        
    def save_result(self):
        """
        It will save the result in a new tab of the same excel file
        called Results
        """
        excel.save_in_new_tab_of_excel(self.filename, self.df_results, 'Results')
        
        
#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    strategy = Strategy()
    strategy.post_open_conditions(ndowns = 4)
    strategy.post_close_conditions(nups = 1)
    col = Collective_simulation(strategy)
    col.process_simulations()
    col.save_result()