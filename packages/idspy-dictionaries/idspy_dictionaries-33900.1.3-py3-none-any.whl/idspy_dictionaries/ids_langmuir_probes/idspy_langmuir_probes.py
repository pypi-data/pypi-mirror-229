# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class DataEntry(IdsBaseClass):
    """
    Definition of a data entry.

    :ivar user: Username
    :ivar machine: Name of the experimental device to which this data is
        related
    :ivar pulse_type: Type of the data entry, e.g. "pulse",
        "simulation", ...
    :ivar pulse: Pulse number
    :ivar run: Run number
    """
    class Meta:
        name = "data_entry"

    user: str = field(
        default=""
    )
    machine: str = field(
        default=""
    )
    pulse_type: str = field(
        default=""
    )
    pulse: int = field(
        default=999999999
    )
    run: int = field(
        default=999999999
    )


@dataclass(slots=True)
class IdentifierStatic(IdsBaseClass):
    """Standard type for identifiers (static).

    The three fields: name, index and description are all
    representations of the same information. Associated with each
    application of this identifier-type, there should be a translation
    table defining the three fields for all objects to be identified.

    :ivar name: Short string identifier
    :ivar index: Integer identifier (enumeration index within a list).
        Private identifier values must be indicated by a negative index.
    :ivar description: Verbose description
    """
    class Meta:
        name = "identifier_static"

    name: str = field(
        default=""
    )
    index: int = field(
        default=999999999
    )
    description: str = field(
        default=""
    )


@dataclass(slots=True)
class IdsProvenanceNode(IdsBaseClass):
    """
    Provenance information for a given node of the IDS.

    :ivar path: Path of the node within the IDS, following the syntax
        given in the link below. If empty, means the provenance
        information applies to the whole IDS.
    :ivar sources: List of sources used to import or calculate this
        node, identified as explained below. In case the node is the
        result of of a calculation / data processing, the source is an
        input to the process described in the "code" structure at the
        root of the IDS. The source can be an IDS (identified by a URI
        or a persitent identifier, see syntax in the link below) or non-
        IDS data imported directly from an non-IMAS database (identified
        by the command used to import the source, or the persistent
        identifier of the data source). Often data are obtained by a
        chain of processes, however only the last process input are
        recorded here. The full chain of provenance has then to be
        reconstructed recursively from the provenance information
        contained in the data sources.
    """
    class Meta:
        name = "ids_provenance_node"

    path: str = field(
        default=""
    )
    sources: Optional[list[str]] = field(
        default=None
    )


@dataclass(slots=True)
class LangmuirProbesPlungePhysicalQuantity(IdsBaseClass):
    """
    Similar to a signal (FLT_1D) but dynamic signals use here a specific time base
    time_within_plunge base located one level above.

    :ivar validity_timed: Indicator of the validity of the data for each
        time slice. 0: valid from automated processing, 1: valid and
        certified by the diagnostic RO; - 1 means problem identified in
        the data processing (request verification by the diagnostic RO),
        -2: invalid data, should not be used (values lower than -2 have
        a code-specific meaning detailing the origin of their
        invalidity)
    :ivar validity: Indicator of the validity of the data for the whole
        plunge. 0: valid from automated processing, 1: valid and
        certified by the diagnostic RO; - 1 means problem identified in
        the data processing (request verification by the diagnostic RO),
        -2: invalid data, should not be used (values lower than -2 have
        a code-specific meaning detailing the origin of their
        invalidity)
    """
    class Meta:
        name = "langmuir_probes_plunge_physical_quantity"

    validity_timed: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity: int = field(
        default=999999999
    )

    @dataclass(slots=True)
    class Data(IdsBaseClass):
        """
        :ivar class_of: Class of Data Item
        """
        class_of: str = field(
            init=False,
            default="FLT_1D"
        )


@dataclass(slots=True)
class LangmuirProbesPlungePhysicalQuantity2(IdsBaseClass):
    """
    Similar to a signal (FLT_1D) but dynamic signals use here a specific time base
    time_within_plunge located two levels above.

    :ivar validity_timed: Indicator of the validity of the data for each
        time slice. 0: valid from automated processing, 1: valid and
        certified by the diagnostic RO; - 1 means problem identified in
        the data processing (request verification by the diagnostic RO),
        -2: invalid data, should not be used (values lower than -2 have
        a code-specific meaning detailing the origin of their
        invalidity)
    :ivar validity: Indicator of the validity of the data for the whole
        plunge. 0: valid from automated processing, 1: valid and
        certified by the diagnostic RO; - 1 means problem identified in
        the data processing (request verification by the diagnostic RO),
        -2: invalid data, should not be used (values lower than -2 have
        a code-specific meaning detailing the origin of their
        invalidity)
    """
    class Meta:
        name = "langmuir_probes_plunge_physical_quantity_2"

    validity_timed: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity: int = field(
        default=999999999
    )

    @dataclass(slots=True)
    class Data(IdsBaseClass):
        """
        :ivar class_of: Class of Data Item
        """
        class_of: str = field(
            init=False,
            default="FLT_1D"
        )


@dataclass(slots=True)
class LangmuirProbesPositionReciprocating(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (1D, dynamic within a type 1 array of
    structure and with a common time base one level above)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle
    :ivar validity_timed: Indicator of the validity of the position data
        for each time slice. 0: valid from automated processing, 1:
        valid and certified by the diagnostic RO; - 1 means problem
        identified in the data processing (request verification by the
        diagnostic RO), -2: invalid data, should not be used (values
        lower than -2 have a code-specific meaning detailing the origin
        of their invalidity)
    :ivar validity: Indicator of the validity of the position data for
        the whole plunge. 0: valid from automated processing, 1: valid
        and certified by the diagnostic RO; - 1 means problem identified
        in the data processing (request verification by the diagnostic
        RO), -2: invalid data, should not be used (values lower than -2
        have a code-specific meaning detailing the origin of their
        invalidity)
    """
    class Meta:
        name = "langmuir_probes_position_reciprocating"

    r: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    z: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    phi: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity_timed: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity: int = field(
        default=999999999
    )


@dataclass(slots=True)
class LangmuirProbesPositionReciprocating2(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (1D, dynamic within a type 1 array of
    structure and with a common time base two levels above)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle
    :ivar validity_timed: Indicator of the validity of the position data
        for each time slice. 0: valid from automated processing, 1:
        valid and certified by the diagnostic RO; - 1 means problem
        identified in the data processing (request verification by the
        diagnostic RO), -2: invalid data, should not be used (values
        lower than -2 have a code-specific meaning detailing the origin
        of their invalidity)
    :ivar validity: Indicator of the validity of the position data for
        the whole plunge. 0: valid from automated processing, 1: valid
        and certified by the diagnostic RO; - 1 means problem identified
        in the data processing (request verification by the diagnostic
        RO), -2: invalid data, should not be used (values lower than -2
        have a code-specific meaning detailing the origin of their
        invalidity)
    """
    class Meta:
        name = "langmuir_probes_position_reciprocating_2"

    r: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    z: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    phi: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity_timed: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity: int = field(
        default=999999999
    )


@dataclass(slots=True)
class Library(IdsBaseClass):
    """
    Library used by the code that has produced this IDS.

    :ivar name: Name of software
    :ivar description: Short description of the software (type, purpose)
    :ivar commit: Unique commit reference of software
    :ivar version: Unique version (tag) of software
    :ivar repository: URL of software repository
    :ivar parameters: List of the code specific parameters in XML format
    """
    class Meta:
        name = "library"

    name: str = field(
        default=""
    )
    description: str = field(
        default=""
    )
    commit: str = field(
        default=""
    )
    version: str = field(
        default=""
    )
    repository: str = field(
        default=""
    )
    parameters: str = field(
        default=""
    )


@dataclass(slots=True)
class PhysicalQuantityFlt1DTime1(IdsBaseClass):
    """Similar to a signal (FLT_1D) but with time base one level above (NB : since this is described in the utilities section, the timebase must be directly below the closest AoS)

    :ivar validity_timed: Indicator of the validity of the data for each
        time slice. 0: valid from automated processing, 1: valid and
        certified by the diagnostic RO; - 1 means problem identified in
        the data processing (request verification by the diagnostic RO),
        -2: invalid data, should not be used (values lower than -2 have
        a code-specific meaning detailing the origin of their
        invalidity)
    :ivar validity: Indicator of the validity of the data for the whole
        acquisition period. 0: valid from automated processing, 1: valid
        and certified by the diagnostic RO; - 1 means problem identified
        in the data processing (request verification by the diagnostic
        RO), -2: invalid data, should not be used (values lower than -2
        have a code-specific meaning detailing the origin of their
        invalidity)
    """
    class Meta:
        name = "physical_quantity_flt_1d_time_1"

    validity_timed: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    validity: int = field(
        default=999999999
    )

    @dataclass(slots=True)
    class Data(IdsBaseClass):
        """
        :ivar class_of: Class of Data Item
        """
        class_of: str = field(
            init=False,
            default="FLT_1D"
        )


@dataclass(slots=True)
class Rzphi0DStatic(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (0D, static)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    """
    class Meta:
        name = "rzphi0d_static"

    r: float = field(
        default=9e+40
    )
    z: float = field(
        default=9e+40
    )
    phi: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class Code(IdsBaseClass):
    """
    Generic decription of the code-specific parameters for the code that has
    produced this IDS.

    :ivar name: Name of software generating IDS
    :ivar description: Short description of the software (type, purpose)
    :ivar commit: Unique commit reference of software
    :ivar version: Unique version (tag) of software
    :ivar repository: URL of software repository
    :ivar parameters: List of the code specific parameters in XML format
    :ivar output_flag: Output flag : 0 means the run is successful,
        other values mean some difficulty has been encountered, the
        exact meaning is then code specific. Negative values mean the
        result shall not be used.
    :ivar library: List of external libraries used by the code that has
        produced this IDS
    """
    class Meta:
        name = "code"

    name: str = field(
        default=""
    )
    description: str = field(
        default=""
    )
    commit: str = field(
        default=""
    )
    version: str = field(
        default=""
    )
    repository: str = field(
        default=""
    )
    parameters: str = field(
        default=""
    )
    output_flag: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    library: list[Library] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )


@dataclass(slots=True)
class IdsIdentification(IdsBaseClass):
    """
    Identifier of an IDS.

    :ivar name: IDS name
    :ivar occurrence: IDS occurrence
    :ivar data_entry: Data entry to which this IDS belongs
    """
    class Meta:
        name = "ids_identification"

    name: str = field(
        default=""
    )
    occurrence: int = field(
        default=999999999
    )
    data_entry: Optional[DataEntry] = field(
        default=None
    )


@dataclass(slots=True)
class IdsProvenance(IdsBaseClass):
    """
    Provenance information about the IDS.

    :ivar node: Set of IDS nodes for which the provenance is given. The
        provenance information applies to the whole structure below the
        IDS node. For documenting provenance information for the whole
        IDS, set the size of this array of structure to 1 and leave the
        child "path" node empty
    """
    class Meta:
        name = "ids_provenance"

    node: list[IdsProvenanceNode] = field(
        default_factory=list,
        metadata={
            "max_occurs": 20,
        }
    )


@dataclass(slots=True)
class LangmuirProbesMultiTemperature(IdsBaseClass):
    """
    Structure for multi-temperature fits.

    :ivar t_e: Electron temperature
    :ivar t_i: Ion temperature
    :ivar time: Timebase for the dynamic nodes of this probe located at
        this level of the IDS structure
    """
    class Meta:
        name = "langmuir_probes_multi_temperature"

    t_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    t_i: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class LangmuirProbesPlungeCollector(IdsBaseClass):
    """
    Probe collector.

    :ivar position: Position of the collector
    :ivar v_floating: Floating potential
    :ivar v_floating_sigma: Standard deviation of the floating
        potential, corresponding to the fluctuations of the quantity
        over time
    :ivar t_e: Electron temperature
    :ivar t_i: Ion temperature
    :ivar j_i_parallel: Ion parallel current density at the probe
        position
    :ivar ion_saturation_current: Ion saturation current measured by the
        probe
    :ivar j_i_saturation: Ion saturation current density
    :ivar j_i_skew: Skew of the ion saturation current density
    :ivar j_i_kurtosis: Pearson kurtosis of the ion saturation current
        density
    :ivar j_i_sigma: Standard deviation of the ion saturation current
        density, corresponding to the fluctuations of the quantity over
        time
    :ivar heat_flux_parallel: Parallel heat flux at the probe position
    """
    class Meta:
        name = "langmuir_probes_plunge_collector"

    position: Optional[LangmuirProbesPositionReciprocating2] = field(
        default=None
    )
    v_floating: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    v_floating_sigma: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    t_e: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    t_i: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    j_i_parallel: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    ion_saturation_current: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    j_i_saturation: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    j_i_skew: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    j_i_kurtosis: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    j_i_sigma: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )
    heat_flux_parallel: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None
    )


@dataclass(slots=True)
class IdsProperties(IdsBaseClass):
    """Interface Data Structure properties.

    This element identifies the node above as an IDS

    :ivar comment: Any comment describing the content of this IDS
    :ivar homogeneous_time: This node must be filled (with 0, 1, or 2)
        for the IDS to be valid. If 1, the time of this IDS is
        homogeneous, i.e. the time values for this IDS are stored in the
        time node just below the root of this IDS. If 0, the time values
        are stored in the various time fields at lower levels in the
        tree. In the case only constant or static nodes are filled
        within the IDS, homogeneous_time must be set to 2
    :ivar provider: Name of the person in charge of producing this data
    :ivar creation_date: Date at which this data has been produced
    :ivar provenance: Provenance information about this IDS
    """
    class Meta:
        name = "ids_properties"

    comment: str = field(
        default=""
    )
    homogeneous_time: int = field(
        default=999999999
    )
    provider: str = field(
        default=""
    )
    creation_date: str = field(
        default=""
    )
    provenance: Optional[IdsProvenance] = field(
        default=None
    )


@dataclass(slots=True)
class LangmuirProbesEmbedded(IdsBaseClass):
    """
    Embedded Langmuir probe description.

    :ivar name: Name of the probe
    :ivar identifier: ID of the probe
    :ivar position: Position of the measurements
    :ivar surface_area: Area of the probe surface exposed to the plasma
        (use when assuming constant effective collection area)
    :ivar surface_area_effective: Effective collection area of the probe
        surface, varying with time due to e.g. changes in the magnetic
        field line incidence angle
    :ivar v_floating: Floating potential
    :ivar v_floating_sigma: Standard deviation of the floating
        potential, corresponding to the fluctuations of the quantity
        over time
    :ivar v_plasma: Plasma potential
    :ivar t_e: Electron temperature
    :ivar n_e: Electron density
    :ivar t_i: Ion temperature
    :ivar j_i_parallel: Ion parallel current density at the probe
        position
    :ivar j_i_parallel_sigma: Standard deviation of ion parallel current
        density at the probe position
    :ivar ion_saturation_current: Ion saturation current measured by the
        probe
    :ivar j_i_saturation: Ion saturation current density
    :ivar j_i_saturation_skew: Skew of the ion saturation current
        density
    :ivar j_i_saturation_kurtosis: Pearson kurtosis of the ion
        saturation current density
    :ivar j_i_saturation_sigma: Standard deviation of the ion saturation
        current density, corresponding to the fluctuations of the
        quantity over time
    :ivar heat_flux_parallel: Parallel heat flux at the probe position
    :ivar fluence: Positive charge fluence normal to an ideal
        axisymmetric surface of the divertor (assuming no shaping),
        estimated at the probe location.
    :ivar b_field_angle: Incident angle of the magnetic field with
        respect to PFC surface
    :ivar distance_separatrix_midplane: Distance between the measurement
        position and the separatrix, mapped along flux surfaces to the
        outboard midplane, in the major radius direction. Positive value
        means the measurement is outside of the separatrix.
    :ivar multi_temperature_fits: Set of temperatures describing the
        electron and ion distribution functions in case of multi-
        temperature fits
    :ivar time: Timebase for the dynamic nodes of this probe located at
        this level of the IDS structure
    """
    class Meta:
        name = "langmuir_probes_embedded"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    position: Optional[Rzphi0DStatic] = field(
        default=None
    )
    surface_area: float = field(
        default=9e+40
    )
    surface_area_effective: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    v_floating: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    v_floating_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    v_plasma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    t_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    n_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    t_i: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_parallel: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_parallel_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    ion_saturation_current: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_saturation: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_saturation_skew: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_saturation_kurtosis: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    j_i_saturation_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    heat_flux_parallel: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    fluence: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    b_field_angle: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    distance_separatrix_midplane: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None
    )
    multi_temperature_fits: list[LangmuirProbesMultiTemperature] = field(
        default_factory=list,
        metadata={
            "max_occurs": 2,
        }
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class LangmuirProbesPlunge(IdsBaseClass):
    """
    Plunge of a reciprocating probe.

    :ivar position_average: Average position of the measurements derived
        from multiple collectors
    :ivar collector: Set of probe collectors including measurements
        specific to each collector. The number of collectors (size of
        this array of structure) is assumed to remain constant for all
        plunges
    :ivar v_plasma: Plasma potential
    :ivar t_e_average: Electron temperature (upstream to downstream
        average)
    :ivar t_i_average: Ion temperature (upstream to downstream average)
    :ivar n_e: Electron density
    :ivar b_field_angle: Incident angle of the magnetic field with
        respect to PFC surface
    :ivar distance_separatrix_midplane: Distance between the measurement
        position and the separatrix, mapped along flux surfaces to the
        outboard midplane, in the major radius direction. Positive value
        means the measurement is outside of the separatrix.
    :ivar distance_x_point_z: Distance in the z direction of the
        measurement position to the closest X-point (Zmeasurement-
        Zx_point)
    :ivar mach_number_parallel: Parallel Mach number
    :ivar time_within_plunge: Time vector for describing the dynamics
        within the plunge
    :ivar time: Time of maximum penetration of the probe during a given
        plunge
    """
    class Meta:
        name = "langmuir_probes_plunge"

    position_average: Optional[LangmuirProbesPositionReciprocating] = field(
        default=None
    )
    collector: list[LangmuirProbesPlungeCollector] = field(
        default_factory=list
    )
    v_plasma: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    t_e_average: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    t_i_average: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    n_e: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    b_field_angle: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    distance_separatrix_midplane: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    distance_x_point_z: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    mach_number_parallel: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None
    )
    time_within_plunge: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class LangmuirProbesReciprocating(IdsBaseClass):
    """
    Reciprocating probe.

    :ivar name: Name of the probe
    :ivar identifier: ID of the probe
    :ivar surface_area: Area of the surface exposed to the plasma of
        each collector (constant assuming negligible dependence on e.g.
        the magnetic field line angle)
    :ivar plunge: Set of plunges of this probe during the pulse, each
        plunge being recorded as a time slice from the Access Layer
        point of view. The time child node corresponds to the time of
        maximum penetration of the probe during a given plunge. The
        dynamics of physical quantities within the plunge are described
        via the time_within_plunge vector.
    """
    class Meta:
        name = "langmuir_probes_reciprocating"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    surface_area: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    plunge: list[LangmuirProbesPlunge] = field(
        default_factory=list
    )


@dataclass(slots=True)
class LangmuirProbes(IdsBaseClass):
    """
    Langmuir probes.

    :ivar ids_properties:
    :ivar equilibrium_id: ID of the IDS equilibrium used to map
        measurements - we may decide that this is superseeded when the
        systematic documentation of input provenance is adopted
    :ivar midplane: Choice of midplane definition for the mapping of
        measurements on an equilibrium (use the lowest index number if
        more than one value is relevant)
    :ivar embedded: Set of embedded (in a plasma facing component)
        probes
    :ivar reciprocating: Set of reciprocating probes
    :ivar latency: Upper bound of the delay between physical information
        received by the detector and data available on the real-time
        (RT) network.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "langmuir_probes"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    equilibrium_id: Optional[IdsIdentification] = field(
        default=None
    )
    midplane: Optional[IdentifierStatic] = field(
        default=None
    )
    embedded: list[LangmuirProbesEmbedded] = field(
        default_factory=list,
        metadata={
            "max_occurs": 100,
        }
    )
    reciprocating: list[LangmuirProbesReciprocating] = field(
        default_factory=list,
        metadata={
            "max_occurs": 100,
        }
    )
    latency: float = field(
        default=9e+40
    )
    code: Optional[Code] = field(
        default=None
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
