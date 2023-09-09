# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Dict, Optional


@dataclass(slots=True)
class BTorVacuum1(IdsBaseClass):
    """Characteristics of the vacuum toroidal field.

    Time coordinate at the root of the IDS

    :ivar r0: Reference major radius where the vacuum toroidal magnetic
        field is given (usually a fixed position such as the middle of
        the vessel at the equatorial midplane)
    :ivar b0: Vacuum toroidal field at R0 [T]; Positive sign means anti-
        clockwise when viewing from above. The product R0B0 must be
        consistent with the b_tor_vacuum_r field of the tf IDS.
    """
    class Meta:
        name = "b_tor_vacuum_1"

    r0: float = field(
        default=9e+40
    )
    b0: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class CoreRadialGrid(IdsBaseClass):
    """
    1D radial grid for core* IDSs.

    :ivar rho_tor_norm: Normalised toroidal flux coordinate. The
        normalizing value for rho_tor_norm, is the toroidal flux
        coordinate at the equilibrium boundary (LCFS or 99.x % of the
        LCFS in case of a fixed boundary equilibium calculation, see
        time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor: Toroidal flux coordinate. rho_tor =
        sqrt(b_flux_tor/(pi*b0)) ~ sqrt(pi*r^2*b0/(pi*b0)) ~ r [m]. The
        toroidal field used in its definition is indicated under
        vacuum_toroidal_field/b0
    :ivar rho_pol_norm: Normalised poloidal flux coordinate =
        sqrt((psi(rho)-psi(magnetic_axis)) /
        (psi(LCFS)-psi(magnetic_axis)))
    :ivar psi: Poloidal magnetic flux
    :ivar volume: Volume enclosed inside the magnetic surface
    :ivar area: Cross-sectional area of the flux surface
    :ivar surface: Surface area of the toroidal flux surface
    :ivar psi_magnetic_axis: Value of the poloidal magnetic flux at the
        magnetic axis (useful to normalize the psi array values when the
        radial grid doesn't go from the magnetic axis to the plasma
        boundary)
    :ivar psi_boundary: Value of the poloidal magnetic flux at the
        plasma boundary (useful to normalize the psi array values when
        the radial grid doesn't go from the magnetic axis to the plasma
        boundary)
    """
    class Meta:
        name = "core_radial_grid"

    rho_tor_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_tor: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_pol_norm: ndarray[(int,), float] = field(
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
    volume: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    area: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    surface: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    psi_magnetic_axis: float = field(
        default=9e+40
    )
    psi_boundary: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class DistributionMarkersOrbit(IdsBaseClass):
    """Test particles for a given time slice : orbit integrals

    :ivar expressions: List of the expressions f(n_tor,m_pol,k,q,...)
        used in the orbit integrals
    :ivar n_tor: Array of toroidal mode numbers, n_tor, where quantities
        vary as exp(i.n_tor.phi) and phi runs anticlockwise when viewed
        from above
    :ivar m_pol: Array of poloidal mode numbers, where quantities vary
        as exp(-i.m_pol.theta) and theta is the angle defined by the
        choice of ../../coordinate_identifier, with its centre at the
        magnetic axis recalled at the root of this IDS
    :ivar bounce_harmonics: Array of bounce harmonics k
    :ivar values: Values of the orbit integrals
    """
    class Meta:
        name = "distribution_markers_orbit"

    expressions: Optional[list[str]] = field(
        default=None
    )
    n_tor: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    m_pol: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    bounce_harmonics: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    values: ndarray[(int, int, int, int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class DistributionMarkersOrbitInstant(IdsBaseClass):
    """Test particles for a given time slice : orbit integrals

    :ivar expressions: List of the expressions f(eq) used in the orbit
        integrals
    :ivar time_orbit: Time array along the markers last orbit
    :ivar values: Values of the orbit integrals
    """
    class Meta:
        name = "distribution_markers_orbit_instant"

    expressions: Optional[list[str]] = field(
        default=None
    )
    time_orbit: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    values: ndarray[(int, int, int ), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class GenericGridDynamicGridSubsetElementObject(IdsBaseClass):
    """
    Generic grid, object part of an element part of a grid_subset (dynamic within a
    type 3 AoS)

    :ivar space: Index of the space from which that object is taken
    :ivar dimension: Dimension of the object
    :ivar index: Object index
    """
    class Meta:
        name = "generic_grid_dynamic_grid_subset_element_object"

    space: int = field(
        default=999999999
    )
    dimension: int = field(
        default=999999999
    )
    index: int = field(
        default=999999999
    )


@dataclass(slots=True)
class GenericGridDynamicGridSubsetMetric(IdsBaseClass):
    """
    Generic grid, metric description for a given grid_subset and base (dynamic
    within a type 3 AoS)

    :ivar jacobian: Metric Jacobian
    :ivar tensor_covariant: Covariant metric tensor, given on each
        element of the subgrid (first dimension)
    :ivar tensor_contravariant: Contravariant metric tensor, given on
        each element of the subgrid (first dimension)
    """
    class Meta:
        name = "generic_grid_dynamic_grid_subset_metric"

    jacobian: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    tensor_covariant: ndarray[(int,int, int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    tensor_contravariant: ndarray[(int,int, int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class GenericGridDynamicSpaceDimensionObjectBoundary(IdsBaseClass):
    """
    Generic grid, description of an object boundary and its neighbours (dynamic
    within a type 3 AoS)

    :ivar index: Index of this (n-1)-dimensional boundary object
    :ivar neighbours: List of indices of the n-dimensional objects
        adjacent to the given n-dimensional object. An object can
        possibly have multiple neighbours on a boundary
    """
    class Meta:
        name = "generic_grid_dynamic_space_dimension_object_boundary"

    index: int = field(
        default=999999999
    )
    neighbours: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class GenericGridScalar(IdsBaseClass):
    """
    Scalar real values on a generic grid (dynamic within a type 3 AoS)

    :ivar grid_index: Index of the grid used to represent this quantity
    :ivar grid_subset_index: Index of the grid subset the data is
        provided on. Corresponds to the index used in the grid subset
        definition: grid_subset(:)/identifier/index
    :ivar values: One scalar value is provided per element in the grid
        subset.
    :ivar coefficients: Interpolation coefficients, to be used for a
        high precision evaluation of the physical quantity with finite
        elements, provided per element in the grid subset (first
        dimension).
    """
    class Meta:
        name = "generic_grid_scalar"

    grid_index: int = field(
        default=999999999
    )
    grid_subset_index: int = field(
        default=999999999
    )
    values: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    coefficients: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


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
class RunawayElectronsGlobalVolume(IdsBaseClass):
    """
    Volume average global quantities related to the runaway_electrons.

    :ivar density: Runaway electrons density
    :ivar current_density: Runaways parallel current density =
        average(j.B) / B0, where B0 =
        runaway_electrons/vacuum_toroidal_field/b0
    :ivar e_field_dreicer: Dreicer electric field (parallel to magnetic
        field)
    :ivar e_field_critical: Critical electric field
    :ivar energy_density_kinetic: Runaways kinetic mean energy density
    :ivar pitch_angle: Average pitch angle of the runaways distribution
        function (v_parallel/|v|)
    :ivar momentum_critical_avalanche: Critical momentum for avalanche,
        Compton and tritium
    :ivar momentum_critical_hot_tail: Critical momentum for hot tail
    :ivar ddensity_dt_total: Total source of runaway electrons
    :ivar ddensity_dt_compton: Compton source of runaway electrons
    :ivar ddensity_dt_tritium: Tritium source of runaway electrons
    :ivar ddensity_dt_hot_tail: Hot tail source of runaway electrons
    :ivar ddensity_dt_dreicer: Dreicer source of runaway electrons
    """
    class Meta:
        name = "runaway_electrons_global_volume"

    density: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    current_density: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_dreicer: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_critical: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    energy_density_kinetic: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pitch_angle: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    momentum_critical_avalanche: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    momentum_critical_hot_tail: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_total: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_compton: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_tritium: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_hot_tail: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_dreicer: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class RunawayElectronsTransport(IdsBaseClass):
    """
    Transport coefficients for runaways.

    :ivar d: Effective diffusivity
    :ivar v: Effective convection
    :ivar flux: Flux
    """
    class Meta:
        name = "runaway_electrons_transport"

    d: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    flux: ndarray[(int,), float] = field(
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
class DistributionMarkers(IdsBaseClass):
    """
    Test particles for a given time slice.

    :ivar coordinate_identifier: Set of coordinate identifiers,
        coordinates on which the markers are represented
    :ivar weights: Weight of the markers, i.e. number of real particles
        represented by each marker. The dimension of the vector
        correspond to the number of markers
    :ivar positions: Position of the markers in the set of coordinates.
        The first dimension corresponds to the number of markers, the
        second dimension to the set of coordinates
    :ivar orbit_integrals: Integrals along the markers orbit. These
        dimensionless expressions are of the form: (1/tau) integral
        (f(n_tor,m_pol,k,eq,...) dt) from time - tau to time, where tau
        is the transit/trapping time of the marker and f() a
        dimensionless function (phase factor,drift,etc) of the
        equilibrium (e.g. q) and perturbation (Fourier harmonics
        n_tor,m_pol and bounce harmonic k) along the particles orbits.
        In fact the integrals are taken during the last orbit of each
        marker at the time value of the time node below
    :ivar orbit_integrals_instant: Integrals/quantities along the
        markers orbit. These dimensionless expressions are of the form:
        (1/tau) integral ( f(eq) dt) from time - tau to time_orbit for
        different values of time_orbit in the interval from time - tau
        to time, where tau is the transit/trapping time of the marker
        and f(eq) a dimensionless function (phase, drift,q,etc) of the
        equilibrium along the markers orbits. The integrals are taken
        during the last orbit of each marker at the time value of the
        time node below
    :ivar toroidal_mode: In case the orbit integrals are calculated for
        a given MHD perturbation, index of the toroidal mode considered.
        Refers to the time_slice/toroidal_mode array of the MHD_LINEAR
        IDS in which this perturbation is described
    :ivar time: Time
    """
    class Meta:
        name = "distribution_markers"

    coordinate_identifier: list[IdentifierDynamicAos3] = field(
        default_factory=list
    )
    weights: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    positions: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    orbit_integrals: Optional[DistributionMarkersOrbit] = field(
        default=None
    )
    orbit_integrals_instant: Optional[DistributionMarkersOrbitInstant] = field(
        default=None
    )
    toroidal_mode: int = field(
        default=999999999
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class DistributionsDGgdExpansion(IdsBaseClass):
    """
    Expansion of the distribution function for a given time slice, using a GGD
    representation.

    :ivar grid_subset: Values of the distribution function expansion,
        for various grid subsets
    """
    class Meta:
        name = "distributions_d_ggd_expansion"

    grid_subset: list[GenericGridScalar] = field(
        default_factory=list
    )


@dataclass(slots=True)
class GenericGridDynamicGridSubsetElement(IdsBaseClass):
    """
    Generic grid, element part of a grid_subset (dynamic within a type 3 AoS)

    :ivar object_value: Set of objects defining the element
    """
    class Meta:
        name = "generic_grid_dynamic_grid_subset_element"

    object_value: list[GenericGridDynamicGridSubsetElementObject] = field(
        default_factory=list
    )


@dataclass(slots=True)
class GenericGridDynamicSpaceDimensionObject(IdsBaseClass):
    """
    Generic grid, list of objects of a given dimension within a space (dynamic
    within a type 3 AoS)

    :ivar boundary: Set of  (n-1)-dimensional objects defining the
        boundary of this n-dimensional object
    :ivar geometry: Geometry data associated with the object, its
        detailed content is defined by ../../geometry_content. Its
        dimension depends on the type of object, geometry and coordinate
        considered.
    :ivar nodes: List of nodes forming this object (indices to
        objects_per_dimension(1)%object(:) in Fortran notation)
    :ivar measure: Measure of the space object, i.e. physical size
        (length for 1d, area for 2d, volume for 3d objects,...)
    :ivar geometry_2d: 2D geometry data associated with the object. Its
        dimension depends on the type of object, geometry and coordinate
        considered. Typically, the first dimension represents the object
        coordinates, while the second dimension would represent the
        values of the various degrees of freedom of the finite element
        attached to the object.
    """
    class Meta:
        name = "generic_grid_dynamic_space_dimension_object"

    boundary: list[GenericGridDynamicSpaceDimensionObjectBoundary] = field(
        default_factory=list
    )
    geometry: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    nodes: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    measure: float = field(
        default=9e+40
    )
    geometry_2d: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
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
class RunawayElectronsGgd(IdsBaseClass):
    """
    GGD data for 2D or 3D runaway_electrons fluid quantities.

    :ivar density: Runaway electrons density, given on various grid
        subsets
    :ivar current_density: Runaways parallel current density =
        average(j.B) / B0, where B0 =
        runaway_electrons/vacuum_toroidal_field/b0, given on various
        grid subsets
    :ivar e_field_dreicer: Dreicer electric field (parallel to B), given
        on various grid subsets
    :ivar e_field_critical: Critical electric field, given on various
        grid subsets
    :ivar energy_density_kinetic: Runaways kinetic energy density, given
        on various grid subsets
    :ivar pitch_angle: Average pitch angle of the runaways distribution
        function (v_parallel/|v|), given on various grid subsets
    :ivar momentum_critical_avalanche: Critical momentum for avalanche,
        Compton and tritium, given on various grid subsets
    :ivar momentum_critical_hot_tail: Critical momentum for hot tail,
        given on various grid subsets
    :ivar ddensity_dt_total: Total source of runaway electrons, given on
        various grid subsets
    :ivar ddensity_dt_compton: Compton source of runaway electrons,
        given on various grid subsets
    :ivar ddensity_dt_tritium: Tritium source of runaway electrons,
        given on various grid subsets
    :ivar ddensity_dt_hot_tail: Hot tail source of runaway electrons,
        given on various grid subsets
    :ivar ddensity_dt_dreicer: Dreicer source of runaway electrons,
        given on various grid subsets
    :ivar time: Time
    """
    class Meta:
        name = "runaway_electrons_ggd"

    density: list[GenericGridScalar] = field(
        default_factory=list
    )
    current_density: list[GenericGridScalar] = field(
        default_factory=list
    )
    e_field_dreicer: list[GenericGridScalar] = field(
        default_factory=list
    )
    e_field_critical: list[GenericGridScalar] = field(
        default_factory=list
    )
    energy_density_kinetic: list[GenericGridScalar] = field(
        default_factory=list
    )
    pitch_angle: list[GenericGridScalar] = field(
        default_factory=list
    )
    momentum_critical_avalanche: list[GenericGridScalar] = field(
        default_factory=list
    )
    momentum_critical_hot_tail: list[GenericGridScalar] = field(
        default_factory=list
    )
    ddensity_dt_total: list[GenericGridScalar] = field(
        default_factory=list
    )
    ddensity_dt_compton: list[GenericGridScalar] = field(
        default_factory=list
    )
    ddensity_dt_tritium: list[GenericGridScalar] = field(
        default_factory=list
    )
    ddensity_dt_hot_tail: list[GenericGridScalar] = field(
        default_factory=list
    )
    ddensity_dt_dreicer: list[GenericGridScalar] = field(
        default_factory=list
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class RunawayElectronsGlobalQuantities(IdsBaseClass):
    """
    Global quantities related to the runaway_electrons.

    :ivar current_tor: Total runaway current (toroidal component)
    :ivar energy_kinetic: Total runaway kinetic energy
    :ivar volume_average: Volume average runaways parameters
    """
    class Meta:
        name = "runaway_electrons_global_quantities"

    current_tor: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    energy_kinetic: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    volume_average: Optional[RunawayElectronsGlobalVolume] = field(
        default=None
    )


@dataclass(slots=True)
class RunawayElectronsProfiles1D(IdsBaseClass):
    """
    1D radial profiles for runaway_electrons data.

    :ivar grid: Radial grid
    :ivar density: Runaway electrons density
    :ivar current_density: Runaways parallel current density =
        average(j.B) / B0, where B0 =
        runaway_electrons/vacuum_toroidal_field/b0
    :ivar e_field_dreicer: Dreicer electric field (parallel to B)
    :ivar e_field_critical: Critical electric field
    :ivar energy_density_kinetic: Runaways kinetic mean energy density
    :ivar pitch_angle: Average pitch angle of the runaways distribution
        function (v_parallel/|v|)
    :ivar momentum_critical_avalanche: Critical momentum for avalanche,
        Compton and tritium
    :ivar momentum_critical_hot_tail: Critical momentum for hot tail
    :ivar ddensity_dt_total: Total source of runaway electrons
    :ivar ddensity_dt_compton: Compton source of runaway electrons
    :ivar ddensity_dt_tritium: Tritium source of runaway electrons
    :ivar ddensity_dt_hot_tail: Hot tail source of runaway electrons
    :ivar ddensity_dt_dreicer: Dreicer source of runaway electrons
    :ivar transport_perpendicular: Effective perpendicular transport to
        the magnetic field for runaways
    :ivar time: Time
    """
    class Meta:
        name = "runaway_electrons_profiles_1d"

    grid: Optional[CoreRadialGrid] = field(
        default=None
    )
    density: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    current_density: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_dreicer: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_critical: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    energy_density_kinetic: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pitch_angle: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    momentum_critical_avalanche: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    momentum_critical_hot_tail: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_total: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_compton: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_tritium: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_hot_tail: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ddensity_dt_dreicer: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    transport_perpendicular: Optional[RunawayElectronsTransport] = field(
        default=None
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class DistributionsDGgdNogrid(IdsBaseClass):
    """
    Distribution function for a given time slice, using a GGD representation
    assumed outside of the structure.

    :ivar temperature: Reference temperature profile used to define the
        local thermal energy and the thermal velocity (for normalisation
        of the grid coordinates)
    :ivar expansion: Distribution function expanded into a vector of
        successive approximations. The first element in the vector
        (expansion(1)) is the zeroth order distribution function, while
        the K:th element in the vector (expansion(K)) is the K:th
        correction, such that the total distribution function is a sum
        over all elements in the expansion vector.
    :ivar expansion_fd3v: Distribution function multiplied by the volume
        of the local velocity cell d3v, expanded into a vector of
        successive approximations. The first element in the vector
        (expansion(1)) is the zeroth order distribution function, while
        the K:th element in the vector (expansion(K)) is the K:th
        correction, such that the total distribution function is a sum
        over all elements in the expansion vector.
    :ivar time: Time
    """
    class Meta:
        name = "distributions_d_ggd_nogrid"

    temperature: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    expansion: list[DistributionsDGgdExpansion] = field(
        default_factory=list
    )
    expansion_fd3v: list[DistributionsDGgdExpansion] = field(
        default_factory=list
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class GenericGridDynamicGridSubset(IdsBaseClass):
    """
    Generic grid grid_subset (dynamic within a type 3 AoS)

    :ivar identifier: Grid subset identifier
    :ivar dimension: Space dimension of the grid subset elements. This
        must be equal to the sum of the dimensions of the individual
        objects forming the element.
    :ivar element: Set of elements defining the grid subset. An element
        is defined by a combination of objects from potentially all
        spaces
    :ivar base: Set of bases for the grid subset. For each base, the
        structure describes the projection of the base vectors on the
        canonical frame of the grid.
    :ivar metric: Metric of the canonical frame onto Cartesian
        coordinates
    """
    class Meta:
        name = "generic_grid_dynamic_grid_subset"

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    dimension: int = field(
        default=999999999
    )
    element: list[GenericGridDynamicGridSubsetElement] = field(
        default_factory=list
    )
    base: list[GenericGridDynamicGridSubsetMetric] = field(
        default_factory=list
    )
    metric: Optional[GenericGridDynamicGridSubsetMetric] = field(
        default=None
    )


@dataclass(slots=True)
class GenericGridDynamicSpaceDimension(IdsBaseClass):
    """
    Generic grid, list of dimensions within a space (dynamic within a type 3 AoS)

    :ivar object_value: Set of objects for a given dimension
    :ivar geometry_content: Content of the ../object/geometry node for
        this dimension
    """
    class Meta:
        name = "generic_grid_dynamic_space_dimension"

    object_value: list[GenericGridDynamicSpaceDimensionObject] = field(
        default_factory=list
    )
    geometry_content: Optional[IdentifierDynamicAos3] = field(
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
class GenericGridDynamicSpace(IdsBaseClass):
    """
    Generic grid space (dynamic within a type 3 AoS)

    :ivar identifier: Space identifier
    :ivar geometry_type: Type of space geometry (0: standard, 1:Fourier,
        &gt;1: Fourier with periodicity)
    :ivar coordinates_type: Type of coordinates describing the physical
        space, for every coordinate of the space. The size of this node
        therefore defines the dimension of the space. The meaning of
        these predefined integer constants can be found in the Data
        Dictionary under utilities/coordinate_identifier.xml
    :ivar objects_per_dimension: Definition of the space objects for
        every dimension (from one to the dimension of the highest-
        dimensional objects). The index correspond to 1=nodes, 2=edges,
        3=faces, 4=cells/volumes, .... For every index, a collection of
        objects of that dimension is described.
    """
    class Meta:
        name = "generic_grid_dynamic_space"

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    geometry_type: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    coordinates_type: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    objects_per_dimension: list[GenericGridDynamicSpaceDimension] = field(
        default_factory=list
    )


@dataclass(slots=True)
class RunawayElectronsDistribution(IdsBaseClass):
    """
    Distribution function of the runaway electrons.

    :ivar gyro_type: Defines how to interpret the spatial coordinates: 1
        = given at the actual particle birth point; 2 =given at the gyro
        centre of the birth point
    :ivar ggd: Distribution represented using the ggd, for various time
        slices
    :ivar markers: Distribution represented by a set of markers (test
        particles)
    """
    class Meta:
        name = "runaway_electrons_distribution"

    gyro_type: int = field(
        default=999999999
    )
    ggd: list[DistributionsDGgdNogrid] = field(
        default_factory=list
    )
    markers: list[DistributionMarkers] = field(
        default_factory=list
    )


@dataclass(slots=True)
class GenericGridAos3Root(IdsBaseClass):
    """
    Generic grid (being itself the root of a type 3 AoS)

    :ivar identifier: Grid identifier
    :ivar path: Path of the grid, including the IDS name, in case of
        implicit reference to a grid_ggd node described in another IDS.
        To be filled only if the grid is not described explicitly in
        this grid_ggd structure. Example syntax:
        IDS::wall/0/description_ggd(1)/grid_ggd, means that the grid is
        located in the wall IDS, occurrence 0, with relative path
        description_ggd(1)/grid_ggd, using Fortran index convention
        (here : first index of the array)
    :ivar space: Set of grid spaces
    :ivar grid_subset: Grid subsets
    :ivar time: Time
    """
    class Meta:
        name = "generic_grid_aos3_root"

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None
    )
    path: str = field(
        default=""
    )
    space: list[GenericGridDynamicSpace] = field(
        default_factory=list
    )
    grid_subset: list[GenericGridDynamicGridSubset] = field(
        default_factory=list
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class RunawayElectrons(IdsBaseClass):
    """
    Description of runaway electrons.

    :ivar ids_properties:
    :ivar e_field_critical_definition: Definition chosen for the
        critical electric field (in global_quantities, profiles_1d and
        ggd)
    :ivar momentum_critical_avalanche_definition: Definition chosen for
        the critical momentum for avalanche, Compton and tritium (in
        global_quantities, profiles_1d and ggd)
    :ivar momentum_critical_hot_tail_definition: Definition chosen for
        the critical momentum for hot tail (in global_quantities,
        profiles_1d and ggd)
    :ivar global_quantities: Global quantities
    :ivar profiles_1d: Radial flux surface averaged profiles for a set
        of time slices
    :ivar grid_ggd: Grid (using the Generic Grid Description), for
        various time slices
    :ivar ggd_fluid: Fluid quantities represented using the general grid
        description for 2D or 3D description
    :ivar distribution: Distribution function of the runaway electrons
    :ivar vacuum_toroidal_field: Characteristics of the vacuum toroidal
        field (used in rho_tor definition and in the normalization of
        current densities)
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "runaway_electrons"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    e_field_critical_definition: Optional[Identifier] = field(
        default=None
    )
    momentum_critical_avalanche_definition: Optional[Identifier] = field(
        default=None
    )
    momentum_critical_hot_tail_definition: Optional[Identifier] = field(
        default=None
    )
    global_quantities: Optional[RunawayElectronsGlobalQuantities] = field(
        default=None
    )
    profiles_1d: list[RunawayElectronsProfiles1D] = field(
        default_factory=list
    )
    grid_ggd: list[GenericGridAos3Root] = field(
        default_factory=list
    )
    ggd_fluid: list[RunawayElectronsGgd] = field(
        default_factory=list
    )
    distribution: Optional[RunawayElectronsDistribution] = field(
        default=None
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None
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
