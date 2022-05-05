import json
from datetime import datetime
from typing import Union

from discord import Guild
from networkx import Graph


class Pairings:

    def __init__(
        self,
        pairing_graph: Graph,
        date_of_pairing: datetime,
        dry_run: bool,
    ):
        self.pairing_graph = pairing_graph
        self.date_of_pairing = date_of_pairing
        self.dry_run = dry_run

    def to_json(self) -> dict:
        json_dict = {
            "dry_run":
            self.dry_run,
            "date_of_pairing":
            self.date_of_pairing.strftime("%Y-%m-%d"),
            "pairing_graph":
            [(edge[0].id, edge[1].id) for edge in self.pairing_graph.edges],
        }
        return json_dict


async def pairings_from_json(json_data: Union[str, dict],
                             guild: Guild) -> Pairings:
    if isinstance(json_data, str):
        return await pairings_from_dict(dictionary=json.loads(json_data),
                                        guild=guild)
    else:
        return await pairings_from_dict(dictionary=json_data, guild=guild)


async def pairings_from_dict(dictionary: dict, guild: Guild) -> Pairings:

    dry_run = dictionary["dry_run"]
    date_of_pairing = datetime.strptime(dictionary["date_of_pairing"],
                                        "%Y-%m-%d")

    pairing_edges = []
    for person_1_id, person_2_id in dictionary["pairing_graph"]:
        person_1 = guild.get_member(person_1_id)
        person_2 = guild.get_member(person_2_id)
        pairing_edges.append((person_1, person_2))

    pairing_graph = Graph()
    pairing_graph.add_edges_from(pairing_edges)

    return Pairings(pairing_graph=pairing_graph,
                    date_of_pairing=date_of_pairing,
                    dry_run=dry_run)
