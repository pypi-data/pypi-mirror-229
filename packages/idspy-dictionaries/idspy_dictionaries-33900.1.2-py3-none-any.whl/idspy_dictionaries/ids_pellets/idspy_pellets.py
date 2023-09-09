# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


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
class PelletsTimeSlicePelletSpecies(IdsBaseClass):
    """
    Species included in pellet compoisition.

    :ivar a: Mass of atom
    :ivar z_n: Nuclear charge
    :ivar label: String identifying the species (e.g. H, D, T, ...)
    :ivar density: Material density of the species in the pellet
    :ivar fraction: Atomic fraction of the species in the pellet
    :ivar sublimation_energy: Sublimation energy per atom
    """
    class Meta:
        name = "pellets_time_slice_pellet_species"

    a: float = field(
        default=9e+40
    )
    z_n: float = field(
        default=9e+40
    )
    label: str = field(
        default=""
    )
    density: float = field(
        default=9e+40
    )
    fraction: float = field(
        default=9e+40
    )
    sublimation_energy: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class PlasmaCompositionNeutralElement(IdsBaseClass):
    """
    Element entering in the composition of the neutral atom or molecule (within a
    type 3 AoS)

    :ivar a: Mass of atom
    :ivar z_n: Nuclear charge
    :ivar atoms_n: Number of atoms of this element in the molecule
    :ivar multiplicity: Multiplicity of the atom
    """
    class Meta:
        name = "plasma_composition_neutral_element"

    a: float = field(
        default=9e+40
    )
    z_n: float = field(
        default=9e+40
    )
    atoms_n: int = field(
        default=999999999
    )
    multiplicity: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class Rzphi0DDynamicAos3(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (0D, dynamic within a type 3 array of
    structures (index on time))

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    """
    class Meta:
        name = "rzphi0d_dynamic_aos3"

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
class Rzphi1DDynamicAos3(IdsBaseClass):
    """
    Structure for R, Z, Phi positions (1D, dynamic within a type 3 array of
    structure)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    """
    class Meta:
        name = "rzphi1d_dynamic_aos3"

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
class LineOfSight2PointsDynamicAos3(IdsBaseClass):
    """
    Generic description of a line of sight, defined by two points, dynamic within a
    type 3 array of structures (index on time)

    :ivar first_point: Position of the first point
    :ivar second_point: Position of the second point
    """
    class Meta:
        name = "line_of_sight_2points_dynamic_aos3"

    first_point: Optional[Rzphi0DDynamicAos3] = field(
        default=None
    )
    second_point: Optional[Rzphi0DDynamicAos3] = field(
        default=None
    )


@dataclass(slots=True)
class PelletsPropellantGas(IdsBaseClass):
    """
    Description of the propellant gas with its number of atoms.

    :ivar element: List of elements forming the gas molecule
    :ivar label: String identifying the neutral molecule (e.g. H2, D2,
        T2, N2, ...)
    :ivar molecules_n: Number of molecules of the propellant gas
        injected in the vacuum vessel when launching the pellet
    """
    class Meta:
        name = "pellets_propellant_gas"

    element: list[PlasmaCompositionNeutralElement] = field(
        default_factory=list,
        metadata={
            "max_occurs": 5,
        }
    )
    label: str = field(
        default=""
    )
    molecules_n: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class PelletsTimeSlicePelletPathProfiles(IdsBaseClass):
    """
    1-D profiles of plasma and pellet along the pellet path.

    :ivar distance: Distance along the pellet path, with the origin
        taken at path_geometry/first_point. Used as the main coordinate
        for the path_profiles structure
    :ivar rho_tor_norm: Normalised toroidal coordinate along the pellet
        path
    :ivar psi: Poloidal flux along the pellet path
    :ivar velocity: Pellet velocity along the pellet path
    :ivar n_e: Electron density along the pellet path
    :ivar t_e: Electron temperature along the pellet path
    :ivar ablation_rate: Ablation rate (electrons) along the pellet path
    :ivar ablated_particles: Number of ablated particles (electrons)
        along the pellet path
    :ivar rho_tor_norm_drift: Difference to due ExB drifts between the
        ablation and the final deposition locations, in terms of the
        normalised toroidal flux coordinate
    :ivar position: Position along the pellet path
    """
    class Meta:
        name = "pellets_time_slice_pellet_path_profiles"

    distance: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_tor_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    psi: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    velocity: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    n_e: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    t_e: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ablation_rate: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ablated_particles: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_tor_norm_drift: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    position: Optional[Rzphi1DDynamicAos3] = field(
        default=None
    )


@dataclass(slots=True)
class PelletsTimeSlicePelletShape(IdsBaseClass):
    """
    Initial shape of a pellet at launch.

    :ivar type_value: Identifier structure for the shape type:
        1-spherical; 2-cylindrical; 3-rectangular
    :ivar size: Size of the pellet in the various dimensions, depending
        on the shape type. Spherical pellets: size(1) is the radius of
        the pellet. Cylindrical pellets: size(1) is the radius and
        size(2) is the height of the cylinder. Rectangular pellets:
        size(1) is the height, size(2) is the width and size(3) is the
        length
    """
    class Meta:
        name = "pellets_time_slice_pellet_shape"

    type_value: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    size: ndarray[(int,), float] = field(
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
class PelletsTimeSlicePellet(IdsBaseClass):
    """
    Description of a pellet.

    :ivar shape: Initial shape of a pellet at launch
    :ivar species: Set of atomic species included in the pellet
        composition
    :ivar velocity_initial: Initial velocity of the pellet as it enters
        the vaccum chamber
    :ivar path_geometry: Geometry of the pellet path in the vaccuum
        chamber
    :ivar path_profiles: 1-D profiles of plasma and pellet along the
        pellet path
    :ivar propellant_gas: Propellant gas
    """
    class Meta:
        name = "pellets_time_slice_pellet"

    shape: Optional[PelletsTimeSlicePelletShape] = field(
        default=None
    )
    species: list[PelletsTimeSlicePelletSpecies] = field(
        default_factory=list
    )
    velocity_initial: float = field(
        default=9e+40
    )
    path_geometry: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None
    )
    path_profiles: Optional[PelletsTimeSlicePelletPathProfiles] = field(
        default=None
    )
    propellant_gas: Optional[PelletsPropellantGas] = field(
        default=None
    )


@dataclass(slots=True)
class PelletsTimeSlice(IdsBaseClass):
    """
    Time slice description of pellets.

    :ivar pellet: Set of pellets ablated in the plasma at a given time
    :ivar time: Time
    """
    class Meta:
        name = "pellets_time_slice"

    pellet: list[PelletsTimeSlicePellet] = field(
        default_factory=list
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class Pellets(IdsBaseClass):
    """
    Description of pellets launched into the plasma.

    :ivar ids_properties:
    :ivar time_slice: Description of the pellets launched at various
        time slices. The time of this structure corresponds to the full
        ablation of the pellet inside the plasma.
    :ivar latency: Upper bound of the delay between input command
        received from the RT network and actuator starting to react.
        Applies globally to the system described by this IDS unless
        specific latencies (e.g. channel-specific or antenna-specific)
        are provided at a deeper level in the IDS structure.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "pellets"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    time_slice: list[PelletsTimeSlice] = field(
        default_factory=list
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
