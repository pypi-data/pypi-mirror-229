# Copyright 2022 by Michał Czuba, Piotr Bródka. All Rights Reserved.
#
# This file is part of Network Diffusion.
#
# Network Diffusion is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# Network Diffusion is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the  GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Network Diffusion. If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

"""Functions for the phenomena spreading definition."""
from typing import List, Optional

from tqdm import tqdm

from network_diffusion.experiment_logger import ExperimentLogger
from network_diffusion.mln.mlnetwork import MultilayerNetwork
from network_diffusion.models.base_model import BaseModel
from network_diffusion.models.utils.types import NetworkUpdateBuffer


class MultiSpreading:
    """Perform experiment defined by PropagationModel on MultiLayerNetwork."""

    def __init__(self, model: BaseModel, network: MultilayerNetwork) -> None:
        """
        Construct an object.

        :param model: model of propagation which determines how experiment
            looks like
        :param network: a network which is being examined during experiment
        """
        self._model = model
        self._network = network
        self.stopping_counter = 0

    def _update_counter(
        self, nodes_to_update: List[NetworkUpdateBuffer]
    ) -> None:
        """Update a counter of dead epochs."""
        if len(nodes_to_update) == 0:
            self.stopping_counter += 1
        else:
            self.stopping_counter = 0

    def perform_propagation(
        self,
        n_epochs: int,
        patience: Optional[int] = None,
    ) -> ExperimentLogger:
        """
        Perform experiment on given network and given model.

        It saves logs in ExperimentLogger object which can be used for further
        analysis.

        :param n_epochs: number of epochs to do experiment
        :param patience: if provided experiment will be stopped when in
            "patience" (e.g. 4) consecutive epoch there was no propagation
        :return: logs of experiment stored in special object
        """
        if patience is not None and patience <= 0:
            raise ValueError("Patience must be None or integer > 0!")
        logger = ExperimentLogger(str(self._model), str(self._network))

        # set and add logs from initialising states
        initial_state = self._model.set_initial_states(self._network)
        logger.add_global_stat(self._network.get_states_num())
        logger.add_local_stat(0, initial_state)

        # iterate through epochs
        progress_bar = tqdm(
            range(n_epochs), desc="experiment", leave=False, colour="blue"
        )
        for epoch in progress_bar:
            progress_bar.set_description_str(f"Processing epoch {epoch}")

            # do a forward step and update network
            nodes_to_update = self._model.network_evaluation_step(
                self._network
            )
            epoch_json = self._model.update_network(
                self._network, nodes_to_update
            )

            # add logs from current epoch
            logger.add_global_stat(self._network.get_states_num())
            logger.add_local_stat(epoch + 1, epoch_json)

            # check if there is no progress and therefore stop simulation
            if patience:
                self._update_counter(nodes_to_update)
                if self.stopping_counter >= patience:
                    progress_bar.set_description_str(
                        f"Experiment stopped - no progress in last "
                        f"{patience} epochs!"
                    )
                    break

        # convert logs to dataframe
        logger.convert_logs(self._model.get_allowed_states(self._network))

        return logger
