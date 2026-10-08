#!/usr/bin/env python3
"""给《碧玺传》各篇排定时发布日期（可选工具）。

默认只“预演”，打印排期，不改任何文件；加 --apply 才真正写入。
写入时会把每篇的 date 改成排定的时间，并把 draft 改成 false。
date 在将来的文章，网站不会显示；每天北京时间 08:07 的定时任务重新生成网站时，
已经到点的文章就会自动上线（前提：改动已合并到 main 分支）。

例子：
  python3 scripts/bixi_schedule.py --start 2026-10-20            # 预演：从 10 月 20 日起每天一篇，08:00
  python3 scripts/bixi_schedule.py --start 2026-10-20 --per-day 2 --apply
  python3 scripts/bixi_schedule.py --start 2026-10-20 --first 1 --last 13 --apply   # 只排卷一（含戒指碎片感知）
"""
import argparse, datetime, glob, os, re

ap = argparse.ArgumentParser()
ap.add_argument('--start', required=True, help='第一篇的发布日期，YYYY-MM-DD（北京时间）')
ap.add_argument('--time', default='08:00', help='每天的发布时间，默认 08:00（需早于 08:07 的定时任务）')
ap.add_argument('--per-day', type=int, default=1, help='每天发几篇，默认 1')
ap.add_argument('--first', type=int, default=1, help='从第几篇开始排（按文件名序号 01–79）')
ap.add_argument('--last', type=int, default=999, help='排到第几篇为止')
ap.add_argument('--apply', action='store_true', help='真正写入文件（不加则只预演）')
a = ap.parse_args()

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content', 'posts', 'bixi')
files = sorted(glob.glob(os.path.join(root, '[0-9][0-9]-*.md')))
files = [f for f in files if a.first <= int(os.path.basename(f)[:2]) <= a.last]
hh, mm = map(int, a.time.split(':'))
start = datetime.datetime.strptime(a.start, '%Y-%m-%d').replace(hour=hh, minute=mm)
for i, f in enumerate(files):
    day, slot = divmod(i, a.per_day)
    d = start + datetime.timedelta(days=day, minutes=slot)  # 同一天的几篇相隔 1 分钟，保证顺序
    ds = d.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    text = open(f, encoding='utf-8').read()
    title = re.search(r'^title: "?(.*?)"?$', text, re.M).group(1)
    print(ds, os.path.basename(f), title)
    if a.apply:
        text = re.sub(r'^date: .*$', 'date: ' + ds, text, count=1, flags=re.M)
        text = re.sub(r'^draft: .*$', 'draft: false', text, count=1, flags=re.M)
        open(f, 'w', encoding='utf-8').write(text)
print(('已写入 ' if a.apply else '预演（未改文件）：') + f'{len(files)} 篇')
