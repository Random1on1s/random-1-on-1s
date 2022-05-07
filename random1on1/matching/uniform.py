import logging
import sys
from datetime import datetime
from typing import List

import numpy
from discord import Member
from networkx import complete_graph
from networkx import difference
from networkx import Graph
from networkx import union

from random1on1.api.algorithm import MatchingAlgorithm
from random1on1.api.pairings import Pairings

logger = logging.getLogger("discord")
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)


class UniformMatchingAlgorithm(MatchingAlgorithm):

    def __init__(self, participants: List[Member],
                 previous_pairings_merged: Pairings):
        self.participants = participants
        self.previous_pairings_merged = previous_pairings_merged
        self.potential_pairings = self.construct_potential_pairings(
            participants, previous_pairings_merged)
        self.random = numpy.random.default_rng()

    def construct_potential_pairings(self, participants: List[Member],
                                     previous_pairings_merged: Pairings):
        logger.debug("Creating potential pairings graph")
        previous_pairings_merged_graph = previous_pairings_merged.pairing_graph
        all_members = set(self.participants).union(
            set(previous_pairings_merged_graph.nodes))
        not_participating = all_members - set(participants)
        previous_pairings_merged_graph.add_nodes_from(participants)
        complete_pairings_graph = complete_graph(all_members)
        potential_pairing_graph = difference(
            complete_pairings_graph,
            self.previous_pairings_merged.pairing_graph)

        for member in not_participating:
            potential_pairing_graph.remove_node(member)

        return potential_pairing_graph

    def generate_pairs(self, dry_run: bool) -> Pairings:
        """
        Generate pairings completely at random by picking remaining edges. As soon as remaining nodes is 3 or less, then deal with edge cases.
        """

        pairing_graph = Graph()

        while (len(self.potential_pairings.nodes) > 3
               and len(self.potential_pairings.edges) > 1):
            person_1, person_2 = self.random.choice(
                list(self.potential_pairings.edges))
            pairing_graph.add_edge(person_1, person_2)
            self.potential_pairings.remove_edge(person_1, person_2)
            self.potential_pairings.remove_node(person_1)
            self.potential_pairings.remove_node(person_2)

        if len(self.potential_pairings.nodes) <= 3:
            remaining_pairings = complete_graph(self.potential_pairings)
            pairing_graph = union(pairing_graph, remaining_pairings)
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
