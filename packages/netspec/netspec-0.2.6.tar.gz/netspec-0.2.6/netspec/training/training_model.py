from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytorch_lightning as pl
import torch
from torch import nn
from torchmetrics import (
    MeanAbsoluteError,
    MeanAbsolutePercentageError,
    MeanSquaredError,
    SymmetricMeanAbsolutePercentageError,
)

import netspec.training.training_data_tools as tdt
import netspec.utils.custom_activation as ca
import netspec.utils.model_utils as mutils

from .optimizer import OptimizerConfig


class TrainingNeuralNet(pl.LightningModule):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        activation_function: str,
        optimizer: OptimizerConfig,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = False,
        dropout: Optional[float] = None,
        learning_rate: float = 1e-3,
        use_mape: bool = False,
        square_loss: bool = False,
        huber_loss: bool = False,
        delta: float = 1.0,
        off_center: bool = False,
        use_scoring_rule: bool = False,
    ) -> None:
        """TODO describe function

        :param n_parameters:
        :type n_parameters: int
        :param n_energies:
        :type n_energies: int
        :param activation_function:
        :type activation_function: str
        :param optimizer:
        :type optimizer: OptimizerConfig
        :param output_activation:
        :type output_activation: Optional[str]
        :param use_batch_norm:
        :type use_batch_norm: bool
        :param dropout:
        :type dropout: Optional[float]
        :param learning_rate:
        :type learning_rate: float
        :param use_mape:
        :type use_mape: bool
        :param square_loss:
        :type square_loss: bool
        :param huber_loss:
        :type huber_loss: bool
        :param delta:
        :type delta: float
        :param off_center:
        :type off_center: bool
        :param use_scoring_rule:
        :type use_scoring_rule: bool
        :returns:

        """
        super().__init__()

        self._n_parameters: int = n_parameters
        self._n_energies: int = n_energies

        self._dropout: Optional[float] = dropout
        self._use_batch_norm: bool = use_batch_norm
        self._activation_function: str = activation_function
        self._output_activation: Optional[str] = output_activation
        self._optimizer: OptimizerConfig = optimizer
        self._off_center: bool = off_center
        self._use_scoring_rule: bool = use_scoring_rule

        self.learning_rate = learning_rate

        self._huber_loss: bool = huber_loss

        if not square_loss:
            self.train_loss = MeanAbsoluteError()
            self.val_loss = MeanAbsoluteError()
        elif huber_loss:

            self.train_loss = torch.nn.HuberLoss(delta=delta, reduction="mean")
            self.val_loss = torch.nn.HuberLoss(delta=delta, reduction="mean")

        else:
            self.train_loss = MeanSquaredError()
            self.val_loss = MeanSquaredError()

        self._use_mape: bool = use_mape

        if not self._use_mape:

            self.train_accuracy = SymmetricMeanAbsolutePercentageError()

            self.val_accuracy = SymmetricMeanAbsolutePercentageError()

        else:

            self.train_accuracy = MeanAbsolutePercentageError()

            self.val_accuracy = MeanAbsolutePercentageError()

    def training_step(self, batch, batch_idx: int) -> Dict[str, Any]:

        x, y = batch

        if self._use_scoring_rule:

            mean, log_var = self.forward(x)

            losses = log_var + (y - mean) ** 2 / torch.exp(log_var)
            loss = torch.mean(
                torch.unsqueeze(losses, 0)
            )  # to keep losses comparable regardless of batch size

            self.log(
                "train_loss",
                loss,
                on_epoch=True,
                on_step=False,
                prog_bar=True,
            )

            self.train_accuracy(mean, y)

        else:

            pred = self.forward(x)

            loss = self.train_loss(pred, y)

            if not self._huber_loss:

                self.log(
                    "train_loss",
                    self.train_loss,
                    on_epoch=True,
                    on_step=False,
                    prog_bar=True,
                )

            else:

                self.log(
                    "train_loss",
                    loss,
                    on_epoch=True,
                    on_step=False,
                    prog_bar=True,
                )

                self.train_accuracy(pred, y)

        self.log(
            "train_accuracy",
            self.train_accuracy,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
        )

        return loss

    def validation_step(self, batch, batch_idx: int) -> Dict[str, Any]:

        x, y = batch

        if self._use_scoring_rule:

            mean, log_var = self.forward(x)

            losses = log_var + (y - mean) ** 2 / torch.exp(log_var)
            loss = torch.mean(
                torch.unsqueeze(losses, 0)
            )  # to keep losses comparable regardless of batch size

            self.log(
                "val_loss",
                loss,
                on_epoch=True,
                on_step=False,
                prog_bar=True,
            )

            self.val_accuracy(mean, y)

        else:

            pred = self.forward(x)

            loss = self.val_loss(pred, y)

            if not self._huber_loss:

                self.log(
                    "val_loss",
                    self.val_loss,
                    on_epoch=True,
                    on_step=False,
                    prog_bar=True,
                )

            else:

                self.log(
                    "val_loss",
                    loss,
                    on_epoch=True,
                    on_step=False,
                    prog_bar=True,
                )

                self.val_accuracy(pred, y)

        self.log(
            "val_accuracy",
            self.val_accuracy,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
        )

        return loss

    def configure_optimizers(self) -> Dict[str, Any]:

        return self._optimizer.optim_dict(self.parameters(), self.trainer)


class StandardTrainingNN(TrainingNeuralNet):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        architecture: List[int],
        activation_function: str,
        optimizer: OptimizerConfig,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = False,
        dropout: Optional[float] = None,
        learning_rate: float = 0.001,
        use_mape: bool = False,
        square_loss: bool = False,
        off_center: bool = False,
        use_scoring_rule: bool = False,
    ) -> None:
        """TODO describe function

        :param n_parameters:
        :type n_parameters: int
        :param n_energies:
        :type n_energies: int
        :param architecture:
        :type architecture: List[int]
        :param activation_function:
        :type activation_function: str
        :param optimizer:
        :type optimizer: OptimizerConfig
        :param output_activation:
        :type output_activation: Optional[str]
        :param use_batch_norm:
        :type use_batch_norm: bool
        :param dropout:
        :type dropout: Optional[float]
        :param learning_rate:
        :type learning_rate: float
        :param use_mape:
        :type use_mape: bool
        :param square_loss:
        :type square_loss: bool
        :param off_center:
        :type off_center: bool
        :param use_scoring_rule:
        :type use_scoring_rule: bool
        :returns:

        """

        super().__init__(
            n_parameters,
            n_energies,
            activation_function,
            optimizer,
            output_activation,
            use_batch_norm,
            dropout,
            learning_rate,
            use_mape,
            square_loss,
            off_center=off_center,
            use_scoring_rule=use_scoring_rule,
        )

        self._architecture: List[int] = architecture

        if not use_scoring_rule:

            self.layers: nn.Module = mutils.Layers(
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

            self.layers: nn.Module = mutils.SRLayers(
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

        return self.layers.forward(x)

    def initialize_weights(
        self, uniform: bool = True, orthogonal: bool = False
    ) -> None:
        def init_weights(m):
            if isinstance(m, torch.nn.Linear):

                if self._activation_function in ["relu", "leaky_relu"]:

                    nl = self._activation_function

                else:

                    nl = "leaky_relu"

                if orthogonal:

                    torch.nn.init.orthogonal_(m.weight)

                elif uniform:

                    torch.nn.init.kaiming_uniform_(m.weight, nonlinearity=nl)

                else:

                    torch.nn.init.kaiming_normal_(m.weight, nonlinearity=nl)

                if not self._use_batch_norm:
                    m.bias.data.fill_(0.01)

            elif isinstance(m, ca.Slimy):

                torch.nn.init.normal_(m.alpha)
                torch.nn.init.normal_(m.beta)

        self.layers.apply(init_weights)

    def save_model(
        self,
        model_name: str,
        checkpoint,
        transformer: tdt.Transformer,
        overwrite: bool = False,
    ) -> None:

        model_params: mutils.ModelParams = mutils.ModelParams(
            n_parameters=self._n_parameters,
            n_energies=self._n_energies,
            architecture=self._architecture,
            activation_function=self._activation_function,
            output_activation=self._output_activation,
            use_batch_norm=self._use_batch_norm,
            dropout=self._dropout,
            filter_size=None,
            kernel_size=None,
            max_pool_kernel_size=None,
            off_center=self._off_center,
            use_scoring_rule=self._use_scoring_rule,
        )

        model_storage: mutils.ModelStorage = mutils.ModelStorage(
            model_params, transformer, checkpoint["state_dict"]
        )

        model_storage.save_to_user_dir(model_name, overwrite)


class ConvTrainingNN(TrainingNeuralNet):
    def __init__(
        self,
        n_parameters: int,
        n_energies: int,
        architecture: List[int],
        activation_function: str,
        optimizer: OptimizerConfig,
        filter_size: List[int],
        kernel_size: List[int],
        max_pool_kernel_size: int,
        max_pool_all: bool = False,
        conv_activation_function: Optional[str] = None,
        conv_output_activation: Optional[str] = None,
        output_activation: Optional[str] = None,
        use_batch_norm: bool = False,
        dropout: Optional[float] = None,
        learning_rate: float = 0.001,
        use_mape: bool = False,
        square_loss: bool = False,
        huber_loss: bool = False,
        delta: float = 1.0,
        fc_layer_size: Optional[List[int]] = None,
        use_scoring_rule: bool = False,
        use_skip_connections: bool = False,
    ) -> None:
        """TODO describe function

        :param n_parameters:
        :type n_parameters: int
        :param n_energies:
        :type n_energies: int
        :param architecture:
        :type architecture: List[int]
        :param activation_function:
        :type activation_function: str
        :param optimizer:
        :type optimizer: OptimizerConfig
        :param filter_size:
        :type filter_size: List[int]
        :param kernel_size:
        :type kernel_size: List[int]
        :param max_pool_kernel_size:
        :type max_pool_kernel_size: int
        :param max_pool_all:
        :type max_pool_all: bool
        :param conv_activation_function:
        :type conv_activation_function: Optional[str]
        :param conv_output_activation:
        :type conv_output_activation: Optional[str]
        :param output_activation:
        :type output_activation: Optional[str]
        :param use_batch_norm:
        :type use_batch_norm: bool
        :param dropout:
        :type dropout: Optional[float]
        :param learning_rate:
        :type learning_rate: float
        :param use_mape:
        :type use_mape: bool
        :param square_loss:
        :type square_loss: bool
        :param huber_loss:
        :type huber_loss: bool
        :param delta:
        :type delta: float
        :param fc_layer_size:
        :type fc_layer_size: Optional[List[int]]
        :param use_scoring_rule:
        :type use_scoring_rule: bool
        :returns:

        """

        super().__init__(
            n_parameters,
            n_energies,
            activation_function,
            optimizer,
            output_activation,
            use_batch_norm,
            dropout,
            learning_rate,
            use_mape,
            square_loss,
            huber_loss=huber_loss,
            delta=delta,
            use_scoring_rule=use_scoring_rule,
        )

        self._architecture: List[int] = architecture
        self._filter_size: List[int] = filter_size
        self._kernel_size: List[int] = kernel_size
        self._max_pool_kernel_size: int = max_pool_kernel_size
        self._max_pool_all: bool = max_pool_all
        self._conv_activation_function: Optional[str] = conv_activation_function
        self._conv_output_activation: Optional[str] = conv_output_activation
        self._fc_layer_size: Optional[List[int]] = fc_layer_size
        self._use_skip_connections: bool = use_skip_connections

        if not use_skip_connections:

            self.conv_layers: nn.Module = mutils.ConvLayers(
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

            self.conv_layers: nn.Module = mutils.SkipConvLayers(
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
            self.layers: nn.Module = mutils.Layers(
                self.conv_layers.final_output_size,
                n_energies,
                architecture,
                activation_function,
                output_activation,
                dropout,
                use_batch_norm=False,
            )

        else:

            self.layers: nn.Module = mutils.SRLayers(
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

    def initialize_weights(
        self, uniform: bool = True, orthogonal: bool = False
    ) -> None:
        def init_weights(m):
            if isinstance(m, torch.nn.Linear):

                if self._activation_function in ["relu", "leaky_relu"]:

                    nl = self._activation_function

                else:

                    nl = "leaky_relu"

                torch.nn.init.kaiming_uniform_(m.weight, nonlinearity=nl)

                if uniform:

                    torch.nn.init.kaiming_uniform_(m.weight, nonlinearity=nl)

                elif orthogonal:

                    torch.nn.init.orthogonal_(m.weight)

                else:

                    torch.nn.init.kaiming_normal_(m.weight, nonlinearity=nl)

                if not self._use_batch_norm:

                    m.bias.data.fill_(0.01)

            elif isinstance(m, torch.nn.Conv1d):

                if self._activation_function in ["relu", "leaky_relu"]:

                    nl = self._activation_function

                else:

                    nl = "leaky_relu"

                if uniform:

                    torch.nn.init.kaiming_uniform_(m.weight, nonlinearity=nl)

                elif orthogonal:

                    torch.nn.init.orthogonal_(m.weight)

                else:

                    torch.nn.init.kaiming_normal_(m.weight, nonlinearity=nl)

                if not self._use_batch_norm:

                    m.bias.data.fill_(0.01)

            elif isinstance(m, ca.Slimy):

                torch.nn.init.normal_(m.alpha)
                torch.nn.init.normal_(m.beta)

        self.layers.apply(init_weights)

        self.conv_layers.apply(init_weights)

    def save_model(
        self,
        model_name: str,
        checkpoint,
        transformer: tdt.Transformer,
        overwrite: bool = False,
    ) -> None:

        model_params: mutils.ModelParams = mutils.ModelParams(
            self._n_parameters,
            self._n_energies,
            self._architecture,
            self._activation_function,
            filter_size=self._filter_size,
            kernel_size=self._kernel_size,
            max_pool_kernel_size=self._max_pool_kernel_size,
            max_pool_all=self._max_pool_all,
            output_activation=self._output_activation,
            conv_activation_function=self._conv_activation_function,
            conv_output_activation=self._conv_output_activation,
            use_batch_norm=self._use_batch_norm,
            dropout=self._dropout,
            fc_layer_size=self._fc_layer_size,
            use_scoring_rule=self._use_scoring_rule,
            use_skip_connections=self._use_skip_connections,
        )

        model_storage: mutils.ModelStorage = mutils.ModelStorage(
            model_params, transformer, checkpoint["state_dict"]
        )

        model_storage.save_to_user_dir(model_name, overwrite)
