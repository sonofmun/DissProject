__author__ = 'matt'

def randomizer(l):
    """Takes a list of words as input, randomizes the list 1000 times,
    and returns the randomized list.
    """
    from numpy.random import shuffle
    [shuffle(l) for x in range(1000)]
    return l
