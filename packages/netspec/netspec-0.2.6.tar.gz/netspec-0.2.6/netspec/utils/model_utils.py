from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import h5py
import numpy as np
import torch
import torch.nn.functional as F
from astromodels.utils import get_user_data_path
from torch import Tensor, from_numpy, nn, no_grad

import netspec.training.training_data_tools as tdt

from ..utils import (
    recursively_load_dict_contents_from_group,
    recursively_save_dict_contents_to_group,
)
from ..utils.logging import setup_logger
from .custom_activation import Slimy

log = setup_logger(__name__)


activation_mapping = {}
activation_mapping["sigmoid"] = nn.Sigmoid
activation_mapping["relu"] = nn.ReLU
activation_mapping["leaky_relu"] = nn.LeakyReLU
activation_mapping["elu"] = nn.ELU
activation_mapping["selu"] = nn.SELU
activation_mapping["gelu"] = nn.GELU
activation_mapping["prelu"] = nn.PReLU
activation_mapping["silu"] = nn.SiLU
activation_mapping["softplus"] = nn.Softplus
activation_mapping["softmax"] = nn.Softmax
activation_mapping["slimy"] = Slimy

_learnable_activations = ["slimy", 'prelu', 'selu']


def len_out(
    len_in: int, padding: int, dilation: int, kernel_size: int, stride: int
) -> int:

    return (len_in + (2 * padding) - dilation * (kernel_size) // stride) + 1

    # return (len_in + 2 * padding - dilation * (kernel_size - 1) - 1) // stride


def len_out_mp(
    len_in: int, padding: int, dilation: int, kernel_size: int, stride: int
) -> int:

    #    return (len_in + (2 * padding) - dilation * (kernel_size) // stride) + 1

    return (len_in + 2 * padding - dilation * (kernel_size - 1) - 1) // stride


class Layers(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        architecture: List[int],
        activation_function: str,
        output_activation: Optional[str] = None,
        dropout: Optional[float] = None,
        use_batch_norm: bool = False,
        off_center: bool = False,
    ) -> None:

        super().__init__()

        if activation_function in _learnable_activations:

            # we want to learn the parameters

            self.activation = activation_mapping[activation_function]

        else:

            self.activation = activation_mapping[activation_function]()

        if output_activation is not None:

            self.output_activation = activation_mapping[output_activation]()

        layers: List[nn.Module] = []

        current_input_dim = n_parameters

        bias = not use_batch_norm

        for i, n_nodes in enumerate(architecture):

            layers.append(nn.Linear(current_input_dim, n_nodes, bias=bias))

            if use_batch_norm:

                layers.append(nn.BatchNorm1d(n_nodes))

            if dropout is not None:
                layers.append(nn.Dropout(dropout))

            if activation_function in _learnable_activations:

                layers.append(self.activation())

            else:

                layers.append(self.activation)

            current_input_dim = n_nodes

        layers.append(nn.Linear(current_input_dim, n_energies, bias=bias))

        # if dropout is not None:
        #     layers.append(nn.Dropout(dropout))

        if output_activation is not None:

            layers.append(self.output_activation)

        self.layers: nn.Module = nn.Sequential(*layers)

        self._off_center: bool = off_center

        if self._off_center:

            self.mu = nn.Parameter(torch.zeros(1))

            self.sigma = nn.Parameter(torch.zeros(1))

    def forward(self, x):

        if not self._off_center:

            return self.layers.forward(x)

        else:

            return self.mu + torch.pow(10.0, self.sigma) * self.layers.forward(
                x
            )


class SRLayers(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        architecture: List[int],
        activation_function: str,
        output_activation: Optional[str] = None,
        dropout: Optional[float] = None,
        use_batch_norm: bool = False,
        off_center: bool = False,
    ) -> None:

        super().__init__()

        self._n_energies: int = n_energies

        if activation_function in _learnable_activations:

            # we want to learn the parameters

            self.activation = activation_mapping[activation_function]

        else:

            self.activation = activation_mapping[activation_function]()

        if output_activation is not None:

            self.output_activation = activation_mapping[output_activation]()

        layers: List[nn.Module] = []

        current_input_dim = n_parameters

        bias = not use_batch_norm

        for i, n_nodes in enumerate(architecture):

            layers.append(nn.Linear(current_input_dim, n_nodes, bias=bias))

            if use_batch_norm:

                layers.append(nn.BatchNorm1d(n_nodes))

            if dropout is not None:

                layers.append(nn.Dropout(dropout))

            if activation_function in _learnable_activations:

                layers.append(self.activation())

            else:

                layers.append(self.activation)

            current_input_dim = n_nodes

        layers.append(nn.Linear(current_input_dim, 2 * n_energies, bias=bias))

        # if dropout is not None:
        #     layers.append(nn.Dropout(dropout))

        if output_activation is not None:

            layers.append(self.output_activation)

        self.layers: nn.Module = nn.Sequential(*layers)

        self._off_center: bool = off_center

        if self._off_center:

            self.mu = nn.Parameter(torch.zeros(1))

            self.sigma = nn.Parameter(torch.zeros(1))

    def forward(self, x):

        out = self.layers.forward(x)

        means = out[..., : self._n_energies]

        # sigmas = F.softplus(out[..., self._n_energies :])
        #log_sigmas = 20.0 * F.tanh(out[..., self._n_energies :])

        log_sigmas = out[..., self._n_energies :]

        return means, log_sigmas


class NeuralNet(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        architecture: List[int],
        activation_function: str,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = False,
        dropout: Optional[float] = None,
        off_center: bool = False,
        use_scoring_rule: bool = False,
    ) -> None:
        super().__init__()

        if not use_scoring_rule:

            self.layers: nn.Module = Layers(
                n_parameters,
                n_energies,
                architecture,
                activation_function,
                output_activation,
                dropout,
                use_batch_norm,
                off_center=off_center,
            )

        else:

            self.layers: nn.Module = SRLayers(
                n_parameters,
                n_energies,
                architecture,
                activation_function,
                output_activation,
                dropout,
                use_batch_norm,
                off_center=off_center,
            )

    def forward(self, x):
        return self.layers(x)


class ConvLayers(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        filter_size: List[int],
        kernel_size: List[int],
        max_pool_kernel_size: int,
        max_pool_all: bool = False,
        activation_function: Optional[str] = None,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = False,
        fc_layer_size: Optional[List[int]] = None,
    ) -> None:
        super().__init__()

        if activation_function is not None:

            self.activation = activation_mapping[activation_function]()

        if output_activation is not None:

            self.output_activation = activation_mapping[output_activation]()

        layers: List[nn.Module] = []

        current_input_dim = n_parameters
        current_filter_size = 1

        assert len(kernel_size) == len(filter_size)

        if fc_layer_size is not None:

            for layer_size in fc_layer_size:

                layers.append(nn.Linear(current_input_dim, layer_size))
                layers.append(self.activation)
                current_input_dim = layer_size

        bias = not use_batch_norm

        for k, f in zip(kernel_size, filter_size):

            layers.append(
                nn.Conv1d(
                    in_channels=current_filter_size,
                    out_channels=f,
                    kernel_size=k,
                    stride=1,
                    padding=1,
                    bias=bias,
                )
            )

            if use_batch_norm:

                layers.append(nn.BatchNorm1d(f))

            if activation_function is not None:

                layers.append(self.activation)

            current_input_dim = len_out(
                current_input_dim,
                padding=1,
                dilation=1,
                kernel_size=k,
                stride=1,
            )

            current_filter_size = f

            if max_pool_all:

                layers.append(
                    nn.MaxPool1d(
                        kernel_size=max_pool_kernel_size,
                        stride=max_pool_kernel_size,
                    )
                )

                current_input_dim = len_out_mp(
                    current_input_dim,
                    1,
                    1,
                    max_pool_kernel_size,
                    max_pool_kernel_size,
                )

        # now max pool

        if not max_pool_all:

            layers.append(
                nn.MaxPool1d(
                    kernel_size=max_pool_kernel_size,
                    stride=max_pool_kernel_size,
                )
            )

            current_input_dim = len_out_mp(
                current_input_dim,
                1,
                1,
                max_pool_kernel_size,
                max_pool_kernel_size,
            )

        layers.append(nn.Flatten(1))

        if output_activation is not None:

            layers.append(self.output_activation)

        self.layers: nn.Module = nn.Sequential(*layers)

        self._final_output_size: int = filter_size[-1] * current_input_dim

    @property
    def final_output_size(self) -> int:
        return self._final_output_size

    def forward(self, x):

        # add zero channels

        return self.layers.forward(x)


class SkipConvLayers(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        filter_size: List[int],
        kernel_size: List[int],
        max_pool_kernel_size: int,
        max_pool_all: bool = False,
        activation_function: Optional[str] = None,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = True,
        fc_layer_size: Optional[List[int]] = None,
    ) -> None:
        super().__init__()

        self._n_layers: int = len(filter_size)

        if activation_function is not None:

            self.activation = activation_mapping[activation_function]()

        if output_activation is not None:

            self.output_activation = activation_mapping[output_activation]()

        bias = not use_batch_norm

        self._convs: nn.ModuleList = nn.ModuleList(
            [nn.Conv1d(1, filter_size[0], kernel_size[0], bias=bias, padding=1)]
        )
        self._bns: nn.ModuleList = nn.ModuleList(
            [nn.BatchNorm1d(filter_size[0])]
        )
        self._skip_convs: nn.ModuleList = nn.ModuleList(
            [nn.Conv1d(1, out_channels=filter_size[0], kernel_size=1)]
        )

        self._flatten = nn.Flatten(1)
        self._max_pool = nn.MaxPool1d(kernel_size=2, stride=2)

        assert len(kernel_size) == len(filter_size)

        for i in range(1, len(filter_size)):

            self._convs.append(
                nn.Conv1d(
                    filter_size[i - 1],
                    filter_size[i],
                    kernel_size=kernel_size[i],
                    bias=bias,
                    padding=1,
                )
            )

            self._bns.append(nn.BatchNorm1d(filter_size[i]))

            self._skip_convs.append(
                nn.Conv1d(filter_size[i - 1], filter_size[i], kernel_size=1)
            )

        dummy_input = torch.randn(1, 1, n_parameters)

        self._final_out_size = self._compute_output_size(dummy_input)

        #     current_input_dim = len_out(
        #         current_input_dim,
        #         padding=1,
        #         dilation=1,
        #         kernel_size=k,
        #         stride=1,
        #     )

        # # now max pool

        # if not max_pool_all:

        #     layers.append(
        #         nn.MaxPool1d(
        #             kernel_size=max_pool_kernel_size,
        #             stride=max_pool_kernel_size,
        #         )
        #     )

        #     current_input_dim = len_out_mp(
        #         current_input_dim,
        #         1,
        #         1,
        #         max_pool_kernel_size,
        #         max_pool_kernel_size,
        #     )

        # layers.append(nn.Flatten(1))

        # if output_activation is not None:

        #     layers.append(self.output_activation)

        # self.layers: nn.Module = nn.Sequential(*layers)

        # self._final_output_size: int = filter_size[-1] * current_input_dim

    def _compute_output_size(self, x) -> int:
        out = x

        for i in range(self._n_layers):
            out = self._convs[i](out)
            out = self._bns[i](out)
            out = self.activation(out)

        #        out = self._max_pool(out)

        out = self._flatten(out)

        _, output_length = out.size()

        return output_length

    @property
    def final_output_size(self) -> int:
        return self._final_out_size

    def forward(self, x):

        out = x

        for i in range(self._n_layers):
            residual = out  # Store the previous output as a residual connection
            out = self._convs[i](out)
            out = self._bns[i](out)
            out = self.activation(
                out
            )  # Apply activation function after batch normalization

            if i % 2 == 0:
                skip = self._skip_convs[i](residual)
                skip_length = skip.size(2)
                out_length = out.size(2)

                if skip_length != out_length:
                    padding = out_length - skip_length
                    skip = nn.functional.pad(skip, (padding, 0))

                # Perform skip connections

                out = out + skip

        # out = self._max_pool(out)
        return self._flatten(out)


class ConvNeuralNet(nn.Module):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        filter_size: List[int],
        kernel_size: List[int],
        max_pool_kernel_size: int,
        architecture: List[int],
        activation_function: str,
        max_pool_all: bool = False,
        output_activation: Optional[str] = None,
        conv_activation_function: Optional[str] = None,
        conv_output_activation: Optional[str] = None,
        dropout: Optional[float] = None,
        use_batch_norm: bool = False,
        fc_layer_size: Optional[List[int]] = None,
        use_scoring_rule: bool = False,
        use_skip_connections: bool = False,
    ) -> None:
        super().__init__()

        if not use_skip_connections:

            self.conv_layers: nn.Module = ConvLayers(
                n_parameters,
                filter_size,
                kernel_size,
                max_pool_kernel_size,
                max_pool_all,
                conv_activation_function,
                conv_output_activation,
                use_batch_norm=use_batch_norm,
                fc_layer_size=fc_layer_size,
            )

        else:

            self.conv_layers: nn.Module = SkipConvLayers(
                n_parameters,
                filter_size,
                kernel_size,
                max_pool_kernel_size,
                max_pool_all,
                conv_activation_function,
                conv_output_activation,
                use_batch_norm=use_batch_norm,
                fc_layer_size=fc_layer_size,
            )

        if not use_scoring_rule:

            self.layers: nn.Module = Layers(
                self.conv_layers.final_output_size,
                n_energies,
                architecture,
                activation_function,
                output_activation,
                dropout,
                use_batch_norm=False,
            )

        else:

            self.layers: nn.Module = SRLayers(
                self.conv_layers.final_output_size,
                n_energies,
                architecture,
                activation_function,
                output_activation,
                dropout,
                use_batch_norm=False,
            )

    def forward(self, x):

        x_out = self.conv_layers(x)

        return self.layers(x_out)


@dataclass
class ModelParams:
    n_parameters: int
    n_energies: int
    architecture: List[int]
    activation_function: str
    filter_size: Optional[List[int]] = None
    kernel_size: Optional[List[int]] = None
    max_pool_kernel_size: Optional[int] = None
    max_pool_all: bool = False
    output_activation: Optional[str] = None
    conv_activation_function: Optional[str] = None
    conv_output_activation: Optional[str] = None
    use_batch_norm: bool = False
    dropout: Optional[float] = None
    fc_layer_size: Optional[List[int]] = None
    off_center: bool = False
    use_scoring_rule: bool = False
    use_skip_connections: bool = False


class ModelStorage:
    def __init__(
        self,
        model_params: ModelParams,
        transformer: tdt.Transformer,
        state_dict: Dict[Any, Any],
    ):

        if model_params.filter_size is not None:

            inputs = asdict(model_params)
            inputs.pop("off_center")

            self._neural_net: Union[NeuralNet, ConvNeuralNet] = ConvNeuralNet(
                **inputs
            )

            self._is_convolutional = True

        else:

            inputs = asdict(model_params)
            inputs.pop("filter_size")
            inputs.pop("kernel_size")
            inputs.pop("max_pool_kernel_size")
            inputs.pop("max_pool_all")
            inputs.pop("conv_activation_function")
            inputs.pop("conv_output_activation")
            inputs.pop("fc_layer_size")
            inputs.pop("use_skip_connections")

            self._neural_net = NeuralNet(**inputs)

            self._is_convolutional = False

        self._transformer: tdt.Transformer = transformer

        self._neural_net.load_state_dict(state_dict)
        self._neural_net.eval()

        self._model_params = model_params

        self._use_scoring_rule: bool = model_params.use_scoring_rule
        self._n_energies: int = model_params.n_energies

    @property
    def transformer(self) -> tdt.Transformer:
        return self._transformer

    def evaluate(self, params) -> np.ndarray:

        transformed_params = self._transformer.transform_parameters(params)

        transformed_params = from_numpy(transformed_params)

        if self._is_convolutional:

            transformed_params = transformed_params.unsqueeze(0).unsqueeze(0)

        with no_grad():

            output: Tensor = self._neural_net(transformed_params)

            if self._use_scoring_rule:

                output = output[0]

        log.debug(f"params: {params}")
        log.debug(f"output: {output}")

        return self._transformer.inverse_values(
            output.numpy(), params
        ).squeeze()

    def evaluate_raw(self, params) -> np.ndarray:

        transformed_params = self._transformer.transform_parameters(params)

        transformed_params = from_numpy(transformed_params)

        if self._is_convolutional:

            transformed_params = transformed_params.unsqueeze(0).unsqueeze(0)

        with no_grad():

            output: Tensor = self._neural_net(transformed_params)

            if self._use_scoring_rule:

                output = output[0]

        return output.numpy().squeeze()

    @property
    def energies(self) -> np.ndarray:
        return self._transformer.energies

    @classmethod
    def from_file(cls, file_name: str) -> "ModelStorage":

        with h5py.File(file_name, "r") as f:

            transformer: tdt.Transformer = tdt.Transformer.from_file(
                f["transformer"]
            )

            state_dict = recursively_load_dict_contents_from_group(
                f, "state_dict"
            )

            model_params = ModelParams(**f.attrs)

        return cls(
            model_params=model_params,
            transformer=transformer,
            state_dict=state_dict,
        )

    def to_file(self, file_name: str) -> None:

        with h5py.File(file_name, "w") as f:

            transform_group: h5py.Group = f.create_group("transformer")

            self._transformer.to_file(transform_group)

            recursively_save_dict_contents_to_group(
                f, "state_dict", self._neural_net.state_dict()
            )

            for k, v in asdict(self._model_params).items():
                if v is not None:

                    f.attrs[k] = v

    def save_to_user_dir(
        self, model_name: str, overwrite: bool = False
    ) -> None:

        # Get the data directory

        data_dir_path: Path = get_user_data_path()

        # Sanitize the data file

        filename_sanitized = data_dir_path.absolute() / f"{model_name}.h5"

        if filename_sanitized.exists() and (not overwrite):

            log.error(f"{model_name}.h5 already exists!")

            raise RuntimeError(f"{model_name}.h5 already exists!")

        self.to_file(filename_sanitized.as_posix())
