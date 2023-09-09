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
class PsiNormalization(IdsBaseClass):
    """
    Quantities used to normalize psi, as a function of time.

    :ivar psi_magnetic_axis: Value of the poloidal magnetic flux at the
        magnetic axis
    :ivar psi_boundary: Value of the poloidal magnetic flux at the
        plasma boundary
    :ivar time: Time for the R,Z,phi coordinates
    """
    class Meta:
        name = "psi_normalization"

    psi_magnetic_axis: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    psi_boundary: ndarray[(int,), float] = field(
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
class ReflectometerDopplerPosition1D(IdsBaseClass):
    """
    R, Z, Phi, psi, rho_tor_norm and theta positions associated to the doppler
    structure (1D, dynamic within a type 1 array of structure)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    :ivar psi: Poloidal flux
    :ivar rho_tor_norm: Normalised toroidal flux coordinate
    :ivar rho_pol_norm: Normalised poloidal flux coordinate =
        sqrt((psi(rho)-psi(magnetic_axis)) /
        (psi(LCFS)-psi(magnetic_axis)))
    :ivar theta: Poloidal angle (oriented clockwise when viewing the
        poloidal cross section on the right hand side of the tokamak
        axis of symmetry, with the origin placed on the plasma magnetic
        axis)
    """
    class Meta:
        name = "reflectometer_doppler_position_1d"

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
    psi: ndarray[(int,), float] = field(
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
    rho_pol_norm: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    theta: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class ReflectometerFluctuationLevelPosition2D(IdsBaseClass):
    """
    R, Z, Phi, psi, rho_tor_norm and theta positions associated to the density
    fluctuations (2D, dynamic within a type 1 array of structure)

    :ivar r: Major radius
    :ivar z: Height
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above)
    :ivar psi: Poloidal flux
    :ivar rho_tor_norm: Normalised toroidal flux coordinate
    :ivar rho_pol_norm: Normalised poloidal flux coordinate =
        sqrt((psi(rho)-psi(magnetic_axis)) /
        (psi(LCFS)-psi(magnetic_axis)))
    :ivar theta: Poloidal angle (oriented clockwise when viewing the
        poloidal cross section on the right hand side of the tokamak
        axis of symmetry, with the origin placed on the plasma magnetic
        axis)
    """
    class Meta:
        name = "reflectometer_fluctuation_level_position_2d"

    r: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    z: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    phi: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    psi: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_tor_norm: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    rho_pol_norm: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    theta: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class ReflectometerFluctuationRaw(IdsBaseClass):
    """
    Raw signal for reflectometer.

    :ivar i_component: I component of the IQ detector used to retrieve
        the phase of signal's envelope
    :ivar q_component: Q component of the IQ detector used to retrieve
        the phase of signal's envelope
    :ivar time: Time
    """
    class Meta:
        name = "reflectometer_fluctuation_raw"

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
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class ReflectometerFluctuationSpectrum(IdsBaseClass):
    """
    Spectrum of the fluctuations.

    :ivar power_log: Power spectrum in log scale
    :ivar frequencies_fourier: Array of frequencies used for the Fourier
        transform
    :ivar time_width: Width of the time interval over which the spectrum
        is processed. By convention, the time interval starts at time-
        time_width and ends at time.
    :ivar time: Time
    """
    class Meta:
        name = "reflectometer_fluctuation_spectrum"

    power_log: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    frequencies_fourier: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time_width: float = field(
        default=9e+40
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
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
class X1X21DStatic(IdsBaseClass):
    """
    Structure for list of X1, X2 positions (1D, static)

    :ivar x1: Positions along x1 axis
    :ivar x2: Positions along x2 axis
    """
    class Meta:
        name = "x1x21d_static"

    x1: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    x2: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class Xyz0DDynamicAos3(IdsBaseClass):
    """
    Structure for list of X, Y, Z components (0D, dynamic within an AoS3)

    :ivar x: Component along X axis
    :ivar y: Component along Y axis
    :ivar z: Component along Z axis
    """
    class Meta:
        name = "xyz0d_dynamic_aos3"

    x: float = field(
        default=9e+40
    )
    y: float = field(
        default=9e+40
    )
    z: float = field(
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
class FlatObjectOrientationAos3(IdsBaseClass):
    """
    Dynamic description of X1, X2, X3 vectors for a planar object within an AoS
    type 3.

    :ivar x1_unit_vector: Components of the X1 direction unit vector in
        the (X,Y,Z) coordinate system, where X is the major radius axis
        for phi = 0, Y is the major radius axis for phi = pi/2, and Z is
        the height axis. The X1 vector is more horizontal than X2 (has a
        smaller abs(Z) component) and oriented in the positive phi
        direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector: Components of the X2 direction unit vector in
        the (X,Y,Z) coordinate system, where X is the major radius axis
        for phi = 0, Y is the major radius axis for phi = pi/2, and Z is
        the height axis. The X2 axis is orthonormal so that uX2 = uX3 x
        uX1.
    :ivar x3_unit_vector: Components of the X3 direction unit vector in
        the (X,Y,Z) coordinate system, where X is the major radius axis
        for phi = 0, Y is the major radius axis for phi = pi/2, and Z is
        the height axis. The X3 axis is normal to the detector/aperture
        plane and oriented towards the plasma.
    """
    class Meta:
        name = "flat_object_orientation_aos3"

    x1_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None
    )
    x2_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None
    )
    x3_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None
    )


@dataclass(slots=True)
class FlatObjectStatic(IdsBaseClass):
    """
    Static part of the description of a planar object.

    :ivar geometry_type: Type of geometry used to describe the surface
        of the detector or aperture (1:'outline', 2:'circular',
        3:'rectangle'). In case of 'outline', the surface is described
        by an outline of point in a local coordinate system defined by a
        centre and three unit vectors X1, X2, X3. Note that there is
        some flexibility here and the data provider should choose the
        most convenient coordinate system for the object, respecting the
        definitions of (X1,X2,X3) indicated below. In case of
        'circular', the surface is a circle defined by its centre,
        radius, and normal vector oriented towards the plasma X3.  In
        case of 'rectangle', the surface is a rectangle defined by its
        centre, widths in the X1 and X2 directions, and normal vector
        oriented towards the plasma X3.
    :ivar centre: If geometry_type=2, coordinates of the centre of the
        circle. If geometry_type=1 or 3, coordinates of the origin of
        the local coordinate system (X1,X2,X3) describing the plane
        detector/aperture. This origin is located within the
        detector/aperture area.
    :ivar radius: Radius of the circle, used only if geometry_type = 2
    :ivar x1_width: Full width of the aperture in the X1 direction, used
        only if geometry_type = 3
    :ivar x2_width: Full width of the aperture in the X2 direction, used
        only if geometry_type = 3
    :ivar outline: Irregular outline of the detector/aperture in the
        (X1, X2) coordinate system. Do NOT repeat the first point.
    :ivar surface: Surface of the detector/aperture, derived from the
        above geometric data
    """
    class Meta:
        name = "flat_object_static"

    geometry_type: int = field(
        default=999999999
    )
    centre: Optional[Rzphi0DStatic] = field(
        default=None
    )
    radius: float = field(
        default=9e+40
    )
    x1_width: float = field(
        default=9e+40
    )
    x2_width: float = field(
        default=9e+40
    )
    outline: Optional[X1X21DStatic] = field(
        default=None
    )
    surface: float = field(
        default=9e+40
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
class ReflectometerFluctuationDoppler(IdsBaseClass):
    """
    Reconstruction of the amplitude of the fluctuations.

    :ivar wavenumber: Wavenumber probed by the diagnostic
    :ivar shift: Doppler frequency shift (for the main peak of the power
        spectrum)
    :ivar velocity_pol: Poloidal velocity
    :ivar e_field_radial: Radial electric field
    :ivar position: Measurement position
    :ivar time_width: Width of the time interval over which fluctuating
        profiles are processed. By convention, the time interval starts
        at time-time_width and ends at time.
    :ivar radial_width: Width in the radial direction over which
        fluctuating profiles are processed
    :ivar time: Time
    """
    class Meta:
        name = "reflectometer_fluctuation_doppler"

    wavenumber: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    shift: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    velocity_pol: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    e_field_radial: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    position: Optional[ReflectometerDopplerPosition1D] = field(
        default=None
    )
    time_width: float = field(
        default=9e+40
    )
    radial_width: float = field(
        default=9e+40
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class ReflectometerFluctuationLevel(IdsBaseClass):
    """
    Reconstruction of the amplitude of the fluctuations.

    :ivar dn_e_over_n_e: Relative amplitude of the density fluctuations
        post-processed for swept and fixed frequency (profile/one point)
    :ivar position: Array of positions at which the fluctuation level is
        computed
    :ivar time_width: Width of the time interval over which fluctuating
        profiles are processed. By convention, the time interval starts
        at time-time_width and ends at time.
    :ivar radial_width: Width in the radial direction over which
        fluctuating profiles are processed
    :ivar time: Time
    """
    class Meta:
        name = "reflectometer_fluctuation_level"

    dn_e_over_n_e: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    position: Optional[ReflectometerFluctuationLevelPosition2D] = field(
        default=None
    )
    time_width: float = field(
        default=9e+40
    )
    radial_width: float = field(
        default=9e+40
    )
    time: ndarray[(int,), float] = field(
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
class ReflectometerAntennas(IdsBaseClass):
    """
    Moving reflectometer antennas.

    :ivar line_of_sight_emission: Description of the line of sight of
        the emission antenna. The first point corresponds to the centre
        of the antenna mouth. The second point correspond to the
        interception of the line of sight with the reflection surface on
        the inner wall.
    :ivar line_of_sight_detection: Description of the line of sight of
        the detection antenna, to be filled only if its position is
        distinct from the emission antenna. The first point corresponds
        to the centre of the antenna mouth. The second point correspond
        to the interception of the line of sight with the reflection
        surface on the inner wall.
    :ivar antenna_emission: Dynamic emission antenna orientation
    :ivar antenna_detection: Dynamic detection antenna orientation, to
        be filled only if it is distinct from the emission antenna.
    :ivar time: Time
    """
    class Meta:
        name = "reflectometer_antennas"

    line_of_sight_emission: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None
    )
    line_of_sight_detection: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None
    )
    antenna_emission: Optional[FlatObjectOrientationAos3] = field(
        default=None
    )
    antenna_detection: Optional[FlatObjectOrientationAos3] = field(
        default=None
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class ReflectometerFluctuationChannel(IdsBaseClass):
    """
    Reflectometer channel.

    :ivar name: Name of the channel
    :ivar identifier: ID of the channel
    :ivar mode: Detection mode "X" or "O"
    :ivar antennas_orientation: Description of lines of sight and
        antenna orientation as a function of time
    :ivar antenna_emission_static: Static part of the geometry of the
        emission antenna
    :ivar antenna_detection_static: Static part of the geometry of the
        detection antenna, to be filled only if it is distinct from the
        emission antenna.
    :ivar sweep_time: Duration of a sweep
    :ivar frequencies: Array of frequencies scanned during a sweep
    :ivar raw_signal: Raw data from IQ detector
    :ivar phase: Measured phase of the probing wave for each frequency
        and time slice (corresponding to the begin time of a sweep),
        relative to the phase at launch
    :ivar amplitude: Measured amplitude of the detected probing wave for
        each frequency and time slice (corresponding to the begin time
        of a sweep)
    :ivar fluctuations_level: Reconstruction of the amplitude of the
        fluctuations
    :ivar fluctuations_spectrum: Spectrum of the fluctuations, obtained
        by Fourier transform
    :ivar doppler: Processed data for Doppler reflectometers
    """
    class Meta:
        name = "reflectometer_fluctuation_channel"

    name: str = field(
        default=""
    )
    identifier: str = field(
        default=""
    )
    mode: str = field(
        default=""
    )
    antennas_orientation: list[ReflectometerAntennas] = field(
        default_factory=list
    )
    antenna_emission_static: Optional[FlatObjectStatic] = field(
        default=None
    )
    antenna_detection_static: Optional[FlatObjectStatic] = field(
        default=None
    )
    sweep_time: float = field(
        default=9e+40
    )
    frequencies: Optional[SignalFlt2D] = field(
        default=None
    )
    raw_signal: Optional[ReflectometerFluctuationRaw] = field(
        default=None
    )
    phase: Optional[SignalFlt2D] = field(
        default=None
    )
    amplitude: Optional[SignalFlt2D] = field(
        default=None
    )
    fluctuations_level: Optional[ReflectometerFluctuationLevel] = field(
        default=None
    )
    fluctuations_spectrum: Optional[ReflectometerFluctuationSpectrum] = field(
        default=None
    )
    doppler: Optional[ReflectometerFluctuationDoppler] = field(
        default=None
    )


@dataclass(slots=True)
class ReflectometerFluctuation(IdsBaseClass):
    """Fluctuation reflectometer diagnostic.

    Multiple reflectometers are considered as independent diagnostics to
    be handled with different occurrence numbers

    :ivar ids_properties:
    :ivar type_value: Type of reflectometer (frequency_swept, radar,
        ...)
    :ivar channel: Set of channels, e.g. different reception antennas or
        frequency bandwidths of the reflectometer
    :ivar psi_normalization: Quantities to use to normalize psi, as a
        function of time
    :ivar latency: Upper bound of the delay between physical information
        received by the detector and data available on the real-time
        (RT) network.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "reflectometer_fluctuation"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    type_value: str = field(
        default=""
    )
    channel: list[ReflectometerFluctuationChannel] = field(
        default_factory=list,
        metadata={
            "max_occurs": 5,
        }
    )
    psi_normalization: Optional[PsiNormalization] = field(
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
