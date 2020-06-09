import math
from sympy import *
from scipy.integrate import quad
import numpy as np

## 连续泄露模型/高斯烟羽烟团混合模型
class ContinuousModel(object):
    # 单位时间泄露量(源强)，风速，大气稳定度，粗糙度，泄露时长
    def __init__(self, Q , u , H ,stability,roughness, tr=np.inf):
        self.Q = float(Q)
        self.u = float(u)
        self.H = float(H)
        self.stability = str(stability)
        self.roughness = float(roughness)
        self.tr = float(tr)

    def getNd(self, x, y, z, t):

        if self.stability == 'A':
            Yksxs = float(0.22) * x * math.pow((int(1) + float(0.0001) * x), (int(-1) / int(2)))
            Zksxs = float(0.20) * x
            a0= float(0.042)
            b0 = float(1.1)
            c0 = float(0.0364)
            d0 = float(0.4364)
            e0 = float(0.05)
            f0 = float(0.273)
            g0 = float(0.024)
        elif self.stability == 'B':
            Yksxs = float(0.16) * x * math.pow((int(1) + float(0.0001) * x), (int(-1) / int(2)))
            Zksxs = float(0.12) * x
            a0 = float(0.115)
            b0 = float(1.5)
            c0 = float(0.045)
            d0 = float(0.853)
            e0 = float(0.0128)
            f0 = float(0.156)
            g0 = float(0.0136)
        elif self.stability == 'C':
            Yksxs = float(0.11) * x * math.pow((int(1) + float(0.0001) * x), (int(-1) / int(2)))
            Zksxs = float(0.08) * x * math.pow((int(1) + float(0.0002) * x), (int(-1) / int(2)))
            a0 = float(0.38)
            b0 = float(1.49)
            c0 = float(0.0182)
            d0 = float(0.87)
            e0 = float(0.01046)
            f0 = float(0.089)
            g0 = float(0.0071)
        elif self.stability == 'D':
            Yksxs = float(0.08) * x * math.pow((int(1) + float(0.0001) * x), (int(-1) / int(2)))
            Zksxs = float(0.06) * x * math.pow((int(1) + float(0.0015) * x), (int(-1) / int(2)))
            a0 = float(0.3)
            b0 = float(2.53)
            c0 = float(0.13)
            d0 = float(0.55)
            e0 = float(0.042)
            f0 = float(0.35)
            g0 = float(0.03)
        elif self.stability == 'E':
            Yksxs = float(0.06) * x * math.pow((int(1) + float(0.0001) * x), (int(-1) / int(2)))
            Zksxs = float(0.03) * x * math.pow((int(1) + float(0.0003) * x), (int(-1) / int(2)                                                                          ))
            a0 = float(0.3)
            b0 = float(2.4)
            c0 = float(0.11)
            d0 = float(0.86)
            e0 = float(0.01682)
            f0 = float(0.27)
            g0 = float(0.022)
        elif self.stability == 'F':
            Yksxs = 0.04 * x * math.pow((1 + 0.0001 * x), (-1 / 2))
            Zksxs = 0.016 * x * math.pow((1 + 0.0003 * x), (-1 / 2))
            a0 = float(0.57)
            b0 = float(2.913)
            c0 = float(0.0944)
            d0 = float(0.753)
            e0 = float(0.0228)
            f0 = float(0.29)
            g0 = float(0.023)
        #其他情况统一归为D档
        else:
            Yksxs = 0.08 * x * math.pow((1 + 0.0001 * x), (-1 / 2))
            Zksxs = 0.06 * x * math.pow((1 + 0.0015 * x), (-1 / 2))
            a0 = float(0.3)
            b0 = float(2.53)
            c0 = float(0.13)
            d0 = float(0.55)
            e0 = float(0.042)
            f0 = float(0.35)
            g0 = float(0.03)
        if self.roughness<= float(0.1):
            Yksxs = Yksxs
            Zksxs = Zksxs
        else:
            Yksxs = Yksxs * (int(1)+a0*self.roughness)
            Zksxs = Zksxs*(b0-c0*(math.log(x,math.e)))*d0+(math.pow((e0*(math.log(x,math.e))),-1))*(math.pow(self.roughness,f0-g0*(math.log(x,math.e))))
        Xksxs = Yksxs

        a = self.Q
        b = math.pow(int(2)*math.pi, int(3)/int(2))*Xksxs*Yksxs*Zksxs
        d = math.exp(-y*y/(int(2)*Yksxs*Yksxs))
        if self.H != 0:
            c = math.exp(-(z-self.H)*(z-self.H)/(int(2)*Zksxs*Zksxs))+math.exp(-(z+self.H)*(z+self.H)/(int(2)*Zksxs*Zksxs))
            f = lambda dt: int(2)*a/b*d*c*math.exp(-(x-self.u*(t-dt))*(x-self.u*(t-dt))/(int(2)*Xksxs*Xksxs))
        else:
            f = lambda dt: int(2)*a/b*d*math.exp(-(x-self.u*(t-dt))*(x-self.u*(t-dt))/(int(2)*Xksxs*Xksxs))
        #f = lambda dt: dt*a/b*d*c*math.exp(-(x-self.u*(t-dt))*(x-self.u*(t-dt))/(2*Xksxs*Xksxs))
        if t <= self.tr:
            res, _ = quad(f, int(0), t)
        else:
            res, _ = quad(f, int(0), self.tr)

        return float(res)



## 瞬时泄露模型/高斯烟团模型
class InstantModel(object):
    # 污染物排放量， 平均风速
    def __init__(self, Q, u):
        self.Q = Q
        self.u = u

    def getNd(self, x, y, t):
        #
        Yksxs = 0.11 * x * math.pow((1 + 0.0004 * x),(-1/2))
        #print(Yksxs)
        Zksxs = 0.08 * x * math.pow((1 + 0.0015 * x),(-1/2))
        #print(Zksxs)
        Xksxs = Yksxs

        a = self.Q / (math.pow(2*math.pi,3/2) * Xksxs * Yksxs * Zksxs)

        b = math.exp(-(math.pow(x-self.u*t,2)/(2*Xksxs*Xksxs)))

        c = math.exp(-(math.pow(y,2)/(2*Yksxs*Yksxs)))

        result = a * b * c

        return result