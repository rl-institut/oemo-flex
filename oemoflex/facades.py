from oemof.solph import sequence, Sink, Source, Flow, Bus
from oemof.solph.components import GenericStorage
from oemof.tabular.facades import Facade


class Reservoir(GenericStorage, Facade):
    r""" A Reservoir storage unit, that is initially half full.

    Note that the investment option is not available for this facade at
    the current development state.

    Parameters
    ----------
    bus: oemof.solph.Bus
        An oemof bus instance where the storage unit is connected to.
    storage_capacity: numeric
        The total storage capacity of the storage (e.g. in MWh)
    capacity: numeric
        Installed production capacity of the turbine installed at the
        reservoir
    efficiency: numeric
        Efficiency of the turbine converting inflow to electricity
        production, default: 1
    profile: array-like
        Absolute inflow profile of inflow into the storage
    input_parameters: dict
        Dictionary to specifiy parameters on the input edge. You can use
        all keys that are available for the  oemof.solph.network.Flow class.
    output_parameters: dict
        see: input_parameters


    The reservoir is modelled as a storage with a constant inflow:

    .. math::

        x^{level}(t) =
        x^{level}(t-1) \cdot (1 - c^{loss\_rate}(t))
        + x^{profile}(t) - \frac{x^{flow, out}(t)}{c^{efficiency}(t)}
        \qquad \forall t \in T

    .. math::
        x^{level}(0) = 0.5 \cdot c^{capacity}

    The inflow is bounded by the exogenous inflow profile. Thus if the inflow
    exceeds the maximum capacity of the storage, spillage is possible by
    setting :math:`x^{profile}(t)` to lower values.

    .. math::
        0 \leq x^{profile}(t) \leq c^{profile}(t) \qquad \forall t \in T


    The spillage of the reservoir is therefore defined by:
    :math:`c^{profile}(t) - x^{profile}(t)`.

    Note
    ----
    As the Reservoir is a sub-class of `oemof.solph.GenericStorage` you also
    pass all arguments of this class.


    Examples
    --------
    Basic usage examples of the GenericStorage with a random selection of
    attributes. See the Flow class for all Flow attributes.

    >>> from oemof import solph
    >>> from oemof.tabular import facades
    >>> my_bus = solph.Bus('my_bus')
    >>> my_reservoir = Reservoir(
    ...     label='my_reservoir',
    ...     bus=my_bus,
    ...     carrier='water',
    ...     tech='reservoir',
    ...     storage_capacity=1000,
    ...     capacity=50,
    ...     profile=[1, 2, 6],
    ...     loss_rate=0.01,
    ...     initial_storage_level=0,
    ...     max_storage_level = 0.9,
    ...     efficiency=0.93)

    """

    def __init__(self, *args, **kwargs):

        kwargs.update(
            {
                "_facade_requires_": [
                    "bus",
                    "carrier",
                    "tech",
                    "profile",
                    "efficiency",
                ]
            }
        )
        super().__init__(*args, **kwargs)

        self.storage_capacity = kwargs.get("storage_capacity")

        self.capacity = kwargs.get("capacity")

        self.efficiency = kwargs.get("efficiency", 1)

        self.profile = kwargs.get("profile")

        self.input_parameters = kwargs.get("input_parameters", {})

        self.output_parameters = kwargs.get("output_parameters", {})

        self.expandable = bool(kwargs.get("expandable", False))

        self.build_solph_components()

    def build_solph_components(self):
        """
        """
        self.nominal_storage_capacity = self.storage_capacity

        self.outflow_conversion_factor = sequence(self.efficiency)

        if self.expandable:
            raise NotImplementedError(
                "Investment for reservoir class is not implemented."
            )

        inflow = Source(
            label=self.label + "-inflow",
            outputs={
                self: Flow(nominal_value=1, max=self.profile, fixed=False)
            },
        )

        self.outputs.update(
            {
                self.bus: Flow(
                    nominal_value=self.capacity, **self.output_parameters
                )
            }
        )

        self.subnodes = (inflow,)
