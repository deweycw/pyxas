__author__ = "Christian Dewey"
__date__ = "2025 January 25"
__version__ = "0.0.1"

import numpy as np
import matplotlib.pyplot as plt
import os

from pyxas.background import Background 
class Scan:

    def __init__(self, data_file):

        self.data_file = data_file

        self.load_scan()

        self.summed_SCA1 = self._sum_det_element_counts( 'SCA1')
        self.summed_SCA2 = self._sum_det_element_counts( 'SCA2')
        self.summed_ICR = self._sum_det_element_counts( 'ICR')

    def load_scan(self):

        columns = {}
        data = []

        with open(self.data_file) as f:
            
            col_i = 0
            line_number = 1

            for line in f:
                
                if (line_number > 19) and (line_number <= 125):
                    columns[line.strip()] = col_i
                    col_i += 1
                
                if line_number >= 127:
                    holder = [float(j) for j in line.split()]
                    data.append(holder)
                
                line_number += 1

        self.data_array = np.asarray(data)
        self.columns = columns
        self.ind_cols = {columns[i]:i for i in columns.keys()}


    def _get_count_cols(self, count_type):

        count_cols = []

        for col_name, col_i in self.columns.items():
            
            if count_type in col_name:
                count_cols.append(col_i)

        return  count_cols


    def _sum_det_element_counts(self, count_type):

        count_cols = self._get_count_cols(count_type)  
        
        subset = self.data_array[:,count_cols[0]:count_cols[-1]]

        summed_counts = subset.sum(axis=1)

        return summed_counts
        

    def plot_mu(self, title = None):
        fig, ax = plt.subplots()
        E = self.data_array[:,self.columns['Requested Energy']]
        I0 = self.data_array[:,self.columns['I0']]
        mu = self.summed_SCA1 / I0
        ax.plot(E, mu)
        if title != None:
            ax.set_title(title)
        plt.show()


    def plot_each_channel(self, count_type = 'SCA1'):

        count_cols = self._get_count_cols(count_type)  
        E = self.data_array[:,self.columns['Requested Energy']]
        I0 = self.data_array[:,self.columns['I0']]

        for i in count_cols:
            
            fig, ax = plt.subplots()
            ax.plot(E, self.data_array[:,i] / I0)
            ax.set_title(self.ind_cols[i])
            plt.show()

    
    def drop_bad_channels(self, channels_to_drop = []):

        bad_channels_inds = [self.columns[c] for c in channels_to_drop]
        self.data_array = np.delete(self.data_array, bad_channels_inds, axis=1)

        for bad_channel in channels_to_drop:

            i_drop = self.columns[bad_channel]

            del self.columns[bad_channel]
            del self.ind_cols[i_drop]


    def plot_SN(self, count_type = 'SCA1', title = '', n_scans = [4], E_plotting_range = (7135,8000)):

        count_cols = self._get_count_cols(count_type)  
        
        self.element_signal_array = self.data_array[:,count_cols[0]:count_cols[-1]]

        self.scan_E = self.data_array[:,self.columns['Requested Energy']]
        self.scan_I0 = self.data_array[:,self.columns['I0']]
        self.scan_signal_std_by_element = self.element_signal_array.copy()

        I0 = self.data_array[:,self.columns['I0']]
        self.scan_signal_std = np.std(self.element_signal_array, axis =1) #/ I0

        mu = np.average(self.summed_SCA1 )    
        sn_1 = mu / self.scan_signal_std 

        E_range = np.where((self.scan_E > E_plotting_range[0]) & (self.scan_E < E_plotting_range[1]))

        n_plots = len(n_scans) + 1
        n_scans = [1] + n_scans
        for n in n_scans:
            plt.plot(self.scan_E[E_range], sn_1[E_range] * np.sqrt(n+1), label = n)
            plt.title(title)
            plt.ylabel('S/N')
            plt.xlabel('E (eV)')
        plt.legend(title = '# Scans', frameon = False)
        
        plt.show()


class ScanGroup(Scan):

    def __init__(self, directory = None, base_name = None):

        self.directory = directory
        self.base_name = base_name

        self.grouped_files = [f for f in os.listdir(directory) if base_name in f]
        self.grouped_files = sorted(self.grouped_files)    

        self.mu_bg_subtracted = [] 

        self.load_scans()

    
    def load_scans(self):
        
        grouped_scans = {}

        for f in self.grouped_files:

            grouped_scans[f] = Scan(data_file = self.directory + f)

        self.grouped_scans = grouped_scans


    def drop_bad_channels(self, channels_to_drop=[]):
        
        for file, scan in self.grouped_scans.items():

            scan.drop_bad_channels(channels_to_drop)

    
    def average_scans(self):

        summed_data = []

        for file, scan in self.grouped_scans.items():

            summed = scan.summed_SCA1 / scan.data_array[:,scan.columns['I0']]
            
            summed_data.append(summed)

        stacked_data = np.column_stack(summed_data)
        self.mu_average = np.average(stacked_data, axis = 1)
        self.mu_std = np.std(stacked_data, axis =1)
        self.E = scan.data_array[:,scan.columns['Requested Energy']]
        
    
    def plot_averaged_mu(self):

        fig, ax = plt.subplots()
        ax.plot(self.E, self.mu_average)
        ax.plot(self.E, self.mu_average + self.mu_std, 'C1', linewidth = 1, alpha = 0.5)
        ax.plot(self.E, self.mu_average - self.mu_std, 'C1', linewidth = 1, alpha = 0.5)
        ax.set_title(self.base_name.replace('.',''))
        plt.show()

    def subtract_preedge(self, pre_edge_range_E):

        if len(self.mu_bg_subtracted) == 0:   
            self.mu_bg_subtracted = self.mu_average.copy()

        self.mu_bg_subtracted = Background.subtract_preedge(self.mu_bg_subtracted, self.E, pre_edge_range_E=pre_edge_range_E)

    def subtract_postedge(self, post_edge_range_E):
        
        if len(self.mu_bg_subtracted) == 0:   
            self.mu_bg_subtracted = self.mu_average.copy()
        
        self.mu_bg_subtracted = Background.subtract_postedge(self.mu_bg_subtracted, self.E, post_edge_range_E=post_edge_range_E)

    def plot_background_subtracted_mu(self):

        fig, ax = plt.subplots()
        ax.plot(self.E, self.mu_bg_subtracted)
        ax.plot(self.E, self.mu_average)
        ax.set_title(self.base_name.replace('.',''))
        plt.show()


    def plot_SN_n_scans(self, n_scans):
        
        scans = list(self.grouped_scans.values())
        files = list(self.grouped_scans.keys())

        scans[0].plot_SN(title = files[0].split('.')[0], n_scans = n_scans, count_type = 'SCA1')
            

