# coding: utf-8
# Step 02
import rhinoscriptsyntax as rs
import math


def UVW2XYZ(surface_id, u, v, w):
    normal = rs.SurfaceNormal(surface_id, [u, v])
    w_normal = rs.PointScale(normal, w)
    surface_xyz = rs.EvaluateSurface(surface_id, u, v)
    dirPos = rs.PointAdd(surface_xyz, w_normal)
    x, y, z = dirPos

    return x, y, z


def pattern(tinySrf, offDis):
    rs.RebuildSurface(tinySrf, degree=(3, 3), pointcount=(3, 3))  # make them (0, 1)
    domain_u = rs.SurfaceDomain(tinySrf, 0)
    domain_v = rs.SurfaceDomain(tinySrf, 1)

    u = domain_u[1]
    v = domain_v[1]

    outPts = [(u / 2, 0), (u, v / 2), (u / 2, v), (0, v / 2)]

    b = 1 / (1 + math.sqrt(3))
    c = math.sqrt(3) / 2
    inPts = [(c * b * u, c * b * v), (c * b * u + b * u, c * b * v), (c * b * u + b * u, c * b * v + b * v),
             (c * b * u, c * b * v + b * v)]

    all_shortPaths = []
    list_offTri = []
    for index, pt in enumerate(outPts):
        if index == 3:
            index1 = 0
        else:
            index1 = index + 1
        point0 = rs.EvaluateSurface(tinySrf, pt[0], pt[1])
        point1 = rs.EvaluateSurface(tinySrf, inPts[index][0], inPts[index][1])
        point2 = rs.EvaluateSurface(tinySrf, inPts[index1][0], inPts[index1][1])
        shortPaths = [rs.ShortPath(tinySrf, point0, point1),
                      rs.ShortPath(tinySrf, point1, point2),
                      rs.ShortPath(tinySrf, point2, point0)]

        triangle = rs.JoinCurves(shortPaths, True)
        offTri = rs.OffsetCurveOnSurface(triangle, tinySrf, -1.0 * offDis)
        list_offTri.append(offTri)
        all_shortPaths.append(rs.ExplodeCurves(triangle))
        rs.DeleteObject(triangle)
        '''ptu = pt[0]
        ptv = pt[1]
        xyzPt = UVW2XYZ(tinySrf, ptu, ptv, 2)
        uvVector = (-ptu/4, -ptv/4*math.sqrt(3), 0)
        nu, nv, nw = rs.PointAdd(pt, uvVector)
        xyzPt1 = UVW2XYZ(tinySrf, nu, nv, nw)
        rs.AddPoints(xyzPt)
        rs.AddPoint(xyzPt1)
        rs.Sleep(1000)'''

    list_sq = []
    list_offEdg = []
    for sp_index, sps in enumerate(all_shortPaths):
        if sp_index == 3:
            sp_index1 = 0
        else:
            sp_index1 = sp_index + 1

        outEdge = rs.JoinCurves([sps[2], all_shortPaths[sp_index1][0]], True)
        list_sq.append(sps[1])

        offEdg = rs.OffsetCurveOnSurface(outEdge, tinySrf, offDis)
        list_offEdg.append(offEdg)
        rs.DeleteObject(outEdge)

    square = rs.JoinCurves(list_sq, True)
    offSqu = rs.OffsetCurveOnSurface(square, tinySrf, offDis)
    rs.DeleteObject(square)

    return offSqu, list_offTri, list_offEdg


def main():
    list_star = []
    surface_id = rs.GetObjects("Surfaces", 8, True, True)

    for midTS in surface_id:
        offLength = math.sqrt(rs.SurfaceArea(midTS)[0])/20
        midSqu, midTris, midEdgs = pattern(midTS, offLength)

        offsetSrf = rs.OffsetSurface(midTS, 0.2, both_sides=True)  # Brep  # thickness!! 0.2, 0.1, 0.2, 0.25
        outTS = rs.ExtractSurface(offsetSrf, 0)
        outSqu, outTris, outEdgs = pattern(outTS, offLength/5)

        inTS = rs.ExtractSurface(offsetSrf, 0)
        inSqu, inTris, inEdgs = pattern(inTS, offLength/5)

        list_loftSrf = []
        loftSqu = rs.AddLoftSrf([outSqu, midSqu, inSqu], loft_type=2)
        list_loftSrf.append(loftSqu)
        rs.DeleteObjects([outSqu, midSqu, inSqu])

        for midT, outT, inT in zip(midTris, outTris, inTris):
            loftTri = rs.AddLoftSrf([outT, midT, inT], loft_type=2)
            list_loftSrf.append(loftTri)
            rs.DeleteObjects([midT, outT, inT])

        for midE, outE, inE in zip(midEdgs, outEdgs, inEdgs):
            loftEdg = rs.AddLoftSrf([outE, midE, inE], loft_type=2)
            list_loftSrf.append(loftEdg)
            rs.DeleteObjects([midE, outE, inE])

        allSrf = list(list_loftSrf)

        for i, srf in enumerate(list_loftSrf):
            splitOT = rs.SplitBrep(outTS, srf, delete_input=True)
            outTS = splitOT[0]
            rs.DeleteObject(splitOT[1])

            splitIT = rs.SplitBrep(inTS, srf, delete_input=True)
            if i < 5:
                inTS = splitIT[0]
                rs.DeleteObject(splitIT[1])
            else:
                inTS = splitIT[1]
                rs.DeleteObject(splitIT[0])

            rs.Sleep(10)

        rs.DeleteObjects(midTS)

        allSrf.append(outTS)
        allSrf.append(inTS)
        star = rs.JoinSurfaces(allSrf)
        list_star.append(star)

        rs.DeleteObjects(allSrf)

    stars = rs.JoinSurfaces(list_star)
    rs.DeleteObjects(list_star)
    cutter = rs.AddSrfPt([[-100, 100, 0.1], [100, 100, 0.1], [100, -100, 0.1], [-100, -100, 0.1]])  # 0.1
    final = rs.SplitBrep(stars, cutter, delete_input=True)
    rs.DeleteObjects([cutter, final[0]])
    rs.CapPlanarHoles(final[1])


if __name__ == '__main__':
    main()
