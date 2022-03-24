import argparse

from scipy.special import softmax
import numpy as np

from random import choices

class Participant:

    def __init__(self, num_people, gamma=1/np.e):
        self.num_people = num_people
        self.meetings_counter = np.zeros(num_people)
        self.log_gamma = np.log(gamma)

    def increment_hits(self, j):
        self.meetings_counter[j] += 1
    
    def sample_match(self, indices):
        feas = self.log_gamma*self.meetings_counter[indices]
        probabilities = softmax(feas)
        match = choices(indices, probabilities, k=1).pop()
        return match

def generate_pairs(participants):
    unmatched = list(range(len(participants)))
    pairs = []
    while len(unmatched)>1:
        index = np.random.choice(unmatched)
        unmatched.remove(index)
        p = participants[index]
        match = p.sample_match(unmatched)
        unmatched.remove(match)
        pairs.append([index, match])
    if len(unmatched)==1:
        pairs[0].append(unmatched[0])
    return pairs

# sampling first person based on stuff
def main(num_people, num_iters, gamma):
    participants = [Participant(num_people, gamma=gamma) for k in range(num_people)]
    for i in range(num_iters):
        pairs = generate_pairs(participants)
        for i,j in pairs:
            participants[i].increment_hits(j)
            participants[j].increment_hits(i)
    print("average hit/person:", num_iters/(num_people-1))
    for i,q in enumerate(participants):
        p = q.meetings_counter
        print("person {}:".format(i), p)

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
    args = vars(parser.parse_args())
    main(**args)
