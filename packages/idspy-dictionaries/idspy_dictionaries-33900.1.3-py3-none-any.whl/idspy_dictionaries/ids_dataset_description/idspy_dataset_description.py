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
class DatasetDescriptionEpochTime(IdsBaseClass):
    """
    Epoch time represented as two integers, since for the moment IMAS is missing
    64bits long integers to represent epoch time with nanoseconds resolution.

    :ivar seconds: Elapsed seconds since the Unix Epoch time (01/01/1970
        00:00:00 UTC)
    :ivar nanoseconds: Elapsed nanoseconds since the time in seconds
        indicated above
    """
    class Meta:
        name = "dataset_description_epoch_time"

    seconds: int = field(
        default=999999999
    )
    nanoseconds: int = field(
        default=999999999
    )


@dataclass(slots=True)
class DatasetDescriptionSimulation(IdsBaseClass):
    """Description of the general simulation characteristics, if this data entry
    has been produced by a simulation.

    Several nodes describe typical time-dependent simulation with a time
    evolution as the main loop

    :ivar comment_before: Comment made when launching a simulation
    :ivar comment_after: Comment made at the end of a simulation
    :ivar time_begin: Start time
    :ivar time_step: Time interval between main steps, e.g. storage step
        (if relevant and constant)
    :ivar time_end: Stop time
    :ivar time_restart: Time of the last restart done during the
        simulation
    :ivar time_current: Current time of the simulation
    :ivar time_begun: Actual wall-clock time simulation started
    :ivar time_ended: Actual wall-clock time simulation finished
    :ivar workflow: Description of the workflow which has been used to
        produce this data entry (e.g. copy of the Kepler MOML if using
        Kepler)
    """
    class Meta:
        name = "dataset_description_simulation"

    comment_before: str = field(
        default=""
    )
    comment_after: str = field(
        default=""
    )
    time_begin: float = field(
        default=9e+40
    )
    time_step: float = field(
        default=9e+40
    )
    time_end: float = field(
        default=9e+40
    )
    time_restart: float = field(
        default=9e+40
    )
    time_current: float = field(
        default=9e+40
    )
    time_begun: str = field(
        default=""
    )
    time_ended: str = field(
        default=""
    )
    workflow: str = field(
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
class DatasetDescription(IdsBaseClass):
    """General description of the dataset (collection of all IDSs within the given
    database entry).

    Main description text to be put in ids_properties/comment

    :ivar ids_properties:
    :ivar data_entry: Definition of this data entry
    :ivar parent_entry: Definition of the parent data entry, if the
        present data entry has been generated by applying a given
        workflow to a unique parent entry
    :ivar pulse_time_begin: Date and time (UTC) at which the pulse
        started on the experiment, expressed in a human readable form
        (ISO 8601) : the format of the string shall be : YYYY-MM-
        DDTHH:MM:SSZ. Example : 2020-07-24T14:19:00Z
    :ivar pulse_time_begin_epoch: Time at which the pulse started on the
        experiment, expressed in Unix Epoch time. Temporarily
        represented as two integers, since for the moment IMAS is
        missing 64bits long integers to represent epoch time with
        nanoseconds resolution
    :ivar pulse_time_end_epoch: Time at which the pulse ended on the
        experiment, expressed in Unix Epoch time. Temporarily
        represented as two integers, since for the moment IMAS is
        missing 64bits long integers to represent epoch time with
        nanoseconds resolution
    :ivar imas_version: Version of the IMAS infrastructure used to
        produce this data entry. Refers to the global IMAS repository
        which links to versions of every infrastructure tools
    :ivar dd_version: Version of the physics data dictionary of this
        dataset
    :ivar simulation: Description of the general simulation
        characteristics, if this data entry has been produced by a
        simulation. Several nodes describe typical time-dependent
        simulation with a time evolution as the main loop
    :ivar time:
    """
    class Meta:
        name = "dataset_description"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    data_entry: Optional[DataEntry] = field(
        default=None
    )
    parent_entry: Optional[DataEntry] = field(
        default=None
    )
    pulse_time_begin: str = field(
        default=""
    )
    pulse_time_begin_epoch: Optional[DatasetDescriptionEpochTime] = field(
        default=None
    )
    pulse_time_end_epoch: Optional[DatasetDescriptionEpochTime] = field(
        default=None
    )
    imas_version: str = field(
        default=""
    )
    dd_version: str = field(
        default=""
    )
    simulation: Optional[DatasetDescriptionSimulation] = field(
        default=None
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
