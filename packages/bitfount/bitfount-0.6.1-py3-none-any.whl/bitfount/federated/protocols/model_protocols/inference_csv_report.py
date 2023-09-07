"""Protocol for combinging a single model inference and a csv algorithm."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, List, Optional, Sequence, Union, cast

import pandas as pd

from bitfount.federated.algorithms.csv_report_algorithm import (
    CSVReportAlgorithm,
    _ModellerSide as _CSVModellerSide,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _ModellerSide as _InferenceModellerSide,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
)
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _WorkerMailbox,
)
from bitfount.types import _SerializedWeights, _Weights

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger("bitfount.federated.protocols" + __name__)


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the protocol.

    Args:
        algorithm: The single model inference algorithm to be used.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[Union[_InferenceModellerSide, _CSVModellerSide]]

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[_InferenceModellerSide, _CSVModellerSide]],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def run(
        self,
        iteration: int = 0,
        **kwargs: Any,
    ) -> Union[List[Any], Any]:
        """Runs Modeller side of the protocol.

        This just sends the model parameters to the workers and then tells
        the workers when the protocol is finished.
        """
        results = []
        for algo in self.algorithm:
            if hasattr(algo, "model"):
                initial_parameters: _Weights = algo.model.get_param_states()
                serialized_params = algo.model.serialize_params(initial_parameters)
                await self._send_parameters(serialized_params)
                result = await self.mailbox.get_evaluation_results_from_workers()
                results.append(result)
                logger.info("Received results from Pods.")
        final_results = [
            algo.run(result_) for algo, result_ in zip(self.algorithm, results)
        ]

        return final_results


class _WorkerSide(BaseWorkerProtocol):
    """Worker side of the protocol.

    Args:
        algorithm: The single model inference worker algorithms to be used.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[Union[_InferenceWorkerSide, _CSVWorkerSide]]

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[_InferenceWorkerSide, _CSVWorkerSide]],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def run(
        self,
        pod_vitals: Optional[_PodVitals] = None,
        **kwargs: Any,
    ) -> None:
        """Runs the algorithm on worker side."""
        # Unpack the algorithm into the two algorithms
        model_inference_algo, csv_report_algo = self.algorithm

        # Run Fovea Algorithm
        model_inference_algo = cast(_InferenceWorkerSide, model_inference_algo)
        model_params = await self._receive_parameters()
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        model_predictions = model_inference_algo.run(
            model_params=model_params,
        )

        model_predictions = cast(pd.DataFrame, model_predictions)

        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        csv_report_algo.run(
            results_df=model_predictions,
            task_id=self.mailbox._task_id,
        )
        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})


class InferenceAndCSVReport(BaseProtocolFactory):
    """Protocol for running a model inference generating a csv report."""

    def __init__(
        self,
        *,
        algorithm: Sequence[Union[ModelInference, CSVReportAlgorithm]],
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithm."""
        if algorithm.class_name not in (
            "bitfount.ModelInference, bitfount.CSVReportAlgorithm"
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[Union[ModelInference, CSVReportAlgorithm]],
            self.algorithms,
        )
        modeller_algos = []
        for algo in algorithms:
            if hasattr(algo, "pretrained_file"):
                modeller_algos.append(
                    algo.modeller(pretrained_file=algo.pretrained_file)
                )
            else:
                modeller_algos.append(algo.modeller())
        return _ModellerSide(
            algorithm=modeller_algos,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns worker side of the protocol."""
        algorithms = cast(
            Sequence[Union[ModelInference, CSVReportAlgorithm]],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
