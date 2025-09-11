from collections.abc import Iterable

import adsk.core, adsk.fusion

from .helpers import collection
from .vector import Vector
from .point3d import point3d


def sketch_fix_all(sketch: adsk.fusion.Sketch):
    """Fix all sketch contents."""
    for p in sketch.sketchPoints:
        p.isFixed = True
    for c in sketch.sketchCurves:
        c.isFixed = True
    for t in sketch.sketchTexts:
        t.isFixed = True


def sketch_line(
    sketch: adsk.fusion.Sketch,
    p1: Vector | adsk.core.Point3D | adsk.fusion.SketchPoint,
    p2: Vector | adsk.core.Point3D | adsk.fusion.SketchPoint,
):
    """Add a line by two points, accepting both Vector and Point3D types."""
    if isinstance(p1, Vector):
        p1 = point3d(p1)
    if isinstance(p2, Vector):
        p2 = point3d(p2)

    return sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)  # type: ignore[arg-type]


def sketch_fitted_splines(
    sketch: adsk.fusion.Sketch, points: Iterable[Vector | adsk.core.Point3D | adsk.fusion.SketchPoint]
):
    """Add a fitted spline to the sketch using a list of points."""
    converted = [point3d(p) if isinstance(p, Vector) else p for p in points]
    return sketch.sketchCurves.sketchFittedSplines.add(collection(converted))


def sketch_arc_center_start_end(
    sketch: adsk.fusion.Sketch,
    center: Vector | adsk.core.Point3D,
    start: Vector | adsk.core.Point3D,
    end: Vector | adsk.core.Point3D,
):
    """Add an arc by center, start, and end points."""
    if isinstance(center, Vector):
        center = point3d(center)
    if isinstance(start, Vector):
        start = point3d(start)
    if isinstance(end, Vector):
        end = point3d(end)

    return sketch.sketchCurves.sketchArcs.addByCenterStartEnd(center, start, end)  # type: ignore[arg-type]
