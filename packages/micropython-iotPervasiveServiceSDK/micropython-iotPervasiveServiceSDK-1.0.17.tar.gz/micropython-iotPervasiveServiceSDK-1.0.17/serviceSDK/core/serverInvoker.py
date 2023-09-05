
import ujson
import os
from . import applicationContext
from .. import config
from ..utils import templateUtils as TemplateUtils
from ..utils import pathUtils as PathUtil
from ..utils import copyUtils as CopyUtils
from .exception.serviceException import ServiceNotExistException
from .exception.serviceException import CapabilityNotExistException
from .exception.serviceException import ProxyNotExistException
from .exception.commonException import invalidParamsException
from ..model.ujinja.source import TemplateEngine
from ..proxy.thingProxy import thingProxy
from ..pojo.serviceBean import ServiceBean
from ..pojo.eventBean import EventBean
from .exception.serviceException import EventNotExistException



class CapabilityInvoker:
  '''
  * 调用服务
  * serviceId  服务id
  * capabilityId 能力id
  * postJsonDict 消息的参数字典
  '''
  def invokeCapability(serviceId:str,capabilityId:str,requestJsonDict:dict):
    requestJsonDict["system"] = applicationContext.getSystemInfo()
    # 特判物模型读写服务    
    if (serviceId == "thingService"):
        return thingProxy({"operation":capabilityId}).handle(requestJsonDict)
    # 从服务字典读取服务信息
    if (serviceId==None):
        raise invalidParamsException("id",serviceId)
    if (capabilityId == None):
        raise invalidParamsException("capabilityId",capabilityId)
    service = applicationContext.serviceDict.get(serviceId,None)
    if (service == None):
        raise ServiceNotExistException(serviceId)
    capability = service.capabilityBeanDict.get(capabilityId,None)
    if (capability==None):
        raise CapabilityNotExistException(capabilityId)
    # jinja2 输入消息转换
    runData = None
    if(capability.inputMapper != None):
      if(capability.inputLanguage == "jinja2"):
          inputTemplateEngine = TemplateEngine()
          inputTemplateEngine.load_template(capability.inputMapper)
          runData = inputTemplateEngine.render_template(requestJsonDict)
          print(runData)
        
    initData = CopyUtils.dictCopy(capability.attributes)
    # 如果是python代理则需要加载脚本所在位置
    if(capability.proxyType == "pythonServiceProxy"):
      scriptPath = PathUtil.joinPath(service.filePath,"script")
      initData["script"] = PathUtil.joinPath(scriptPath,initData["script"])
    response = CapabilityInvoker.invokeProxy(capability.proxyType,initData,runData)
    #输出消息转换
    if(capability.outputMapper != None):
      if(capability.outputLanguage == "jinja2"):
        outputTemplateEngine = TemplateEngine()
        outputTemplateEngine.load_template(capability.outputMapper)
        response = outputTemplateEngine.render_template(ujson.loads(response))
        print(response)
    return response


  '''
  * 运行代理
  * proxyName 代理名称
  * initData  初始化数据
  * runData   运行时数据
  '''
  def invokeProxy(proxyName:str,initData:any,runData):
      proxyModel = applicationContext.proxyDict.get(proxyName,None)
      if(proxyModel==None):
          raise ProxyNotExistException(proxyName)
      if(hasattr(proxyModel,proxyName)):
        proxyClass = getattr(proxyModel,proxyName)
        proxy = proxyClass(initData)
        return proxy.handle(runData)
  


'''
* 事件调用类
'''
class EventInvoker:

  '''
  *调用系统事件
  '''
  @staticmethod
  def invokeSystemEvent(eventId:str,eventArgs:dict = {}):
    EventInvoker.invokeEvent("systemService",eventId,eventArgs)


  '''
  * 调用事件
  * serviceId 服务id
  * eventId 事件id
  * eventArgs 事件参数字典
  '''
  @staticmethod
  def invokeEvent(serviceId:str,eventId:str,eventArgs:dict = {}):
    eventArgs["system"] = applicationContext.getSystemInfo()
    service:ServiceBean = applicationContext.serviceDict.get(serviceId,None)
    if service == None:
      raise ServiceNotExistException(serviceId)
    
    event:EventBean = service.eventBeanDict.get(eventId,None)
    if event == None:
      raise EventNotExistException(eventId,serviceId)
    
    eventMsg = None
    if event.messageMapper!=None:
      if(event.messageLanguage == "jinja2" or event.messageLanguage == None):
          inputTemplateEngine = TemplateEngine()
          inputTemplateEngine.load_template(event.messageMapper)
          eventMsg = inputTemplateEngine.render_template(eventArgs)
          print("== event msg Mapper == ")
          print(eventMsg)

    # 默认是mqtt的方式上报topic
    if event.protocolType == "MQTT" or event.protocolType == None:
      EventInvoker._MQTTEventSender(service,event,eventMsg)


  '''
  * mqtt事件发送
  '''
  @staticmethod
  def _MQTTEventSender(service:ServiceBean,event:EventBean,eventMsg:str):
    from ..systemService.mqttService import MqttService
    host:str = event.attributes.get("host",None)
    isSystemMqtt = False
    mqttClient = None

    # 默认使用系统的mqtt客户端
    if host == "" or host == None:
      isSystemMqtt = True
      mqttClient = applicationContext.pervasiveMqttClient
    else:
      addressList:list = host.split(":")
      mqttClient = MqttService(''.join([('0'+hex(ord(os.urandom(1)))[2:])[-2:] for x in range(8)]),addressList[0],addressList[1])

    topic = event.attributes.get("topic",config.ON_EVENT_TOPIC)
    msgJsonDict = {
      "deviceInstanceId":config.DEVICE_ID,
      "serviceUrl": service.url,
      "versionCode": service.versionCode,
      "eventId":event.eventId,
      "msg": eventMsg
    }

    mqttClient.sendMsg(topic,ujson.dumps(msgJsonDict))
    # 如果非系统的mqtt客户端则关闭
    if not isSystemMqtt:
      mqttClient.close()


  def getEventMsgStr(service:ServiceBean,event:EventBean,eventMsg:str):
    msgJsonDict = {
      "deviceInstanceId":config.DEVICE_ID,
      "serviceUrl": service.url,
      "versionCode": service.versionCode,
      "eventId":event.eventId,
      "msg": eventMsg
    }
    return ujson.dumps(msgJsonDict)
        