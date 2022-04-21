from datetime import datetime

from networkx import complete_graph
from networkx import difference
from networkx import Graph

from random1on1.api.algorithm import MatchingAlgorithm
from random1on1.api.pairings import Pairings
from random1on1.api.participant import Participant


class UniformMatchingAlgorithm(MatchingAlgorithm):

    def __init__(self, participants: list[Participant],
                 previous_pairings: Pairings):
        self.participants = participants
        self.previous_pairings = previous_pairings

        complete_pairings_graph = complete_graph(participants)
        self.potential_pairings = difference(
            complete_pairings_graph, self.previous_pairings.pairing_graph)

    def generate_pairs(self, dry_run: bool) -> Pairings:
        """
        Generate pairings completely at random by picking remaining edges. As soon as remaining nodes is 3 or less, then deal with edge cases.
        """

        pairing_graph = Graph()

        while (len(self.potential_pairings.nodes) > 3
               and len(self.potential_pairings.edges) > 1):
            person_1, person_2, _ = self.random.choice(
                list(self.potential_pairings.edge))
            pairing_graph.add_edge(person_1, person_2)
            self.potential_pairings.remove_edge(person_1, person_2)
            self.potential_pairings.remove_node(person_1)
            self.potential_pairings.remove_node(person_2)

        if len(self.potential_pairings.nodes) <= 3:
            pairing_graph.add_edges_from(
                complete_graph(self.potential_pairings.nodes))
        else:
            # TODO: Address algorithm completeness error for unpaired people
            #       This error occurs when the algorithm draws pairings and then winds up with more than 3 people after having pulled all the edges
            #       in a random order. Because we remove nodes that could have connections to these nodes at random earlier in the algorithm, it does
            #       not mean that there isn't a possible pairings for this week that avoids duplicates, merely that this algorithm is not currently
            #       setup to find those pairings. We need to fix this in future versions.
            raise NotImplementedError()

        return Pairings(pairing_graph=pairing_graph,
                        date_of_pairing=datetime.now(),
                        dry_run=dry_run)
