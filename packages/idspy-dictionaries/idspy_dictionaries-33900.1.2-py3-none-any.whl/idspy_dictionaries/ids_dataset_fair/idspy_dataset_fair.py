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
class DatasetFair(IdsBaseClass):
    """FAIR metadata related to the dataset, providing inforrmation on licensing,
    annotations, references using this dataset, versioning and validity,
    provenance.

    This IDS is using Dublin Core metadata standard whenever possible

    :ivar ids_properties:
    :ivar identifier: Persistent identifier allowing to cite this data
        in a public and persistent way, should be provided as HTTP URIs
    :ivar replaces: Persistent identifier referencing the previous
        version of this data
    :ivar is_replaced_by: Persistent identifier referencing the new
        version of this data (replacing the present version)
    :ivar valid: Date range during which the data is or was valid.
        Expressed as YYYY-MM-DD/YYYY-MM-DD, where the former (resp.
        latter) date is the data at which the data started (resp.
        ceased) to be valid. If the data is still valid, the slash
        should still be present, i.e. indicate the validity start date
        with YYYY-MM-DD/. If the data ceased being valid but there is no
        information on the validity start date, indicate /YYYY-MM-DD.
    :ivar rights_holder: The organisation owning or managing rights over
        this data
    :ivar license: License(s) under which the data is made available
        (license description or, more convenient, publicly accessible
        URL pointing to the full license text)
    :ivar is_referenced_by: List of documents (e.g. publications) or
        datasets making use of this data entry (e.g. PIDs of other
        datasets using this data entry as input)
    :ivar time:
    """
    class Meta:
        name = "dataset_fair"

    ids_properties: Optional[IdsProperties] = field(
        default=None
    )
    identifier: str = field(
        default=""
    )
    replaces: str = field(
        default=""
    )
    is_replaced_by: str = field(
        default=""
    )
    valid: str = field(
        default=""
    )
    rights_holder: str = field(
        default=""
    )
    license: str = field(
        default=""
    )
    is_referenced_by: Optional[list[str]] = field(
        default=None
    )
    time: ndarray[(int,), float] = field(
        default_factory=list,
        metadata={
            "max_occurs": 999,
        }
    )
