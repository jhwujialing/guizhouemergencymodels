import math

class RiverModel(object):
    # 河流宽度，河流深度，水流速度，污染物质量，扩散系数，降解速率常数
    def __init__(self,riverwidth,riverdepth,waterspeed,wrwzl,ksxs,k=0):
        self.riverwidth = riverwidth
        self.riverdepth = riverdepth
        self.waterspeed = waterspeed
        self.wrwzl = wrwzl
        self.ksxs = ksxs
        self.k = k

    def getNd(self,x,t):
        a = self.wrwzl / (2 * self.riverwidth * self.riverdepth * math.sqrt(math.pi * self.ksxs * t) )
        b = math.exp(0 - math.pow((x - self.waterspeed * t),2) / (4 * self.ksxs * t))
        c = math.exp(0 - self.k * t)
        result = a * b * c
        return result


if __name__ == '__main__':
    river = RiverModel(50,8,0.5,28800000000,6)

    print(river.getNd(10000,18000))