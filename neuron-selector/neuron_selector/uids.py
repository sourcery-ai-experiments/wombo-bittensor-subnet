import random
from bisect import bisect
from itertools import accumulate
from math import ceil
from typing import Any, Callable, Generic, Sequence, TypeVar

import bittensor

import torch
from bittensor import AxonInfo
from torch import Tensor

from tensor.protocol import NeuronInfoSynapse

DEFAULT_NEURON_INFO = NeuronInfoSynapse()

T = TypeVar("T")


def weighted_sample(weighted_items: Sequence[tuple[float, T]], k=1):
    k = min(k, len(weighted_items))

    population: list[T] = list([item for _, item in weighted_items])
    cumulative_weights: list[float] = list(accumulate([len(weighted_items) * weight for weight, _ in weighted_items]))
    population_size = ceil(cumulative_weights[-1])

    bias_population = [
        (index, population[bisect(cumulative_weights, index, 0, len(population) - 1)])
        for index in range(population_size)
    ]

    result: list[T] = []

    while len(result) < k:
        index, item = random.choice(bias_population)

        bias_population.remove((index, item))

        if item in result:
            continue

        result.append(item)

    return result


async def sync_neuron_info(self, dendrite: bittensor.dendrite):
    uids: list[int] = [
        uid
        for uid in range(self.metagraph.n.item())
        if self.metagraph.axons[uid].is_serving
    ]

    uid_by_hotkey: dict[str, int] = {
        self.metagraph.axons[uid].hotkey: uid
        for uid in uids
        if self.metagraph.axons[uid].hotkey != self.wallet.hotkey.ss58_address
    }

    axon_by_hotkey: dict[str, AxonInfo] = {
        self.metagraph.axons[uid].hotkey: self.metagraph.axons[uid]
        for uid in uids
    }

    axons = [axon_by_hotkey[hotkey] for hotkey in uid_by_hotkey.keys()]

    neuron_info: list[NeuronInfoSynapse] = await dendrite(
        axons=axons,
        synapse=NeuronInfoSynapse(),
        deserialize=False,
    )

    info_by_hotkey = {
        info.axon.hotkey: info
        for info in neuron_info
    }

    self.neuron_info = {
        uid_by_hotkey[hotkey]: info
        for hotkey, info in info_by_hotkey.items()
    }


def get_best_uids(
    blacklist: Any,
    metagraph: bittensor.metagraph,
    neuron_info: dict[int, NeuronInfoSynapse],
    rank: Tensor,
    condition: Callable[[int, NeuronInfoSynapse], bool],
    k: int = 3,
) -> Tensor:
    available_uids = [
        uid
        for uid in range(metagraph.n.item())
        if (
            metagraph.axons[uid].is_serving and
            (not blacklist or
             (
                 metagraph.axons[uid].hotkey not in blacklist.hotkeys and
                 metagraph.axons[uid].coldkey not in blacklist.coldkeys
             ))
        )
    ]

    infos = {
        uid: neuron_info.get(uid, DEFAULT_NEURON_INFO)
        for uid in available_uids
    }

    bittensor.logging.info(f"Neuron info found: {infos}")

    available_uids = [
        uid
        for uid in available_uids
        if condition(uid, infos[uid])
    ]

    if not len(available_uids):
        return torch.tensor([], dtype=torch.int64)

    uids = torch.tensor(
        random.sample(
            weighted_sample([(rank[uid].item(), uid) for uid in available_uids]),
            k=min(k, len(available_uids)),
        )
    )

    return uids
