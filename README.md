# taped-toggl
Duct Taped Toggl.com API client

#Usage
```python
from tapedtoggl import tapedtoggl
import datetime

toggl = tapedtoggl.TapedToggl('xxx') # xxx is api key
workspaces = toggl.get_workspaces()
if workspaces is not None:
    report = toggl.get_detailed_report(
        workspaces[0]['id'],
        since=datetime.date.today() - datetime.timedelta(days=6),
        until=datetime.date.today(),
    )
    print(report['data'])
else:
    print('Error:', toggl.error)

```
