# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class CameraVisibleFrame(IdsBaseClass):
    """
    Frame of a camera.

    :ivar image_raw: Raw image (unprocessed) (digital levels). First
        dimension : line index (horizontal axis). Second dimension:
        column index (vertical axis).
    :ivar radiance: Radiance image. First dimension : line index
        (horizontal axis). Second dimension: column index (vertical
        axis).
    :ivar time: Time
    """
    class Meta:
        name = "camera_visible_frame"

    image_raw: ndarray[(int, int), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    radiance: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    time: Optional[float] = field(
        default=None
    )


@dataclass(slots=True)
class CameraVisibleGeometryMatrixInterpolated(IdsBaseClass):
    """
    Interpolated geometry matrix.

    :ivar r: Major radius of interpolation knots
    :ivar z: Height of interpolation knots
    :ivar phi: Toroidal angle (oriented counter-clockwise when viewing
        from above) of interpolation knots
    """
    class Meta:
        name = "camera_visible_geometry_matrix_interpolated"

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
    class Data(IdsBaseClass):
        """
        :ivar class_of: Class of Data Item
        """
        class_of: str = field(
            init=False,
            default="FLT_3D"
        )


@dataclass(slots=True)
class CameraVisibleGeometryMatrixStep2(IdsBaseClass):
    """
    Geometry matrix of the detector.

    :ivar voxel_indices: List of voxel indices (defined in the voxel
        map) used in the sparse data array
    :ivar pixel_indices: List of pixel indices used in the sparse data
        array. The first dimension refers to the data array index. The
        second dimension lists the line index (horizontal axis) in first
        position, then the column index (vertical axis).
    """
    class Meta:
        name = "camera_visible_geometry_matrix_step2"

    voxel_indices: ndarray[(int,), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pixel_indices: ndarray[(int, int), int] = field(
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
class Xyz0DStatic(IdsBaseClass):
    """
    Structure for list of X, Y, Z components (0D, static)

    :ivar x: Component along X axis
    :ivar y: Component along Y axis
    :ivar z: Component along Z axis
    """
    class Meta:
        name = "xyz0d_static"

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
class CurvedSurface(IdsBaseClass):
    """
    Curvature of a surface.

    :ivar curvature_type: Curvature of the surface
    :ivar x1_curvature: Radius of curvature in the X1 direction, to be
        filled only for curvature_type/index = 2, 4 or 5
    :ivar x2_curvature: Radius of curvature in the X2 direction, to be
        filled only for curvature_type/index = 3 or 5
    """
    class Meta:
        name = "curved_surface"

    curvature_type: Optional[IdentifierStatic] = field(
        default=None
    )
    x1_curvature: float = field(
        default=9e+40
    )
    x2_curvature: float = field(
        default=9e+40
    )


@dataclass(slots=True)
class DetectorAperture(IdsBaseClass):
    """
    Generic description of a plane detector or collimating aperture.

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
        name = "detector_aperture"

    geometry_type: int = field(
        default=999999999
    )
    centre: Optional[Rzphi0DStatic] = field(
        default=None
    )
    radius: float = field(
        default=9e+40
    )
    x1_unit_vector: Optional[Xyz0DStatic] = field(
        default=None
    )
    x2_unit_vector: Optional[Xyz0DStatic] = field(
        default=None
    )
    x3_unit_vector: Optional[Xyz0DStatic] = field(
        default=None
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
class GeometryMatrixEmission(IdsBaseClass):
    """
    Emission grid for the geometry matrix of a detector.

    :ivar grid_type: Grid type
    :ivar dim1: First dimension values
    :ivar dim2: Second dimension values
    :ivar dim3: Third dimension values
    """
    class Meta:
        name = "geometry_matrix_emission"

    grid_type: Optional[IdentifierStatic] = field(
        default=None
    )
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
    dim3: ndarray[(int,), float] = field(
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
class OpticalElementMaterial(IdsBaseClass):
    """
    Material of an optical element of a camera.

    :ivar type_value: Type of optical element material. In case of
        'metal' refractive_index and extinction_coefficient are used. In
        case of 'dielectric' refractive_index and
        transmission_coefficient are used.
    :ivar wavelengths: Wavelengths array for refractive_index,
        extinction_coefficient and transmission_coefficient
    :ivar refractive_index: Refractive index (for metal and dielectric)
    :ivar extinction_coefficient: Extinction coefficient (for metal)
    :ivar transmission_coefficient: Transmission coefficient (for
        dielectric)
    :ivar roughness: Roughness parameter of the material. Varies in
        range [0, 1]. 0 is perfectly specular, 1 is perfectly rough
    """
    class Meta:
        name = "optical_element_material"

    type_value: Optional[IdentifierStatic] = field(
        default=None
    )
    wavelengths: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    refractive_index: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    extinction_coefficient: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    transmission_coefficient: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    roughness: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )


@dataclass(slots=True)
class CameraVisibleGeometryMatrix(IdsBaseClass):
    """
    Geometry matrix of the camera.

    :ivar with_reflections: Geometry matrix with reflections
    :ivar without_reflections: Geometry matrix without reflections
    :ivar interpolated: Interpolated geometry matrix for reflected light
    :ivar voxel_map: Voxel map for geometry matrix. The cells with same
        number are merged in the computation into a single emission
        source meta-cell (the voxel). Cells with number -1 are excluded.
        Voxel count starts from 0.
    :ivar voxels_n: Number of voxels defined in the voxel_map.
    :ivar emission_grid: Grid defining the light emission cells
    """
    class Meta:
        name = "camera_visible_geometry_matrix"

    with_reflections: Optional[CameraVisibleGeometryMatrixStep2] = field(
        default=None
    )
    without_reflections: Optional[CameraVisibleGeometryMatrixStep2] = field(
        default=None
    )
    interpolated: Optional[CameraVisibleGeometryMatrixInterpolated] = field(
        default=None
    )
    voxel_map: ndarray[(int, int, int), int] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    voxels_n: int = field(
        default=999999999
    )
    emission_grid: Optional[GeometryMatrixEmission] = field(
        default=None
    )


@dataclass(slots=True)
class FibreBundle(IdsBaseClass):
    """
    Fibre bundle.

    :ivar geometry: Geometry of the fibre bundle entrance
    :ivar fibre_radius: Radius of a single fibre
    :ivar fibre_positions: Individual fibres centres positions in the
        (X1, X2) coordinate system
    """
    class Meta:
        name = "fibre_bundle"

    geometry: Optional[DetectorAperture] = field(
        default=None
    )
    fibre_radius: float = field(
        default=9e+40
    )
    fibre_positions: Optional[X1X21DStatic] = field(
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
class OpticalElement(IdsBaseClass):
    """
    Optical element of a camera.

    :ivar type_value: Type of optical element. In case of 'mirror' and
        'diaphragm', the element is described by one 'front_surface'. In
        case of 'lens', the element is described by 'front_surface' and
        'back_surface'.
    :ivar front_surface: Curvature of the front surface
    :ivar back_surface: Curvature of the front surface
    :ivar thickness: Distance between front_surface and back_surface
        along the X3 vector
    :ivar material_properties: Material properties of the optical
        element
    :ivar geometry: Further geometrical description of the element
    """
    class Meta:
        name = "optical_element"

    type_value: Optional[IdentifierStatic] = field(
        default=None
    )
    front_surface: Optional[CurvedSurface] = field(
        default=None
    )
    back_surface: Optional[CurvedSurface] = field(
        default=None
    )
    thickness: float = field(
        default=9e+40
    )
    material_properties: Optional[OpticalElementMaterial] = field(
        default=None
    )
    geometry: Optional[DetectorAperture] = field(
        default=None
    )


@dataclass(slots=True)
class CameraVisibleDetector(IdsBaseClass):
    """
    Detector for a visible camera.

    :ivar pixel_to_alpha: Alpha angle of each pixel in the horizontal
        axis
    :ivar pixel_to_beta: Beta angle of each pixel in the vertical axis
    :ivar wavelength_lower: Lower bound of the detector wavelength range
    :ivar wavelength_upper: Upper bound of the detector wavelength range
    :ivar counts_to_radiance: Counts to radiance factor, for each pixel
        of the detector. Includes both the transmission losses in the
        relay optics and the quantum efficiency of the camera itself,
        integrated over the wavelength range
    :ivar exposure_time: Exposure time
    :ivar noise: Detector noise (e.g. read-out noise) (rms counts per
        second exposure time)
    :ivar columns_n: Number of pixel columns in the horizontal direction
    :ivar lines_n: Number of pixel lines in the vertical direction
    :ivar frame: Set of frames
    :ivar geometry_matrix: Description of geometry matrix (ray transfer
        matrix)
    """
    class Meta:
        name = "camera_visible_detector"

    pixel_to_alpha: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    pixel_to_beta: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    wavelength_lower: float = field(
        default=9e+40
    )
    wavelength_upper: float = field(
        default=9e+40
    )
    counts_to_radiance: ndarray[(int,int), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    exposure_time: float = field(
        default=9e+40
    )
    noise: float = field(
        default=9e+40
    )
    columns_n: int = field(
        default=999999999
    )
    lines_n: int = field(
        default=999999999
    )
    frame: list[CameraVisibleFrame] = field(
        default_factory=list
    )
    geometry_matrix: Optional[CameraVisibleGeometryMatrix] = field(
        default=None
    )


@dataclass(slots=True)
class CameraVisibleChannel(IdsBaseClass):
    """
    Channel of a camera.

    :ivar name: Name of the channel
    :ivar aperture: Description of apertures between plasma and the
        detectors (position, outline shape and orientation)
    :ivar viewing_angle_alpha_bounds: Minimum and maximum values of
        alpha angle of the field of view, where alpha is the agle
        between the axis X3 and projection of the chord of view  on the
        plane X1X3 counted clockwise from the top view of X2 axis. X1,
        X2, X3 are the ones of the first aperture (i.e. the closest to
        the plasma).
    :ivar viewing_angle_beta_bounds: Minimum and maximum values of beta
        angle of the field of view, where beta is the angle between the
        axis X3 and projection of the chord of view on the plane X2X3
        counted clockwise from the top view of X1 axis. X1, X2, X3 are
        the ones of the first aperture (i.e. the closest to the plasma).
    :ivar detector: Set of detectors
    :ivar optical_element: Set of optical elements
    :ivar fibre_bundle: Description of the fibre bundle
    """
    class Meta:
        name = "camera_visible_channel"

    name: str = field(
        default=""
    )
    aperture: list[DetectorAperture] = field(
        default_factory=list,
        metadata={
            "max_occurs": 3,
        }
    )
    viewing_angle_alpha_bounds: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    viewing_angle_beta_bounds: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    detector: list[CameraVisibleDetector] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    optical_element: list[OpticalElement] = field(
        default_factory=list,
        metadata={
            "max_occurs": 10,
        }
    )
    fibre_bundle: Optional[FibreBundle] = field(
        default=None
    )


@dataclass(slots=True)
class CameraVisible(IdsBaseClass):
    """
    Camera in the visible light range.

    :ivar ids_properties:
    :ivar name: Name of the camera
    :ivar channel: Set of channels (a front aperture, possibly followed
        by others, viewing the plasma recorded by one or more detectors
        e.g. for different wavelength ranges)
    :ivar latency: Upper bound of the delay between physical information
        received by the detector and data available on the real-time
        (RT) network.
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "camera_visible"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    name: str = field(
        default=""
    )
    channel: list[CameraVisibleChannel] = field(
        default_factory=list,
        metadata={
            "max_occurs": 20,
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
