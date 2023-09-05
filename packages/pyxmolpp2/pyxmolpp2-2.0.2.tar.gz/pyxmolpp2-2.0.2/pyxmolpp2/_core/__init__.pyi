"""
pyxmolpp2 implementation
"""
from __future__ import annotations

import typing

import numpy
import pybind11_stubgen.typing_ext

from . import _pipe

__all__ = ['AmberNetCDF', 'AngleValue', 'Atom', 'AtomIdPredicateGenerator', 'AtomNamePredicateGenerator', 'AtomPredicate', 'AtomSelection', 'AtomSpan', 'CoordSelection', 'CoordSelectionSizeMismatchError', 'CoordSpan', 'DeadFrameAccessError', 'DeadObserverAccessError', 'Degrees', 'Frame', 'GeomError', 'GromacsXtcFile', 'Molecule', 'MoleculeNamePredicateGenerator', 'MoleculePredicate', 'MoleculeSelection', 'MoleculeSpan', 'MultipleFramesSelectionError', 'PdbFile', 'Radians', 'Residue', 'ResidueId', 'ResidueIdPredicateGenerator', 'ResidueNamePredicateGenerator', 'ResiduePredicate', 'ResidueSelection', 'ResidueSpan', 'Rotation', 'SpanSplitError', 'TorsionAngle', 'TorsionAngleFactory', 'Trajectory', 'TrajectoryDoubleTraverseError', 'TrajectoryInputFile', 'Transformation', 'Translation', 'TrjtoolDatFile', 'UniformScale', 'UnitCell', 'XYZ', 'XtcReadError', 'XtcWriteError', 'XtcWriter', 'aId', 'aName', 'calc_alignment', 'calc_autocorr_order_2', 'calc_autocorr_order_2_PRE', 'calc_inertia_tensor', 'calc_rmsd', 'calc_sasa', 'degrees_to_radians', 'mName', 'rId', 'rName', 'radians_to_degrees']
class AmberNetCDF(TrajectoryInputFile):
    """
    Amber trajectory file
    """
    def __init__(self, filename: str) -> None:
        """
        Amber binary trajectory ``.nc`` file
        """
    def advance(self, shift: int) -> None:
        """
        Shift internal pointer by `shift`
        """
    def n_atoms(self) -> int:
        """
        Number of atoms per frame
        """
    def n_frames(self) -> int:
        """
        Number of frames
        """
    def read_frame(self, index: int, frame: Frame) -> None:
        """
        Assign `index` frame coordinates, cell, etc
        """
class AngleValue:
    """
    Angular value
    """
    def __add__(self, arg0: AngleValue) -> AngleValue:
        ...
    def __ge__(self, arg0: AngleValue) -> bool:
        ...
    def __gt__(self, arg0: AngleValue) -> bool:
        ...
    def __le__(self, arg0: AngleValue) -> bool:
        ...
    def __lt__(self, arg0: AngleValue) -> bool:
        ...
    def __mul__(self, arg0: float) -> AngleValue:
        ...
    def __neg__(self) -> AngleValue:
        ...
    def __rmul__(self, arg0: float) -> AngleValue:
        ...
    def __sub__(self, arg0: AngleValue) -> AngleValue:
        ...
    def __truediv__(self, arg0: float) -> AngleValue:
        ...
    def abs(self) -> AngleValue:
        ...
    def cos(self) -> float:
        ...
    def sin(self) -> float:
        ...
    def tan(self) -> float:
        ...
    def to_standard_range(self) -> AngleValue:
        """
        Wraps value to :math:`[-\pi..\pi)` range
        """
    @property
    def degrees(self) -> float:
        """
        Angle value in degrees
        """
    @property
    def radians(self) -> float:
        """
        Angle value in radians
        """
class Atom:
    """
    Atom reference
    """
    id: int
    mass: float
    name: str
    r: XYZ
    vdw_radius: float
    def __eq__(self, arg0: Atom) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, arg0: Atom) -> None:
        ...
    def __ne__(self, arg0: Atom) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def frame(self) -> Frame:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def molecule(self) -> Molecule:
        ...
    @property
    def residue(self) -> Residue:
        ...
class AtomIdPredicateGenerator:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: int) -> AtomPredicate:
        ...
    def __ge__(self, arg0: int) -> AtomPredicate:
        ...
    def __gt__(self, arg0: int) -> AtomPredicate:
        ...
    def __le__(self, arg0: int) -> AtomPredicate:
        ...
    def __lt__(self, arg0: int) -> AtomPredicate:
        ...
    def __ne__(self, arg0: int) -> AtomPredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[int]) -> AtomPredicate:
        ...
    @typing.overload
    def is_in(self, *args) -> AtomPredicate:
        ...
class AtomNamePredicateGenerator:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: str) -> AtomPredicate:
        ...
    def __ne__(self, arg0: str) -> AtomPredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[str]) -> AtomPredicate:
        ...
    @typing.overload
    def is_in(self, *args) -> AtomPredicate:
        ...
class AtomPredicate:
    """
    Atom Preidcate
    """
    @typing.overload
    def __and__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __and__(self, arg0: ResiduePredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __and__(self, arg0: MoleculePredicate) -> AtomPredicate:
        ...
    def __call__(self, arg0: Atom) -> bool:
        ...
    def __init__(self, arg0: typing.Callable[[pyxmolpp2._core.Atom], bool]) -> None:
        ...
    def __invert__(self) -> AtomPredicate:
        ...
    @typing.overload
    def __or__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __or__(self, arg0: ResiduePredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __or__(self, arg0: MoleculePredicate) -> AtomPredicate:
        ...
    def __ror__(self, arg0: MoleculePredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: ResiduePredicate) -> AtomPredicate:
        ...
class AtomSelection:
    """
    Ordered set of atom references
    """
    def __and__(self, arg0: AtomSelection) -> AtomSelection:
        ...
    def __contains__(self, arg0: Atom) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Atom:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> AtomSelection:
        ...
    @typing.overload
    def __init__(self, arg0: AtomSelection) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Atom]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: AtomSelection) -> AtomSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: AtomSelection) -> AtomSelection:
        ...
    @typing.overload
    def align_to(self, other: AtomSelection, *, weighted: bool = ...) -> None:
        ...
    @typing.overload
    def align_to(self, other: AtomSpan, *, weighted: bool = ...) -> None:
        ...
    @typing.overload
    def alignment_to(self, other: AtomSelection, *, weighted: bool = ...) -> Transformation:
        ...
    @typing.overload
    def alignment_to(self, other: AtomSpan, *, weighted: bool = ...) -> Transformation:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Atom], bool]) -> AtomSelection:
        ...
    def guess_mass(self) -> None:
        ...
    def inertia_tensor(self) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]:
        ...
    def mean(self, weighted: bool = ...) -> XYZ:
        """
        Mean coordinates
        """
    @typing.overload
    def rmsd(self, other: AtomSelection, *, weighted: bool = ...) -> float:
        ...
    @typing.overload
    def rmsd(self, other: AtomSpan, *, weighted: bool = ...) -> float:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def coords(self) -> CoordSelection:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def molecules(self) -> MoleculeSelection:
        ...
    @property
    def residues(self) -> ResidueSelection:
        ...
    @property
    def size(self) -> int:
        ...
class AtomSpan:
    """
    Continuous span of atom references
    """
    def __and__(self, arg0: AtomSpan) -> AtomSpan:
        ...
    def __contains__(self, arg0: Atom) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Atom:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> AtomSpan | AtomSelection:
        ...
    def __init__(self, arg0: AtomSpan) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Atom]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: AtomSpan) -> AtomSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: AtomSpan) -> AtomSelection:
        ...
    @typing.overload
    def align_to(self, other: AtomSelection, *, weighted: bool = ...) -> None:
        ...
    @typing.overload
    def align_to(self, other: AtomSpan, *, weighted: bool = ...) -> None:
        ...
    @typing.overload
    def alignment_to(self, other: AtomSelection, *, weighted: bool = ...) -> Transformation:
        ...
    @typing.overload
    def alignment_to(self, other: AtomSpan, *, weighted: bool = ...) -> Transformation:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Atom], bool]) -> AtomSelection:
        ...
    def guess_mass(self) -> None:
        ...
    def inertia_tensor(self) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]:
        """
        Inertia tensor
        """
    def mean(self, weighted: bool = ...) -> XYZ:
        """
        Mean coordinates
        """
    @typing.overload
    def rmsd(self, other: AtomSelection, *, weighted: bool = ...) -> float:
        ...
    @typing.overload
    def rmsd(self, other: AtomSpan, *, weighted: bool = ...) -> float:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        """
        Write atoms as `.pdb` file
        """
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        """
        Write atoms in PDB format
        """
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def molecules(self) -> MoleculeSpan:
        ...
    @property
    def residues(self) -> ResidueSpan:
        ...
    @property
    def size(self) -> int:
        ...
class CoordSelection:
    """
    Ordered set of atomic coordinate references
    """
    values: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)]
    @typing.overload
    def __getitem__(self, arg0: int) -> XYZ:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> CoordSelection:
        ...
    def __init__(self, arg0: CoordSelection) -> None:
        ...
    def __iter__(self) -> typing.Iterator[XYZ]:
        ...
    def __len__(self) -> int:
        ...
    def __str__(self) -> str:
        ...
    @typing.overload
    def align_to(self, arg0: CoordSpan) -> None:
        ...
    @typing.overload
    def align_to(self, arg0: CoordSelection) -> None:
        ...
    @typing.overload
    def alignment_to(self, arg0: CoordSelection) -> Transformation:
        ...
    @typing.overload
    def alignment_to(self, arg0: CoordSpan) -> Transformation:
        ...
    @typing.overload
    def apply(self, arg0: Transformation) -> None:
        ...
    @typing.overload
    def apply(self, arg0: UniformScale) -> None:
        ...
    @typing.overload
    def apply(self, arg0: Rotation) -> None:
        ...
    @typing.overload
    def apply(self, arg0: Translation) -> None:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.XYZ], bool]) -> CoordSelection:
        ...
    def inertia_tensor(self) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]:
        ...
    def mean(self) -> XYZ:
        ...
    @typing.overload
    def rmsd(self, arg0: CoordSelection) -> float:
        ...
    @typing.overload
    def rmsd(self, arg0: CoordSpan) -> float:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def size(self) -> int:
        ...
class CoordSelectionSizeMismatchError(Exception):
    pass
class CoordSpan:
    """
    Continuous span of atomic coordinate references
    """
    @typing.overload
    def __getitem__(self, arg0: int) -> XYZ:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> CoordSpan | CoordSelection:
        ...
    def __init__(self, arg0: CoordSpan) -> None:
        ...
    def __iter__(self) -> typing.Iterator[XYZ]:
        ...
    def __len__(self) -> int:
        ...
    def __str__(self) -> str:
        ...
    @typing.overload
    def align_to(self, arg0: CoordSelection) -> None:
        ...
    @typing.overload
    def align_to(self, arg0: CoordSpan) -> None:
        ...
    @typing.overload
    def alignment_to(self, arg0: CoordSelection) -> Transformation:
        ...
    @typing.overload
    def alignment_to(self, arg0: CoordSpan) -> Transformation:
        ...
    @typing.overload
    def apply(self, arg0: Transformation) -> None:
        ...
    @typing.overload
    def apply(self, arg0: UniformScale) -> None:
        ...
    @typing.overload
    def apply(self, arg0: Rotation) -> None:
        ...
    @typing.overload
    def apply(self, arg0: Translation) -> None:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.XYZ], bool]) -> CoordSelection:
        ...
    def inertia_tensor(self) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]:
        ...
    def mean(self) -> XYZ:
        ...
    @typing.overload
    def rmsd(self, arg0: CoordSelection) -> float:
        ...
    @typing.overload
    def rmsd(self, arg0: CoordSpan) -> float:
        ...
    @property
    def __frame(self) -> Frame:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def size(self) -> int:
        ...
    @property
    def values(self) -> numpy.ndarray:
        ...
class DeadFrameAccessError(Exception):
    pass
class DeadObserverAccessError(Exception):
    pass
class Frame:
    """
    Molecular frame
    """
    cell: UnitCell
    def __eq__(self, arg0: Frame) -> bool:
        ...
    def __getitem__(self, arg0: str) -> Molecule:
        ...
    def __hash__(self) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: Frame) -> None:
        ...
    def __ne__(self, arg0: Frame) -> bool:
        ...
    def __str__(self) -> str:
        ...
    def add_molecule(self) -> Molecule:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSpan:
        ...
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def index(self) -> int:
        """
        Zero-based index in trajectory
        """
    @index.setter
    def index(self, arg0: int) -> None:
        ...
    @property
    def molecules(self) -> MoleculeSpan:
        ...
    @property
    def residues(self) -> ResidueSpan:
        ...
    @property
    def time(self) -> float:
        """
        Time point in trajectory, a.u.
        """
    @time.setter
    def time(self, arg0: float) -> None:
        ...
class GeomError(Exception):
    pass
class GromacsXtcFile(TrajectoryInputFile):
    """
    Gromacs binary `.xtc` input file
    """
    def __init__(self, filename: str, n_frames: int) -> None:
        ...
    def advance(self, shift: int) -> None:
        """
        Shift internal pointer by `shift`
        """
    def n_atoms(self) -> int:
        """
        Number of atoms per frame
        """
    def n_frames(self) -> int:
        """
        Number of frames
        """
    def read_frame(self, index: int, frame: Frame) -> None:
        """
        Assign `index` frame coordinates, cell, etc
        """
class Molecule:
    """
    Molecule reference
    """
    name: str
    def __eq__(self, arg0: Molecule) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: ResidueId) -> Residue:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Residue:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, arg0: Molecule) -> None:
        ...
    def __ne__(self, arg0: Molecule) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def add_residue(self) -> Residue:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSpan:
        ...
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def empty(self) -> bool:
        ...
    @property
    def frame(self) -> Frame:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def residues(self) -> ResidueSpan:
        ...
    @property
    def size(self) -> int:
        ...
class MoleculeNamePredicateGenerator:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: str) -> MoleculePredicate:
        ...
    def __ne__(self, arg0: str) -> MoleculePredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[str]) -> MoleculePredicate:
        ...
    @typing.overload
    def is_in(self, *args) -> MoleculePredicate:
        ...
class MoleculePredicate:
    """
    Molecule Predicate
    """
    @typing.overload
    def __and__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __and__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __and__(self, arg0: MoleculePredicate) -> MoleculePredicate:
        ...
    @typing.overload
    def __call__(self, arg0: Molecule) -> bool:
        ...
    @typing.overload
    def __call__(self, arg0: Residue) -> bool:
        ...
    @typing.overload
    def __call__(self, arg0: Atom) -> bool:
        ...
    def __init__(self, arg0: typing.Callable[[pyxmolpp2._core.Molecule], bool]) -> None:
        ...
    def __invert__(self) -> MoleculePredicate:
        ...
    @typing.overload
    def __or__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __or__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __or__(self, arg0: MoleculePredicate) -> MoleculePredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: MoleculePredicate) -> MoleculePredicate:
        ...
class MoleculeSelection:
    """
    Ordered set of molecule references
    """
    def __and__(self, arg0: MoleculeSelection) -> MoleculeSelection:
        ...
    def __contains__(self, arg0: Molecule) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Molecule:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> MoleculeSelection:
        ...
    @typing.overload
    def __init__(self, arg0: MoleculeSelection) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Molecule]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: MoleculeSelection) -> MoleculeSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: MoleculeSelection) -> MoleculeSelection:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Molecule], bool]) -> MoleculeSelection:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSelection:
        ...
    @property
    def coords(self) -> CoordSelection:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def residues(self) -> ResidueSelection:
        ...
    @property
    def size(self) -> int:
        ...
class MoleculeSpan:
    """
    Continuous span of molecule references
    """
    def __and__(self, arg0: MoleculeSpan) -> MoleculeSpan:
        ...
    def __contains__(self, arg0: Molecule) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Molecule:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> MoleculeSpan | MoleculeSelection:
        ...
    def __init__(self, arg0: MoleculeSpan) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Molecule]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: MoleculeSpan) -> MoleculeSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: MoleculeSpan) -> MoleculeSelection:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Molecule], bool]) -> MoleculeSelection:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSpan:
        ...
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def residues(self) -> ResidueSpan:
        ...
    @property
    def size(self) -> int:
        ...
class MultipleFramesSelectionError(Exception):
    pass
class PdbFile(TrajectoryInputFile):
    """
    PDB file
    """
    class Dialect:
        """
        PDB file dialect
        
        Members:
        
          STANDARD_V3 : Standard records (https://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html)
        
          AMBER_99 : Amber-MD convention
        """
        AMBER_99: typing.ClassVar[PdbFile.Dialect]  # value = <Dialect.AMBER_99: 1>
        STANDARD_V3: typing.ClassVar[PdbFile.Dialect]  # value = <Dialect.STANDARD_V3: 0>
        __members__: typing.ClassVar[dict[str, PdbFile.Dialect]]  # value = {'STANDARD_V3': <Dialect.STANDARD_V3: 0>, 'AMBER_99': <Dialect.AMBER_99: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    AMBER_99: typing.ClassVar[PdbFile.Dialect]  # value = <Dialect.AMBER_99: 1>
    STANDARD_V3: typing.ClassVar[PdbFile.Dialect]  # value = <Dialect.STANDARD_V3: 0>
    def __init__(self, filename: str, dialect: PdbFile.Dialect = ...) -> None:
        """
        Constructor
        """
    def advance(self, arg0: int) -> None:
        """
        No-op
        """
    def frames(self) -> list[Frame]:
        """
        Get copy of frames
        """
    def n_atoms(self) -> int:
        """
        Number of atoms in first frame
        """
    def n_frames(self) -> int:
        """
        Number of frames
        """
    def read_frame(self, index: int, frame: Frame) -> None:
        """
        Assign `index` frame coordinates, cell, etc
        """
class Residue:
    """
    Residue reference
    """
    id: ResidueId
    name: str
    def __eq__(self, arg0: Residue) -> bool:
        ...
    def __getitem__(self, arg0: str) -> Atom:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, arg0: Residue) -> None:
        ...
    def __ne__(self, arg0: Residue) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def add_atom(self) -> Atom:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSpan:
        ...
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def empty(self) -> bool:
        ...
    @property
    def frame(self) -> Frame:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def molecule(self) -> Molecule:
        ...
    @property
    def next(self) -> Residue | None:
        ...
    @property
    def prev(self) -> Residue | None:
        ...
    @property
    def size(self) -> int:
        ...
class ResidueId:
    """
    Residue id
    """
    @typing.overload
    def __eq__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __eq__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __eq__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __ge__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __ge__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __ge__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __gt__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __gt__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __gt__(self, arg0: int) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor
        """
    @typing.overload
    def __init__(self, serial: int) -> None:
        """
        Construct from serial
        """
    @typing.overload
    def __init__(self, serial: int, icode: str) -> None:
        """
        Construct from serial and insertion code
        """
    @typing.overload
    def __le__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __le__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __le__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __lt__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __lt__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __lt__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __ne__(self, arg0: ResidueId) -> bool:
        ...
    @typing.overload
    def __ne__(self, arg0: int) -> bool:
        ...
    @typing.overload
    def __ne__(self, arg0: int) -> bool:
        ...
    def __str__(self) -> str:
        ...
    @property
    def iCode(self) -> str:
        """
        Insertion code
        """
    @iCode.setter
    def iCode(self, arg1: str) -> None:
        ...
    @property
    def serial(self) -> int:
        """
        Serial number
        """
    @serial.setter
    def serial(self, arg0: int) -> None:
        ...
class ResidueIdPredicateGenerator:
    __hash__: typing.ClassVar[None] = None
    @typing.overload
    def __eq__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __eq__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def __ge__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __ge__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def __gt__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __gt__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def __le__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __le__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def __lt__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __lt__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def __ne__(self, arg0: ResidueId) -> ResiduePredicate:
        ...
    @typing.overload
    def __ne__(self, arg0: int) -> ResiduePredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[int]) -> ResiduePredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[ResidueId]) -> ResiduePredicate:
        ...
    @typing.overload
    def is_in(self, *args) -> ResiduePredicate:
        ...
class ResidueNamePredicateGenerator:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: str) -> ResiduePredicate:
        ...
    def __ne__(self, arg0: str) -> ResiduePredicate:
        ...
    @typing.overload
    def is_in(self, arg0: set[str]) -> ResiduePredicate:
        ...
    @typing.overload
    def is_in(self, *args) -> ResiduePredicate:
        ...
class ResiduePredicate:
    """
    Residue Predicate
    """
    @typing.overload
    def __and__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __and__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __and__(self, arg0: MoleculePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __call__(self, arg0: Residue) -> bool:
        ...
    @typing.overload
    def __call__(self, arg0: Atom) -> bool:
        ...
    def __init__(self, arg0: typing.Callable[[pyxmolpp2._core.Residue], bool]) -> None:
        ...
    def __invert__(self) -> ResiduePredicate:
        ...
    @typing.overload
    def __or__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __or__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __or__(self, arg0: MoleculePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: AtomPredicate) -> AtomPredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: ResiduePredicate) -> ResiduePredicate:
        ...
    @typing.overload
    def __xor__(self, arg0: MoleculePredicate) -> ResiduePredicate:
        ...
class ResidueSelection:
    """
    Ordered set of residue references
    """
    def __and__(self, arg0: ResidueSelection) -> ResidueSelection:
        ...
    def __contains__(self, arg0: Residue) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Residue:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> ResidueSelection:
        ...
    @typing.overload
    def __init__(self, arg0: ResidueSelection) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Residue]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: ResidueSelection) -> ResidueSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: ResidueSelection) -> ResidueSelection:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Residue], bool]) -> ResidueSelection:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSelection:
        ...
    @property
    def coords(self) -> CoordSelection:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def molecules(self) -> MoleculeSelection:
        ...
    @property
    def size(self) -> int:
        ...
class ResidueSpan:
    """
    Continuous span of residue references
    """
    def __and__(self, arg0: ResidueSpan) -> ResidueSpan:
        ...
    def __contains__(self, arg0: Residue) -> bool:
        ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Residue:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> ResidueSpan | ResidueSelection:
        ...
    def __init__(self, arg0: ResidueSpan) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Residue]:
        ...
    def __len__(self) -> int:
        ...
    def __or__(self, arg0: ResidueSpan) -> ResidueSelection:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: ResidueSpan) -> ResidueSelection:
        ...
    def filter(self, arg0: typing.Callable[[pyxmolpp2._core.Residue], bool]) -> ResidueSelection:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: str) -> None:
        ...
    @typing.overload
    def to_pdb(self, path_or_buf: typing.Any) -> None:
        ...
    @property
    def atoms(self) -> AtomSpan:
        ...
    @property
    def coords(self) -> CoordSpan:
        ...
    @property
    def empty(self) -> int:
        ...
    @property
    def index(self) -> list[int]:
        ...
    @property
    def molecules(self) -> MoleculeSpan:
        ...
    @property
    def size(self) -> int:
        ...
class Rotation:
    """
    Rotational transformation
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor
        """
    @typing.overload
    def __init__(self, rotation_axis: XYZ, rotation_angle: AngleValue) -> None:
        """
        Construct from axis and angle
        """
    @typing.overload
    def __init__(self, rotation_matrix: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]) -> None:
        """
        Construct from matrix
        """
    @typing.overload
    def __mul__(self, arg0: Rotation) -> Rotation:
        ...
    @typing.overload
    def __mul__(self, arg0: Translation) -> Transformation:
        ...
    @typing.overload
    def __mul__(self, arg0: UniformScale) -> Transformation:
        ...
    @typing.overload
    def __rmul__(self, arg0: Translation) -> Transformation:
        ...
    @typing.overload
    def __rmul__(self, arg0: UniformScale) -> Transformation:
        ...
    def axis(self) -> XYZ:
        """
        Rotational axis
        """
    def inverted(self) -> Rotation:
        """
        Inverted rotation
        """
    def matrix3d(self) -> typing.Annotated[numpy.ndarray, numpy.float64]:
        """
        Rotational matrix
        """
    def theta(self) -> AngleValue:
        """
        Rotational angle
        """
    def transform(self, r: XYZ) -> XYZ:
        """
        Returns rotated point
        """
class SpanSplitError(Exception):
    pass
class TorsionAngle:
    """
    Torsion angle
    """
    @typing.overload
    def __init__(self, a: Atom, b: Atom, c: Atom, d: Atom) -> None:
        """
        Constructor of read-only value
        """
    @typing.overload
    def __init__(self, a: Atom, b: Atom, c: Atom, d: Atom, affected_atoms_selector: typing.Callable[[pyxmolpp2._core.Atom, pyxmolpp2._core.Atom, pyxmolpp2._core.Atom, pyxmolpp2._core.Atom], AtomSelection]) -> None:
        """
        Constructor of read-write value
        """
    def rotate_to(self, value: AngleValue, noop_tolerance: AngleValue = ...) -> None:
        """
        Perform rotation around torsion angle
        
        :param value: target value of torsion angle
        :param noop_tolerance: no-op tolerance to skip negligible rotations
        
        Precondition:
           Must be a read-write
        
        Note that this is O(N) operation where N is number of affected atoms
        """
    def value(self) -> AngleValue:
        """
        Current value
        """
class TorsionAngleFactory:
    """
    Generates torsion angles for standard residues
    """
    @staticmethod
    def chi1(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def chi2(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def chi3(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def chi4(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def chi5(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def get(residue: Residue, angle_name: str) -> TorsionAngle | None:
        ...
    @staticmethod
    def omega(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def phi(residue: Residue) -> TorsionAngle | None:
        ...
    @staticmethod
    def psi(residue: Residue) -> TorsionAngle | None:
        ...
class Trajectory:
    """
    Trajectory of frames
    """
    class Iterator:
        pass
    class Slice:
        def __getitem__(self, arg0: int) -> Frame:
            ...
        def __iter__(self) -> typing.Iterator[Frame]:
            ...
        def __len__(self) -> int:
            ...
        @property
        def n_atoms(self) -> int:
            """
            Number of atoms in frame
            """
        @property
        def n_frames(self) -> int:
            """
            Number of frames
            """
    @typing.overload
    def __getitem__(self, arg0: int) -> Frame:
        ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> Trajectory.Slice:
        ...
    def __init__(self, arg0: Frame) -> None:
        ...
    def __iter__(self) -> typing.Iterator[Frame]:
        ...
    def __len__(self) -> int:
        ...
    def extend(self, trajectory_file: typing.Any) -> None:
        """
        Extend trajectory
        """
    @property
    def n_atoms(self) -> int:
        """
        Number of atoms in frame
        """
    @property
    def n_frames(self) -> int:
        """
        Number of frames
        """
    @property
    def size(self) -> int:
        """
        Number of frames
        """
class TrajectoryDoubleTraverseError(Exception):
    pass
class TrajectoryInputFile:
    """
    Trajectory input file ABC
    """
    def __init__(self) -> None:
        ...
    def advance(self, shift: int) -> None:
        """
        Shift internal data pointer
        """
    def n_atoms(self) -> int:
        """
        Number of atoms per frame
        """
    def n_frames(self) -> int:
        """
        Number of frames
        """
    def read_frame(self, index: int, frame: Frame) -> None:
        """
        Assign `index` frame coordinates, cell, etc
        """
class Transformation:
    """
    Generic transformation
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, rotation_followed_by: Rotation, translation: Translation) -> None:
        ...
    @typing.overload
    def __mul__(self, arg0: Transformation) -> Transformation:
        ...
    @typing.overload
    def __mul__(self, arg0: Translation) -> Transformation:
        ...
    @typing.overload
    def __mul__(self, arg0: Rotation) -> Transformation:
        ...
    @typing.overload
    def __mul__(self, arg0: UniformScale) -> Transformation:
        ...
    @typing.overload
    def __rmul__(self, arg0: Translation) -> Transformation:
        ...
    @typing.overload
    def __rmul__(self, arg0: Rotation) -> Transformation:
        ...
    @typing.overload
    def __rmul__(self, arg0: UniformScale) -> Transformation:
        ...
    def inverted(self) -> Transformation:
        """
        Inverted transformation
        """
    def matrix3d(self) -> typing.Annotated[numpy.ndarray, numpy.float64]:
        """
        Non-translational part of transformation
        """
    def transform(self, r: XYZ) -> XYZ:
        """
        Returns transformed point
        """
    def vector3d(self) -> XYZ:
        """
        Translational part of transformation
        """
class Translation:
    """
    Translational transformation
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Identity transformation
        """
    @typing.overload
    def __init__(self, dr: XYZ) -> None:
        """
        :param a: translation vector
        """
    def __mul__(self, arg0: Translation) -> Translation:
        ...
    def dr(self) -> XYZ:
        """
        Translation vector
        """
    def inverted(self) -> Translation:
        """
        Inverted transform
        """
    def transform(self, r: XYZ) -> XYZ:
        """
        Returns translated point
        """
class TrjtoolDatFile(TrajectoryInputFile):
    """
    Trajtool trajectory file
    """
    def __init__(self, filename: str) -> None:
        ...
    def advance(self, shift: int) -> None:
        """
        Shift internal pointer by `shift`
        """
    def n_atoms(self) -> int:
        """
        Number of atoms per frame
        """
    def n_frames(self) -> int:
        """
        Number of frames
        """
    def read_frame(self, index: int, frame: Frame) -> None:
        """
        Assign `index` frame coordinates, cell, etc
        """
class UniformScale:
    """
    Uniform scale transformation
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, scale_factor: float) -> None:
        ...
    @typing.overload
    def __mul__(self, arg0: UniformScale) -> UniformScale:
        ...
    @typing.overload
    def __mul__(self, arg0: Translation) -> Transformation:
        ...
    def __rmul__(self, arg0: Translation) -> Transformation:
        ...
    def inverted(self) -> UniformScale:
        """
        Inverted transform
        """
    def transform(self, r: XYZ) -> XYZ:
        """
        Returns scaled point
        """
    @property
    def scale(self) -> float:
        """
        Linear scale factor
        """
class UnitCell:
    """
    Unit cell
    """
    class ClosestImage:
        """
        Result of closest periodic image search
        """
        @property
        def distance(self) -> float:
            """
            Distance to target
            """
        @property
        def pos(self) -> XYZ:
            """
            Position of closest image
            """
        @property
        def shift(self) -> XYZ:
            """
            Applied translation vector
            """
        @property
        def shift_int(self) -> tuple[int, int, int]:
            """
            Integer coefficients of applied translation vector
            """
    @staticmethod
    def from_rst7_line(arg0: str) -> UnitCell:
        ...
    def __getitem__(self, i: int) -> XYZ:
        """
        Get i-th cell lattice vector
        """
    @typing.overload
    def __init__(self, arg0: UnitCell) -> None:
        ...
    @typing.overload
    def __init__(self, v1: XYZ, v2: XYZ, v3: XYZ) -> None:
        """
        Construct cell from primitive vectors
        """
    @typing.overload
    def __init__(self, a: float, b: float, c: float, alpha: AngleValue, beta: AngleValue, gamma: AngleValue) -> None:
        """
        Construct cell from lengths and angles
        """
    def __len__(self) -> int:
        ...
    def closest_image_to(self, ref: XYZ, var: XYZ) -> UnitCell.ClosestImage:
        """
        Closest periodic image to `ref`
        
            :param ref: reference point
            :param var: variable point
        """
    def scale_by(self, factor: float) -> None:
        """
        Scale cell by linear factor
        """
    def scale_to_volume(self, volume: float) -> None:
        """
        Scale cell to match volume
        """
    def translation_vector(self, i: int, j: int, k: int) -> XYZ:
        """
        Returns :math:`i  \vec v_1 + j \vec  v_2 + k \vec  v_3`
        """
    @property
    def a(self) -> float:
        """
        Length of :math:`v_1`
        """
    @property
    def alpha(self) -> AngleValue:
        """
        Angle between :math:`v_2` and :math:`v_3`
        """
    @property
    def b(self) -> float:
        """
        Length of :math:`v_2`
        """
    @property
    def beta(self) -> AngleValue:
        """
        Angle between :math:`v_1` and :math:`v_3`
        """
    @property
    def c(self) -> float:
        """
        Length of :math:`v_3`
        """
    @property
    def gamma(self) -> AngleValue:
        """
        Angle between :math:`v_1` and :math:`v_2`
        """
    @property
    def volume(self) -> float:
        """
        Volume
        """
class XYZ:
    """
    3D Vector
    """
    def __add__(self, arg0: XYZ) -> XYZ:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor
        """
    @typing.overload
    def __init__(self, x: float, y: float, z: float) -> None:
        """
        Constructor
        """
    @typing.overload
    def __init__(self, arg0: XYZ) -> None:
        """
        Copy constructor
        """
    def __mul__(self, arg0: float) -> XYZ:
        ...
    def __neg__(self) -> XYZ:
        ...
    def __repr__(self) -> str:
        ...
    def __rmul__(self, arg0: float) -> XYZ:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: XYZ) -> XYZ:
        ...
    def __truediv__(self, arg0: float) -> XYZ:
        ...
    @typing.overload
    def angle(self, r: XYZ) -> AngleValue:
        """
        Angle between two vectors
        """
    @typing.overload
    def angle(self, b: XYZ, c: XYZ) -> AngleValue:
        """
        Linear angle by three points
        """
    def cross(self, arg0: XYZ) -> XYZ:
        """
        Cross product
        """
    def dihedral(self, b: XYZ, c: XYZ, d: XYZ) -> AngleValue:
        """
        Dihedral angle by four points
        """
    def distance(self, r: XYZ) -> float:
        """
        Distance
        """
    def distance2(self, r: XYZ) -> float:
        """
        Distance squared
        """
    def dot(self, arg0: XYZ) -> float:
        """
        Dot product
        """
    def len(self) -> float:
        """
        Vector length
        """
    def len2(self) -> float:
        """
        Vector length squared
        """
    @property
    def values(self) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(1, 3)]:
        """
        Convert to/from numpy.ndarray[float, 3]
        """
    @values.setter
    def values(self, arg1: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(1, 3)]) -> None:
        ...
    @property
    def x(self) -> float:
        """
        x coordinate
        """
    @x.setter
    def x(self, arg1: float) -> XYZ:
        ...
    @property
    def y(self) -> float:
        """
        y coordinate
        """
    @y.setter
    def y(self, arg1: float) -> XYZ:
        ...
    @property
    def z(self) -> float:
        """
        z coordinate
        """
    @z.setter
    def z(self, arg1: float) -> XYZ:
        ...
class XtcReadError(Exception):
    pass
class XtcWriteError(Exception):
    pass
class XtcWriter:
    """
    Writes frames in `.xtc` binary format
    """
    def __init__(self, filename: str, precision: float) -> None:
        ...
    def write(self, arg0: Frame) -> None:
        """
        Write frame
        """
def Degrees(degrees: float) -> AngleValue:
    ...
def Radians(radians: float) -> AngleValue:
    ...
def calc_alignment(ref: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)], var: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)]) -> Transformation:
    ...
def calc_autocorr_order_2(vectors: typing.Annotated[numpy.ndarray, numpy.float64], limit: int = ...) -> typing.Annotated[numpy.ndarray, numpy.float64]:
    ...
def calc_autocorr_order_2_PRE(vectors: typing.Annotated[numpy.ndarray, numpy.float64], limit: int = ...) -> typing.Annotated[numpy.ndarray, numpy.float64]:
    ...
def calc_inertia_tensor(coords: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)]) -> typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.FixedSize(3, 3)]:
    ...
def calc_rmsd(ref: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)], var: typing.Annotated[numpy.ndarray, numpy.float64, pybind11_stubgen.typing_ext.DynamicSize('m', 3)]) -> float:
    ...
def calc_sasa(coordinates: typing.Annotated[numpy.ndarray, numpy.float64], vdw_radii: typing.Annotated[numpy.ndarray, numpy.float64], solvent_radius: float, indices_of_interest: typing.Annotated[numpy.ndarray, numpy.int32] | None = ..., n_samples: int = ...) -> typing.Annotated[numpy.ndarray, numpy.float64]:
    ...
def degrees_to_radians(degrees: float) -> float:
    ...
def radians_to_degrees(radians: float) -> float:
    ...
aId: AtomIdPredicateGenerator  # value = <pyxmolpp2._core.AtomIdPredicateGenerator object>
aName: AtomNamePredicateGenerator  # value = <pyxmolpp2._core.AtomNamePredicateGenerator object>
mName: MoleculeNamePredicateGenerator  # value = <pyxmolpp2._core.MoleculeNamePredicateGenerator object>
rId: ResidueIdPredicateGenerator  # value = <pyxmolpp2._core.ResidueIdPredicateGenerator object>
rName: ResidueNamePredicateGenerator  # value = <pyxmolpp2._core.ResidueNamePredicateGenerator object>
