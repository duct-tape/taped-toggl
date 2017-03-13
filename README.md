# taped-toggl
Duct Taped Toggl.com API client

#Usage
```python
from tapedtoggl import TapedToggl, TapedTogglException
import datetime

toggl = TapedToggl('xxx') # xxx is api key
try:
    workspaces = toggl.get_workspaces()
    report = toggl.get_detailed_report(
        workspaces[0]['id'],
        since=datetime.date.today() - datetime.timedelta(days=6),
        until=datetime.date.today(),
    )
    print(report['data'])
except TapedTogglException as e:
    print('Error:', e.get_message(), ' http status code:', e.get_code())

```
