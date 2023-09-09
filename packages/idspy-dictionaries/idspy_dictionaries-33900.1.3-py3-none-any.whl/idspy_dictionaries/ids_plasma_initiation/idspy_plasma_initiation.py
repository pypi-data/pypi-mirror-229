# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class EquilibriumProfiles2DGrid(IdsBaseClass):
    """
    Definition of the 2D grid.

    :ivar dim1: First dimension values
    :ivar dim2: Second dimension values
    :ivar volume_element: Elementary plasma volume of plasma enclosed in
        the cell formed by the nodes [dim1(i) dim2(j)], [dim1(i+1)
        dim2(j)], [dim1(i) dim2(j+1)] and [dim1(i+1) dim2(j+1)]
    """
    class Meta:
        name = "equilibrium_profiles_2d_grid"

    dim1: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    dim2: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    volume_element: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class IdentifierDynamicAos3(IdsBaseClass):
    """Standard type for identifiers (dynamic within type 3 array of structures
    (index on time)).

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
        name = "identifier_dynamic_aos3"

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
class Rz1DDynamicAos(IdsBaseClass):
    """
    Structure for list of R, Z positions (1D list of Npoints, dynamic within a type
    3 array of structures (index on time))

    :ivar r: Major radius
    :ivar z: Height
    """
    class Meta:
        name = "rz1d_dynamic_aos"

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
class PlasmaInitiationFieldLines(IdsBaseClass):
    """
    Field lines tracing at a given time slice.

    :ivar grid_type: Selection of one of a set of grid types
    :ivar grid: Definition of the 2D grid (the content of dim1 and dim2
        is defined by the selected grid_type)
    :ivar townsend_or_closed_positions: List of all R, Z positions along
        all field lines encoutering Townsend condition or being closed
        field lines
    :ivar townsend_or_closed_grid_positions: List of all R, Z grid
        positions (from ../grid) containing field lines encoutering
        Townsend condition or being closed field lines
    :ivar starting_positions: Starting position to initiate field line
        tracing, for each field line
    :ivar e_field_townsend: Townsend electric field along each field
        line
    :ivar e_field_parallel: Parallel electric field along each field
        line
    :ivar lengths: Length of each field line
    :ivar pressure: Prefill gas pressure used in Townsend E field
        calculation
    :ivar open_fraction: Fraction of open field lines : ratio open
        fields lines / (open+closed field lines)
    :ivar time: Time
    """
    class Meta:
        name = "plasma_initiation_field_lines"

    grid_type: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    grid: Optional[EquilibriumProfiles2DGrid] = field(
        default=None
    )
    townsend_or_closed_positions: Optional[Rz1DDynamicAos] = field(
        default=None
    )
    townsend_or_closed_grid_positions: Optional[Rz1DDynamicAos] = field(
        default=None
    )
    starting_positions: Optional[Rz1DDynamicAos] = field(
        default=None
    )
    e_field_townsend: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_parallel: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    lengths: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure: float = field(
        default=9e+40
    )
    open_fraction: float = field(
        default=9e+40
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class PlasmaInitiationGlobalQuantities(IdsBaseClass):
    """
    Global quantities.

    :ivar b_field_stray: Stray magnetic field at plasma position
    :ivar b_field_perpendicular: Perpendicular magnetic field at plasma
        position. b_field_perpendicular =
        sqrt(b_field_stray^2+b_field_eddy^2)
    :ivar connection_length: Average length of open magnetic field
        lines. In the case of fully closed field lines,
        connection_length = 1
    :ivar coulomb_logarithm: Coulomb logarithm
    """
    class Meta:
        name = "plasma_initiation_global_quantities"

    b_field_stray: Optional[SignalFlt1D] = field(
        default=None
    )
    b_field_perpendicular: Optional[SignalFlt1D] = field(
        default=None
    )
    connection_length: Optional[SignalFlt1D] = field(
        default=None
    )
    coulomb_logarithm: Optional[SignalFlt1D] = field(
        default=None
    )


@dataclass(slots=True)
class PlasmaInitiationProfiles2D(IdsBaseClass):
    """
    2D profiles at a given time slice.

    :ivar grid_type: Selection of one of a set of grid types
    :ivar grid: Definition of the 2D grid (the content of dim1 and dim2
        is defined by the selected grid_type)
    :ivar e_field_tor: Toroidal component of the electric field
    :ivar time: Time
    """
    class Meta:
        name = "plasma_initiation_profiles_2d"

    grid_type: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    grid: Optional[EquilibriumProfiles2DGrid] = field(
        default=None
    )
    e_field_tor: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time: Optional[float] = field(
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
class PlasmaInitiation(IdsBaseClass):
    """
    Description the early phases of the plasma, before an equilibrium can be
    calculated.

    :ivar ids_properties:
    :ivar global_quantities: Global quantities
    :ivar b_field_lines: Magnetic field line tracing results, given at
        various time slices
    :ivar profiles_2d: 2D profiles in the poloidal plane, given at
        various time slices
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "plasma_initiation"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    global_quantities: Optional[PlasmaInitiationGlobalQuantities] = field(
        default=None
    )
    b_field_lines: list[PlasmaInitiationFieldLines] = field(
        default_factory=list
    )
    profiles_2d: list[PlasmaInitiationProfiles2D] = field(
        default_factory=list
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
