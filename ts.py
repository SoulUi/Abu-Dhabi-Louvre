# coding: utf-8
# Step 01
import rhinoscriptsyntax as rs
import math


def divideSphere(sphere, num, angleA):
    rs.RebuildSurface(sphere, degree=(3, 3), pointcount=(2*num, num+3))
    if rs.IsSurface(sphere):
        domainU = rs.SurfaceDomain(sphere, 0)
        domainV = rs.SurfaceDomain(sphere, 1)

        # print("Domain in U direction:", domainU)
        # print("Domain in V direction:", domainV)

        minU = int((90-angleA)/360 * domainU[1])
        maxU = int((90+angleA)/360 * domainU[1]) + 1

        minV = int((90-angleA)/180 * domainV[1])
        maxV = int((90+angleA)/180 * domainV[1]) + 1

        listTS = []

        for n in range(minU, maxU):
            u0 = n
            u1 = n + 1
            subSrf = rs.TrimSurface(sphere, 0, (u0, u1))  # surface_id, direction(0 or 1)==(U or V), interval=(0, 1)
            # list_subSrf.append(subSrf)
            for m in range(minV, maxV):
                v0 = m
                v1 = m + 1
                tinySrf = rs.TrimSurface(subSrf, 1, (v0, v1))
                listTS.append(tinySrf)

                rs.Sleep(10)

            rs.DeleteObject(subSrf)

        # print(len(list_tinySrf))
        rs.DeleteObject(sphere)
        # rs.DeleteObjects(listTS)


def dome():
    plane = rs.WorldXYPlane()
    width = 160
    high = 16
    r = width/2
    R = (r**2 + high**2) / (2*high)
    angleA = math.degrees(math.asin(r/R))
    # print(angleA)
    circle = rs.AddCircle((0, 0, 0), r)

    sphCentre = (0, 0, -(R-high))
    sphere0 = rs.AddSphere(sphCentre, R)
    rs.RotateObject(sphere0, sphCentre, rotation_angle=90,  axis=plane.XAxis)

    sphere = rs.OffsetSurface(sphere0, -1.55)  # -0.25, -0.55, -0.85, -1.3
    rs.RotateObject(sphere, sphCentre, rotation_angle=0,  axis=plane.ZAxis)  # use betweenwhiles 0, 45, 135, 180
    rs.DeleteObject(sphere0)

    divideSphere(sphere, 50, angleA)  # 50, 85, 54, 29


if __name__ == '__main__':
    dome()
