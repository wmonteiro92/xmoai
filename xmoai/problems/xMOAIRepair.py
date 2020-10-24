# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 21:36:28 2020

@author: wmonteiro92
"""

import random
import numpy as np
from pymoo.model.repair import Repair

class xMOAIRepair(Repair):
    def __init__(self, X_current, max_changed_vars, categorical_columns,
                 integer_columns, immutable_column_indexes):
        """Class constructor.
        
        
        :param X_current: the individual generated by the optimization algorithm
            to be evaluated
        :type X_current: numpy.array
        :param max_changed_vars: the maximum number of attributes to be
            modified
        :type max_changed_vars: Integer
        :param categorical_columns: dictionary containing the categorical columns
            and their allowed values. The keys are the i-th position of the indexes
            and the values are the allowed categories. The minimum and maximum categories
            must respect the values in lower_bounds and upper_bounds since this variable
            is called after it in code.
        :type categorical_columns: dict
        :param integer_columns: lists the columns that allows only integer values.
            It is used by xMOAI in rounding operations.
        :type integer_columns: numpy.array
        :param immutable_column_index: lists columns that are not allowed to
            be modified.
        :type immutable_column_index: numpy.array
        """
        self.X_current = X_current.flatten()
        self.n_var = self.X_current.shape[0]
        self.max_changed_vars = max_changed_vars
        self.categorical_columns = categorical_columns
        self.integer_columns = integer_columns
        self.immutable_column_indexes = immutable_column_indexes
    
    def _do(self, problem, pop, **kwargs):
        """Checks and fixes an individual based on the xMOAI rules.
    
        :param problem: the optimization problem
        :type problem: xMOAIProblem
        :param pop: the individuals to be evaluated
        :type pop: numpy.array
        
        :return: the individuals fixed considering the xMOAI rules
        :rtype: np.array
        """
        for k in range(len(pop)):
            x = pop[k].X
            
            # keeping the immutable indexes
            x[self.immutable_column_indexes] = self.X_current[self.immutable_column_indexes]
            
            # checking categorical values
            for col in self.categorical_columns:
                available_values = self.categorical_columns[col]
                if x[col] not in available_values:
                    x[col] = available_values[np.abs(available_values-x[col]).argmin()]
                    
            # rounding integer columns
            for col in self.integer_columns:
                try:
                    x[col] = int(np.round(x[col]))
                except:
                    x[col] = 0
                    
            # checking the constraint g1
            diff = self.X_current - x
            
            # checking if more variables than needed were changed
            # if affirmative, some of them will be reset to their original values
            modifiable_columns = set(range(self.n_var)) - \
                set(np.where(diff == 0)[0]) - \
                set(self.immutable_column_indexes)
                
            vars_to_equal = np.count_nonzero(diff) - self.max_changed_vars
            
            if vars_to_equal > 0:
                indexes_to_equal = random.sample(modifiable_columns, k=vars_to_equal)
                x[indexes_to_equal] = self.X_current[indexes_to_equal]
        return pop