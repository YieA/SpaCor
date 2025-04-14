'''
    生成自然查询语句
'''

import pandas as pd
import random
import re
import csv
import os
import sys
sys.stdout.flush()
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
    spatial_relations: 存储数据库各表信息
                —————————————————————————————————————————
                | id | name | GeoData | place_name_attr |
                —————————————————————————————————————————
    places: 存储各表内实体, 其中rel_id为外键, 对应spatial_relations中的id
                —————————————————
                | rel_id | name | 
                —————————————————
    QueryTemplate: 存储查询语句模板
                —————————————————————————
                | cat | template | type |
                —————————————————————————
"""
base_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录

spatial_relations_path = os.path.join(base_path, 'knowledge_base', 'spatial_relations.csv')
geo_entities_path = os.path.join(base_path, 'knowledge_base', 'places.csv')
template_path = os.path.join(base_path, 'knowledge_base', 'QueryTemplate.csv')
type_path = os.path.join(base_path, 'knowledge_base', 'type.csv')


spatial_relations = pd.read_csv(spatial_relations_path)
geo_entities = pd.read_csv(geo_entities_path)
template = pd.read_csv(template_path)
type_file = pd.read_csv(type_path)

# spatial_relations = pd.read_csv('SpaCor\knowledge_base\spatial_relations.csv')
# geo_entities = pd.read_csv('SpaCor/knowledge_base/places.csv')
# template = pd.read_csv('SpaCor/knowledge_base/QueryTemplate.csv')
# type_file = pd.read_csv('SpaCor/knowledge_base/type.csv')

# 从 spatial_relations 中分别选取属性为line、point、region的元组    关系
line_relation = spatial_relations[spatial_relations['GeoData'] == 'line']
point_relation = spatial_relations[spatial_relations['GeoData'] == 'point']
region_relation = spatial_relations[spatial_relations['GeoData'] == 'region']
# 从 places 中分别选择出属性为line、point、region的元组             实体
line_entities = geo_entities[geo_entities['rel_id'].isin(line_relation['id'])]
point_entities = geo_entities[geo_entities['rel_id'].isin(point_relation['id'])]
region_entities = geo_entities[geo_entities['rel_id'].isin(region_relation['id'])]



"""
    获取 place1 和 place2 的替换词
        place1 从spatial_relations中根据类型随机选取一个
        place2 从places中根据类型随机选取一个
"""
def place_replace_word(type1, type2):
    # place1
    # 随机选取一个 GeoData = 'line'/'point'/region 的关系
    if type1 == 'LINE':
        random_relation = line_relation.sample().iloc[0]['name']
    elif type1 == 'POINT':        
        random_relation = point_relation.sample().iloc[0]['name']   
    else:
        random_relation = region_relation.sample().iloc[0]['name']       
    # place2
    # 随机选取一个 GeoData = 'line'/'point'/region 的实体
    if type2 == 'LINE':
        random_entity = line_entities.sample().iloc[0]['name']      
    elif type2 == 'POINT':   
        random_entity = point_entities.sample().iloc[0]['name']        
    else:
        random_entity = region_entities.sample().iloc[0]['name']  

    return random_relation, random_entity 
# 通过传入一个类型词语，传回一个关系及其实体
def place_replace_word1(type):
    if type == 'LINE':
        random_relation = line_relation.sample(n=1)
        relation_id = random_relation['id'].iloc[0]
        related_places = geo_entities[geo_entities['rel_id'] == relation_id]
        random_entity = related_places.sample(n=1)
    elif type == 'REGION':
        random_relation = region_relation.sample(n=1)
        relation_id = random_relation['id'].iloc[0]
        related_places = geo_entities[geo_entities['rel_id'] == relation_id]
        random_entity = related_places.sample(n=1)
    else:
        random_relation = point_relation.sample(n=1)
        relation_id = random_relation['id'].iloc[0]
        related_places = geo_entities[geo_entities['rel_id'] == relation_id]
        random_entity = related_places.sample(n=1)
    return random_relation['name'].iloc[0], random_entity['name'].iloc[0]

# print(place_replace_word1('REGION'))

"""
    根据类型随机选择模板并返回
"""
def catch_template(type):
    # 从QueryTemplate中选择出不同类型的Template
    if type == 'Range Query':
        query_templates = template[template['cat'] == 'Range Query']
    elif type == 'Nearest Neighbor Query':
        query_templates = template[template['cat'] == 'Nearest Neighbor Query']
    elif type == 'Basic-area Query':
        query_templates = template[template['cat'] == 'Basic-area Query']
    elif type == 'Basic-length Query':
        query_templates = template[template['cat'] == 'Basic-length Query']
    elif type == 'Basic-distance Query':
        query_templates = template[template['cat'] == 'Basic-distance Query']
    elif type == 'Basic-direction Query':
        query_templates = template[template['cat'] == 'Basic-direction Query']
    elif type == 'Aggregation-count Query':
        query_templates = template[template['cat'] == 'Aggregation-count Query']
    elif type == 'Aggregation-sum Query':
        query_templates = template[template['cat'] == 'Aggregation-sum Query']
    elif type == 'Aggregation-max Query':
        query_templates = template[template['cat'] == 'Aggregation-max Query']
    elif type == 'Distance Join Query':
        query_templates = template[template['cat'] == 'Distance Join Query']
    elif type == 'Spatial Join Query':
        query_templates = template[template['cat'] == 'Spatial Join Query']
    else:
        print("Error: 不存在", type, "类型！")
        return
    # 随机选取一个自然语言查询模板
    random_template = query_templates.sample().iloc[0]
    return random_template['type'], random_template['template']

"""
    去除's
"""
def remove_s(word):
    if "'s" in word:
        word_without_apostrophe = word.replace("'s", "")
        return word_without_apostrophe
    else:
        return word
    
"""
    替换包含's的单词
"""
def replace_s(word_repalce, word):
    if "'s" in word_repalce:
        parts = word_repalce.split("'")
        parts[0] = word
        return "'".join(parts)
    else:
        return word

# 测试函数
# print(replace_s("LINE", "bbb"))


"""
    根据获取的模板、替换词进行语料生成
    What are the X nearest LINE to LINE?  -->  What are the two nearest Rehwiese to Landstrassen?
"""
def replace_template(type):
    # 获取模板
    query_num, query_template = catch_template(type)
    # print(query_template)
    # 判断是否有距离表示 X， 有的话替换
    X_english = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five"
    }
    X_value = random.randint(1, 5)
    if 'X' in query_template:
        # query_template = query_template.replace('X', X_english[X_value])
        query_template = query_template.replace('X', str(X_value))
    
    # 定位类型词位置
    # words = query_template.split()
    words = re.findall(r'\w+|[^\w\s]', query_template)
    # print(words)
    uppercase_word_positions = []
    for index, word in enumerate(words):
        # if (word.isupper() and word != "I") or (word.endswith("'s") and word not in ("What's", "is", "what's")):
        if word.isupper() and word != "I":
            uppercase_word_positions.append(index)
    # print(uppercase_word_positions)

    # NLQ内部的关系和实体
    corpus_entities = []
    corpus_relations = []

    if type in ('Range Query', 'Nearest Neighbor Query'):        
        if len(uppercase_word_positions) != 2:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        # # 获取替换词
        # if (words[uppercase_word_positions[0]] in ('POINT', 'LINE', 'REGION') and \
        #     words[uppercase_word_positions[1]] in ('POINT', 'LINE', 'REGION')):
        #     place1, place2 = place_replace_word(words[uppercase_word_positions[0]], words[uppercase_word_positions[1]])
        # else:
        #     print("ERROR: 未找到实体填入位置")
        #     print(words[uppercase_word_positions[0]], words[uppercase_word_positions[1]])
        #     exit(1)
        # # print(words[uppercase_word_positions[0]], words[uppercase_word_positions[1]])
        if int(query_num) == int(0):    # RE
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_entities.sample().iloc[0]['name']
            else:
                place2 = region_entities.sample().iloc[0]['name']
            # 替换第一个位置的词
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_entities.append(place2)
        else:   # ER
            if words[uppercase_word_positions[1]] == 'LINE':
                place1 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place1 = point_entities.sample().iloc[0]['name']
            else:
                place1 = region_entities.sample().iloc[0]['name']
            if words[uppercase_word_positions[0]] == 'LINE':
                place2 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place2 = point_relation.sample().iloc[0]['name']
            else:
                place2 = region_relation.sample().iloc[0]['name']
            # 替换第一个位置的词
            words[uppercase_word_positions[0]] = place2
            words[uppercase_word_positions[1]] = place1
            corpus_entities.append(place1)
            corpus_relations.append(place2)
    elif type in ('Basic-length Query', 'Basic-area Query'):
        if len(uppercase_word_positions) > 2:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        if int(query_num) == int(0):
            # if re.findall(r'\b\w+\b', words[uppercase_word_positions[0]])[0] == 'REGION':
            if words[uppercase_word_positions[0]] == 'REGION':
                place = region_entities.sample().iloc[0]['name']
            else:
                place = line_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place
            corpus_entities.append(place)          
        else:
            if words[uppercase_word_positions[0]] in ('LINE', 'REGION'):
                relation, entity = place_replace_word1(words[uppercase_word_positions[0]])
                words[uppercase_word_positions[0]] = replace_s(words[uppercase_word_positions[0]], entity)
                words[uppercase_word_positions[1]] = replace_s(words[uppercase_word_positions[1]], relation)
            else:
                relation, entity = place_replace_word1(words[uppercase_word_positions[1]])
                words[uppercase_word_positions[0]] = replace_s(words[uppercase_word_positions[0]], relation)
                words[uppercase_word_positions[1]] = replace_s(words[uppercase_word_positions[1]], entity)
            corpus_entities.append(entity)
            corpus_relations.append(relation)    
    elif type in ('Basic-direction Query', 'Basic-distance Query'):
        if len(uppercase_word_positions) != 2:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        place1 = geo_entities.sample(n=1)['name'].iloc[0]
        place2 = geo_entities.sample(n=1)['name'].iloc[0]
        words[uppercase_word_positions[0]] = place1
        words[uppercase_word_positions[1]] = place2
        corpus_entities.append(place1)
        corpus_entities.append(place2)
    elif type in ('Aggregation-count Query', 'Aggregation-max Query'):
        if len(uppercase_word_positions) > 2:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        if int(query_num) == int(0):    # R
            if words[uppercase_word_positions[0]] == 'LINE':
                place = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place = point_relation.sample().iloc[0]['name']
            else:
                place = region_relation.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place
            corpus_relations.append(place)
        elif int(query_num) == int(1):  # RE
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_entities.sample().iloc[0]['name']
            else:
                place2 = region_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_entities.append(place2)
        else:                           # RR
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_relation.sample().iloc[0]['name']
            else:
                place2 = region_relation.sample().iloc[0]['name']
            while (place1 == place2):
                if words[uppercase_word_positions[1]] == 'LINE':
                    place2 = line_relation.sample().iloc[0]['name']
                elif words[uppercase_word_positions[1]] == 'POINT':
                    place2 = point_relation.sample().iloc[0]['name']
                else:
                    place2 = region_relation.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_relations.append(place2)
    elif type in ('Aggregation-sum Query'):
        if len(uppercase_word_positions) > 2:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        if int(query_num) == int(0):        # E
            if words[uppercase_word_positions[0]] == 'LINE':
                place = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place = point_entities.sample().iloc[0]['name']
            else:
                place = region_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place
            corpus_entities.append(place)
        else:                               # RE
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_entities.sample().iloc[0]['name']
            else:
                place2 = region_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_entities.append(place2)
    elif type in ('Distance Join Query'):
        if len(uppercase_word_positions) > 3:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        if int(query_num) == int(0):        # RR
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_relation.sample().iloc[0]['name']
            else:
                place2 = region_relation.sample().iloc[0]['name']
            while (place1 == place2):       # 防止两个地点是一样的
                if words[uppercase_word_positions[1]] == 'LINE':
                    place2 = line_relation.sample().iloc[0]['name']
                elif words[uppercase_word_positions[1]] == 'POINT':
                    place2 = point_relation.sample().iloc[0]['name']
                else:
                    place2 = region_relation.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_relations.append(place2)
        else:                               # EER-后面两个ER是对应关系
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_entities.sample().iloc[0]['name']
            else:
                place1 = region_entities.sample().iloc[0]['name']
            relation, entity = place_replace_word1(words[uppercase_word_positions[1]])
            words[uppercase_word_positions[1]] = entity
            words[uppercase_word_positions[2]] = relation
            words[uppercase_word_positions[0]] = place1
            corpus_entities.append(place1)
            corpus_entities.append(entity)
            corpus_relations.append(relation)
    elif type in ('Spatial Join Query'):
        if len(uppercase_word_positions) > 3:
            print("ERROR: 填充实体数量错误！")
            print(query_template)
            exit(1)
        if int(query_num) == int(0):        # RE
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_entities.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_entities.sample().iloc[0]['name']
            else:
                place2 = region_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_entities.append(place2)
        elif int (query_num) == int(1):     # RR
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_relation.sample().iloc[0]['name']
            else:
                place2 = region_relation.sample().iloc[0]['name']
            while (place1 == place2):
                if words[uppercase_word_positions[1]] == 'LINE':
                    place2 = line_relation.sample().iloc[0]['name']
                elif words[uppercase_word_positions[1]] == 'POINT':
                    place2 = point_relation.sample().iloc[0]['name']
                else:
                    place2 = region_relation.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            corpus_relations.append(place1)
            corpus_relations.append(place2)
        else:                               # RRE
            if words[uppercase_word_positions[0]] == 'LINE':
                place1 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[0]] == 'POINT':
                place1 = point_relation.sample().iloc[0]['name']
            else:
                place1 = region_relation.sample().iloc[0]['name']
            if words[uppercase_word_positions[1]] == 'LINE':
                place2 = line_relation.sample().iloc[0]['name']
            elif words[uppercase_word_positions[1]] == 'POINT':
                place2 = point_relation.sample().iloc[0]['name']
            else:
                place2 = region_relation.sample().iloc[0]['name']
            while (place1 == place2):
                if words[uppercase_word_positions[1]] == 'LINE':
                    place2 = line_relation.sample().iloc[0]['name']
                elif words[uppercase_word_positions[1]] == 'POINT':
                    place2 = point_relation.sample().iloc[0]['name']
                else:
                    place2 = region_relation.sample().iloc[0]['name']
            place3 = region_entities.sample().iloc[0]['name']
            words[uppercase_word_positions[0]] = place1
            words[uppercase_word_positions[1]] = place2
            words[uppercase_word_positions[2]] = place3
            corpus_relations.append(place1)
            corpus_relations.append(place2)
            corpus_entities.append(place3)
    # print(words)
    replaced_query = ' '.join(words).replace(' ,', ',').replace(' .', '.').replace(' ?', '?').replace(' :', ':').replace(' !', '!')\
        .replace(' \'', '\'').replace("' ", "'").strip()       # .replace(' s', 's').replace(' m', 'm')
    if '*' in replaced_query:
        replaced_query = replaced_query.replace('*', random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    return type, replaced_query, corpus_relations, corpus_entities

# print("--------------------------------------")
# print(replace_template("Distance Join Query"))
# print("--------------------------------------")


"""
    对生成的csv文件根据类型进行排序
"""
def sort_csv(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # 读取第一行作为表头
        header = next(reader)
        # 读取剩余行作为列表
        rows = list(reader)
        csvfile.close()

    sorted_rows = sorted(rows, key=lambda row: row[0])

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow(header)
        # 写入排序后的行
        for row in sorted_rows:
            writer.writerow(row)
        csvfile.close()
    
    # print('Sort completed.')


"""
    输出csv文件
"""
def output_csv_file(list, file_path):
    if os.path.exists(file_path):   # 文件存在
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
            file.truncate()     # 清空
            writer = csv.writer(file)
            writer.writerow(['cat', 'query', 'relations', 'entities'])  
            for row in list:
                writer.writerow(row)
            file.close()
        # print(f'File {file_path} cleared.')
    else:                           # 文件不存在
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as file:
            file.write('')
            writer = csv.writer(file)
            writer.writerow(['cat', 'query', 'relations', 'entities'])
            for row in list:
                writer.writerow(row)
            file.close()
        print(f'File {file_path} created.')


"""
    批量生成查询语句
"""
def query_generation(num):
    results = []    # 存放replace_template产生结果

    for i in range(num):
        # random_query = random.choice(query_type)    # 随机生成不同类型查询
        # 随机选取不同类型查询
        random_type_row = type_file.sample(n=1)         # 随机选取type.csv文件中的一行
        random_query = random_type_row['cat'].iloc[0]  # 获取选中的type值

        cat, query, relations, entities = replace_template(random_query)
        # # 将 relations 和 entities 转换为字符串格式
        # relations_str = ", ".join(relations)  # 用逗号分隔元素
        # entities_str = ", ".join(entities)    # 用逗号分隔元素
        results.append((cat, query, relations, entities))

    # 生成NLQ保存地址
    file_path = 'SpaCor\knowledge_base\SpaCorOutput.csv'

    # 保存为csv格式文件
    output_csv_file(results, file_path)
    sort_csv(file_path)

    # print('Data appended to SpaCorOutput.csv')

    return results


if __name__ == "__main__":
    # print("接收到的参数:", sys.argv)
    corpus = "berlintest"
    query_count = 100  # 默认值

    if len(sys.argv) > 1:
        corpus = sys.argv[1]
    if len(sys.argv) > 2:
        query_count = int(sys.argv[2])

    result = query_generation(query_count)
    print("cat, query, relations, entities")
    for nlq in result:
        print(f"{nlq[0]}, {nlq[1]}, {nlq[2]}, {nlq[3]}".encode('utf-8').decode('utf-8'), flush=True)



    # print(sys.argv, sys.argv[0])