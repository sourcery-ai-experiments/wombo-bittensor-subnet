import torch
import random
import bittensor as bt
from typing import Callable, List

from tensor.protocol import NeuronInfoSynapse, NeuronType


def sync_neuron_info(self):
    axons = [self.metagraph.axons[uid] for uid in self.metagraph.uids]
    uids_by_hotkey = {axon.hotkey: uid for uid, axon in zip(self.metagraph.uids, axons)}

    neuron_info: List[NeuronInfoSynapse] = self.dendrite.query(
        axons=axons,
        synapse=NeuronInfoSynapse(),
        deserialize=False,
    )

    info_by_hotkey = {
        info.axon.hotkey: info
        for info in neuron_info
    }

    self.neuron_info = {
        uids_by_hotkey[hotkey]: info
        for hotkey, info in info_by_hotkey
    }


def get_random_uids(
    self,
    k: int,
    validators: bool,
) -> torch.LongTensor:
    if validators:
        def validator_condition(uid: int) -> bool:
            return self.neuron_info[uid].neuron_type == NeuronType.VALIDATOR and self.metagraph.validator_permit[uid]
    else:
        def validator_condition(uid: int) -> bool:
            return not self.neuron_info[uid].neuron_type == NeuronType.MINER

    available_uids = [
        uid
        for uid in range(self.metagraph.n.item())
        if (
                self.metagraph.active[uid] and
                self.metagraph.axons[uid].is_serving and
                validator_condition(uid)
        )
    ]

    uids = torch.tensor(random.sample(available_uids, min(k, len(available_uids))))
    return uids
