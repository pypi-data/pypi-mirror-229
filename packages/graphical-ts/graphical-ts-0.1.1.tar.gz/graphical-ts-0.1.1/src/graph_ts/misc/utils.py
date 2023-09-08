import numpy as np
from stochastic.processes import continuous


def to_camel_case(s):
    s = s.replace("-", " ")  # replace "-" with space
    words = s.split()  # split string into words
    words = [word.capitalize() for word in words]  # capitalize each word
    return "".join(words)  # join words without space

def identity(x):
    return x

def bound_it(x, scale, up, low):
    return scale * ((x>low) and (x<up))

def step2sawtooth(x, height):
    dx = np.where(np.diff(x)==1.0)[0] + 1
    incremental_seq = np.hstack([
        np.arange(1, b-a+1) for a, b in 
        zip([0] + dx.tolist(), dx.tolist() + [len(x)])
    ])
    y = x.copy()
    y[x == 1] = incremental_seq[x == 1]
    return height*y

def scale(x, scl):
    return scl*x

def constant_signal(ts, height):
    return np.ones_like(ts)*height

def bessel_process(ts):
    return continuous.BesselProcess().sample_at(ts)

def mfbm(ts):
    return continuous.MultifractionalBrownianMotion(t=max(ts)).sample(len(ts)-1)


def uniform_discrete(ts, values, trans_freq=0.008, start_val=None, end_val=None, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    
    n_trans = max(round(len(ts)*trans_freq), 1)
    
    trans_pt = np.sort(rng.choice(ts, size=n_trans, replace=False))
    
    trans_v = rng.choice(values, size=n_trans-1)
    
    if start_val is None:
        start_val = rng.choice(values, 1)
    
    if end_val is None:
        end_val = rng.choice(values, 1)
        
    trans_v = np.concatenate([start_val, trans_v, end_val])
    
    result = np.zeros_like(ts)
    for i in range(n_trans):
        start_idx = 0 if i == 0 else trans_pt[i-1]
        result[start_idx:trans_pt[i]] = trans_v[i]
        
    return result