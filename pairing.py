import argparse

from scipy.special import softmax
import numpy as np

from random import choices

class CollisionCounter:

    def __init__(self, num_people, gamma=1/np.e):
        self.num_people = num_people
        self.collission_counter = np.zeros(num_people)
        self.log_gamma = np.log(gamma)

    def increment_hits(self, j):
        self.collission_counter[j] += 1
    
    def sample_match(self, feasible):
        feas = self._log_gamma*self._collission_counter[feasible]
        probabilities = softmax(feas)
        match = choices(feasible, probabilities, k=1).pop()
        return match

def generate_pairs(meeting_counts, num_people):
    feasible = list(range(num_people))
    pairs = []
    while len(feasible) != 0:
        index = np.random.choice(feasible)
        feasible.remove(index)
        cc = meeting_counts[index]
        match = cc.sample_match(feasible)
        feasible.remove(match)
        pairs.append((index, match))
    return pairs

def generate_circuit(meeting_counts, num_people):
    feasible = list(range(num_people))
    pairs = []
    start = np.random.choice(feasible)
    index = start
    while len(feasible) > 1:
        feasible.remove(index)
        cc = meeting_counts[index]
        match = cc.sample_match(feasible)
        pairs.append((index, match))
        index = match
    pairs.append((index,start))
    return pairs

# sampling first person based on stuff
def main(num_people, num_iters, gamma, circuit):
    meeting_counts = [CollisionCounter(num_people, gamma=gamma) for k in range(num_people)]
    for i in range(num_iters):
        if circuit:
            pairs = generate_circuit(meeting_counts, num_people)
        else:
            pairs = generate_pairs(meeting_counts, num_people)
        for i,j in pairs:
            meeting_counts[i].increment_hits(j)
            meeting_counts[j].increment_hits(i)
    print("average hit/person:",
            (2 if circuit else 1)*num_iters/(num_people-1))
    for i,q in enumerate(meeting_counts):
        cc = q.collision_counter()
        print("person {}:".format(i), cc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='plot example data')
    parser.add_argument('num_people',
                        type=int,
                        help='number of participants')
    parser.add_argument('--gamma',
                        '-g',
                        type=float,
                        default=1/np.e,
                        help='decay factor')
    parser.add_argument('--num_iters',
                        '-n',
                        type=int,
                        default=10,
                        help='number of iterations')
    parser.add_argument('--circuit',
                        '-c',
                        default=False,
                        action='store_true',
                        help='simulate circuit')
    args = vars(parser.parse_args())
    main(**args)
