"""
This script will simulate a strategy of entering once a condition
has been met and exiting once another has been met and
will show a graph of the result and different measures
"""

#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt
from datetime import date 

from strategy import Strategy 


#===============================================================================
# CLASSES
#===============================================================================
class Simulation():
    """
    Class that will store all data and functions related to a simulation
    """
    def __init__(self, symbol, from_date=None, to_date=None):
        """
        If dates not entered it will take a default to determine ######### TODO
        """
        self.symbol = symbol
        self.from_date = from_date
        self.to_date = to_date
        self.df_prices = pd.DataFrame()
        self.open = None # Price of current open trade
        self.close = None # Price of current closed trade
        self.status = 'out' # 'out' not invested, 'in' invested
        self.signal = False  # It will get records in which the signal activates
        self.max_open = 0.0 # Max individual investment (for % profit calculation)
        ### Measures
        self.nperiods = 0
        self.ntrades = 0
        self.abs_profit = 0.0 # Accumulated abs_profit ($ value gained/loss)
#         self.pct_simple_profit = 0.0 # Profit over max investment (without reinvestment)
        self.pct_compound_profit = 1.0 # Profit over max investment (with reinvestment)
#         self.pct_annual_simple_profit = 0.0 # Annualized simple profit
#         self.pct_annual_compound_profit = 0.0 # Annualized compound profit
        self.volatility = 0.0 # Volatility of returns (annualized)
        self.sharpe = 0.0 # Sharpe ratio (Rf = 0)
        self.drawdown = 0.0 # It will store the worst abs_profit
        
        ### Years calculation
        d_from_date = date(int(from_date[0:4]), int(from_date[4:6]), int(from_date[6:8]))
        d_to_date = date(int(to_date[0:4]), int(to_date[4:6]), int(to_date[6:8]))
        self.years = (d_to_date-d_from_date).days/365.0
        self.profit_trades = []
        
    def get_prices_yahoo(self):
        """
        It get prices data from yahoo
        """
        try:
            self.df_prices = DataReader(self.symbol, "yahoo", self.from_date,
                                              self.to_date)
            
            self.df_prices['pct Adj Close'] = self.df_prices.pct_change()['Adj Close'] 
            
            
        except Exception, e:
            print e
            raise 
        
        
    def apply_strategy(self, strategy):
        """
        It will apply the selected strategy to this simulation.
        Strategy in this case is a class with all the information it requires
        """
        # 1. Loop through all the prices
        count = 0
        status = 'out'
        prevclose = self.df_prices.ix[0]['Adj Close']
        df_result = pd.DataFrame()
        s_record = pd.Series()
        change=0.0
        pct_profit_temp = 0.0
        self.nperiods = len(self.df_prices.index)-1
        for day in self.df_prices[1:].iterrows():
            ###### TODO: See ways of generalized for different strategies###################################################################
            ###### Depending on the strategy it should count ones or others ###############################################################
            
            currclose = day[1]['Adj Close']
            change = (currclose - prevclose)/prevclose * 100
            # 2. Counting and testing 
            if self.status == 'out':
                if currclose < prevclose:
                    count += 1
                    if count == strategy.ndowns:
                        self.open_trade(currclose)
                        count = 0
                else:
                    count = 0
                    
            if self.status == 'in':
                pct_profit_temp += change
                if currclose > prevclose:
                    self.close_trade(currclose, pct_profit_temp)
                    pct_profit_temp = 0.0
            
            # 3. Log
            s_record["date"]=day[0]
            s_record["price"]=str(currclose)
            s_record["change"]=change
            s_record["status"]=self.status
            s_record["abs_profit"]=self.abs_profit
            s_record["signal"]=self.signal
            df_result = df_result.append(s_record, ignore_index=True)
            columns = ['date', 'price', 'change', 'status', 'abs_profit', 'signal']
            df_result = df_result[columns]
            
            prevclose = currclose
            self.signal = False
            
            
        # 3. Print result
#         print "The result is:" + str(self.abs_profit)
#         print "The log is:"
#         print df_result
        
                
            
    def open_trade(self, open):
        self.open = open
        if self.open > self.max_open:
            self.max_open = self.open 
        self.status = 'in'
        self.signal = True
        
    def close_trade(self, close, pct_profit_trade):
        self.close = close
        self.abs_profit += self.close - self.open 
        self.pct_compound_profit = np.sqrt((1+self.pct_compound_profit)*(1+pct_profit_trade)) - 1.0
        self.status = 'out'
        self.ntrades += 1
        self.profit_trades.append(pct_profit_trade)
        if self.abs_profit < self.drawdown:   # Calculation of drawdown
            self.drawdown = self.abs_profit 
        
    def get_result(self):
        s_result = pd.Series()
        s_result['abs_profit'] = self.abs_profit 
        s_result['drawdown'] = self.drawdown
        s_result['max_open'] = self.max_open
        s_result['pct_simple_profit'] = self.abs_profit / self.max_open 
        s_result['pct_compound_profit'] = self.pct_compound_profit
        s_result['annual_pct_simple_profit'] = (1+s_result['pct_simple_profit'])**self.years-1
        s_result['annual_pct_compound_profit'] = (1+s_result['pct_compound_profit'])**self.years-1
        s_result['volatility'] = np.std(self.profit_trades) * (1/self.years)**(1/2) # Annual volatility
        s_result['sharpe'] = s_result['annual_pct_simple_profit'] / s_result['volatility']
        print s_result['sharpe']
        return s_result
    
    def save_result(self):
        writer = pd.ExcelWriter("test_simulation.xlsx")
        df_result.to_excel(writer,"simulation")

#===============================================================================
# FUNCTIONS
#===============================================================================



#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    strategy = Strategy()
    strategy.post_open_conditions(ndowns = 4)
    strategy.post_close_conditions(nups = 1)
    sim = Simulation("SPY", from_date='20050101', to_date='20120612')
    sim.get_prices_yahoo()
    sim.apply_strategy(strategy)
    s_result = sim.get_result()
    print s_result 