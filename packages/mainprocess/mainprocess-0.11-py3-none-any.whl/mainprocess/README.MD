# Runs EXE-files as independent main processes

## pip install mainprocess


```python
from mainprocess import mainprocess
# cmd.exe and notepad.exe won't be subprocesses of python.exe
# If you close python.exe, they won't be closed automatically
mainprocess(["cmd.exe"])
mainprocess(["notepad.exe", r"C:\ipconfigdata.txt"])
```
