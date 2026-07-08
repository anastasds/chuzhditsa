#!/usr/bin/env python3
"""Join linter: find stroke endpoints that ALMOST meet.

Two failure classes ruin a monoline at a glance:
  MISS   two endpoints 4..30 units apart — meant to join, don't. The chain
         snap (tol 4) can't save them; the outlines meet in a notch.
  GRAZE  an endpoint hovering 25..100 units from another stroke's centerline
         — the butt cap pokes about the band edge and leaves a wedge.
Endpoints nearer than 4 units chain cleanly; farther than the thresholds is
read as intentional (a genuine terminal). Run after any glyph-data edit."""
import math, sys
from build_font import G, arc_pts, L, A, R, D

MISS_LO, MISS_HI = 4.0, 30.0
GRAZE_LO, GRAZE_HI = 25.0, 100.0

# reviewed and intentional: Д's bottom bar extends 40 units past its legs
# into feet (29 after lowercase scaling)
WAIVED_MISS = {"d", "lc.d", "je", "lc.je"}  # d: bar feet; je: hook junction is engine-pinned


def stroke_geometry(st):
    """-> (endpoints, centerline_polyline or None-for-dot)"""
    k = st[0]
    if k == L:
        pts = [(st[1], st[2]), (st[3], st[4])]
        return pts, pts
    if k == A:
        pts = arc_pts(st[1], st[2], st[3], st[4], st[5])
        if st[3] >= 290 and abs(st[5]-st[4]) >= 120:  # match builder compression
            pts = [(st[1]+(x-st[1])*0.965, y) for x, y in pts]
        return [pts[0], pts[-1]], pts
    if k == R:
        n = 64
        ring = [(st[1]+st[3]*math.cos(2*math.pi*i/n), st[2]+st[3]*math.sin(2*math.pi*i/n))
                for i in range(n+1)]
        return [], ring
    return [], None  # dot


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay
    L2 = dx*dx + dy*dy
    t = 0 if L2 == 0 else max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L2))
    return math.hypot(px-ax-t*dx, py-ay-t*dy)


def poly_dist(p, poly):
    return min(seg_dist(p, poly[i], poly[i+1]) for i in range(len(poly)-1))


def segs_cross(a1, a2, b1, b2):
    def o(p, q, r):
        v = (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    return (o(a1,a2,b1) != o(a1,a2,b2)) and (o(b1,b2,a1) != o(b1,b2,a2))


def polys_cross(pa, pb):
    return any(segs_cross(pa[i], pa[i+1], pb[j], pb[j+1])
               for i in range(len(pa)-1) for j in range(len(pb)-1))


def lint(names=None, graze=False):
    findings = []
    for name in sorted(names or G):
        strokes = G[name]["strokes"]
        geo = [stroke_geometry(st) for st in strokes]
        # class 1: endpoint near-misses across strokes
        eps = [(i, p) for i, (ends, _) in enumerate(geo) for p in ends]
        for a in range(len(eps)):
            for b in range(a+1, len(eps)):
                (ia, pa), (ib, pb) = eps[a], eps[b]
                if ia == ib:
                    continue
                d = math.hypot(pa[0]-pb[0], pa[1]-pb[1])
                if MISS_LO < d <= MISS_HI and name not in WAIVED_MISS:
                    # strokes that cross past each other (the bowls of З) are
                    # joined by their crossing, not by their endpoints
                    if polys_cross(geo[ia][1], geo[ib][1]):
                        continue
                    findings.append((name, "MISS", f"stroke{ia}@{pa} .. stroke{ib}@{pb} d={d:.1f}"))
        # class 2 (advisory, off by default: T-joins on stroke interiors and
        # deliberate free terminals dominate; scan it after adding glyphs)
        if not graze:
            continue
        for i, (ends, _) in enumerate(geo):
            for p in ends:
                for j, (ends_j, poly) in enumerate(geo):
                    if i == j or poly is None:
                        continue
                    # skip if this is already an endpoint join (class-1 territory)
                    if any(math.hypot(p[0]-q[0], p[1]-q[1]) <= MISS_HI for q in ends_j):
                        continue
                    d = poly_dist(p, poly)
                    if GRAZE_LO < d <= GRAZE_HI:
                        findings.append((name, "GRAZE", f"stroke{i} end {p} is {d:.1f} from stroke{j} centerline"))
    return findings


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--graze"]
    fs = lint(args or None, graze="--graze" in sys.argv)
    for name, kind, msg in fs:
        print(f"{name:14s} {kind:6s} {msg}")
    print(f"{len(fs)} finding(s)")
    sys.exit(1 if fs else 0)
