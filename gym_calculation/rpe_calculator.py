# https://articles.reactivetrainingsystems.com/2015/11/29/beginning-rts/


import numpy as np
import pandas as pd


prc = [1.000, 
0.978, 
0.955, 
0.939, 
0.922, 
0.907, 
0.892, 
0.878, 
0.863, 
0.850, 
0.837, 
0.824, 
0.811, 
0.799,
0.786, 
0.774, 
0.762, 
0.751, 
0.739, 
0.723, 
0.707, 
0.694, 
0.680, 
0.667, 
0.653, 
0.640, 
0.626, 
0.613, 
0.599, 
0.586, 
]


np.diff(prc)


rpe = pd.DataFrame({'rpe': np.flip(np.arange(1, 10.5, 0.5))})
rpe['prc'] = prc[:len(rpe)]

max_reps = 8

