# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class CodePartialConstant(IdsBaseClass):
    """
    Description of code-specific parameters and constant output flag.

    :ivar parameters: List of the code specific parameters in XML format
    :ivar output_flag: Output flag : 0 means the run is successful,
        other values mean some difficulty has been encountered, the
        exact meaning is then code specific. Negative values mean the
        result shall not be used.
    """
    class Meta:
        name = "code_partial_constant"

    parameters: str = field(
        default=""
    )
    output_flag: int = field(
        default=999999999
    )


@dataclass(slots=True)
class EntryTag(IdsBaseClass):
    """
    Tag qualifying an entry or a list of entries.

    :ivar name: Name of the tag
    :ivar comment: Any comment describing the content of the tagged list
        of entries
    """
    class Meta:
        name = "entry_tag"

    name: str = field(
        default=""
    )
    comment: str = field(
        default=""
    )


@dataclass(slots=True)
class Collisions(IdsBaseClass):
    """
    Collisions related quantities.

    :ivar collisionality_norm: Normalised collisionality between two
        species
    """
    class Meta:
        name = "gyrokinetics_collisions"

    collisionality_norm: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class FluxSurface(IdsBaseClass):
    """
    Flux surface characteristics.

    :ivar r_minor_norm: Normalised minor radius of the flux surface of
        interest = 1/2 * (max(R) - min(R))/L_ref
    :ivar elongation: Elongation
    :ivar delongation_dr_minor_norm: Derivative of the elongation with
        respect to r_minor_norm
    :ivar dgeometric_axis_r_dr_minor: Derivative of the major radius of
        the surface geometric axis with respect to r_minor
    :ivar dgeometric_axis_z_dr_minor: Derivative of the height of the
        surface geometric axis with respect to r_minor
    :ivar q: Safety factor
    :ivar magnetic_shear_r_minor: Magnetic shear, defined as
        r_minor_norm/q . dq/dr_minor_norm (different definition from the
        equilibrium IDS)
    :ivar pressure_gradient_norm: Normalised pressure gradient
        (derivative with respect to r_minor_norm)
    :ivar ip_sign: Sign of the plasma current
    :ivar b_field_tor_sign: Sign of the toroidal magnetic field
    :ivar shape_coefficients_c: 'c' coefficients in the formula defining
        the shape of the flux surface
    :ivar dc_dr_minor_norm: Derivative of the 'c' shape coefficients
        with respect to r_minor_norm
    :ivar shape_coefficients_s: 's' coefficients in the formula defining
        the shape of the flux surface
    :ivar ds_dr_minor_norm: Derivative of the 's' shape coefficients
        with respect to r_minor_norm
    """
    class Meta:
        name = "gyrokinetics_flux_surface"

    r_minor_norm: float = field(
        default=9e+40
    )
    elongation: float = field(
        default=9e+40
    )
    delongation_dr_minor_norm: float = field(
        default=9e+40
    )
    dgeometric_axis_r_dr_minor: float = field(
        default=9e+40
    )
    dgeometric_axis_z_dr_minor: float = field(
        default=9e+40
    )
    q: float = field(
        default=9e+40
    )
    magnetic_shear_r_minor: float = field(
        default=9e+40
    )
    pressure_gradient_norm: float = field(
        default=9e+40
    )
    ip_sign: float = field(
        default=9e+40
    )
    b_field_tor_sign: float = field(
        default=9e+40
    )
    shape_coefficients_c: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    dc_dr_minor_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    shape_coefficients_s: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    ds_dr_minor_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class Fluxes(IdsBaseClass):
    """
    Turbulent fluxes for a given eigenmode and a given species.

    :ivar particles_phi_potential: Contribution of the perturbed
        electrostatic potential to the normalised particle flux
    :ivar particles_a_field_parallel: Contribution of the perturbed
        parallel electromagnetic potential to the normalised particle
        flux
    :ivar particles_b_field_parallel: Contribution of the perturbed
        parallel magnetic field to the normalised particle flux
    :ivar energy_phi_potential: Contribution of the perturbed
        electrostatic potential to the normalised energy flux
    :ivar energy_a_field_parallel: Contribution of the perturbed
        parallel electromagnetic potential to the normalised energy flux
    :ivar energy_b_field_parallel: Contribution of the perturbed
        parallel magnetic field to the normalised energy flux
    :ivar momentum_tor_parallel_phi_potential: Contribution of the
        perturbed electrostatic potential to the parallel component of
        the normalised toroidal momentum flux
    :ivar momentum_tor_parallel_a_field_parallel: Contribution of the
        perturbed parallel electromagnetic potential to the parallel
        component of the normalised toroidal momentum flux
    :ivar momentum_tor_parallel_b_field_parallel: Contribution of the
        perturbed parallel magnetic field to the parallel component of
        the normalised toroidal momentum flux
    :ivar momentum_tor_perpendicular_phi_potential: Contribution of the
        perturbed electrostatic potential to the perpendicular component
        of the normalised toroidal momentum flux
    :ivar momentum_tor_perpendicular_a_field_parallel: Contribution of
        the perturbed parallel electromagnetic potential to the
        perpendicular component of the normalised toroidal momentum flux
    :ivar momentum_tor_perpendicular_b_field_parallel: Contribution of
        the perturbed parallel magnetic field to the perpendicular
        component of the normalised toroidal momentum flux
    """
    class Meta:
        name = "gyrokinetics_fluxes"

    particles_phi_potential: float = field(
        default=9e+40
    )
    particles_a_field_parallel: float = field(
        default=9e+40
    )
    particles_b_field_parallel: float = field(
        default=9e+40
    )
    energy_phi_potential: float = field(
        default=9e+40
    )
    energy_a_field_parallel: float = field(
        default=9e+40
    )
    energy_b_field_parallel: float = field(
        default=9e+40
    )
    momentum_tor_parallel_phi_potential: float = field(
        default=9e+40
    )
    momentum_tor_parallel_a_field_parallel: float = field(
        default=9e+40
    )
    momentum_tor_parallel_b_field_parallel: float = field(
        default=9e+40
    )
    momentum_tor_perpendicular_phi_potential: float = field(
        default=9e+40
    )
    momentum_tor_perpendicular_a_field_parallel: float = field(
        default=9e+40
    )
    momentum_tor_perpendicular_b_field_parallel: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class InputNormalizing(IdsBaseClass):
    """
    GK normalizing quantities.

    :ivar t_e: Electron temperature at outboard equatorial midplane of
        the flux surface (poloidal_angle = 0)
    :ivar n_e: Electron density at outboard equatorial midplane of the
        flux surface (poloidal_angle = 0)
    :ivar r: Major radius of the flux surface of interest, defined as
        (min(R)+max(R))/2
    :ivar b_field_tor: Toroidal magnetic field at major radius r
    """
    class Meta:
        name = "gyrokinetics_input_normalizing"

    t_e: float = field(
        default=9e+40
    )
    n_e: float = field(
        default=9e+40
    )
    r: float = field(
        default=9e+40
    )
    b_field_tor: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class InputSpeciesGlobal(IdsBaseClass):
    """
    Species global parameters.

    :ivar beta_reference: Reference plasma beta (see detailed
        documentation at the root of the IDS)
    :ivar velocity_tor_norm: Normalised toroidal velocity of species
        (all species are assumed to have a purely toroidal velocity with
        a common toroidal angular frequency)
    :ivar zeff: Effective charge
    :ivar debye_length_reference: Debye length computed from the
        reference quantities (see detailed documentation at the root of
        the IDS)
    :ivar shearing_rate_norm: Normalised ExB shearing rate (for non-
        linear runs only)
    """
    class Meta:
        name = "gyrokinetics_input_species_global"

    beta_reference: float = field(
        default=9e+40
    )
    velocity_tor_norm: float = field(
        default=9e+40
    )
    zeff: float = field(
        default=9e+40
    )
    debye_length_reference: float = field(
        default=9e+40
    )
    shearing_rate_norm: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class Model(IdsBaseClass):
    """
    Description of the GK model assumptions.

    :ivar include_centrifugal_effects: Flag = 1 if centrifugal effects
        are retained, 0 otherwise
    :ivar include_a_field_parallel: Flag = 1 if fluctuations of the
        parallel vector potential are retained, 0 otherwise
    :ivar include_b_field_parallel: Flag = 1 if fluctuations of the
        parallel magnetic field are retained, 0 otherwise
    :ivar include_full_curvature_drift: Flag = 1 if all contributions to
        the curvature drift are included (including beta_prime), 0
        otherwise. Neglecting the beta_prime contribution (Flag=0) is
        only recommended together with the neglect of parallel magnetic
        field fluctuations
    :ivar collisions_pitch_only: Flag = 1 if only pitch-angle scattering
        is retained, 0 otherwise
    :ivar collisions_momentum_conservation: Flag = 1 if the collision
        operator conserves momentum, 0 otherwise
    :ivar collisions_energy_conservation: Flag = 1 if the collision
        operator conserves energy, 0 otherwise
    :ivar collisions_finite_larmor_radius: Flag = 1 if finite larmor
        radius effects are retained in the collision operator, 0
        otherwise
    :ivar non_linear_run: Flag = 1 if this is a non-linear run, 0 for a
        linear run
    :ivar time_interval_norm: Normalised time interval used to average
        fluxes in non-linear runs
    """
    class Meta:
        name = "gyrokinetics_model"

    include_centrifugal_effects: int = field(
        default=999999999
    )
    include_a_field_parallel: int = field(
        default=999999999
    )
    include_b_field_parallel: int = field(
        default=999999999
    )
    include_full_curvature_drift: int = field(
        default=999999999
    )
    collisions_pitch_only: int = field(
        default=999999999
    )
    collisions_momentum_conservation: int = field(
        default=999999999
    )
    collisions_energy_conservation: int = field(
        default=999999999
    )
    collisions_finite_larmor_radius: int = field(
        default=999999999
    )
    non_linear_run: int = field(
        default=999999999
    )
    time_interval_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class Moments(IdsBaseClass):
    """
    Turbulent moments for a given eigenmode and a given species, with gyroaveraged
    quantities.

    :ivar density: Normalised density
    :ivar density_gyroav: Normalised density (gyroaveraged)
    :ivar j_parallel: Normalised parallel current density
    :ivar j_parallel_gyroav: Normalised parallel current density
        (gyroaveraged)
    :ivar pressure_parallel: Normalised parallel temperature
    :ivar pressure_parallel_gyroav: Normalised parallel temperature
        (gyroaveraged)
    :ivar pressure_perpendicular: Normalised perpendicular temperature
    :ivar pressure_perpendicular_gyroav: Normalised perpendicular
        temperature (gyroaveraged)
    :ivar heat_flux_parallel: Normalised parallel heat flux (integral of
        0.5 * m * v_par * v^2)
    :ivar heat_flux_parallel_gyroav: Normalised parallel heat flux
        (integral of 0.5 * m * v_par * v^2, gyroaveraged)
    :ivar v_parallel_energy_perpendicular: Normalised moment (integral
        over 0.5 * m * v_par * v_perp^2)
    :ivar v_parallel_energy_perpendicular_gyroav: Normalised moment
        (integral over 0.5 * m * v_par * v_perp^2, gyroaveraged)
    :ivar v_perpendicular_square_energy: Normalised moment (integral
        over 0.5 * m * v_perp^2 * v^2)
    :ivar v_perpendicular_square_energy_gyroav: Normalised moment
        (integral over 0.5 * m * v_perp^2 * v^2, gyroaveraged)
    """
    class Meta:
        name = "gyrokinetics_moments"

    density: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    density_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    j_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    j_parallel_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_parallel_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_perpendicular: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_perpendicular_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    heat_flux_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    heat_flux_parallel_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_parallel_energy_perpendicular: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_parallel_energy_perpendicular_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_perpendicular_square_energy: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_perpendicular_square_energy_gyroav: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class MomentsParticles(IdsBaseClass):
    """
    Turbulent moments for a given eigenmode and a given species, without
    gyroaveraged quantities.

    :ivar density: Normalised density
    :ivar j_parallel: Normalised parallel current density
    :ivar pressure_parallel: Normalised parallel temperature
    :ivar pressure_perpendicular: Normalised perpendicular temperature
    :ivar heat_flux_parallel: Normalised parallel heat flux (integral of
        0.5 * m * v_par * v^2)
    :ivar v_parallel_energy_perpendicular: Normalised moment (integral
        over 0.5 * m * v_par * v_perp^2)
    :ivar v_perpendicular_square_energy: Normalised moment (integral
        over 0.5 * m * v_perp^2 * v^2)
    """
    class Meta:
        name = "gyrokinetics_moments_particles"

    density: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    j_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pressure_perpendicular: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    heat_flux_parallel: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_parallel_energy_perpendicular: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    v_perpendicular_square_energy: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class Species(IdsBaseClass):
    """
    List of species.

    :ivar charge_norm: Normalised charge
    :ivar mass_norm: Normalised mass
    :ivar density_norm: Normalised density
    :ivar density_log_gradient_norm: Normalised logarithmic gradient
        (with respect to r_minor_norm) of the density
    :ivar temperature_norm: Normalised temperature
    :ivar temperature_log_gradient_norm: Normalised logarithmic gradient
        (with respect to r_minor_norm) of the temperature
    :ivar velocity_tor_gradient_norm: Normalised gradient (with respect
        to r_minor_norm) of the toroidal velocity
    """
    class Meta:
        name = "gyrokinetics_species"

    charge_norm: float = field(
        default=9e+40
    )
    mass_norm: float = field(
        default=9e+40
    )
    density_norm: float = field(
        default=9e+40
    )
    density_log_gradient_norm: float = field(
        default=9e+40
    )
    temperature_norm: float = field(
        default=9e+40
    )
    temperature_log_gradient_norm: float = field(
        default=9e+40
    )
    velocity_tor_gradient_norm: float = field(
        default=9e+40
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
class FluxesMoments(IdsBaseClass):
    """
    Turbulent fluxes and moments for a given eigenmode and a given species.

    :ivar moments_norm_gyrocenter: Moments (normalised) of the perturbed
        distribution function of gyrocenters
    :ivar moments_norm_particle: Moments (normalised) of the perturbed
        distribution function of particles
    :ivar fluxes_norm_gyrocenter: Normalised gyrocenter fluxes in the
        laboratory frame
    :ivar fluxes_norm_gyrocenter_rotating_frame: Normalised gyrocenter
        fluxes in the rotating frame
    :ivar fluxes_norm_particle: Normalised particle fluxes in the
        laboratory frame
    :ivar fluxes_norm_particle_rotating_frame: Normalised particle
        fluxes in the rotating frame
    """
    class Meta:
        name = "gyrokinetics_fluxes_moments"

    moments_norm_gyrocenter: Optional[Moments] = field(
        default=None
    )
    moments_norm_particle: Optional[MomentsParticles] = field(
        default=None
    )
    fluxes_norm_gyrocenter: Optional[Fluxes] = field(
        default=None
    )
    fluxes_norm_gyrocenter_rotating_frame: Optional[Fluxes] = field(
        default=None
    )
    fluxes_norm_particle: Optional[Fluxes] = field(
        default=None
    )
    fluxes_norm_particle_rotating_frame: Optional[Fluxes] = field(
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
class Eigenmode(IdsBaseClass):
    """
    Output of the GK calculation for a given eigenmode.

    :ivar poloidal_turns: Number of poloidal turns considered in the
        flux-tube simulation
    :ivar growth_rate_norm: Growth rate
    :ivar frequency_norm: Frequency
    :ivar growth_rate_tolerance: Relative tolerance on the growth rate
        (convergence of the simulation)
    :ivar phi_potential_perturbed_weight: Amplitude of the perturbed
        electrostatic potential normalised to the sum of amplitudes of
        all perturbed fields
    :ivar phi_potential_perturbed_parity: Parity of the perturbed
        electrostatic potential with respect to theta = 0 (poloidal
        angle)
    :ivar a_field_parallel_perturbed_weight: Amplitude of the perturbed
        parallel vector potential normalised to the sum of amplitudes of
        all perturbed fields
    :ivar a_field_parallel_perturbed_parity: Parity of the perturbed
        parallel vector potential with respect to theta = 0 (poloidal
        angle)
    :ivar b_field_parallel_perturbed_weight: Amplitude of the perturbed
        parallel magnetic field normalised to the sum of amplitudes of
        all perturbed fields
    :ivar b_field_parallel_perturbed_parity: Parity of the perturbed
        parallel magnetic field with respect to theta = 0 (poloidal
        angle)
    :ivar poloidal_angle: Poloidal angle grid (see detailed
        documentation at the root of the IDS)
    :ivar phi_potential_perturbed_norm: Normalised perturbed
        electrostatic potential
    :ivar a_field_parallel_perturbed_norm: Normalised perturbed parallel
        vector potential
    :ivar b_field_parallel_perturbed_norm: Normalised perturbed parallel
        magnetic field
    :ivar time_norm: Normalised time of the gyrokinetic simulation
    :ivar fluxes_moments: Fluxes and moments of the perturbed
        distribution function, for this eigenmode and for each species.
        The fluxes are time averaged for non-linear runs (using model/
        time_interval_norm) and given at the last time step for linear
        runs.
    :ivar code: Code-specific parameters used for this eigenmode
    :ivar initial_value_run: Flag = 1 if this is an initial value run, 0
        for an eigenvalue run
    """
    class Meta:
        name = "gyrokinetics_eigenmode"

    poloidal_turns: int = field(
        default=999999999
    )
    growth_rate_norm: float = field(
        default=9e+40
    )
    frequency_norm: float = field(
        default=9e+40
    )
    growth_rate_tolerance: float = field(
        default=9e+40
    )
    phi_potential_perturbed_weight: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    phi_potential_perturbed_parity: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    a_field_parallel_perturbed_weight: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    a_field_parallel_perturbed_parity: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    b_field_parallel_perturbed_weight: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    b_field_parallel_perturbed_parity: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    poloidal_angle: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    phi_potential_perturbed_norm: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    a_field_parallel_perturbed_norm: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    b_field_parallel_perturbed_norm: ndarray[(int, int), complex] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    fluxes_moments: list[FluxesMoments] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    code: Optional[CodePartialConstant] = field(
        default=None
    )
    initial_value_run: int = field(
        default=999999999
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
class Wavevector(IdsBaseClass):
    """
    Components of the linear mode wavevector.

    :ivar radial_component_norm: Normalised radial component of the
        wavevector
    :ivar binormal_component_norm: Normalised binormal component of the
        wavevector
    :ivar eigenmode: Set of eigenmode for this wavector
    """
    class Meta:
        name = "gyrokinetics_wavevector"

    radial_component_norm: float = field(
        default=9e+40
    )
    binormal_component_norm: float = field(
        default=9e+40
    )
    eigenmode: list[Eigenmode] = field(
        default_factory=list,
        metadata={
            "max_occurs": 5,
        }
    )


@dataclass(slots=True)
class Gyrokinetics(IdsBaseClass):
    """Description of a gyrokinetic simulation (delta-f, flux-tube).

    All quantities within this IDS are normalised (apart from time and
    from the normalizing quantities structure), thus independent of
    rhostar, consistently with the local approximation and a spectral
    representation is assumed in the perpendicular plane (i.e.
    homogeneous turbulence).

    :ivar ids_properties:
    :ivar tag: Set of tags to which this entry belongs
    :ivar normalizing_quantities: Physical quantities used for
        normalization (useful to link to the original
        simulation/experience)
    :ivar flux_surface: Flux surface characteristics
    :ivar model: Assumptions of the GK calculations
    :ivar species_all: Physical quantities common to all species
    :ivar species: Set of species (including electrons) used in the
        calculation and related quantities
    :ivar collisions: Collisions related quantities
    :ivar wavevector: Set of wavevectors
    :ivar fluxes_integrated_norm: Normalised fluxes of particles
        computed in the laboratory frame per species, summed over all
        wavevectors, and averaged over the time interval specified in
        model/time_interval_norm (non-linear runs only)
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "gyrokinetics"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    tag: list[EntryTag] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    normalizing_quantities: Optional[InputNormalizing] = field(
        default=None
    )
    flux_surface: Optional[FluxSurface] = field(
        default=None
    )
    model: Optional[Model] = field(
        default=None
    )
    species_all: Optional[InputSpeciesGlobal] = field(
        default=None
    )
    species: list[Species] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    collisions: Optional[Collisions] = field(
        default=None
    )
    wavevector: list[Wavevector] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    fluxes_integrated_norm: list[Fluxes] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
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
