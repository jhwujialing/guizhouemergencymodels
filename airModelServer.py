from tornado.wsgi import WSGIContainer  
from tornado.httpserver import HTTPServer  
from tornado.ioloop import IOLoop  
from tornado.options import options  
from airModelWeb import app

import tornado

http_server = HTTPServer(WSGIContainer(app))  
http_server.listen(5000)  #flask默认的端口  
print("气体扩散模型服务正在运行，请勿关闭！！！")
IOLoop.instance().start()
