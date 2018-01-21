import numpy as np

def unpack(N,t_max,backtrack):
    tags = [0 for j in xrange(N)]
    i = N
    while i > 0:
        tags[i-1] = t_max
        t_max = backtrack[t_max][i-1]
        i -= 1
    return tags


def run_viterbi(emission_scores, trans_scores, start_scores, end_scores):
    """Run the Viterbi algorithm.

    N - number of tokens (length of sentence)
    L - number of labels

    As an input, you are given:
    - Emission scores, as an NxL array
    - Transition scores (Yp -> Yc), as an LxL array
    - Start transition scores (S -> Y), as an Lx1 array
    - End transition scores (Y -> E), as an Lx1 array

    You have to return a tuple (s,y), where:
    - s is the score of the best sequence
    - y is a size N array of integers representing the best sequence.
    """

    L = start_scores.shape[0]
    assert end_scores.shape[0] == L
    assert trans_scores.shape[0] == L
    assert trans_scores.shape[1] == L
    assert emission_scores.shape[1] == L
    N = emission_scores.shape[0]

    emission_scores = np.array(emission_scores).T.tolist()
    #print emission_scores
    y = []
    #for i in xrange(N):
        # stupid sequence
        #y.append(i % L)
    # score set to 0
    values = [[-np.inf for i in xrange(N+1)] for j in xrange(L)]
    backtrack = [[0 for i in xrange(N + 1)] for j in xrange(L)]

    for t in range(0,L):
        values[t][0] = start_scores[t] + emission_scores[t][0]

    for i in range(1,N):
        for j in range(0,L):
            for k in range(0,L):
                tmp = values[k][i-1] + trans_scores[k][j]
                if tmp > values[j][i]:
                    values[j][i] = tmp
                    backtrack[j][i] = k
            values[j][i] += emission_scores[j][i]

    for j in range(0, L):
        values[j][N] = values[j][N - 1] + end_scores[j]
        backtrack[j][N] = j

    t_max = -np.inf
    vit_max = -np.inf

    for t in range(0,L):
        if values[t][N] > vit_max:
            t_max = t
            vit_max = values[t][N]
    return(vit_max, unpack(N,t_max,backtrack))


