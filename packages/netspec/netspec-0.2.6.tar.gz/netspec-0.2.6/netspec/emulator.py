import collections

from pathlib import Path
from typing import Optional

import astropy.units as u

import scipy.interpolate as interp

import numpy as np
from astromodels.core.parameter import Parameter
from astromodels.core.property import FunctionProperty
from astromodels.functions import Function1D, FunctionMeta
from astromodels.functions.function import Function1D, FunctionMeta
from astromodels.utils import get_user_data_path


from .utils.logging import setup_logger
from .utils.model_utils import ModelStorage

log = setup_logger(__name__)


class MissingDataFile(RuntimeError):
    pass


class EmulatorModel(Function1D, metaclass=FunctionMeta):

    r"""
    description :
        An emulator model
    latex :
        $n.a.$
    parameters :
        K :
            desc : Normalization (freeze this to 1 if the template provides the normalization by itself)
            initial value : 1.0
        scale :
            desc : Scale for the independent variable. The templates are handled as if they contains the fluxes
                   at E = scale * x.This is useful for example when the template describe energies in the rest
                   frame, at which point the scale describe the transformation between rest frame energy and
                   observer frame energy. Fix this to 1 to neutralize its effect.
            initial value : 1.0
            min : 1e-5

        redshift:
            desc: redshift the energies
            initial value: 0.
            min: 0
            fix: True

    properties:
        source_frame:
            desc: is the emission in the lab or source frame
            initial value: False
            allowed values:
                - True
                - False
            function: _set_frame

        divide_by_scale:
            desc: divide the final output by scale to conserve energy
            initial value: True
            allowed values:
                - True
                - False
            function: _set_scale


    """

    def _custom_init_(
        self,
        model_name: str,
        other_name: Optional[str] = None,
        log_interp: bool = True,
        as_raw_model: bool = False,
    ):
        """
        Custom initialization for this model

        :param model_name: the name of the model, corresponding to the root of the .h5 file in the data directory
        :param other_name: (optional) the name to be used as name of the model when used in astromodels. If None
        (default), use the same name as model_name
        :return: none
        """

        self._log_interp: bool = log_interp

        self._as_raw_model: bool = as_raw_model

        # Get the data directory

        data_dir_path: Path = get_user_data_path()

        # Sanitize the data file

        filename_sanitized = data_dir_path.absolute() / f"{model_name}.h5"

        if not filename_sanitized.exists():

            log.error(f"The data file {filename_sanitized} does not exists.")

            raise MissingDataFile(
                f"The data file {filename_sanitized} does not exists."
            )

        # Open the template definition and read from it

        self._data_file: Path = filename_sanitized

        # use the file shadow to read

        self._model_storage: ModelStorage = ModelStorage.from_file(
            filename_sanitized
        )

        self._energies = self._model_storage.energies

        function_definition = collections.OrderedDict()

        description = "blah"

        function_definition["description"] = description

        function_definition["latex"] = "n.a."

        # Now build the parameters according to the content of the parameter grid

        parameters = collections.OrderedDict()

        parameters["K"] = Parameter("K", 1.0)
        parameters["scale"] = Parameter("scale", 1.0)
        parameters["redshift"] = Parameter("redshift", 0.0, free=False)

        for i, parameter_name in enumerate(
            self._model_storage.transformer.parameter_names
        ):

            par_range = np.array(
                [
                    self._model_storage.transformer.param_min[i],
                    self._model_storage.transformer.param_max[i],
                ]
            )

            parameters[parameter_name] = Parameter(
                parameter_name,
                np.median(par_range),
                min_value=par_range.min(),
                max_value=par_range.max(),
            )

        properties = collections.OrderedDict()
        properties["source_frame"] = FunctionProperty(
            "source_frame",
            "is the emission in the lab or source frame",
            False,
            [True, False],
            eval_func="_set_frame",
        )
        properties["divide_by_scale"] = FunctionProperty(
            "divide_by_scale",
            "divide the final output by scale to conserve energy",
            True,
            [True, False],
            eval_func="_set_scale",
        )

        if other_name is None:

            super(EmulatorModel, self).__init__(
                model_name,
                function_definition,
                parameters,
                properties=properties,
            )

        else:

            super(EmulatorModel, self).__init__(
                other_name,
                function_definition,
                parameters,
                properties=properties,
            )

    def _set_scale(self):

        self._divide_by_scale: bool = self.divide_by_scale.value

    def _set_frame(self):

        self._source_frame: bool = self.source_frame.value

    def _set_units(self, x_unit, y_unit):

        self.K.unit = y_unit

        self.scale.unit = 1 / x_unit
        self.redshift.unit = u.dimensionless_unscaled

    def _redshift_scaling(self, z) -> float:

        if self._source_frame:
            return 1.0 / (1 + z)

        else:

            return 1.0 + z

    # This function will be substituted during construction by another version with
    # all the parameters of this template

    def evaluate(self, x, K, scale, redshift, *args):

        if not self._as_raw_model:
            net_output = self._model_storage.evaluate(
                np.array(args, dtype=np.float32)
            )

        else:

            net_output = self._model_storage.evaluate_raw(
                np.array(args, dtype=np.float32)
            )
        # clear the crap out

        if not self._as_raw_model:

            idx = (net_output <= 0) | (~np.isfinite(net_output))
            net_output[idx] = 1e-99

        if isinstance(x, u.Quantity):

            # models are always saved with energy in keV. We need to transform it to
            # a dimensionless quantity (actually we take the .value property) because otherwise
            # the logarithm below will fail.

            energies = np.array(
                x.to("keV").value, ndmin=1, copy=False, dtype=float
            )

            # Same for the scale

            scale = scale.to(1 / u.keV).value

        else:

            energies = x

        e_tilde = self._energies * scale

        factor = 1.0

        if self._divide_by_scale:

            # this conserves energy if it is
            # not explicit in the model itself

            factor = 1.0 / scale

        if self._log_interp:

            interpolator = interp.PchipInterpolator(np.log(e_tilde), net_output)

            return (
                K
                * interpolator(
                    np.log(energies * self._redshift_scaling(redshift))
                )
                * factor
            )

        else:

            interpolator = interp.PchipInterpolator(e_tilde, net_output)

            return (
                K
                * interpolator(energies * self._redshift_scaling(redshift))
                * factor
            )
