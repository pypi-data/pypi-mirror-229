import numpy as np
from inspect import signature
import copy
from ..structure.edge_id import EdgeID
from ..misc.utils import *

class EdgeFunction:
    """
    A class representing an edge function for generating signal transformations along directed edges.

    EdgeFunction encapsulates a function that describes how a signal is transformed along an edge in a
    dynamic graph. It allows for various signal transformations and optionally adds Gaussian noise to the
    output. Edge functions can be matched with EdgeIDs to ensure compatibility with the edge's temporal
    structure.

    Parameters:
        function (callable, optional): The edge transformation function. If not provided, the EdgeFunction
                                      will be created with an empty function.
        indim (int or dict, optional): The input dimensionality of the function. An integer represents the
                                       input dimension for uniform functions, while a dictionary specifies
                                       input dimensions for functions with multiple inputs. Default is None.
        outdim (int, optional): The output dimensionality of the function (default is 1).
        gauss_loc (float, optional): The mean (loc) of the Gaussian noise (default is 0).
        gauss_scl (float, optional): The scale (standard deviation) of the Gaussian noise (default is 1).
        replace (bool, optional): Whether to replace existing edges with the same EdgeID in the graph
                                  (default is False).
        rng (numpy.random.Generator or int, optional): The random number generator to use for noise
                                                      generation. If an integer is provided, a new
                                                      generator will be created with that seed. If not
                                                      provided, the default generator will be used.

    Attributes:
        indim (int or dict): The input dimensionality of the function.
        outdim (int): The output dimensionality of the function.
        replace (bool): Whether existing edges with the same EdgeID should be replaced.
        gauss_loc (float): The mean (loc) of the Gaussian noise.
        gauss_scl (float): The scale (standard deviation) of the Gaussian noise.
        rng (numpy.random.Generator): The random number generator used for noise generation.

    Methods:
        __call__(self, with_noise=False, **kwargs): Apply the edge function to input data with optional noise.
        match_with(self, eid): Check if the EdgeFunction is compatible with an EdgeID.
        __str__(self): Get a string representation of the EdgeFunction.

    Class Methods:
        Identity(cls): Create an EdgeFunction that represents an identity transformation.
        Sweep(cls): Create an EdgeFunction that sweeps to zero (sets all values to zero).
        Step(cls, scale, up=np.inf, low=-np.inf): Create an EdgeFunction for a step function with optional bounds.
        Scale(cls, scl): Create an EdgeFunction for scaling input values.
        Grad(cls, length): Create an EdgeFunction for computing the gradient of input signals.
        SawtoothFromStep(cls, height=1, length=1): Create an EdgeFunction to convert step signals to sawtooth.

    Example Usage:
        # Create an EdgeFunction for an identity transformation
        identity_function = EdgeFunction.Identity()

        # Apply the function to input data
        output_signal = identity_function(with_noise=True, input_data=[1, 2, 3])

        # Create an EdgeFunction for scaling input values
        scaling_function = EdgeFunction.Scale(scl=2)

        # Check compatibility with an EdgeID
        edge_id = EdgeID([(0, 'A'), (1, 'B')])  # Example EdgeID
        is_compatible = scaling_function.match_with(edge_id)
    """

    def __init__(self, function=None, indim=None, outdim=1, gauss_loc=0, gauss_scl=1, replace=False, rng=None, **params):
        self._signature = signature(function) if function else None
        self._function = function
        self._indim = indim
        self._outdim = outdim
        self._params = params
        self._replace = replace
        self.gauss_loc = gauss_loc
        self.gauss_scl = gauss_scl

        # Random Gaussian noise generator
        if isinstance(rng, int):
            self.rng = np.random.default_rng(rng)
        elif rng is not None:
            self.rng = rng
        else:
            self.rng = np.random.default_rng()

    def __call__(self, with_noise=False, **kwargs):
        """
        Apply the edge function to input data with optional Gaussian noise.

        Parameters:
            with_noise (bool, optional): If True, Gaussian noise will be added to the output (default is False).
            **kwargs: Keyword arguments representing input data for the function.

        Returns:
            numpy.ndarray: The transformed output data.

        Example Usage:
            # Apply the function to input data
            output_signal = edge_function(with_noise=True, input_data=[1, 2, 3])
        """
        if isinstance(self._indim, int):
            result = self._function(list(kwargs.values())[0], **self._params)
        else:
            bound_args = self._signature.bind_partial(**kwargs)
            bound_args.apply_defaults()

            merged_params = self._params.copy()
            merged_params.update(bound_args.kwargs)
            result = self._function(**merged_params)

        result = np.array(result).reshape((-1))

        if with_noise:
            return result + self.rng.normal(self.gauss_loc, self.gauss_scl, result.shape)
        else:
            return result

    def __str__(self):
        """
        Get a string representation of the EdgeFunction.

        Returns:
            str: A string representing the EdgeFunction.

        Example Usage:
            # Get a string representation of the EdgeFunction
            function_string = str(edge_function)
        """
        return f'EdgeFunction: {self._function.__name__}'

    def match_with(self, eid):
        """
        Check if the EdgeFunction is compatible with an EdgeID.

        The EdgeFunction is considered compatible if it can operate on the temporal structure described by
        the EdgeID.

        Parameters:
            eid (EdgeID): The EdgeID to check compatibility with.

        Returns:
            bool: True if the EdgeFunction is compatible with the EdgeID; otherwise, False.

        Example Usage:
            # Check compatibility with an EdgeID
            edge_id = EdgeID([(0, 'A'), (1, 'B')])  # Example EdgeID
            is_compatible = edge_function.match_with(edge_id)
        """
        assert isinstance(eid, EdgeID), "Only EdgeID is supported"
        if isinstance(self._indim, int):
            return len(eid.lag_origins) == 1 and self._indim <= 1 + eid.lag_origins[0][0]  # 1 extra for the instantaneous value
        else:
            origins = {item[1] for item in eid.lag_origins}
            if origins != self._indim.keys():
                return False
            else:
                return all(self._indim[lo_item[1]] <= 1 + lo_item[0] for lo_item in eid.lag_origins)

    @property
    def indim(self):
        """
        Get a deep copy of the input dimensionality of the EdgeFunction.

        Returns:
            int or dict: The input dimensionality of the EdgeFunction.

        Example Usage:
            # Get the input dimensionality of the EdgeFunction
            input_dimension = edge_function.indim
        """
        return copy.deepcopy(self._indim)

    @property
    def outdim(self):
        """
        Get the output dimensionality of the EdgeFunction.

        Returns:
            int: The output dimensionality of the EdgeFunction.

        Example Usage:
            # Get the output dimensionality of the EdgeFunction
            output_dimension = edge_function.outdim
        """
        return self._outdim

    @property
    def replace(self):
        """
        Get whether existing edges with the same EdgeID should be replaced.

        Returns:
            bool: True if existing edges with the same EdgeID should be replaced; otherwise, False.

        Example Usage:
            # Check if existing edges should be replaced
            should_replace = edge_function.replace
        """
        return self._replace

    ################################################################
    #region static
    @classmethod
    def Identity(cls):
        """
        Create an EdgeFunction that represents an identity transformation.

        Returns:
            EdgeFunction: An EdgeFunction instance representing an identity transformation.

        Example Usage:
            identity_function = EdgeFunction.Identity()
        """
        return cls(identity, indim=1, outdim=1)

    @classmethod
    def Sweep(cls):
        """
        Create an EdgeFunction that sweeps to zero (sets all values to zero).

        Returns:
            EdgeFunction: An EdgeFunction instance representing a sweep to zero.

        Example Usage:
            sweep_function = EdgeFunction.Sweep()
        """
        return cls(np.zeros_like, indim=1, outdim=1)

    @classmethod
    def Step(cls, scale, up=np.inf, low=-np.inf):
        """
        Create an EdgeFunction for a step function with optional bounds.

        Parameters:
            scale (float): The scaling factor for the step function.
            up (float, optional): The upper bound for the step function (default is positive infinity).
            low (float, optional): The lower bound for the step function (default is negative infinity).

        Returns:
            EdgeFunction: An EdgeFunction instance representing a step function.

        Example Usage:
            step_function = EdgeFunction.Step(scale=2, up=5, low=0)
        """
        return cls(bound_it, indim=1, outdim=1, scale=scale, up=up, low=low)

    @classmethod
    def Scale(cls, scl):
        """
        Create an EdgeFunction for scaling input values.

        Parameters:
            scl (float): The scaling factor for input values.

        Returns:
            EdgeFunction: An EdgeFunction instance representing a scaling transformation.

        Example Usage:
            scaling_function = EdgeFunction.Scale(scl=2)
        """
        return cls(scale, indim=1, outdim=1, scl=scl)

    @classmethod
    def Grad(cls, length):
        """
        Create an EdgeFunction for computing the gradient of input signals.

        Parameters:
            length (int): The input dimensionality and the length of the gradient output.

        Returns:
            EdgeFunction: An EdgeFunction instance representing a gradient computation.

        Example Usage:
            gradient_function = EdgeFunction.Grad(length=3)
        """
        return cls(np.gradient, indim=length, outdim=length)

    @classmethod
    def SawtoothFromStep(cls, height=1, length=1):
        """
        Create an EdgeFunction to convert step signals to sawtooth signals.

        Parameters:
            height (float, optional): The height of the sawtooth wave (default is 1).
            length (int, optional): The length of the input and output signals (default is 1).

        Returns:
            EdgeFunction: An EdgeFunction instance representing the conversion.

        Example Usage:
            sawtooth_function = EdgeFunction.SawtoothFromStep(height=2, length=3)
        """
        return cls(step2sawtooth, indim=length, outdim=length, height=height)
    #endregion
    ################################################################
