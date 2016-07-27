  # encoding: utf-8

from workflow import Workflow

wf = Workflow()
wf.clear_cache()
wf.add_item(u'清除完毕')
wf.send_feedback();