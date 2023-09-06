import re
import time

from ats_base.common import func
from ats_base.log.logger import logger
from ats_base.service import app, pro, em, udm, build_in

from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *

"""
    常用操作命令
"""


def send(context: Context, todo: dict, types=2, retry_times: int = 3):
    """
    发送操作命令 - 向测试端app
    :param context:         上下文
    :param todo:            任务
    :param types:
    :param retry_times:     失败重试次数（默认：3次）
    :return:
    """
    result = None

    try:
        data = {
            'type': types,
            'exec_time': func.sys_current_time(),
            'test_sn': context.test_sn,
            'case_id': context.case.id,
            'meter_pos': context.meter.pos,
            'step_id': context.runtime.step,
            'todo': todo
        }

        logger.info('~ @TCC-SEND-> client:{} data:{}'.format(context.tester.api, data))
        result = app.send(context.tester.api, data)
        logger.info('~ @TCC-SEND<- result:{}'.format(result))
    # except requests.exceptions.MissingSchema as me:
    #     logger.error(str(me))
    #     raise AssertionError(str(me))
    except Exception as ae:
        logger.error(str(ae))

        retry_times -= 1
        if retry_times <= 0:
            raise APIError(context.tester.api)
        else:
            sleep(5)
            send(context, todo, types, retry_times)

    return result


def sleep(seconds: float):
    """
    休眠
    :param seconds:     秒
    :return:
    """
    logger.info('~ @TCC-SLEEP-> {}secs'.format(seconds))
    time.sleep(seconds)


def offbench(context: Context, disabled=1):
    """
    脱表台
    :param context:
    :param disabled:     使能
    :return:
    """
    clazz = OperationClazz(context.case.steps[str(context.runtime.step)].get('type'))

    if disabled == 1:
        if clazz == OperationClazz.BENCH:
            return True

    return False


"""
    内部方法
"""


def _replace(context: Context, data: dict):
    sd = str(data)
    sd = sd.replace('$', '"')

    re_list = re.findall(r"#(.+?)\'", sd)
    for r in re_list:
        v = eval(r)
        if type(v) is str:
            sd = sd.replace('#{}'.format(r), v)
        else:
            sd = sd.replace('\'#{}\''.format(r), str(v))

    re_list = re.findall(r"&(.+?)\'", sd)
    for r in re_list:
        sd = sd.replace(r, '{}:{}:{}:{}'.format(context.test_sn, context.case.id, context.meter.pos, r))

    return eval(sd)


def _replace_bench0(context: Context, data: dict):
    sd = str(data)

    re_list = re.findall(r"#(.+?)\'", sd)
    for r in re_list:
        v = eval(r)
        if type(v) is str:
            sd = sd.replace('#{}'.format(r), v)
        else:
            sd = sd.replace('\'#{}\''.format(r), str(v))

    return eval(sd)


def step_annotation(**param):
    """
    测试步骤方法注释 - 装饰器
    :param param: desc-测试步骤描述
    :return:
    """
    desc = param.get('desc')

    def decorate(callback):
        def fn(*args, **kwargs):
            client().message(desc).show(args[0])  # send(args[0], todo={'app:show': {'msg': desc}})
            r = callback(*args, **kwargs)
            return r

        return fn

    return decorate


"""
    通讯协议篇
"""


def meter(protocol: str):
    return Meter(protocol)


class Meter(object):
    def __init__(self, protocol):
        self._protocol = ProClazz(protocol)
        self._comm_addr = None
        self._operation = None
        self._element = None
        self._parameter = None
        self._addition = None
        self._security = None
        self._secs = 0
        self._chip_id = None
        self._frame = None
        self._parse = None
        self._func_module = None
        self._func = None
        self._expect_result = None
        self._func_parameter = {}

    def comm_addr(self, addr: str):
        self._comm_addr = addr
        return self

    def operation(self, op: str):
        self._operation = op
        return self

    def element(self, di):
        self._element = di
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def addition(self, addi=None):
        self._addition = addi
        return self

    def security(self, se=None):
        self._security = se
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def chip_id(self, ci):
        self._chip_id = ci
        return self

    def compare(self, data):
        self._func_module = data.get('module')
        self._func = data.get('code')
        self._expect_result = data.get('expect_result', None)
        self._func_parameter = data.get('parameter', {})

        return self

    def frame(self, hexStr: str):
        self._frame = hexStr
        return self

    def encode(self, context: Context):
        logger.info(
            '~ @PRO-ENCODE-> protocol:{} comm_addr:{} operation:{} element:{}'.format(self._protocol,
                                                                                      self._comm_addr,
                                                                                      self._operation,
                                                                                      self._element))

        self._element = _replace_global_result(context, self._element)
        if isinstance(self._parameter, dict):
            self._parameter = _replace(context, self._parameter)
            self._parameter = _replace_global_result(context, self._parameter)

        parse = pro.encode(func.to_dict(protocol=self._protocol.name, comm_addr=self._comm_addr,
                                        operation=self._operation, element=self._element,
                                        chip_id=self._chip_id, parameter=self._parameter,
                                        addition=self._addition, security=self._security,
                                        session_key=context.test_sn))
        logger.info('~ @PRO-ENCODE<- protocol:{} frame:{}'.format(self._protocol, parse.get('frame')))

        self._frame = parse.get('frame')
        return self._frame

    def decode(self, context: Context, index=0):
        # 异常判断 - 客户端返回结果
        if self._frame is None or len(self._frame) <= 0:
            # raise ClientError(self._frame)
            self._parse = '无响应帧'
            return

        logger.info('~ @PRO-DECODE-> protocol:{} frame:{}'.format(self._protocol, self._frame))
        data = pro.decode(
            func.to_dict(protocol=self._protocol.name, frame=self._frame, session_key=context.test_sn))
        logger.info('~ @PRO-DECODE<- protocol:{} parse:{}'.format(self._protocol, data))

        # 异常判断 - 协议服务返回结果
        if data.get('error') == 1:
            raise MeterOperationError(data.get('result'))

        # 分帧处理开始
        next_frame = data.get('next_frame', None)
        if next_frame is not None:
            result = send(context,
                          todo={'meter:comm': {'channel': context.case.steps[str(context.runtime.step)].get('channel'),
                                               'frame': next_frame}})
            self._frame = result.get('result')
            self.decode(context, index + 1)
        else:
            context.runtime.final_result = data.get('result')
        # 分帧处理结束

        if index == 0:
            self._parse = context.runtime.final_result
            self._flush(context)
            return self._parse

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='meter', op=self._operation
                                                                       , element=self._element
                                                                       , parameter=self._parameter,
                                                                       result=self._parse)})

    def sleep(self, context: Context):
        if isinstance(self._secs, int) and self._secs > 0:
            send(context, todo={'app:show': {'msg': '系统休眠{}秒, 等待电表操作完毕...'.format(self._secs)}})
            sleep(self._secs)

    def acv(self, context: Context):
        result = str(self._parse)
        if self._func is not None:
            if type(self._func_parameter) is dict:
                self._func_parameter['mode'] = context.mode.name
                self._func_parameter = _replace(context, self._func_parameter)
                self._func_parameter = _replace_global_result(context, self._func_parameter)
            try:
                if self._expect_result is None:
                    expect_result = context.runtime.sos[context.runtime.step - 1]
                else:
                    expect_result = context.runtime.sos[int(self._expect_result)]
            except:
                expect_result = None
            data = func.to_dict(result=self._parse, expect_result=expect_result, parameter=self._func_parameter)

            logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format(
                self._func_module, self._func, self._func_parameter))
            result = udm.handle(module='meter.{}'.format(self._func_module), function=self._func, data=data,
                                debug_url=context.debug_service_url.get('acd'))
            logger.info('~ @ACD<- module:{} function:{} result:{}'.format(self._func_module, self._func, result))

            context.runtime.sas[context.runtime.step] = result

        return result

    def exec(self, context: Context):
        self.encode(context)
        result = send(context,
                      todo={'meter:comm': {'channel': context.case.steps[str(context.runtime.step)].get('channel'),
                                           'frame': self._frame}})
        self._frame = result.get('result')
        self.decode(context)

        send(context, todo={'app:show': {'msg': self.acv(context)}})

        self.sleep(context)


"""
    加密机篇
"""


def encrypt(protocol: str):
    return Encryptor(protocol)


class Encryptor(object):
    def __init__(self, protocol):
        self._protocol = ProClazz(protocol)
        self._operation = None
        self._parameter = None
        self._result = None

    def operation(self, op: str):
        self._operation = op
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def handle(self, context: Context):
        try:
            if self._parameter is None:
                self._parameter = {}
            self._parameter = context.runtime.sos[context.runtime.step - 1]['result']
            self._parameter['session_key'] = context.test_sn
        except:
            pass

        logger.info(
            '~ @EM-> protocol:{} operation:{} parameter:{}'.format(self._protocol, self._operation, self._parameter))
        self._result = em.handle(self._protocol.name, self._operation, self._parameter)
        logger.info('~ @EM<- protocol:{} operation:{} result:{}'.format(self._protocol, self._operation, self._result))
        self._flush(context)

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='em', op=self._operation
                                                                       , parameter=self._parameter,
                                                                       result=self._result)})

    def acv(self, context: Context):
        data = func.to_dict(result=self._result)

        logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format(
            self._protocol.name, self._operation, self._parameter))
        result = udm.handle(module='em.{}'.format(self._protocol.name), function=self._operation,
                            data=data, debug_url=context.debug_service_url.get('acd'))
        logger.info('~ @ACD<- module:{} function:{} result:{}'.format(self._protocol.name, self._operation, result))

        context.runtime.sas[context.runtime.step] = result

        return result

    def exec(self, context: Context):
        self.handle(context)
        send(context, todo={'app:show': {'msg': self.acv(context)}})


"""
    表台篇
"""


def bench():
    return Bench()


class Bench(object):
    def __init__(self):
        self._operation = None
        self._parameter = None
        self._interval = None
        self._secs = 0
        self._result = None
        self._exec_times = 0
        self._func = None
        self._expect_result = None
        self._func_parameter = {}

    def operation(self, command: str):
        self._operation = command
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def interval(self, times):
        self._interval = times
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def compare(self, data):
        self._func = data.get('code')
        self._expect_result = data.get('expect_result', None)
        self._func_parameter = data.get('parameter', {})

        return self

    def encode(self, context: Context):
        logger.info(
            '~ @BENCH-> manufacture:{} operation:{} parameter:{}'.format(context.bench.manufacture, self._operation,
                                                                         self._parameter))

        if type(self._parameter) is dict:
            self._parameter = _replace_bench0(context, self._parameter)
            self._parameter = _replace_global_result(context, self._parameter)

    def decode(self, context: Context):
        logger.info('~ @BENCH<- manufacture:{} operation:{} result:{}'.format(context.bench.manufacture,
                                                                              self._operation, self._result))
        self._flush(context)

    def acv(self, context: Context):
        result = str(self._result)
        data = func.to_dict(result=self._result)
        if self._func is not None:
            if type(self._func_parameter) is dict:
                data['parameter'] = _replace_bench0(context, self._func_parameter)
            try:
                if self._expect_result is None:
                    data['expect_result'] = context.runtime.sos[context.runtime.step - 1]
                else:
                    data['expect_result'] = context.runtime.sos[int(self._expect_result)]
            except:
                pass

            logger.info('~ @ACD-> module:{} function:{} parameter:{}'.format('bench', self._func, data['parameter']))
            result = udm.handle(module='bench', function=self._func, data=data,
                                debug_url=context.debug_service_url.get('acd'))
            logger.info('~ @ACD<- module:{} function:{} result:{}'.format('bench', self._func, result))

            context.runtime.sas[context.runtime.step] = result

        return result

    def _flush(self, context: Context):
        context.runtime.sos.update({context.runtime.step: func.to_dict(obj='bench', op=self._operation
                                                                       , parameter=self._parameter,
                                                                       result=self._result)})

    def sleep(self, context: Context):
        if isinstance(self._secs, int) and self._secs > 0:
            send(context, todo={'app:show': {'msg': '系统休眠{}秒, 等待表台调整完毕...'.format(self._secs)}})
            sleep(self._secs)

    def _times(self, context: Context):
        self._interval = _replace_global_result(context, self._interval)
        if self._interval > 0:
            if context.runtime.loop_index == 0 or (context.runtime.loop_index + 1) % self._interval != 0:
                return False

        self._exec_times += 1
        return True

    def exec(self, context: Context):
        if context.meter.index == 0:
            if self._times(context):
                self.encode(context)
                self._result = send(context, todo={'bench:{}'.format(self._operation): self._parameter})
                self._result = self._result.get('result')
                self.decode(context)

                send(context, todo={'app:show': {'msg': self.acv(context)}})

                self.sleep(context)


"""
    测试终端篇
"""


def client():
    return App()


class App(object):
    def __init__(self):
        self._name = 'app'
        self._operation = None
        self._message = None
        self._parameter = None

    def operation(self, command: str):
        self._operation = command
        return self

    def message(self, msg):
        self._message = {'msg': msg}
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def show(self, context: Context, types=2):
        logger.info('~ @APP-> operation:{} message:{}'.format('show', self._message))
        send(context, todo={'{}:{}'.format(self._name, 'show'): self._message}, types=types)

    def error(self, context: Context, types=2):
        logger.info('~ @APP-> operation:{} message:{}'.format('error', self._message))
        send(context, todo={'{}:{}'.format(self._name, 'error'): self._message}, types=types)

    def exec(self, context: Context):
        logger.info('~ @APP-> operation:{} message:{}'.format(self._operation, self._message))
        send(context, todo={'{}:{}'.format(self._name, self._operation): self._message})


"""
    平台篇
"""


def _replace_context(context: Context, data: dict):
    sd = str(data)

    re_list = re.findall(r"#(.+?)\'", sd)
    for r in re_list:
        v = eval(r)
        if type(v) is str:
            sd = sd.replace('#{}'.format(r), v)
        else:
            sd = sd.replace('\'#{}\''.format(r), str(v))

    return eval(sd)


def _replace_global_result(context: Context, data):
    if data is None:
        return None
    if isinstance(data, int) or isinstance(data, float):
        return data
    if isinstance(data, str):
        sd = data
        if sd.find('~') < 0:
            return data
        else:
            index = sd.find('::')
            key = sd[index + 2:]

            if sd.find('global') >= 0:
                sd = 'context.runtime.glo.get("{}")'.format(key)
            if sd.find('result') >= 0:
                sd = 'context.runtime.sos[{}]["result"]'.format(key)
    else:
        sd = str(data)

    re_list = re.findall(r"~(.+?)\'", sd)
    for r in re_list:
        index = r.find('::')
        if index > 0:
            key = r[index + 2:]
            gl = r.find('global')
            if gl >= 0:
                sd = sd.replace('\'~{}\''.format(r), 'context.runtime.glo.get("{}")'.format(key))
            rt = r.find('result')
            if rt >= 0:
                sd = sd.replace('\'~{}\''.format(r), 'context.runtime.sos[{}]["result"]'.format(key))

    return eval(sd)


def ats():
    return ATS()


class ATS(object):
    def __init__(self):
        self._name = 'ats'
        self._operation = None
        self._parameter = None
        self._glo = None
        self._ctx = None
        self._jp = None
        self._secs = 0
        self._result = None

    def operation(self, command: str):
        self._operation = command
        return self

    def parameter(self, param=None):
        self._parameter = param
        return self

    def glo(self, g=None):
        self._glo = g
        return self

    def ctx(self, c=None):
        self._ctx = c
        return self

    def jp(self, j=None):
        self._jp = j
        return self

    def secs(self, s=0):
        self._secs = s
        return self

    def build_in(self, context: Context):
        if isinstance(self._operation, str) and len(self._operation) > 0:
            self._parameter = _replace_global_result(context, self._parameter)
            self._parameter = _replace_context(context, self._parameter)
            logger.info('~ @ATS:BUILD-IN-> operation:{} parameter:{}'.format(self._operation, self._parameter))
            try:
                self._result = build_in.handle(function=self._operation, data=self._parameter,
                                               debug_url=context.debug_service_url.get('build_in'))
                result = self._message(1)
                client().message(result).show(context)
            except Exception as e:
                result = self._message(2, str(e))
                client().message(result).show(context)

            context.runtime.sas[context.runtime.step] = result

    def _message(self, tag, err: str = None):
        """
        格式化结论
        :param tag:
        :param err:
        :return:
        """
        msg = []

        if tag == 1:
            msg.append('结论: {}.'.format('合格'))
        else:
            msg.append('结论: {}.'.format('代码发生异常'))

        msg.append('\r\n--------------------详细---------------------')

        if self._operation is not None:
            msg.append('\r\n内置方法: {}'.format(self._operation))
        if self._parameter is not None:
            msg.append('\r\n方法参数: {}'.format(self._parameter))
        if err is not None:
            msg.append('\r\n返回异常: {}'.format(err))
        else:
            if self._result is not None:
                msg.append('\r\n返回结果: {}'.format(self._result))

        return ''.join(msg) + '\r\n'

    def flush(self, context: Context):
        if isinstance(self._glo, dict) and len(self._glo) > 0:
            logger.info('~ @ATS:GLOBAL-> global:{} result:{}'.format(self._glo, self._result))
            for result, name in self._glo.items():
                context.runtime.glo[name] = self._result[result]

    def set(self, context: Context):
        if isinstance(self._ctx, dict) and len(self._ctx) > 0:
            logger.info('~ @ATS:SET-> context:{} result:{}'.format(self._ctx, self._result))
            for result, name in self._ctx.items():
                exec('{} = {}'.format(name, self._result[result]))

    def jump(self, context: Context):
        if isinstance(self._jp, dict) and len(self._jp) > 0:
            step = self._jp.get('step')
            times = self._jp.get('times')

            times = _replace_global_result(context, times)

            logger.info('~ @ATS:JUMP-> context:{} step:{} times:{}'.format(self._ctx, step, times))

            context.runtime.jump_times += 1

            if context.runtime.jump_times >= times:
                context.runtime.step_jump = False
                context.runtime.jump_times = 0
            else:
                context.runtime.step_jump = True
                context.runtime.step = step
                context.runtime.loop_sn = self._loop_sn(context)
                context.runtime.loop_index = 0

            client().message('步骤跳转[第{}次/共{}次] - 跳转并开始执行第{}步'.format(
                context.runtime.jump_times, times, step)).show(context)

    def _loop_sn(self, context: Context):
        loops = context.case.control.get('loops')
        if loops is None or type(loops) is not list or len(loops) <= 0:
            return 0

        bl = []
        for loop in loops:
            ranges = loop.get('range')
            s = ranges.split(':')
            bl.append(int(s[0]))
            bl.append(int(s[1]))

        step = self._jp.get('step')
        count = int(len(bl) / 2)
        for index in range(count):
            if index == (count - 1):
                return index

            y = bl[index * 2 + 2]

            if y > step:
                return index

        return 0

    def sleep(self):
        if isinstance(self._secs, int) and self._secs > 0:
            sleep(self._secs)

    def exec(self, context: Context):
        self.build_in(context)
        self.flush(context)
        self.set(context)
        self.jump(context)
        self.sleep()


if __name__ == '__main__':
    a = '98:90'
    print(a.split(':'))
