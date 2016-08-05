# encoding: utf-8

import subprocess
import webbrowser
import sys
import os
import youdao
from workflow import Workflow, web

def downloadAudio(wf, word):
    BriURL = "http://dict.youdao.com/dictvoice?audio=" + word + "&type=1"
    AmeURL = "http://dict.youdao.com/dictvoice?audio=" + word + "&type=2"
    dirname = wf.cachedir + "/"

    res = web.get(BriURL)
    if res.status_code == 200:
        res.save_to_path(dirname + word + ".bri")
    res = web.get(AmeURL)
    if res.status_code == 200:
        res.save_to_path(dirname + word + ".ame")

def main(wf):
    args = wf.args

    if args[0].startswith("http"):
        webbrowser.open(args[0])
    else:
        audioPath = wf.cachedir + "/" + args[0] + "." + args[1]
        if not os.path.exists(audioPath):
            downloadAudio(wf, args[0])
        subprocess.call(["afplay", audioPath])

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))