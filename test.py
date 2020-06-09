'''
from airModels import ContinuousModel
air = ContinuousModel(5000000,1,0,'D',0,660)
def as_num(x):
	y='{:.5f}'.format(x) # 5f表示保留5位小数点的float型
	return(y)
for i in range(0,1000,10):
	res = air.getNd(500, 500,0, 500)
	res = as_num(res)'''
	#print (res)
import math
a = 2
b =1
H = 3
array = [{'a':1,'b':2},{'a':2,'b':3}]

if 1 not in array['a']:
	print (123)
