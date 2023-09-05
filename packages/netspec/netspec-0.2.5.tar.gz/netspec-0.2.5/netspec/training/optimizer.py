from typing import Optional

import torch
from torch.optim.lr_scheduler import SequentialLR, ReduceLROnPlateau


class OptimizerConfig:
    def __init__(
        self,
        optimizer,
        learning_rate: float,
        on_step: bool = False,
        **optimizer_args,
    ) -> None:

        """TODO describe function

        :param optimizer:
        :type optimizer:
        :param learning_rate:
        :type learning_rate: float
        :param on_step:
        :type on_step: bool
        :returns:

        """
        self._optimizer = optimizer
        self._scheduler_class = None
        self._learning_rate = learning_rate
        self._on_step: bool = on_step

        self._optimizer_args = optimizer_args

        self._trainer_args = None

    def add_scheduler(
        self,
        scheduler_class,
        reduce_on_plateau: bool = False,
        milestone=None,
        **kwargs,
    ) -> None:

        """TODO describe function

        :param scheduler_class:
        :type scheduler_class:
        :param reduce_on_plateau:
        :type reduce_on_plateau: bool
        :param milestone:
        :type milestone:
        :returns:

        """
        self._scheduler_class = scheduler_class
        self._scheduler_args = kwargs
        self._reduce_on_plateau: bool = reduce_on_plateau
        self._milestone = milestone

    def trainer_access(self, **trainer_args):

        self._trainer_args = trainer_args

    @property
    def learning_rate(self) -> float:
        return self._learning_rate

    def optim_dict(self, parameters, trainer):

        """TODO describe function

        :param parameters:
        :type parameters:
        :param trainer:
        :type trainer:
        :returns:

        """
        optimizer = self._optimizer(
            parameters, lr=self._learning_rate, **self._optimizer_args
        )

        out = {"optimizer": optimizer}

        if self._scheduler_class is not None:

            trainer_args = {}

            if self._trainer_args is not None:

                for k, v in self._trainer_args.items():

                    trainer_args[k] = getattr(trainer, v)

                print(trainer_args)

            if not self._reduce_on_plateau:

                out["lr_scheduler"] = dict(
                    scheduler=self._scheduler_class(
                        optimizer, **self._scheduler_args, **trainer_args
                    ),
                    monitor="train_loss",
                )

            else:

                sched_1 = self._scheduler_class(
                    optimizer, **self._scheduler_args, **trainer_args
                )

                sched_2 = ReduceLROnPlateau(optimizer, patience=15)

                seq_sched = SequentialLR(
                    optimizer,
                    schedulers=[sched_1, sched_2],
                    milestones=[self._milestone],
                )

                out["lr_scheduler"] = dict(
                    scheduler=seq_sched,
                    monitor="val_accuracy",
                )

            if self._on_step:
                out["lr_scheduler"]["interval"] = "step"

        out["monitor"] = "train_loss"

        return out


class NAdamOptimizer(OptimizerConfig):
    def __init__(
        self, learning_rate: float, rate: Optional[float] = None, **kwargs
    ) -> None:

        super().__init__(torch.optim.NAdam, learning_rate, **kwargs)

        if rate is not None:

            f = lambda epoch: rate**epoch

            self.add_scheduler(torch.optim.lr_scheduler.LambdaLR, lr_lambda=f)


class AdamOptimizer(OptimizerConfig):
    def __init__(
        self, learning_rate: float, rate: Optional[float] = None, **kwargs
    ) -> None:

        super().__init__(torch.optim.Adam, learning_rate, **kwargs)

        if rate is not None:

            f = lambda epoch: rate**epoch

            self.add_scheduler(torch.optim.lr_scheduler.LambdaLR, lr_lambda=f)


class AdamPlateauOptimizer(OptimizerConfig):
    def __init__(
        self,
        learning_rate: float,
        patience=10,
        cooldown=0,
        min_lr=1e-10,
        **kwargs,
    ) -> None:

        super().__init__(torch.optim.Adam, learning_rate, **kwargs)

        self.add_scheduler(
            torch.optim.lr_scheduler.ReduceLROnPlateau,
            patience=patience,
            cooldown=cooldown,
            min_lr=min_lr,
        )


class NAdamPlateauOptimizer(OptimizerConfig):
    def __init__(self, learning_rate: float, patience=10, **kwargs) -> None:

        super().__init__(torch.optim.NAdam, learning_rate, **kwargs)

        self.add_scheduler(
            torch.optim.lr_scheduler.ReduceLROnPlateau, patience=patience
        )


class AdamWPlateauOptimizer(OptimizerConfig):
    def __init__(
        self,
        learning_rate: float,
        patience=10,
        cooldown=0.0,
        min_lr=1e-10,
        **kwargs,
    ) -> None:

        super().__init__(torch.optim.AdamW, learning_rate, **kwargs)

        self.add_scheduler(
            torch.optim.lr_scheduler.ReduceLROnPlateau,
            patience=patience,
            cooldown=cooldown,
            min_lr=min_lr,
        )


class AdamWOptimizer(OptimizerConfig):
    def __init__(
        self, learning_rate: float, rate: Optional[float] = None, **kwargs
    ) -> None:

        super().__init__(torch.optim.AdamW, learning_rate, **kwargs)

        if rate is not None:

            f = lambda epoch: rate**epoch

            self.add_scheduler(torch.optim.lr_scheduler.LambdaLR, lr_lambda=f)


class AdamOptimizerT2(OptimizerConfig):
    def __init__(
        self,
        learning_rate: float,
        min_rate: float = 1e-5,
        max_rate: float = 1e-2,
        step_size_up: int = 1000,
        **kwargs,
    ) -> None:

        super().__init__(torch.optim.NAdam, learning_rate, on_step=True)

        self.add_scheduler(
            torch.optim.lr_scheduler.CyclicLR,
            base_lr=min_rate,
            max_lr=max_rate,
            step_size_up=step_size_up,
            cycle_momentum=False,
            mode="triangular2",
        )


class AdamWOptimizerT2(OptimizerConfig):
    def __init__(
        self,
        learning_rate: float,
        min_rate: float = 1e-5,
        max_rate: float = 1e-2,
        step_size_up: int = 1000,
        mode="triangular2",
        reduce_on_plateau: bool = False,
        milestone: int = 1,
        **kwargs,
    ) -> None:

        super().__init__(
            torch.optim.AdamW, learning_rate, on_step=True, **kwargs
        )

        self.add_scheduler(
            torch.optim.lr_scheduler.CyclicLR,
            reduce_on_plateau=reduce_on_plateau,
            milestone=milestone,
            base_lr=min_rate,
            max_lr=max_rate,
            step_size_up=step_size_up,
            cycle_momentum=False,
            mode=mode,
        )


class AdamWOptimizerOneCycle(OptimizerConfig):
    def __init__(
        self, learning_rate: float, max_rate: float = 1e-2, **kwargs
    ) -> None:

        super().__init__(
            torch.optim.AdamW, learning_rate, on_step=True, **kwargs
        )

        self.add_scheduler(
            torch.optim.lr_scheduler.OneCycleLR,
            max_lr=max_rate,
        )

        self.trainer_access(total_steps="estimated_stepping_batches")
