# encoding: utf-8

import sys
import re
import textwrap
from bs4 import BeautifulSoup
from workflow import Workflow, web


# remove whitespaces in string


def strip_spaces(string):
    return re.sub(re.compile(r'\s+'), ' ', string)


# parse li element to get meaning strings


def parse_meaning(li):
    m = {"title": "", "subtitle": ""}
    define = li.find("span", class_="def").string.encode("utf-8")
    m["title"] = define

    eg = li.find("p")
    # print (eg)
    if eg and eg.string:
        m["subtitle"] = eg.string.encode("utf-8")

    syns = li.find("p", class_="gray")
    if syns and syns.text:
        m["subtitle"] += "   " + strip_spaces(syns.text)

    return m


# helper to get dict structure


def get_dict(title, subtitle="", **kwargs):
    replace = {u"（": "(", u"）": ")", u"；": "; ", u"，": ","}
    for k in replace:
        title = title.replace(k, replace[k])
    base_dict = {"title": title, "subtitle": subtitle}
    for k in kwargs:
        base_dict[k] = kwargs[k]
    return base_dict


# helper to wrap title


def wrap_title(title, length=58):
    # 根据中文字符数量调整 wrap 长度
    utf8len = len(title.encode('utf-8'))
    l = len(title)
    chinses_count = (utf8len - l) / 2
    length -= chinses_count

    l = textwrap.wrap(title, length)
    for i, v in enumerate(l):
        if i > 0:
            l[i] = "     " + l[i]
    return l


# helper to add item to data list


def add_item(data, m_dict):
    l = wrap_title(m_dict["title"])
    # print(l)
    last = l.pop()
    for item in l:
        data.append(get_dict(item))
    data.append(get_dict(last, m_dict["subtitle"]))


# get data from web


def get_data(word):
    url = "http://dict.youdao.com/w/" + word
    res = web.get(url)
    if res.status_code != 200:
        return [{"title": u"网页无法打开", "subtitle": ""}]
    else:
        # soup = BeautifulSoup(res.text, "html.parser")
        # res = soup.select("div#results-contents")[0]   #
        # 部分页面用这个之后英文释义找不到，所以下面直接全文解析
        res = BeautifulSoup(res.text, "html.parser")
        if res.find("div", class_="error-wrapper"):
            return [{"title": u"词语不存在", "subtitle": ""}]
        else:
            data = []
            # 发音
            pronounces = res.select('span.pronounce .phonetic')
            pstring = ""
            for p in pronounces:
                parent = p.find_parent()
                pstring += strip_spaces(parent.text)

            # addition
            addition = res.select('#phrsListTab p.additional')
            if addition:
                data.append(get_dict(pstring, strip_spaces(
                    addition[0].string), arg=word))
            elif pstring:
                data.append(get_dict(pstring, arg=word))

            # 中文释义
            chinese = res.select("#phrsListTab li")
            for m in chinese:
                add_item(data, get_dict(m.string))

            # 英文释义
            english = res.find("div", id="tEETrans")
            if english:
                english = english.find('ul')
                for lev1 in english.find_all('li', recursive=False):
                    # pos.
                    pos = lev1.find("span", class_="pos")
                    pos_str = ""
                    if pos:
                        pos_str = pos.string

                    # meanings
                    ul = lev1.find("ul")
                    if ul:
                        j = 1
                        for lev2 in ul.find_all("li", recursive=False):
                            m_dict = parse_meaning(lev2)
                            m_dict["title"] = str(j) + ".  " + m_dict["title"]
                            if j == 1:
                                m_dict["title"] = pos_str + " " + m_dict["title"]
                            add_item(data, m_dict)
                            j += 1
                    else:
                        m_dict = parse_meaning(lev1)
                        m_dict["title"] = pos_str + "  " + m_dict["title"]
                        add_item(data, m_dict)
            else:
                data.append(get_dict(u"打开网页", "", arg=url))

            return data


def get_results(wf, word):
    # data = wf.cached_data(word, max_age=86400 * 20)
    data = wf.cached_data(word, max_age=1)
    if data is None:
        data = get_data(word)
        wf.cache_data(word, data)
    for line in data:
        if line.get("arg"):
            wf.add_item(line["title"], line["subtitle"],
                        valid=True, arg=line["arg"])
        else:
            wf.add_item(line["title"], line["subtitle"])


def main(wf):
    args = wf.args

    if len(args) < 1:
        wf.add_item(u'请输入查询词语')
    elif not args[0].strip():
        wf.add_item(u'请输入查询词语')
    else:
        get_results(wf, args[0].strip())
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
