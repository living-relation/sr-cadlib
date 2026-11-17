"""Minimal Autodesk Fusion API stub so unit tests can run without Fusion."""
from __future__ import annotations


class _Named:
    def __init__(self, name: str) -> None:
        self.name = name
        self.id = "id:" + name
        self.isComplete = True


class Point3D:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x, self.y, self.z = float(x), float(y), float(z)

    @staticmethod
    def create(x: float, y: float, z: float) -> Point3D:
        return Point3D(x, y, z)

    def asArray(self) -> list[float]:
        return [self.x, self.y, self.z]


class Vector3D:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x, self.y, self.z = float(x), float(y), float(z)

    @staticmethod
    def create(x: float, y: float, z: float) -> Vector3D:
        return Vector3D(x, y, z)

    def asArray(self) -> list[float]:
        return [self.x, self.y, self.z]

    def crossProduct(self, other: Vector3D) -> Vector3D:
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dotProduct(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z


class ValueInput:
    def __init__(self, value: float) -> None:
        self.value = float(value)

    @staticmethod
    def createByReal(v: float) -> ValueInput:
        return ValueInput(v)


class OrientedBoundingBox3D:
    def __init__(self, center, xdir, ydir, length, width, height) -> None:
        self.center = center
        self.xdir, self.ydir = xdir, ydir
        self.length, self.width, self.height = length, width, height

    @staticmethod
    def create(center, xdir, ydir, length, width, height) -> OrientedBoundingBox3D:
        return OrientedBoundingBox3D(center, xdir, ydir, length, width, height)


class Matrix3D:
    def __init__(self) -> None:
        self.origin = None
        self.axes = None

    @staticmethod
    def create() -> Matrix3D:
        return Matrix3D()

    def setWithCoordinateSystem(self, origin, xdir, ydir, zdir) -> None:
        self.origin = origin
        self.axes = (xdir, ydir, zdir)


class ObjectCollection(list):
    @staticmethod
    def create() -> ObjectCollection:
        return ObjectCollection()

    def add(self, item) -> None:
        self.append(item)


class TemporaryBRepManager:
    _inst = None

    @staticmethod
    def get() -> TemporaryBRepManager:
        if TemporaryBRepManager._inst is None:
            TemporaryBRepManager._inst = TemporaryBRepManager()
        return TemporaryBRepManager._inst

    def createBox(self, obb):
        return {"kind": "box", "obb": obb}

    def createCylinderOrCone(self, p1, r1, p2, r2):
        return {"kind": "cyl", "p1": p1, "r1": r1, "p2": p2, "r2": r2}

    def booleanOperation(self, a, b, typ):
        a.setdefault("ops", []).append((typ, b))
        return a


class _Enum:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class BooleanTypes:
    UnionBooleanType = _Enum("union")
    DifferenceBooleanType = _Enum("difference")
    IntersectionBooleanType = _Enum("intersection")


class FeatureOperations:
    NewBodyFeatureOperation = _Enum("new")
    CutFeatureOperation = _Enum("cut")
    JoinFeatureOperation = _Enum("join")


class ExtentDirections:
    PositiveExtentDirection = _Enum("positive")
    NegativeExtentDirection = _Enum("negative")
    SymmetricExtentDirection = _Enum("symmetric")


class DistanceUnits:
    MillimeterDistanceUnits = _Enum("mm")
    InchDistanceUnits = _Enum("in")


class DesignTypes:
    ParametricDesignType = _Enum("parametric")
    DirectDesignType = _Enum("direct")


class DocumentTypes:
    FusionDesignDocumentType = _Enum("fusion")


class DistanceExtentDefinition:
    @staticmethod
    def create(value):
        return {"extent": value}


class _UnitsManager:
    def __init__(self) -> None:
        self.distanceDisplayUnits = None


class _Root:
    def __init__(self) -> None:
        self.partNumber = ""
        self.description = ""


class _Design:
    def __init__(self) -> None:
        self.designType = None
        self.fusionUnitsManager = _UnitsManager()
        self.rootComponent = _Root()
        self.appearances = _NamedList()


class _Doc:
    def __init__(self, name: str = "scratch") -> None:
        self.name = name
        self.dataFile = _Named(name)
        self.products = _Products(self)

    def saveAs(self, name, fold, desc, extra):
        self.name = name
        self.dataFile = _Named(name)
        return True

    def close(self, save):
        self.closed = (False if save is False else True)


class _Products:
    def __init__(self, doc) -> None:
        self._doc = doc
        self._design = _Design()

    def itemByProductType(self, typ):
        return self._design


class _NamedList:
    def __init__(self) -> None:
        self._items = {}

    def itemByName(self, name):
        return self._items.get(name)

    def addByCopy(self, src, name):
        self._items[name] = src
        return src


class _Documents:
    def __init__(self) -> None:
        self._docs = []

    @property
    def count(self) -> int:
        return len(self._docs)

    def add(self, typ):
        doc = _Doc()
        self._docs.append(doc)
        return doc

    def item(self, i):
        return self._docs[i]


class _Folder:
    def __init__(self, name: str) -> None:
        self.name = name
        self.dataFolders = _FolderList(self)
        self.dataFiles = []

    def add(self, name: str) -> _Folder:
        child = _Folder(name)
        self.dataFolders._items.append(child)
        return child


class _FolderList:
    def __init__(self, owner: _Folder) -> None:
        self._owner = owner
        self._items: list[_Folder] = []

    def __iter__(self):
        return iter(self._items)

    def add(self, name: str) -> _Folder:
        return self._owner.add(name)


class _Project:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rootFolder = _Folder("")


class _Data:
    def __init__(self) -> None:
        self.dataProjects: list[_Project] = []
        self._files: dict[str, _Named] = {}

    def findFileById(self, file_id: str):
        return self._files.get(file_id)


class _App:
    def __init__(self) -> None:
        self.documents = _Documents()
        self.data = _Data()
        self.materialLibraries = _NamedList()

    @staticmethod
    def get() -> _App:
        return _APP


_APP = _App()


class Application:
    @staticmethod
    def get() -> _App:
        return _APP


class Design:
    @staticmethod
    def cast(obj):
        return obj


def doEvents() -> None:
    return None


# Namespaces that fusion.py imports as adsk.core / adsk.fusion
class _Core:
    Point3D = Point3D
    Vector3D = Vector3D
    ValueInput = ValueInput
    OrientedBoundingBox3D = OrientedBoundingBox3D
    Matrix3D = Matrix3D
    ObjectCollection = ObjectCollection
    Application = Application
    DocumentTypes = DocumentTypes


class _Fusion:
    TemporaryBRepManager = TemporaryBRepManager
    BooleanTypes = BooleanTypes
    FeatureOperations = FeatureOperations
    ExtentDirections = ExtentDirections
    DistanceUnits = DistanceUnits
    DesignTypes = DesignTypes
    DistanceExtentDefinition = DistanceExtentDefinition
    Design = Design


core = _Core()
fusion = _Fusion()
