import shutil
import subprocess
import os
from shortpath83 import convert_path_in_string

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
creationflags = subprocess.CREATE_NO_WINDOW
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}
def mainprocess(cmd,**kwargs):
    exists=False
    if isinstance(cmd, str):
        cmd = [cmd]
    if not os.path.exists(cmd[0]):
        _exefile = shutil.which(cmd[0])
        if _exefile:
            cmd[0] = _exefile
    else:
        exists=True
    exefile = cmd[0]
    if exists:
        exefile = exefile.strip().strip('"\' ').strip()
        exefile = os.path.normpath(exefile)
        exefile = convert_path_in_string(exefile)
    try:
        arguments = cmd[1:]
    except Exception:
        arguments = []

    cwd = os.path.dirname(exefile)
    if not cwd or not os.path.exists(str(cwd)):
        cwd = os.getcwd()
    args_command = " ".join(arguments).strip()
    args_command = convert_path_in_string(args_command)
    wholecommand = f'start /min "" {exefile} {args_command}'
    print(f'Executing: {wholecommand}')
    p = subprocess.Popen(wholecommand, cwd=cwd, env=os.environ.copy(), shell=True,**invisibledict,**kwargs)
    return p
