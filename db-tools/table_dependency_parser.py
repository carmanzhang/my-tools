# encoding: utf-8
import json
import os
import re

import matplotlib.pyplot as plt
import networkx as nx

scan_sql_path = r'./database'
regenerated_table = 'mag.mag_pm_id'
regenerate_sql_path = os.path.join(scan_sql_path, 'regenerate.sql')


def extract_first_string_after_fixed_string_using_re(content: str, fixed_str: str):
    match = re.findall(fixed_str + ' (\\w+\.\\w+)', content)
    if len(match) == 0:
        match = re.findall(fixed_str.upper() + ' (\\w+\.\\w+)', content)
    return match


def extract_first_string_after_fixed_string(content: str, fixed_str: str):
    if not fixed_str in content:
        return ''
    fixed_str += ' '  # 增加一个空格
    sub_content = content[content.index(fixed_str) + len(fixed_str):]
    if ' ' in sub_content:
        return sub_content[:sub_content.index(' ')]
    else:
        return sub_content


def split_sqls(lines: list):
    sqls = '\n'.join(lines)
    sql_list = sqls.split(';\n')
    table_name_runnable_sql_mapping = {}
    table_dependencies = []
    for sql in sql_list:
        print('-' * 200)
        runnable_sql = sql + ';'
        # print(runnable_sql)
        sql = re.sub(' +', ' ', sql.replace('\n', ' '))  # 多个空格合并一个
        # 过滤掉 if not exists
        sql = sql.replace('if not exists', '').replace('if exists', '')
        sql = sql.replace('IF NOT EXISTS', '').replace('IF EXISTS', '')
        sql = re.sub(' +', ' ', sql)  # 多个空格合并一个
        # create_table_name = extract_first_string_after_fixed_string(sql, 'view')
        # from_table_name = extract_first_string_after_fixed_string(sql, 'from')
        create_table_mv = extract_first_string_after_fixed_string_using_re(sql, 'create materialized view')
        create_table_v = extract_first_string_after_fixed_string_using_re(sql, 'create view')
        create_table_t = extract_first_string_after_fixed_string_using_re(sql, 'create table')
        from_table_name = extract_first_string_after_fixed_string_using_re(sql, 'from')
        from_join_table_name = extract_first_string_after_fixed_string_using_re(sql, 'join')
        from_table_name = list(set(from_table_name + from_join_table_name))

        assert len(create_table_mv) + len(create_table_v) + len(create_table_t) <= 1
        create_table = create_table_mv[0] if len(create_table_mv) > 0 else (
            create_table_v[0] if len(create_table_v) > 0 else (
                create_table_t[0] if len(create_table_t) > 0 else None))

        print({'create_table': create_table, 'create_table_mv': create_table_mv, 'create_table_v': create_table_v,
               'create_table_t': create_table_t, 'from_table_name': from_table_name})

        if create_table is None:
            continue

        # 建表语句与runnable_sql进行对应
        table_name_runnable_sql_mapping[create_table] = runnable_sql
        # 保存表之间的依赖关系
        for tn in from_table_name:
            table_dependencies.append((tn, create_table))

    return table_name_runnable_sql_mapping, table_dependencies


def remove_comment(f):
    clean_lines = []
    with open(f, 'r', encoding='utf-8') as fr:
        for line in fr.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if '--' in line:
                line = line[:line.index('--')]
            if len(line) == 0:
                continue
            clean_lines.append(line)
    return clean_lines


table_name_runnable_sql_mappings = {}
table_dependencies = []
files = os.listdir(scan_sql_path)
for file in files:
    if os.path.isdir(file):
        continue
    if not file.endswith('.sql'):
        continue

    f = os.path.join(scan_sql_path, file)
    print(f)
    lines = remove_comment(f)
    mappings, dependency = split_sqls(lines)
    table_name_runnable_sql_mappings.update(mappings)
    table_dependencies.extend(dependency)

print(
    json.dumps({'table_name_runnable_sql_mapping': table_name_runnable_sql_mappings,
                'table_dependencies': table_dependencies}))

# 可视化依赖图
G = nx.DiGraph()
for dep in table_dependencies:
    # start = dep[0][dep[0].index('.') + 1:]
    # end = dep[1][dep[1].index('.') + 1:]
    # G.add_edge(start, end)
    G.add_edge(dep[0], dep[1])

# __all__ = ['bipartite_layout',
#            'circular_layout',
#            'kamada_kawai_layout',
#            'random_layout',
#            'rescale_layout',
#            'shell_layout',
#            'spring_layout',
#            'spectral_layout',
#            'planar_layout',
#            'fruchterman_reingold_layout',
#            'spiral_layout']
pos = nx.circular_layout(G)

nx.draw_networkx(G, pos, node_size=10, font_size=4,
                 width=0.3)  # ,node_color=values,  edge_color=edge_colors, edge_cmap=plt.cm.Reds
plt.savefig('table-relations.png', format="PNG", dpi=1000)
plt.show()  # block = False

specific_deps = list(nx.bfs_edges(G, regenerated_table))
print(specific_deps)

regenerated_tables_tmp = [n for a in specific_deps for n in a]  # 二维变1维度
regenerated_table_order = list(set(regenerated_tables_tmp))
regenerated_table_order.sort(key=regenerated_tables_tmp.index)

print(regenerated_table_order)  # [0, 3, 2, 1, 9, 8, 7]
drop_table_order = regenerated_table_order[::-1]

drop_table_order_sqls = '\n'.join(['drop table if exists ' + t + ';' for t in drop_table_order])
regenerated_table_order_sqls = ('--' * 40).join(
    ['\n' + table_name_runnable_sql_mappings[t] + '\n' for t in regenerated_table_order])

with open(regenerate_sql_path, 'w', encoding='utf-8') as fw:
    fw.write(drop_table_order_sqls)
    fw.write('\n\n')
    fw.write(regenerated_table_order_sqls)
