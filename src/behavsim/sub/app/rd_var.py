import scipy.stats as stats


# Defines the norm function.
def norm(mu, sigma, flag, trunc_neg=-3, trunc_pos=3):
    
    # Computes a random normal variable.
    rv = stats.truncnorm.rvs(trunc_neg, trunc_pos, loc=mu, scale=sigma)
    
    # Continues only of flag is True.
    if flag:
        
        # Transforms the random variable into an integer.
        rv = int(round(rv))
        
    # Returns the random variable.  
    return rv


# Defines the uni function.
def uni(start, length, flag):
    
    # Computes a random uniform variable.
    rv = stats.uniform.rvs(loc=start, scale=length, size=1)
    
    # Continues only of flag is True.
    if flag:
        
        # Transforms the random variable into an integer.
        rv = int(round(rv))
    
    # Returns the random variable. 
    return rv
