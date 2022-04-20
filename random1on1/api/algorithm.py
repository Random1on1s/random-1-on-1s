from abc import ABC
from abc import abstractmethod

from networkx import Graph
from numpy.random import default_rng

from random1on1.api.pairings import Pairings


class MatchingAlgorithm(ABC):
    """
    MatchingAlgorithm provides an abstract framework for running matching algorithms. Every algorithm needs a few things in order
    to be considered valid for the random 1 on 1 bot:
      - an initialization method with some validations on the graph of possible participants
      - a method to generate pairings
    TODO: Add further documentation + implement multiple forms of this algorithm
    """

    @abstractmethod
    def __init__(
        self,
        participants: list[Participant],
        previous_pairings: Pairings,
        seed=None,
    ):
        # TODO: Add preconditions on participant graph
        self.random = default_rng(seed=seed)

    @abstractmethod
    def generate_pairs(self) -> Pairings:
        pass
