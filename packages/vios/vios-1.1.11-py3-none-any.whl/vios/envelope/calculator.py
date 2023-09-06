"""所有指令都会由此模块进行预处理, 如采样、失真、串扰等, 
并送入设备执行(见device模块)
"""

import numpy as np
from qlisp.kernel_utils import sample_waveform
from waveforms import Waveform, wave_eval


def calculate(step: str, target: str, cmd: list, targets: dict = {}):
    """指令的预处理

    Args:
        step (str): 步骤名, 如main/step1/...
        target (str): 设备通道, 如AWG.CH1.Offset
        cmd (list): 操作指令, 格式为(操作类型, 值, 单位, kwds). 其中
            操作类型包括WRITE/READ/WAIT, kwds见assembler.preprocess说明. 

    Returns:
        tuple: 预处理结果
    
    >>> calculate('main', 'AWG.CH1.Waveform',('WRITE',square(100e-6),'au',{'calibration':{}}))
    """
    ctype, value, unit, kwds = cmd

    line = {}

    if ctype != 'WRITE':
        return (step, target, cmd), line

    if isinstance(value, str):
        try:
            func = wave_eval(value)
        except SyntaxError as e:
            func = value
    else:
        func = value

    delay = 0

    if isinstance(func, Waveform):
        if target.startswith(tuple(kwds.get('filter', ['zzzzz']))):
            support_waveform_object = True
        else:
            support_waveform_object = False
        ch = kwds['target'].split('.')[-1]
        delay = kwds['calibration'][ch].get('delay', 0)
        cmd[1] = sample_waveform(func, kwds['calibration'][ch],
                                 sample_rate=kwds['srate'],
                                 start=0, stop=kwds['LEN'],
                                 support_waveform_object=support_waveform_object)
    else:
        cmd[1] = func

    cmd[-1] = {'sid': kwds['sid'], 'autokeep': kwds['autokeep'],
               'target': kwds['target'], 'srate': kwds['srate']}
    
    try:
        line = preview(target, cmd, targets, delay)
    except Exception as e:
        print('>'*30, '  failed to calculate waveform', e)

    return (step, target, cmd), line


def preview(target, cmd: dict, targets: dict = {}, delay: float = 0.0):
    """预览进入设备的波形, 可由etc.preview关闭. 
    # NOTE: 耗时操作, 慎用！！！

    Args:
        cmd (list): calculate计算返回的cmd
    """
    if not targets['filter']:
        return {}

    if cmd[-1]['target'].split('.')[0] not in targets['filter'] or cmd[-1]['sid'] < 0:
        return {}
    if target.endswith('Waveform'):
        val = cmd[1]
        if isinstance(val, Waveform):
            val = val.sample()
        # val = np.random.random((1024000))
        srate = cmd[-1]['srate']
        xt = np.arange(len(val))/srate
        t1, t2 = targets['range']
        xr = slice(int(t1*srate), int(t2*srate))
        return {cmd[-1]['target']: {'data': (xt[xr]-delay, val[xr])}}
    return {}
                


if __name__ == "__main__":
    import doctest
    doctest.testmod()