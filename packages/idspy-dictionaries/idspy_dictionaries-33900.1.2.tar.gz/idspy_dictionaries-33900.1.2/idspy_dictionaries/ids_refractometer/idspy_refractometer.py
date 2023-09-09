# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class Identifier(IdsBaseClass):
    """Standard type for identifiers (constant).

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
        name = "identifier"

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
class SignalFlt1D(IdsBaseClass):
    """
    Signal (FLT_1D) with its time base.

    :ivar time: Time
    """
    class Meta:
        name = "signal_flt_1d"

    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
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
class SignalFlt2D(IdsBaseClass):
    """
    Signal (FLT_2D) with its time base.

    :ivar time: Time
    """
    class Meta:
        name = "signal_flt_2d"

    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )

    @dataclass(slots=True)
    class Data(IdsBaseClass):
        """
        :ivar class_of: Class of Data Item
        """
        class_of: str = field(
            init=False,
            default="FLT_2D"
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
class LineOfSight2Points(IdsBaseClass):
    """
    Generic description of a line of sight, defined by two points.

    :ivar first_point: Position of the first point
    :ivar second_point: Position of the second point
    """
    class Meta:
        name = "line_of_sight_2points"

    first_point: Optional[Rzphi0DStatic] = field(
        default=None
    )
    second_point: Optional[Rzphi0DStatic] = field(
        default=None
    )


@dataclass(slots=True)
class RefractometerChannelBandwidth(IdsBaseClass):
    """
    Refractometer channel bandwidth.

    :ivar frequency_main: Main frequency used to probe the plasma
        (before upshifting and modulating)
    :ivar phase: Phase of the envelope of the probing signal, relative
        to the phase at launch
    :ivar i_component: I component of the IQ detector used to retrieve
        the phase of signal's envelope, sampled on a high resolution
        time_detector grid just before each measurement time slice
        represented by the ../time vector
    :ivar q_component: Q component of the IQ detector used to retrieve
        the phase of signal's envelope, sampled on a high resolution
        time_detector grid just before each measurement time slice
        represented by the ../time vector
    :ivar n_e_line: Integral of the electron density along the line of
        sight, deduced from the envelope phase measurements
    :ivar phase_quadrature: In-phase and Quadrature components of the
        analysed signal. They are returned by an IQ-detector, that takes
        carrying and reference signals as the input and yields I and Q
        components. These are respectively stored as the first and the
        second index of the first dimension of the data child.
    :ivar time_detector: High sampling timebase of the IQ-detector
        signal measurements
    :ivar time: Timebase for this bandwidth
    """
    class Meta:
        name = "refractometer_channel_bandwidth"

    frequency_main: float = field(
        default=9e+40
    )
    phase: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    i_component: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    q_component: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    n_e_line: Optional[SignalFlt1D] = field(
        default=None
    )
    phase_quadrature: Optional[SignalFlt2D] = field(
        default=None
    )
    time_detector: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class RefractometerShapeApproximation(IdsBaseClass):
    """
    Shape approximation for the electron density profile.

    :ivar formula: Analytical formula representing the electron density
        profile as a function of a radial coordinate and adjustable
        parameters f(rho_tor_norm, alpha1, ... alphaN)
    :ivar parameters: Values of the formula's parameters alpha1, ...,
        alphaN
    """
    class Meta:
        name = "refractometer_shape_approximation"

    formula: Optional[Identifier] = field(
        default=None
    )
    parameters: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
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
class RefractometerChannel(IdsBaseClass):
    """
    Refractometer channel.

    :ivar name: Name of the channel
    :ivar identifier: ID of the channel
    :ivar mode: Detection mode "X" or "O"
    :ivar line_of_sight: Description of the line of sight. The first
        point corresponds to the probing wave emission point. The second
        point corresponds to the probing wave detection point
    :ivar bandwidth: Set of frequency bandwidths
    :ivar n_e_line: Integral of the electron density along the line of
        sight, deduced from the envelope phase measurements
    :ivar n_e_profile_approximation: Approximation of the radial
        electron density profile with an array of parameters and an
        approximation formula, used by post-processing programs for the
        identification of the electron density profile.
    """
    class Meta:
        name = "refractometer_channel"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    mode: str = field(
        default=""
    )
    line_of_sight: Optional[LineOfSight2Points] = field(
        default=None
    )
    bandwidth: list[RefractometerChannelBandwidth] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    n_e_line: Optional[SignalFlt1D] = field(
        default=None
    )
    n_e_profile_approximation: Optional[RefractometerShapeApproximation] = field(
        default=None
    )


@dataclass(slots=True)
class Refractometer(IdsBaseClass):
    """
    Density profile refractometer diagnostic.

    :ivar ids_properties:
    :ivar type_value: Type of refractometer (differential, impulse, ...)
    :ivar channel: Set of channels, e.g. different reception antennas of
        the refractometer
    :ivar latency: Upper bound of the delay between physical information
        received by the detector and data available on the real-time
        (RT) network.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "refractometer"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    type_value: str = field(
        default=""
    )
    channel: list[RefractometerChannel] = field(
        default_factory=list,
        metadata={
            "max_occurs": 5,
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
