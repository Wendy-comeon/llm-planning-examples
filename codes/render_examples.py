"""从公开样例生成说明页和任务依赖图，只使用 Python 标准库。"""
from collections import defaultdict
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def task_name(value):
    return '任务' + value.removeprefix('T')


def part_name(value):
    return '部件' + value.removeprefix('part')


def task_order(value):
    return int(value.removeprefix('T'))


def graph_layers(case):
    """检查公开数据的引用关系，并按依赖关系排列节点。"""
    tasks = case['result']['tasks']
    ids = [task['id'] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError('子任务编号重复')
    parts = {part['id'] for part in case['input']['parts']}
    connections = {frozenset(pair) for pair in case['input']['connections']}
    if any(part not in parts for pair in connections for part in pair):
        raise ValueError('连接关系包含未定义的部件')
    for task in tasks:
        if not task['robots'] or frozenset(task['parts']) not in connections:
            raise ValueError('子任务缺少分配，或引用了未定义的连接关系')
    parents = {tid: [] for tid in ids}
    for start, end in case['result']['dependencies']:
        if start not in parents or end not in parents:
            raise ValueError('依赖边引用了未定义的子任务')
        parents[end].append(start)
    levels = {}
    while len(levels) < len(ids):
        ready = [tid for tid in ids if tid not in levels and all(p in levels for p in parents[tid])]
        if not ready:
            raise ValueError('任务依赖图包含环')
        for tid in ready:
            levels[tid] = max((levels[p] + 1 for p in parents[tid]), default=0)
    layers = defaultdict(list)
    for tid in sorted(ids, key=task_order):
        layers[levels[tid]].append(tid)
    return levels, layers


def render_svg(case):
    levels, layers = graph_layers(case)
    tasks = {task['id']: task for task in case['result']['tasks']}
    width = max(660, max(map(len, layers.values())) * 226 + 56)
    height = 142 + len(layers) * 116
    node_width, node_height = 194, 78
    positions = {}
    for level, ids in layers.items():
        for index, tid in enumerate(ids):
            x = width / 2 + (index - (len(ids) - 1) / 2) * 226
            positions[tid] = (x, 119 + level * 116)
    status = '修复后通过检验' if case['result']['repair_applied'] else '初始分配通过检验'
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(case["title"])}：任务依赖与最终分配</title>',
        '<desc id="desc">箭头从前置任务指向后续任务。节点列出连接部件及匿名机器人编号。</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#8595a9"/></marker></defs>',
        '<style>text{font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif}</style>',
        f'<rect width="{width}" height="{height}" rx="16" fill="#f5f8fc"/>',
        f'<text x="28" y="38" font-size="23" font-weight="600" fill="#17304e">{escape(case["title"])}</text>',
        f'<text x="28" y="67" font-size="14" fill="#53667d">{len(tasks)} 个子任务 · {escape(case["feature"])} · {status}</text>',
    ]
    for start, end in case['result']['dependencies']:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        y1 += node_height
        if levels[end] - levels[start] > 1:
            side = width - 20 if x1 >= width / 2 else 20
            d = f'M{x1},{y1} L{x1},{y1 + 13} L{side},{y1 + 13} L{side},{y2 - 18} L{x2},{y2 - 18} L{x2},{y2 - 5}'
        else:
            middle = (y1 + y2) / 2
            d = f'M{x1},{y1} C{x1},{middle} {x2},{middle} {x2},{y2 - 5}'
        svg.append(f'<path d="{d}" fill="none" stroke="#8595a9" stroke-width="1.8" marker-end="url(#arrow)"/>')
    for tid, (x, y) in positions.items():
        task = tasks[tid]
        pair = ' — '.join(part_name(p) for p in task['parts'])
        robots = '、'.join(task['robots']).replace('机器人', '')
        svg.extend([
            f'<rect x="{x - node_width / 2}" y="{y}" width="{node_width}" height="{node_height}" rx="9" fill="#fff" stroke="#c5d3e5"/>',
            f'<text x="{x}" y="{y + 23}" text-anchor="middle" font-size="16" font-weight="600" fill="#17304e">{task_name(tid)}</text>',
            f'<text x="{x}" y="{y + 46}" text-anchor="middle" font-size="14" fill="#53667d">{pair}</text>',
            f'<text x="{x}" y="{y + 66}" text-anchor="middle" font-size="13" fill="#245b91">机器人：{robots}</text>',
        ])
    svg.append(f'<text x="28" y="{height - 18}" font-size="12" fill="#64758a">箭头表示任务依赖；图中位置不表示执行时间或机器人轨迹。</text>')
    svg.append('</svg>')
    return '\n'.join(svg) + '\n'


def render_markdown(case):
    cid = case['id']
    repair = case['result']['repair_applied']
    status = '初始分配未通过检验，经修复后通过。' if repair else '初始分配直接通过检验。'
    rows = [
        f'# {case["title"]}', '', '[返回项目说明](../README.md)', '',
        f'原始任务编号：`{case["source_task"]}`。本例展示{case["feature"]}，共 {len(case["result"]["tasks"])} 个子任务。', '',
        '## 任务输入', '', f'任务指令：{case["input"]["instruction"]}。', '',
        '| 部件 | 几何类别 |', '| --- | --- |',
    ]
    rows.extend(f'| {part_name(p["id"])} | {p["geometry"]} |' for p in case['input']['parts'])
    rows.extend(['', '目标连接关系：' + '；'.join('与'.join(part_name(p) for p in pair) for pair in case['input']['connections']) + '。', '',
                 '输入仅展示基本部件信息与连接关系，实验使用的完整属性和执行条件未包含在本页。', '',
                 '## 任务依赖与最终分配', '', f'![任务依赖与最终分配](../figures/{cid}.svg)', '',
                 '| 子任务 | 连接操作 | 分配的机器人 |', '| --- | --- | --- |'])
    rows.extend(f'| {task_name(t["id"])} | 连接' + '与'.join(part_name(p) for p in t['parts']) + f' | {"、".join(t["robots"])} |' for t in case['result']['tasks'])
    rows.extend(['', '目标连接关系描述装配对象的连接要求，上表展示最终规划中的连接子任务，二者数量不必相同。', '',
                 '## 实验结果', '', f'本次记录中的任务分解和完整规划均成功。{status}', '',
                 '机器人编号已在本例内重新命名；不同样例中的同名机器人不表示同一个执行体。最终可行性来自原实验检验记录，本页不包含完整约束配置或内部修复过程。', '',
                 f'[查看结构化样例数据](../examples/{cid}.json)', ''])
    return '\n'.join(rows)


def main():
    files = sorted((ROOT / 'examples').glob('*.json'))
    if not files:
        raise SystemExit('未找到样例数据')
    for folder in ['docs', 'figures']:
        (ROOT / folder).mkdir(exist_ok=True)
    for path in files:
        case = json.loads(path.read_text(encoding='utf-8'))
        if case['id'] != path.stem:
            raise ValueError('样例编号与文件名不一致')
        (ROOT / 'figures' / f'{path.stem}.svg').write_text(render_svg(case), encoding='utf-8')
        (ROOT / 'docs' / f'{path.stem}.md').write_text(render_markdown(case), encoding='utf-8')
        print(f'已生成：{case["title"]}')


if __name__ == '__main__':
    main()
