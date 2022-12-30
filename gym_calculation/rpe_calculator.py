# https://articles.reactivetrainingsystems.com/2015/11/29/beginning-rts/
# https://www.rpecalculator.com/?

import numpy as np
import pandas as pd


prc = [
    1.000, 
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
    0.586
]


np.diff(prc)


rpe = pd.DataFrame({'rpe': np.flip(np.arange(1, 10.5, 0.5))})
#rpe['prc'] = prc[:len(rpe)]

max_reps = 5


rpe = np.flip(np.arange(0.5, 10.5, 0.5))
reps = {k: np.zeros(len(rpe)) for k in range(1, (max_reps + 1))}
rpe = {'rpe': rpe}
rpe.update(reps)
rpe = pd.DataFrame(rpe)
rpe

len_rpe = len(rpe)



# prc = {k: v for k, v in enumerate(prc)}
prc



for r in range(1, max_reps + 1):
    if r == 1:
        curr = prc[(r - 1):len_rpe]
        rpe[r] = curr
    else:
        curr = prc[((r - 1) * 2):(len_rpe + ((r - 1) * 2))]
        rpe[r] = curr

weight = 255
reps = 1
feels_like = 9.5


min_weight_inc = 1
assert min_weight_inc == 1 
# andra hur? window?



x = rpe.loc[rpe['rpe'] == feels_like,reps].iloc[0]
one_rm = (1 + (1 - x)) * weight
one_rm


round(rpe[reps] * one_rm)



round(rpe[5] * one_rm)


