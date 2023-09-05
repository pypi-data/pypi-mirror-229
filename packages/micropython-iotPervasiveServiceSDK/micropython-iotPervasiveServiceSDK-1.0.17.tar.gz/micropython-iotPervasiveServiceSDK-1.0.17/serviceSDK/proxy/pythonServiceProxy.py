from .proxyBase import ProxyBase 
import sys

'''
python服务代理
'''
class pythonServiceProxy(ProxyBase):
  script = None

  '''
  python服务代理初始化
  '''
  def __init__(self,script) -> None:
    print("====pythonServiceProxy====")
    print(script)
    path = script["script"]
    path = path.split("/")
    #todo 增加验证
    path[-1] = path[-1][0:-3]
    t="."
    packageName = t.join(path)
    print(packageName)
    packageName=packageName[1:]
    exec("import "+packageName)
    self.script = sys.modules[packageName]
    

  '''
  python服务代理执行
  '''
  def handle(self,request):
    return self.script.execute(request)
    