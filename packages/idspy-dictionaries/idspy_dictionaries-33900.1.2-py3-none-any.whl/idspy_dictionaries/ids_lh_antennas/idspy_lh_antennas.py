# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


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
class Rz0DConstant(IdsBaseClass):
    """
    Structure for a single R, Z position (0D, constant)

    :ivar r: Major radius
    :ivar z: Height
    """
    class Meta:
        name = "rz0d_constant"

    r: float = field(
        default=9e+40
    )
    z: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class Rzphi1DDynamicAos1CommonTime(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (1D, dynamic within a type 1 array of
    structure and with a common time base at the same level)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle
    :ivar time: Time for the R,Z,phi coordinates
    """
    class Meta:
        name = "rzphi1d_dynamic_aos1_common_time"

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
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
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
class LhAntennasAntennaModule(IdsBaseClass):
    """
    Module of an LH antenna.

    :ivar name: Name of the module
    :ivar identifier: Identifier of the module
    :ivar power_launched: Power launched from this module into the
        vacuum vessel
    :ivar power_forward: Forward power arriving to the back of the
        module
    :ivar power_reflected: Reflected power
    :ivar reflection_coefficient: Power reflection coefficient
    :ivar phase: Phase of the forward power arriving at the back of this
        module
    """
    class Meta:
        name = "lh_antennas_antenna_module"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None
    )
    power_forward: Optional[SignalFlt1D] = field(
        default=None
    )
    power_reflected: Optional[SignalFlt1D] = field(
        default=None
    )
    reflection_coefficient: Optional[SignalFlt1D] = field(
        default=None
    )
    phase: Optional[SignalFlt1D] = field(
        default=None
    )


@dataclass(slots=True)
class LhAntennasAntennaRow(IdsBaseClass):
    """
    Horizontal row of LH waveguides.

    :ivar name: Name of the row
    :ivar position: Position of the middle on the row
    :ivar n_tor: Refraction index in the toroidal direction
    :ivar n_pol: Refraction index in the poloidal direction. The
        poloidal angle is defined from the reference point; the angle at
        a point (R,Z) is given by atan((Z-Zref)/(R-Rref)), where
        Rref=reference_point/r and Zref=reference_point/z
    :ivar power_density_spectrum_1d: 1D power density spectrum
        dP/dn_tor, as a function of time
    :ivar power_density_spectrum_2d: 2D power density spectrum
        d2P/(dn_tor.dn_pol), as a function of time
    :ivar time: Timebase for the dynamic nodes of this probe located at
        this level of the IDS structure
    """
    class Meta:
        name = "lh_antennas_antenna_row"

    name: str = field(
        default=""
    )
    position: Optional[Rzphi1DDynamicAos1CommonTime] = field(
        default=None
    )
    n_tor: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    n_pol: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    power_density_spectrum_1d: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    power_density_spectrum_2d: ndarray[(int,int, int), float] = field(
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
class Rzphi1DDynamicAos1Definition(IdsBaseClass):
    """
    Structure for list of R, Z, Phi positions (1D, dynamic within a type 1 array of
    structures (indexed on objects, data/time structure), including a definition of
    the reference point.

    :ivar definition: Definition of the reference point
    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    """
    class Meta:
        name = "rzphi1d_dynamic_aos1_definition"

    definition: str = field(
        default=""
    )
    r: Optional[SignalFlt1D] = field(
        default=None
    )
    z: Optional[SignalFlt1D] = field(
        default=None
    )
    phi: Optional[SignalFlt1D] = field(
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
class LhAntennasAntenna(IdsBaseClass):
    """
    LH antenna.

    :ivar name: Name of the antenna (unique within the set of all
        antennas of the experiment)
    :ivar identifier: Identifier of the antenna (unique within the set
        of all antennas of the experiment)
    :ivar model_name: Name of the antenna model used for antenna
        spectrum computation
    :ivar frequency: Frequency
    :ivar power_launched: Power launched from this antenna into the
        vacuum vessel
    :ivar power_forward: Forward power arriving at the back of the
        antenna
    :ivar power_reflected: Reflected power
    :ivar reflection_coefficient: Power reflection coefficient, averaged
        over modules
    :ivar phase_average: Phase difference between two neighbouring
        modules (average over modules), at the mouth (front) of the
        antenna
    :ivar n_parallel_peak: Peak parallel refractive index of the
        launched wave spectrum (simple estimate based on the measured
        phase difference)
    :ivar position: Position of a reference point on the antenna
        (allowing also tracking the possible movements of the antenna)
    :ivar pressure_tank: Pressure in the vacuum tank of the antenna
    :ivar distance_to_antenna: Radial distance to the antenna mouth
        (grid for the electron density profile). 0 at antenna mouth,
        increasing towards the plasma
    :ivar n_e: Electron density profile in front of the antenna
    :ivar module: Set of antenna modules
    :ivar row: Set of horizontal rows of waveguides (corresponding to
        different poloidal positions). A power spectrum is provided for
        each row.
    """
    class Meta:
        name = "lh_antennas_antenna"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    model_name: str = field(
        default=""
    )
    frequency: float = field(
        default=9e+40
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None
    )
    power_forward: Optional[SignalFlt1D] = field(
        default=None
    )
    power_reflected: Optional[SignalFlt1D] = field(
        default=None
    )
    reflection_coefficient: Optional[SignalFlt1D] = field(
        default=None
    )
    phase_average: Optional[SignalFlt1D] = field(
        default=None
    )
    n_parallel_peak: Optional[SignalFlt1D] = field(
        default=None
    )
    position: Optional[Rzphi1DDynamicAos1Definition] = field(
        default=None
    )
    pressure_tank: Optional[SignalFlt1D] = field(
        default=None
    )
    distance_to_antenna: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    n_e: Optional[SignalFlt2D] = field(
        default=None
    )
    module: list[LhAntennasAntennaModule] = field(
        default_factory=list,
        metadata={
            "max_occurs": 16,
        }
    )
    row: list[LhAntennasAntennaRow] = field(
        default_factory=list,
        metadata={
            "max_occurs": 6,
        }
    )


@dataclass(slots=True)
class LhAntennas(IdsBaseClass):
    """Antenna systems for heating and current drive in the Lower Hybrid (LH)
    frequencies.

    In the definitions below, the front (or mouth) of the antenna refers
    to the plasma facing side of the antenna, while the back refers to
    the waveguides connected side of the antenna (towards the RF
    generators).

    :ivar ids_properties:
    :ivar reference_point: Reference point used to define the poloidal
        angle, e.g. the geometrical centre of the vacuum vessel. Used to
        define the poloidal refraction index under antenna/row
    :ivar antenna: Set of Lower Hybrid antennas
    :ivar power: Power coupled to the plasma by the whole LH system (sum
        over antennas)
    :ivar power_launched: Power launched into the vacuum vessel by the
        whole LH system (sum over antennas)
    :ivar latency: Upper bound of the delay between input command
        received from the RT network and actuator starting to react.
        Applies globally to the system described by this IDS unless
        specific latencies (e.g. channel-specific or antenna-specific)
        are provided at a deeper level in the IDS structure.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "lh_antennas"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    reference_point: Optional[Rz0DConstant] = field(
        default=None
    )
    antenna: list[LhAntennasAntenna] = field(
        default_factory=list,
        metadata={
            "max_occurs": 2,
        }
    )
    power: Optional[SignalFlt1D] = field(
        default=None
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None
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
