__author__ = "Christian Dewey"
__date__ = "2025 January 25"
__version__ = "0.0.1"

import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import LinearRegression


class Background:

    @staticmethod
    def subtract_postedge(mu, E, post_edge_range_E):
        
        post_edge_condition = np.where((E>post_edge_range_E[0]) & (E<post_edge_range_E[1]))

        bg_model = LinearRegression()
        bg_model.fit(E[post_edge_condition].reshape(-1,1), mu[post_edge_condition])
        bg_function = bg_model.predict(E[post_edge_condition].reshape(-1,1))

        plt.plot(E, mu)
        plt.plot(E[post_edge_condition], bg_function)
        plt.show()

        mu_bg = mu.copy()
        mu_bg[post_edge_condition] = mu_bg[post_edge_condition] - bg_function + mu[post_edge_condition][0]
        #plt.plot(E, mu_bg)
        #plt.show()

        return mu_bg
    
    @staticmethod
    def subtract_preedge(mu, E, pre_edge_range_E):
        
        pre_edge_condition = np.where((E>pre_edge_range_E[0]) & (E<pre_edge_range_E[1]))

        bg_model = LinearRegression()
        bg_model.fit(E[pre_edge_condition].reshape(-1,1), mu[pre_edge_condition])
        bg_function = bg_model.predict(E[pre_edge_condition].reshape(-1,1))

        plt.plot(E, mu)
        plt.plot(E[pre_edge_condition], bg_function)
        plt.show()

        mu_bg = mu.copy()
        mu_bg[pre_edge_condition] = mu_bg[pre_edge_condition] - bg_function + mu[pre_edge_condition][0]
        #plt.plot(E, mu_bg)
        #plt.show()

        return mu_bg