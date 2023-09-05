import base64
from typing import List, Optional, Tuple, Union

import dill
import h5py
import numba as nb
import numpy as np
import scipy.interpolate as interp
from joblib import Parallel, delayed
from ronswanson import Database
from scipy.special import boxcox, inv_boxcox
from sklearn.decomposition import PCA, IncrementalPCA
from tqdm.auto import tqdm

from ..utils.logging import setup_logger

log = setup_logger(__name__)


def first_last_nonzero(arr, axis, invalid_val=-1):
    mask = arr > 0.0

    first = np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

    mask = np.flip(mask, axis=1)

    last = np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)
    return first, -last


def min_max_fit(X) -> Tuple[np.ndarray]:

    x_min = X.min(axis=0)
    x_max = X.max(axis=0)

    return x_min, x_max


def standard_fit(X, robust: bool = False) -> Tuple[np.ndarray]:

    if not robust:

        shift = np.mean(X, axis=0)
        scale = np.std(X, axis=0)

    else:

        shift = np.median(X, axis=0)

        q1 = np.percentile(X, 25, axis=0)
        q3 = np.percentile(X, 75, axis=0)
        scale = q3 - q1

    return shift, scale


@nb.njit(cache=True)
def standard_transform(X, shift, scale) -> np.ndarray:

    return (X - shift) / scale


@nb.njit(cache=True)
def standard_inverse(X, shift, scale) -> np.ndarray:

    return X * scale + shift


@nb.njit(cache=True)
def min_max_transform(X, x_min, min_max_difference) -> np.ndarray:

    x_std = (X - x_min) / min_max_difference

    return x_std


@nb.njit(cache=True)
def min_max_inverse(X_scaled, x_min, x_max) -> np.ndarray:

    return X_scaled * (x_max - x_min) + x_min


@nb.njit(cache=True)
def arcsinh(x) -> np.ndarray:
    return np.arcsinh(x)


@nb.njit(cache=True)
def sinh(x) -> np.ndarray:
    return np.sinh(x)


class Transformer:
    def __init__(
        self,
        param_min: np.ndarray,
        param_max: np.ndarray,
        param_shift: Optional[np.ndarray],
        param_scale: Optional[np.ndarray],
        value_min: Optional[np.ndarray],
        value_max: Optional[np.ndarray],
        value_shift: Optional[np.ndarray],
        value_scale: Optional[np.ndarray],
        energies: np.ndarray,
        parameter_names: Optional[List[str]] = None,
        pca_matrix: Optional[np.ndarray] = None,
        use_vFv: bool = False,
        shift_parameters: bool = True,
        box_cox_lambda: Optional[float] = None,
        use_log10: Optional[bool] = False,
    ) -> None:

        """
        Class that handles transformation from
        training to execution space

        :param param_min:
        :type param_min: np.ndarray
        :param param_max:
        :type param_max: np.ndarray
        :param param_shift:
        :type param_shift: Optional[np.ndarray]
        :param param_scale:
        :type param_scale: Optional[np.ndarray]
        :param value_min:
        :type value_min: Optional[np.ndarray]
        :param value_max:
        :type value_max: Optional[np.ndarray]
        :param value_shift:
        :type value_shift: Optional[np.ndarray]
        :param value_scale:
        :type value_scale: Optional[np.ndarray]
        :param energies:
        :type energies: np.ndarray
        :param parameter_names:
        :type parameter_names: Optional[List[str]]
        :param pca_matrix:
        :type pca_matrix: Optional[np.ndarray]
        :param use_vFv:
        :type use_vFv: bool
        :param shift_parameters:
        :type shift_parameters: bool
        :returns:

        """
        self._param_min = param_min
        self._param_max = param_max

        self._shift_parameters: bool = shift_parameters

        self._param_shift = param_shift
        self._param_scale = param_scale

        # if the difference is zero, this will
        # blow up, so we fix it to one

        self._param_min_max_difference = param_max - param_min

        idx = self._param_min_max_difference == 0.0

        self._param_min_max_difference[idx] = 1

        self._value_min = value_min
        self._value_max = value_max

        self._value_shift = value_shift
        self._value_scale = value_scale

        if value_min is not None:

            self._value_min_max_difference = value_max - value_min

            idx = self._value_min_max_difference == 0.0

            self._value_min_max_difference[idx] = 1

        else:

            self._value_min_max_difference = None

        if value_shift is not None:

            idx = self._value_scale == 0.0

            self._value_scale[idx] = 1

        self._energies: np.ndarray = energies

        self._parameter_names: Optional[List[str]] = parameter_names

        self._pca_matrix: Optional[np.ndarray] = pca_matrix

        self._use_vFv: bool = use_vFv

        self._box_cox_lambda = box_cox_lambda

        self._use_log10: bool = use_log10

        if box_cox_lambda is None:

            if not use_log10:

                log.debug("using asinh transform")

                self._transform = arcsinh
                self._inverse_transform = sinh

            else:

                log.debug("using log10 transform")

                self._transform = np.log10

                self._inverse_transform = lambda x: np.power(10.0, x)

        else:

            log.debug("using boxcox transform")

            self._transform = lambda x: inv_boxcox(x, box_cox_lambda)
            self._inverse_transform = lambda x: boxcox(x, box_cox_lambda)

        # these are functions that transform the data
        # as a function of the parameters

    @property
    def parameter_names(self) -> Optional[List[str]]:
        return self._parameter_names

    @property
    def energies(self) -> np.ndarray:
        return self._energies

    def to_file(self, file_name: Union[str, h5py.Group]) -> None:

        """TODO describe function

        :param file_name:
        :type file_name: Union[str, h5py.Group]
        :returns:

        """
        if isinstance(file_name, h5py.Group):

            f = file_name

            is_file: bool = False

        else:

            f = h5py.File(file_name, "w")
            is_file = True

        f.attrs["use_vFv"] = self._use_vFv

        if self._box_cox_lambda is not None:

            f.attrs["box_cox_lambda"] = self._box_cox_lambda

        f.attrs["use_log10"] = self._use_log10

        if self._parameter_names is not None:

            for i in range(len(self._parameter_names)):

                f.attrs[f"par_{i}"] = self._parameter_names[i]

        f.create_dataset("param_min", data=self._param_min, compression="gzip")
        f.create_dataset("param_max", data=self._param_max, compression="gzip")

        if self._param_shift is not None:

            f.create_dataset(
                "param_shift", data=self._param_shift, compression="gzip"
            )
            f.create_dataset(
                "param_scale", data=self._param_scale, compression="gzip"
            )

        if self._value_min is not None:

            f.create_dataset(
                "value_min", data=self._value_min, compression="gzip"
            )
            f.create_dataset(
                "value_max", data=self._value_max, compression="gzip"
            )

        if self._value_shift is not None:

            f.create_dataset(
                "value_shift", data=self._value_shift, compression="gzip"
            )
            f.create_dataset(
                "value_scale", data=self._value_scale, compression="gzip"
            )

        f.create_dataset("energies", data=self._energies, compression="gzip")

        if self._pca_matrix is not None:

            f.create_dataset("pca_matrix", data=self._pca_matrix)

        if is_file:

            f.close()

    @classmethod
    def from_file(cls, file_name: Union[str, h5py.Group]) -> "Transformer":

        if isinstance(file_name, h5py.Group):

            f = file_name

            is_file: bool = False

        else:

            f = h5py.File(file_name, "r")
            is_file = True

        indent = 0

        if "use_vFv" in f.attrs:

            use_vFv = f.attrs["use_vFv"]

            indent += 1

        else:

            use_vFv = False

        if "use_log10" in f.attrs:

            log.debug("found log10 attr")

            use_log10 = f.attrs["use_log10"]

            indent += 1

        else:

            use_log10 = False

        if "box_cox_lambda" in f.attrs:

            box_cox_lambda = f.attrs["box_cox_lambda"]

            indent += 1

        else:

            box_cox_lambda = None

        if "par_0" in f.attrs:

            parameter_names = []

            for i in range(len(f.attrs) - indent):

                parameter_names.append(f.attrs[f"par_{i}"])

        else:

            parameter_names = None

        param_min: np.ndarray = f["param_min"][()]
        param_max: np.ndarray = f["param_max"][()]

        param_shift = None
        param_scale = None

        if "param_shift" in f.keys():

            param_shift: np.ndarray = f["param_shift"][()]
            param_scale: np.ndarray = f["param_scale"][()]

        if "value_min" in f.keys():

            value_min: np.ndarray = f["value_min"][()]
            value_max: np.ndarray = f["value_max"][()]

        else:

            value_min, value_max = None, None

        if "value_shift" in f.keys():

            value_shift: np.ndarray = f["value_shift"][()]
            value_scale: np.ndarray = f["value_scale"][()]

        else:

            value_shift, value_scale = None, None

        energies: np.ndarray = f["energies"][()]

        pca_matrix = None

        if "pca_matrix" in f.keys():

            pca_matrix = f["pca_matrix"][()]

        if is_file:

            f.close()

        return cls(
            param_min=param_min,
            param_max=param_max,
            param_shift=param_shift,
            param_scale=param_scale,
            value_min=value_min,
            value_max=value_max,
            value_shift=value_shift,
            value_scale=value_scale,
            energies=energies,
            parameter_names=parameter_names,
            pca_matrix=pca_matrix,
            use_vFv=use_vFv,
            box_cox_lambda=box_cox_lambda,
            use_log10=use_log10,
        )

    @property
    def param_min(self) -> np.ndarray:

        return self._param_min

    @property
    def param_max(self) -> np.ndarray:
        return self._param_max

    @property
    def param_shift(self) -> Optional[np.ndarray]:
        return self._param_shift

    @property
    def param_scale(self) -> Optional[np.ndarray]:
        return self._param_scale

    @property
    def inverse_transform_function(self) -> Optional[float]:
        return self._inverse_transform_function

    def transform_parameters(self, parameters: np.ndarray) -> np.ndarray:
        """TODO describe function

        :param parameters:
        :type parameters: np.ndarray
        :returns:

        """
        if self._param_shift is not None:

            return standard_transform(
                parameters, self._param_shift, self._param_scale
            )

        else:

            return min_max_transform(
                parameters, self._param_min, self._param_min_max_difference
            )

    def inverse_parameters(
        self, transformed_parameters: np.ndarray
    ) -> np.ndarray:

        """TODO describe function

        :param transformed_parameters:
        :type transformed_parameters: np.ndarray
        :returns:

        """
        if self._param_shift is not None:

            return standard_inverse(
                transformed_parameters, self._param_shift, self._param_scale
            )

        else:

            return min_max_inverse(
                transformed_parameters,
                self._param_min,
                self._param_max,
            )

    def transform_values(
        self, values: np.ndarray, pca: Optional[PCA] = None
    ) -> np.ndarray:

        """TODO describe function

        :param values:
        :type values: np.ndarray
        :param pca:
        :type pca: Optional[PCA]
        :returns:

        """
        if not self._use_vFv:

            values = self._transform(values)

        else:

            values = self._transform(self._energies**2 * values)

        if self._value_shift is not None:
            values = standard_transform(
                values, self._value_shift, self._value_scale
            )

        if pca is not None:

            values = pca.transform(values)

        if self._value_min is not None:

            values = min_max_transform(
                values, self._value_min, self._value_min_max_difference
            )

        return values

    def inverse_values(
        self,
        transformed_values: np.ndarray,
        parameters: Optional[np.ndarray] = None,
    ) -> np.ndarray:

        """TODO describe function

        :param transformed_values:
        :type transformed_values: np.ndarray
        :returns:

        """

        log.debug(f"about to inverse: {transformed_values}")

        if self._value_min is not None:

            transformed_values = min_max_inverse(
                transformed_values, self._value_min, self._value_max
            )

            log.debug(f"applied min max inverse: {transformed_values}")

        if self._pca_matrix is not None:

            transformed_values = np.dot(transformed_values, self._pca_matrix)

        if self._value_shift is not None:

            transformed_values = standard_inverse(
                transformed_values, self._value_shift, self._value_scale
            )

            log.debug(f"applied standard inverse: {transformed_values}")

        if not self._use_vFv:

            inverted_values = self._inverse_transform(transformed_values)

            log.debug(f"applied inverse: {inverted_values}")

        else:

            inverted_values = self._inverse_transform(
                transformed_values / (self._energies**2)
            )

        return inverted_values


class TransformedData:
    def __init__(
        self, params: np.ndarray, values: np.ndarray, transformer: Transformer
    ) -> None:

        """
        Class to hold transformed training data

        :param params:
        :type params: np.ndarray
        :param values:
        :type values: np.ndarray
        :param transformer:
        :type transformer: Transformer
        :returns:

        """
        self._params: np.ndarray = params
        self._values: np.ndarray = values

        self._n_energies: int = len(transformer.energies)
        self._n_parameters: int = params.shape[1]

        self._transformer: Transformer = transformer

    def to_file(self, file_name: str) -> None:

        """
        TODO describe function

        :param file_name:
        :type file_name: str
        :returns:

        """
        with h5py.File(file_name, "w") as f:

            transformer_grp = f.create_group("transformer")

            self._transformer.to_file(transformer_grp)

            f.create_dataset("params", data=self._params, compression="gzip")
            f.create_dataset("values", data=self._values, compression="gzip")

    @classmethod
    def from_file(cls, file_name: str) -> "TransformedData":

        with h5py.File(file_name, "r") as f:

            transformer = Transformer.from_file(f["transformer"])

            params: np.ndarray = f["params"][()]
            values: np.ndarray = f["values"][()]

        return cls(params=params, values=values, transformer=transformer)

    @property
    def values(self) -> np.ndarray:
        return self._values

    @property
    def params(self) -> np.ndarray:
        return self._params

    @property
    def transformer(self) -> Transformer:
        return self._transformer

    @property
    def n_energies(self) -> int:
        return self._n_energies

    @property
    def n_parameters(self) -> int:
        return self._n_parameters


def prepare_training_data(
    database: Database,
    file_name_stub: str,
    normalization_factor: float = 1.0,
    scale_values: bool = True,
    shift_values: bool = True,
    shift_parameters: bool = False,
    n_pca_components: Optional[float] = None,
    pca_split: Optional[int] = None,
    dirty_data_check: bool = False,
    energy_cut: Optional[np.array] = None,
    use_vFv: bool = False,
    n_oversample_points: Optional[int] = None,
    n_oversample_jobs: int = 8,
    robust: bool = False,
    min_value: Optional[float] = None,
    ratio_maximum: Optional[float] = None,
    box_cox_lambda: Optional[float] = None,
    use_log10: bool = False,
    energy_shift: float = 1,
    **sub_selections,
) -> None:

    """

    :param database: ronswanson database
    :type database: Database
    :param file_name_stub: file name stub for training data file
    :type file_name_stub: str
    :param normalization_factor: factor to multiply data by
    :type normalization_factor: float
    :param scale_values: scale the values via min/max
    :type scale_values: bool
    :param shift_values: shift the values by standardization
    :type shift_values: bool
    :param shift_parameters: shift the parameters by standardization
    :type shift_parameters: bool
    :param n_pca_components: number of PCA components to use
    :type n_pca_components: Optional[float]
    :param pca_split: incremental PCA shift
    :type pca_split: Optional[int]
    :param dirty_data_check: check for bad data in simulations and clean
    :type dirty_data_check: bool
    :param energy_cut: index array for cutting on energy
    :type energy_cut: Optional[np.array]
    :param use_vFv: work in vFv space
    :type use_vFv: bool
    :param n_oversample_points: oversample the data with this many points
    :type n_oversample_points: Optional[int]
    :param n_oversample_jobs: number of parallel jobs
    :type n_oversample_jobs: int
    :param robust: use robust standardization
    :type robust: bool
    :param min_value:
    :returns:

    """
    if sub_selections:

        database = database.new_from_selections(**sub_selections)

    # if energy cut is none

    if energy_cut is None:

        energy_cut = np.ones_like(database.energy_grid, dtype=bool)

    # remove all zero rows
    zero_idx = database.values.sum(axis=1) == 0

    # if we still have dirty data

    if dirty_data_check:

        ok_idx = np.ones(database.n_entries, dtype=bool)

        first, last = first_last_nonzero(database.values, axis=1)

        for i, datum in enumerate(database.values):

            if np.any(datum[first[i] : last[i]] == 0):

                ok_idx[i] = 0

        log.info(f"there were {(~ok_idx).sum()} dirty entries")

        if (~ok_idx).sum() > 0:

            with h5py.File(f"{file_name_stub}_dirty_log.h5", "w") as f:

                f.create_dataset(
                    "parameters",
                    data=database.grid_points[~ok_idx],
                    compression="gzip",
                )
                f.create_dataset(
                    "values", data=database.values[~ok_idx], compression="gzip"
                )
                f.create_dataset(
                    "energy_grid", data=database.energy_grid, compression="gzip"
                )

                f.create_dataset(
                    "run_id",
                    data=np.arange(database.n_entries, dtype=int)[~ok_idx],
                )

            log.info(f"bad entries logged to {file_name_stub}_dirty_log.h5")

        zero_idx = zero_idx & ok_idx

    log.info("scaling parameters")

    # scale the parmeters
    param_min, param_max = min_max_fit(database.grid_points[~zero_idx])

    param_shift, param_scale = None, None

    if shift_parameters:

        param_shift, param_scale = standard_fit(database.grid_points[~zero_idx])

    # arcsinh the data
    # this is similar to a log transform
    # but it preserves zeros

    input_data = (
        database.values[~zero_idx].astype("float64") * normalization_factor
    )

    if min_value is not None:

        input_data[input_data < min_value] = 0.0

        log.info(f"values below {min_value} have been set to zero")

    if ratio_maximum is not None:

        peak_data = np.log10(database.energy_grid**2 * input_data)

        nano = np.isfinite(peak_data)

        peak_data[~nano] = -999.0

        peak_maxima = np.max(peak_data, axis=1)

        idx = peak_data < (peak_maxima[:, np.newaxis] - np.log10(ratio_maximum))

        input_data[idx] = 0.0

    if (~np.isfinite(input_data)).sum() > 0:

        msg = "There are infinite values in the input data"

        log.error(msg)

        raise RuntimeError(msg)

    input_data = input_data[..., energy_cut]

    if box_cox_lambda is None:

        if not use_log10:

            transformed_data = arcsinh(input_data)

        else:

            input_data[input_data <= 0] = 1e-99

            transformed_data = np.log10(input_data)

    else:

        transformed_data = inv_boxcox(input_data, box_cox_lambda)

    if n_oversample_points is not None:

        def _interpolate(values):

            x = np.arange(len(values))

            spl = interp.PchipInterpolator(x, values)

            new_x = np.linspace(0, len(values), n_oversample_points)

            return spl(new_x).tolist()

        new_transformed_data = Parallel(n_jobs=n_oversample_jobs)(
            delayed(_interpolate)(transformed_data[i])
            for i in tqdm(range(len(transformed_data)))
        )

        transformed_data = np.array(new_transformed_data)

    # transformed_data = transformed_data[..., energy_cut]

    value_shift, value_scale = None, None

    if shift_values:

        log.info("standardizing values")

        value_shift, value_scale = standard_fit(transformed_data, robust=robust)

        # all the values will be 0 anyhow
        idx = value_scale == 0
        value_scale[idx] = 1

        transformed_data = standard_transform(
            transformed_data, value_shift, value_scale
        )

    pca_matrix = None
    pca = None

    if n_pca_components is not None:

        log.info("performing pca transformation on data")

        if pca_split is None:

            pca = PCA(n_components=n_pca_components)

            pca.fit(transformed_data)

        else:

            log.info("performing partial fit")

            pca = IncrementalPCA(
                n_components=n_pca_components, batch_size=pca_split, copy=True
            )

            n_per_spilt = int(np.floor(transformed_data.shape[0] / pca_split))

            log.info(f"n per split: {n_per_spilt}")

            pca.fit(transformed_data)

        transformed_data = pca.transform(transformed_data)

        pca_matrix = pca.components_

    # now min, max data

    if scale_values:

        log.info("scaling values")

        value_min, value_max = min_max_fit(transformed_data)

        value_min_max_difference = value_max - value_min

        idx = value_min_max_difference == 0.0

        value_min_max_difference[idx] = 1

        transformed_data = min_max_transform(
            transformed_data, value_min, value_min_max_difference
        )

    else:

        value_min, value_max = None, None

    # if we are going to oversample,
    # then we need to create new energies

    if n_oversample_points is not None:

        ene_interp = interp.interp1d(
            np.arange(len(database.energy_grid[energy_cut])),
            database.energy_grid[energy_cut],
            bounds_error=False,
            fill_value="extrapolate",
        )

        energies = ene_interp(
            np.linspace(
                0,
                len(database.energy_grid[energy_cut]) - 1,
                n_oversample_points,
            )
        )

    else:

        energies = database.energy_grid[energy_cut]

    # now squash the it all

    transformer: Transformer = Transformer(
        param_min=param_min,
        param_max=param_max,
        param_shift=param_shift,
        param_scale=param_scale,
        value_min=value_min,
        value_max=value_max,
        value_shift=value_shift,
        value_scale=value_scale,
        energies=energies * energy_shift,
        parameter_names=database.parameter_names,
        pca_matrix=pca_matrix,
        use_vFv=use_vFv,
        box_cox_lambda=box_cox_lambda,
        use_log10=use_log10
        #        inverse_transform_function=inverse_transform_function,
    )

    log.info("normalizing")

    # squashed_data = transformer.transform_values(
    #     input_data,
    #     pca=pca,
    # )

    squashed_params = transformer.transform_parameters(
        database.grid_points[~zero_idx]
    )

    log.info("writing training data")

    transformed_data: TransformedData = TransformedData(
        params=squashed_params, values=transformed_data, transformer=transformer
    )

    transformed_data.to_file(f"{file_name_stub}.h5")
    transformer.to_file(f"{file_name_stub}_transformer.h5")
