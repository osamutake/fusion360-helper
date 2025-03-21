from __future__ import annotations

import adsk.core, adsk.fusion

from . import vector
from .vector3d import vector3d
from .point3d import point3d


def matrix_flip_axes(
    x: bool = False,
    y: bool = False,
    z: bool = False,
    base: adsk.core.Matrix3D | None = None,
):
    matrix = adsk.core.Matrix3D.create()
    matrix.setToAlignCoordinateSystems(
        point3d(),
        vector3d(x=1),
        vector3d(y=1),
        vector3d(z=1),
        point3d(),
        vector3d(x=-1 if x else 1),
        vector3d(y=-1 if y else 1),
        vector3d(z=-1 if z else 1),
    )
    if base is None:
        return matrix
    base.transformBy(matrix)
    return base


def matrix_rotate(
    angle: float,
    axis: adsk.core.Vector3D = adsk.core.Vector3D.create(z=1),
    center: adsk.core.Point3D = adsk.core.Point3D.create(),
    translation: adsk.core.Vector3D | None = None,
    base: adsk.core.Matrix3D | None = None,
):
    matrix = adsk.core.Matrix3D.create()
    matrix.setToRotation(angle, axis, center)
    if translation is not None:
        matrix.translation = translation
    if base is None:
        return matrix
    base.transformBy(matrix)
    return base


def matrix_translate(
    x: adsk.core.Vector3D | vector.Vector | float = 0,
    y: float = 0,
    z: float = 0,
    base: adsk.core.Matrix3D | None = None,
):
    matrix = adsk.core.Matrix3D.create()
    matrix.translation = vector3d(x, y, z)
    if base is None:
        return matrix
    base.transformBy(matrix)
    return base
