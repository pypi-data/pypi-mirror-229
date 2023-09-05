import os
import threading

import gevent
import pytest

from datetime import datetime

from ats_base.common import func
from ats_base.service import mm, db

from ats_case.common.enum import WorkMode


def run(**kwargs):
    try:
        mode = WorkMode(kwargs.get('mode'))
        if mode == WorkMode.FORMAL:
            pt = FormalMode(kwargs)
        else:
            pt = DebugMode(kwargs)
        pt.run()
    except:
        pass


class ExecMode(object):
    def __init__(self, data: dict):
        self._data = data
        self._username = self._data.get('tester', {}).get('username', '')
        self._now = datetime.now().strftime('%y%m%d%H%M%S%f')
        self._sn = self._username.upper() + self._now

        self._init()

    def _init(self):
        pass

    def run(self):
        pass

    def _flush(self):
        mm.Dict.put('test:log', self._sn, self._data)

    def _build(self, work_mode: WorkMode, code: str = None):
        if code is None:
            code = 'case'

        user_dir = func.makeDir(func.project_dir(), 'testcase', work_mode.value.lower(), self._username)
        template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'testcase_v1.tmp')
        script_file = os.path.join(user_dir, 'test_{}.py'.format(code))

        with open(template_file, 'r', encoding='UTF-8') as file:
            content = file.read()
            content = content.replace('{script}', code.upper())
        with open(script_file, 'w', encoding='UTF-8') as file:
            file.write(content)

        return script_file


class FormalMode(ExecMode):
    def _init(self):
        sn = self._data.get('test_sn')
        if sn is None or len(sn) == 0:
            self._flush()
            self._save()
        else:  # 断点续测
            self._sn = sn
            self._data['renew'] = 1
            self._data = mm.Dict.get('test:log', self._sn)

        self._cases = self._data.get('usercases', [])
        self.meters = self._data.get('meters', [])

    def _save(self):
        self._data['start_time'] = func.sys_current_time()
        # db.save('test:log', **self._data)

    def run(self):
        # while self._cases:
        for id_v in self._cases:
            case = self._get_case(id_v)

            case_task = self.CaseTask(self, case)
            case_task.start()
            case_task.join()

    class CaseTask(threading.Thread):
        def __init__(self, parent, case):
            super(FormalMode.CaseTask, self).__init__()
            self._parent = parent
            self._case = case

        def run(self):
            gs = []
            for i in range(len(self._parent.meters)):
                # i = 0 执行操作表台 传入参数index
                self._parent.meters[i]['index'] = i
                gs.append(gevent.spawn(self._parent.exec, self._parent.handle(case=self._case,
                                                                              meter=self._parent.meters[i])))

            gevent.joinall(gs)

    def handle(self, case, meter):
        self._data['usercase'] = case
        self._data['meter'] = meter

        test_sn = '{}:{}'.format(self._sn, meter['pos'])
        mm.Dict.put('test:log', test_sn, self._data)

        return test_sn

    def _get_case(self, id_v: str):
        idv = id_v.split(':')
        case_id = idv[0]
        version = idv[1]

        return db.query('view:case:version', id=case_id, version=version)

    def exec(self, test_sn):
        pytest.main(["-sv", self._build(WorkMode.FORMAL), '--sn={}'.format(test_sn)])


class DebugMode(ExecMode):
    def _init(self):
        self._flush()

    def run(self):
        pytest.main(["-sv", self._build(WorkMode.DEBUG), '--sn={}'.format(self._sn)])
