import random1on1
import numpy as np

# TODO: Refactor this class to implement methods in random1on1.api.algorithm
random = np.random.default_rng()


def softmax(v):
    v -= v.min()
    return np.exp(v) / np.exp(v).sum()


class Participant:

    def __init__(self, num_people):
        self.meetings_counter = np.zeros(num_people)

    def increment_meetings_count(self, *other_participants):
        for other in other_participants:
            self.meetings_counter[other] += 1

    def sample_match(self, indices, gamma):
        meeting_counts = gamma * self.meetings_counter[indices]
        probabilities = softmax(meeting_counts)
        match = random.choice(indices, p=probabilities)
        return match


def generate_pairs(participants, gamma):
    unmatched = list(range(len(participants)))
    pairs = []
    while len(unmatched) > 1:
        index = random.choice(unmatched)
        unmatched.remove(index)
        participant = participants[index]
        match = participant.sample_match(unmatched, gamma)
        unmatched.remove(match)
        pairs.append([index, match])
    if len(unmatched) == 1:
        pairs[0].append(unmatched[0])
    return pairs


def main(num_people, num_iters, gamma):
    gamma = np.log(gamma)
    participants = [Participant(num_people) for _ in range(num_people)]
    for iteration in range(num_iters):
        pairs = generate_pairs(participants, gamma)
        for match in pairs:
            for index in match:
                participants[index].increment_meetings_count(
                    *filter(lambda i: i != index, match))
    for participant_no, participant in enumerate(participants):
        print("participant {}:".format(participant_no),
              participant.meetings_counter)
