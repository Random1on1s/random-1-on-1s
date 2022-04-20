from datetime import datetime

from networkx import Graph


class Pairings:
    """
    Wrapper class to serialize and deserialization information about a set of a pairings
    """

    def __init__(
        self,
        pairing_graph: Graph,
        date_of_pairing: datetime,
        dry_run: bool,
    ):
        self.pairing_graph = pairing_graph
        self.date_of_pairing = date_of_pairing
        self.dry_run = dry_run

    def to_json(self) -> str:
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_dict: dict) -> Pairings:
        raise NotImplementedError()
