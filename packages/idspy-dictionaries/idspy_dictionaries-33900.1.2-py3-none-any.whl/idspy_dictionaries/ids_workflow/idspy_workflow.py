# __version__= "033900.1.2"
# __version_data_dictionary__= "3.39.0"
# __git_version_hash__= "f981ec5408e8702b7bdc5f2f37a0c2ac56df9d9a"
# 
from ..dataclasses_idsschema import _IDSPYDD_USE_SLOTS,IdsBaseClass
from dataclasses import dataclass, field
from numpy import ndarray
from typing import Optional


@dataclass(slots=True)
class CodeConstant(IdsBaseClass):
    """
    Description of code-specific parameters without dynamic output_flag parameter.

    :ivar name: Name of software used
    :ivar description: Short description of the software (type, purpose)
    :ivar commit: Unique commit reference of software
    :ivar version: Unique version (tag) of software
    :ivar repository: URL of software repository
    :ivar parameters: List of the code specific parameters in XML format
    """
    class Meta:
        name = "code_constant"

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
class WorkflowComponent(IdsBaseClass):
    """
    Control parameters for the set of participting components defined in
    ../../component_list.

    :ivar index: Index of the component in the ../../../component array
    :ivar execution_mode: Component execution mode for current workflow
        cycle. 0 means the component is not executed and the workflow
        uses results from previous workflow cycle. 1 means the component
        is executed for this workflow cycle.
    :ivar time_interval: Simulation time interval during which this
        component has to compute its results.
    :ivar control_float: Array of real workflow control parameters used
        by this component (component specific)
    :ivar control_integer: Array of integer workflow control parameters
        used by this component (component specific)
    """
    class Meta:
        name = "workflow_component"

    index: int = field(
        default=999999999
    )
    execution_mode: int = field(
        default=999999999
    )
    time_interval: float = field(
        default=9e+40
    )
    control_float: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
    control_integer: ndarray[(int,), int] = field(
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
class WorkflowCycle(IdsBaseClass):
    """
    Control structure for the time associated with the workflow cycle.

    :ivar component: Control parameters for the set of participting
        components defined in ../../component
    :ivar time: Time
    """
    class Meta:
        name = "workflow_cycle"

    component: list[WorkflowComponent] = field(
        default_factory=list,
        metadata={
            "max_occurs": 20,
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
class WorkflowTimeLoop(IdsBaseClass):
    """
    Description of a workflow with a main time loop.

    :ivar component: List of components partcipating in the workflow
    :ivar time_end: Termination time for the workflow main time loop
    :ivar workflow_cycle: Set of time slices corresponding to the
        beginning of workflow cycles (main time loop of the workflow).
        During each workflow cycle, active components compute their
        result during their given time_interval. Components having
        completed their computation are frozen until the end of the
        workflow cycle. The next workflow cycle begins when the maximum
        time_interval (over the components) has been reached.
    """
    class Meta:
        name = "workflow_time_loop"

    component: list[CodeConstant] = field(
        default_factory=list,
        metadata={
            "max_occurs": 20,
        }
    )
    time_end: float = field(
        default=9e+40
    )
    workflow_cycle: list[WorkflowCycle] = field(
        default_factory=list
    )


@dataclass(slots=True)
class Workflow(IdsBaseClass):
    """Description of the workflow that has produced this data entry.

    The workflow IDS can also be used to communicate information about
    workflow state between workflow components.

    :ivar ids_properties:
    :ivar time_loop: Description of a workflow based on a time loop
        which calls components defined in component_list sequentially
        during each cycle of the loop (workflow_cycle).
    :ivar code:
    :ivar time:
    """
    class Meta:
        name = "workflow"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    time_loop: Optional[WorkflowTimeLoop] = field(
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
