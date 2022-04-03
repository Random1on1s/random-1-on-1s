from datetime import datetime

from networkx import Graph


class Pairings(object):
    """
    Wrapper class to serialize and deserialization information about a set of a pairings
    """

    def __init__(
        self,
        pairings_tuple_list: Graph,
        date_of_pairing: datetime,
        dry_run: bool,
    ):
        self.pairings_tuple_list = pairings_tuple_list
        self.date_of_pairing = date_of_pairing
        self.dry_run = dry_run
