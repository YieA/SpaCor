'''
    对LLM生成的查询语句进行检测判断
'''

# 关闭警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torch')

import csv
import random
import pandas as pd
import spacy
import re
import time
import os
from spacy.matcher import PhraseMatcher
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from QueryGeneration import sort_csv, output_csv_file
from PredictText import predict_type
import sys


nlp = spacy.load("en_core_web_sm")


# knowledge base
entity_file = pd.read_csv('SpaCor/knowledge_base/places.csv')
relation_file = pd.read_csv('SpaCor/knowledge_base/spatial_relations.csv')

terms0 = relation_file['name'].tolist()
terms1 = entity_file['name'].tolist()
terms2 = terms0 + terms1

'''
    进行实体命名匹配
    index: 0 提取relation名词
           1 提取entity名词
           2 提取所有能够匹配到的名词
    query: 句子/文本

    Discover line in strassen found within 2 kilometers from Borussenstr.. -> strassen, Borussenstr.
'''
def phrase_matcher(index, query):
    matcher = PhraseMatcher(nlp.vocab)

    if len(query) > 2 and query[-2:] in ("..", ").", ".?", ")?", ".!", ")!", ".,", "),", "A.", "C.", "L.", "R.", "I.", "M.", "X.", "V.", "Z."):
        query = query[:-1]                                                                  # A.这一些是为了识别末尾为Café M.这类单词

    # 使用 nlp.make_doc 加速
    patterns = [("0", nlp.make_doc(text)) for text in terms0]           # 0: 关系
    patterns += [("1", nlp.make_doc(text)) for text in terms1]          # 1: 实体

    # matcher.add("TerminologyList", patterns)
    for label, pattern in patterns:
        matcher.add(label, [pattern])

    results = []    # 存放提取的结果

    doc = nlp(query)

    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        if int(index) == int(2):
            span = doc[start:end]
            results.append(span.text)
        else:
            if int(string_id) == int(index):            # 如果 index=0，则匹配关系名词, =1匹配实体
                span = doc[start:end]
                results.append(span.text)
    # print(results)
    return results

# print(phrase_matcher(0, 'Discover line in strassen found within 2 kilometers from Borussenstr..'))
# print(phrase_matcher(1, "Directional path Putbus to Libauer Str.."))
# print(phrase_matcher(2, "Discover point in Restaurants found within 2 kilometers from A."))
# s = time.time()
# print(phrase_matcher(0, "Show me Sehenswuerdreg that are located in Landschaftspark Wuhletal."))
# e = time.time()
# print(phrase_matcher(1, "Show me Sehenswuerdreg that are located in Landschaftspark Wuhletal."))
# print(phrase_matcher(2, "Show me Sehenswuerdreg that are located in Landschaftspark Wuhletal."))
# t = e - s
# print(f"{t:.2f}")


'''
    在原有返回实体和关系的基础上 还返回名词在句子中的位置
    例如
        print(phrase_matcher2(2, "Discover point in Restaurants found within 2 kilometers from A.")) -> [('Restaurants', 3)]
'''
def phrase_matcher2(index, query):
    matcher = PhraseMatcher(nlp.vocab)

    if len(query) > 2 and query[-2:] in ("..", ").", ".?", ")?", ".!", ")!", ".,", "),", "A.", "C.", "L.", "R.", "I.", "M.", "X.", "V.", "Z."):
        query = query[:-1]  # A.这一些是为了识别末尾为Café M.这类单词

    # 使用 nlp.make_doc 加速
    patterns = [("0", nlp.make_doc(text)) for text in terms0]  # 0：关系
    patterns += [("1", nlp.make_doc(text)) for text in terms1]  # 1: 实体

    # 添加模式到matcher
    for label, pattern in patterns:
        matcher.add(label, [pattern])

    results = []  # 存放提取的结果

    doc = nlp(query)

    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if int(index) == 2:
            results.append((span.text, start, end))  # 包括匹配文本和位置
        else:
            if int(string_id) == int(index):  # 如果 index=0，则匹配关系名词, =1匹配实体
                results.append((span.text, start))

    return results
# print(phrase_matcher2(1, "Calculate the driving distance from Stadtpark Steglitz to Auswärtiges Amt in Sehenswuerdreg.")[-1][0])
# print(phrase_matcher2(1, "Calculate the driving distance from Stadtpark Steglitz to Auswärtiges Amt in Sehenswuerdreg."))
# print(phrase_matcher2(2, "Calculate the driving distance from Stadtpark Steglitz to Auswärtiges Amt in Sehenswuerdreg."))


'''
    找最匹配的空间实体  
    index: 0 匹配relation中的最佳
           1 匹配entity中的最佳
    text: 实体名词

    Kino -> Kinos
'''
def similar_match(index, text):
    if int(index) == int(0):
        most_similar, similarity_score = process.extractOne(text, terms0)
    else:
        most_similar, similarity_score = process.extractOne(text, terms1)
    # print(f'最匹配的词：{most_similar}')
    # print(f'最佳匹配度：{similarity_score}%')

    return most_similar, similarity_score

# print(similar_match(1, "Lübars | b . Möck3ern"))
# print(similar_match(0, "kino"))
# print(similar_match(1, "walther"))

def find_most_similar(index, text):
    if int(index) == int(0):
        terms = terms0
    elif int(index) == int(1):
        terms = terms1
    else:
        terms = terms2
    # 初始化最相似单词和最高相似度分数
    most_similar = terms[0]
    highest_score = fuzz.ratio(text, terms[0])

    # 遍历词汇列表，查找最相似的单词
    for term in terms:
        score = fuzz.ratio(text, term)
        if score > highest_score:
            most_similar = term
            highest_score = score

    return most_similar, highest_score

# # 测试函数
# result = find_most_similar(1, 'F2 . 2 : Gel2tow - Wildpark West')
# print(f'最匹配的词：{result[0]}')
# print(f'最佳匹配度：{result[1]}%')



'''
    单数变复数
    word: 单词

    Kino -> Kinos
'''
def plurelize(word):
    if word.endswith('o'):
        if word[-2] in 'eiy':
            return word + 'es'
        else:
            return word + 's'
    elif word.endswith('ch'):
        return word + 'es'
    elif word.endswith('sh'):
        return word + 'es'
    elif word.endswith('f'):
        if word.endswith('ff'):
            return word[:-2] + 'vves'
        else:
            return word[:-1] + 'ves'
    elif word.endswith('fe'):
        return word[:-1] + 'ves'
    elif word.endswith('y'):
        if word[-2] in 'aeiou':
            return word + 's'
        else:
            return word[:-1] + 'ies'
    elif word.endswith('s'):
        return word + 'es'
    else:
        return word + 's'

# print(plurelize("kino"))

"""
    输出csv文件
    原本调用的是QueryGeneration.py中的output_csv_file 但是文件头格式不一样 因此重新在这边定义
"""
def output_csv_file(list, file_path):
    if os.path.exists(file_path):   # 文件存在
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
            file.truncate()     # 清空
            writer = csv.writer(file)
            writer.writerow(['cat', 'query', 'relations', 'entities', 'type', 'error', 'err_id'])
            for row in list:
                writer.writerow(row)
            file.close()
        # print(f'File {file_path} cleared.')
    else:                           # 文件不存在
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as file:
            file.write('')
            writer = csv.writer(file)
            writer.writerow(['cat', 'query', 'relations', 'entities', 'type', 'error', 'err_id'])
            for row in list:
                writer.writerow(row)
            file.close()
        print(f'File {file_path} created.')


'''
    提取空间实体并替换(通过关键词确定位置进行查找)
    text: 文本/查询语句

    return: 错误类型 正确语句
    Find the nearest Kino to alexanderplatz. -> (0, 'Find the nearest Kinos to alexanderplatz.')
'''
def replace_entity(text):
    # print(text)
    output_flag = []     # 原始flag为空，将错误问题标号放进去

    # 特殊情况：poi
    temp_text = text
    phrases_to_search = ["points of interest", "point of interest"]
    replaced_text = "poi"
    for phrase in phrases_to_search:
        temp_text = re.sub(phrase, replaced_text, temp_text, flags=re.IGNORECASE)
        if temp_text != text:
            text = temp_text
            output_flag.append(1)
            break
    query = text
    query_category = predict_type(query)
    # print(predict_type("Which way is it from Restauration Sophien 11 to Dresdener? "))
    # print(query_category)

    if query_category in ("Range Query", "Nearest Neighbor Query"):
        keywords = ['in', 'to', 'the', 'from', 'all', 'of', 'on', 'a', 'by', 'this', 'which', 'many', 'nearest', 'closest', 'near',
                     'specific', 'particular']
        specificwords = ['range', 'list', 'directory', 'district', '1.5', '15', 'specific', 'parallel',
                          'a', 'borough', 'the', 'to', '1','2', '3', '4', '5', '8', '9', 'one', 'two',' theree', 'four', 'five',
                            'line', 'region', 'point', 'lines', 'regions', 'points', '500', 'address', ]
    elif query_category in ("Basic-distance Query", "Basic-direction Query"):
        keywords = ['from', 'to', 'between', 'and', 'query:', 'are', 'is', 'towards', 'heading', 'direction', 'point', 'orientation', 'at', 'for', 'reach',
                    'route', 'Pathfinding', 'path', 'specific']
        specificwords = ['it', 'the', 'what', 'guidance', 'details', 'map', '?', 'should', 'advice', 'assistance', 'planner', 'when', 'me', 'if', 'perpendicular',
                         'a']
    elif query_category in ("Basic-area Query", "Basic-length Query"):
        keywords = ['of', 'in', 'by', 'for', 'is', ',', 's', 'long', 'ancient', 'charming', 'bustling', 'historic', 'iconic', 'lively', 'majestic',
                    'meandering', 'picturesque', 'scenic', 'vibrant', 'winding', 'along', 'all', 'that']
        specificwords = ['the', 'geographical', 'terms', 'knowing', 'please', 'expensive', 'area', 'surface', 'dimensions', 'expanse', 'size', 'length'
                         'main', 'perimeter', 'immensity', 'proportions', 'land', 'areal', 'sheer', 'cover', 'information', 'are']
    elif query_category in ("Distance Join Query"):
        keywords = ['any', 'each', 'from', 'to', 'closest', 'between', 'the', 'List', 'of', 'Which', 'nearby', 'list', 'are', 'What', 'in', 'which']
        specificwords = ['driving', 'flight', 'travel', 'distance', 'walking', 'within', 'available', 'situated', 'located', 'is', 'knowing',
                         '1', '2', '3', '4', '5', '6', '7', '8', '9', 'there']
    elif query_category in ("Spatial Join Query"):
        keywords = ['in', 'of', 'me', 'the', 'within', 'What', 'which', 'these', 'what', 'each', 'where', 'Which', 'are', 'any', 'intersect', 'is', 'whose'
                    '1', '2', '3', '4', '5', '6', '7', '8', '9']
        specificwords = ['all', '?', 'less', 'more', 'boundaries', 'region', 'letter', 'neighborhoods', 'situated', 'located', 'on', 'miles', 'kilometers'
                         'point', 'line', 'square', 'that', 'nodes', 'neighborhood', 'there', 'available', 'name', 'names', 'kilometers']
    elif query_category in ("Aggregation-count Query"):
        keywords = ['in', 'of', 'many', 'through', 'pass', 'with', 'on']
        specificwords = ['each', 'knowing', 'the', 'each', 'region', 'point', 'line']
    elif query_category in ("Aggregation-sum Query"):
        keywords = ['by', 'in', 'all', 'within', 'total', 'of', 'intersecting', 'intersect', 'from', 'between', 'and']
        specificwords = ['#', 'area', 'length', 'lakes', 'protected', 'the', 'number', 'water', 'land', 'value', 'endangered']
    elif query_category in ("Aggregation-max Query"):
        keywords = ['all', 'with', 'Among', 'most', 'which', 'What', 'of', 'intersecting', 'where', 'number', 'Which']
        specificwords = ['intersections', 'convergence', 'extensive', 'substantial', 'significant', 'intersection', 'one', 'roads', 'paths', 'rivers'
                         'road', 'crossing', 'at', '?', 'within']

    results = []            # 保存提取词和替换词


    # 确定keywords的位置
    positions = {word: [index for index, word_in_sentence in enumerate(re.findall(r'\w+|[^\w\s]', query)) if word_in_sentence.lower() == word] for word in keywords}
    # print(positions.items())

    temp_words = re.findall(r'\w+|[^\w\s]', query)
    # # 删除关键词搜索情况为空的
    # positions_list = []
    # for word, position_list in positions.items():
    #     if position_list and (temp_words[position_list[0] + 1] not in specificwords):
    #         positions_list.append([word, position_list[0]])
    # 修改后的代码
    positions_list = []
    for word, position_list in positions.items():
        if position_list:  # 确保位置列表不为空
            for position in position_list:
                if position_list and (temp_words[position + 1] not in specificwords):
                    positions_list.append([word, position])
    positions_list = sorted(positions_list, key=lambda x: x[1], reverse=False)
    # print(positions_list)

    # 避免关键词连续出现
    final_positions = []        # [['the',3], ['of', 5]]
    for i in range(len(positions_list)):
        if i == len(positions_list) - 1 or positions_list[i][1] + 1 != positions_list[i + 1][1]:
            final_positions.append(positions_list[i])
    # print(final_positions)

    # 存在两个空间命名，但是只有一个关键词，例如“Shanghai to Beijing azimuth.”，则要添加一个从-1位置
    if query_category == "Basic-direction Query" and len(final_positions) == 1:
        final_positions.append(['', -1])
    final_positions = sorted(final_positions, key=lambda x: x[1], reverse=False)

    # print("Keywords: ", final_positions)


    # 寻找替换词
    for index, position_list in enumerate(final_positions):
        if position_list:
            words = re.findall(r'\w+|[^\w\s]', query)
            # print(words)
            if position_list[0] == 'of' and (words[position_list[1] - 1] == 'points' or words[position_list[1] - 1] == 'point') and words[position_list[1] + 1] == 'interest':
                results.append(['points of interest', 'poi'])
                break
            start_position = position_list[1] + 1   # 开始提取的位置
            extract_words = []      # 保存提取的单词
            simliar_result = []     # 存储相似度匹配情况
            # 确保开始位置在句子范围内
            if start_position >= len(words):
                return []
            # 找关键词后1-9个单词 标点也会被拆分
            for i in range(1, 10):
                if len(words) >= start_position + i:
                    # 查找范围不能包含下一个keywords及其之后的
                    if index < len(final_positions) - 1:
                        if start_position + i <= final_positions[index + 1][1]:
                            extracted = words[start_position : start_position + i]
                            extract_words.append(" ".join(extracted))
                            if (start_position + i < len(words) - 1 and words[start_position + i] in keywords):
                                break
                    else:
                        extracted = words[start_position : start_position + i]
                        extract_words.append(" ".join(extracted))
                        # 不能包括关键词和最后一个标点符号
                        if (start_position + i < len(words) - 1 and words[start_position + i] in keywords) or start_position + i == len(words) - 1:
                            break
            # 进行词匹配
            # print(extract_words)
            flag = 1
            for word in extract_words:
                # print(word)

                if query_category in ("Range Query", "Nearest Neighbor Query"):
                    match_index = index     # 第一个词匹配关系，第二个词匹配实体
                elif query_category in ("Basic-distance Query", "Basic-direction Query"):
                    match_index = 1         # 全部匹配实体
                elif query_category in ("Basic-length Query", "Basic-area Query"):
                    match_index = 2         # 匹配所有的词
                elif query_category in ("Aggregation-count Query", "Aggregation-max Query"):    # R/RE/RR
                    if index == 0:
                        match_index = 0
                    else:
                        match_index = 2
                elif query_category in ("Aggregation-sum Query"):       # E/RE
                    if len(final_positions) == 1:
                        match_index = 1
                    else:
                        match_index = index
                elif query_category in ("Distance Join Query"):     # RR/EER
                    if len(final_positions) == 2:
                        match_index = 0
                    else:
                        if index == 0 or index == 1:
                            match_index = 1
                        else:
                            match_index = 0
                elif query_category in ("Spatial Join Query"):      # RE/RR/RRE
                    if len(final_positions) == 2:
                        if index == 0:
                            match_index = 0
                        else:
                            match_index = 2
                    else:
                        if index == 0 or index == 1:
                            match_index = 0
                        else:
                            match_index = 1

                # 如果句子原本有正确的实体名词，则直接跳过
                if word in phrase_matcher(match_index, word):
                    flag = 0
                    break
                # 如果复数存在，则替换为复数词，不继续进行相似度匹配
                if phrase_matcher(match_index, plurelize(word)) != []:
                    word_depunctuate = plurelize(word)
                    if plurelize(word)[-1] in (".", "?", ")"):
                        word_depunctuate = word_depunctuate[:-1]
                    results.append([word, word_depunctuate])
                    flag = 0
                    break
                similar_word, score = find_most_similar(match_index, word)
                # print(similar_word,"   ", score )
                simliar_result.append([word, similar_word, score])
            # for line in simliar_result:
            #     print(line)
            # 保存匹配度最高的
            if flag:
                highest_score_word = max(simliar_result, key=lambda x: x[-1])
                # if highest_score_word[1][-1] in (".", "?", ")"):            # 不去掉的话，会出现str.结果最后是str..的情况
                #     highest_score_word[1] = highest_score_word[1][:-1]
                results.append([highest_score_word[0], highest_score_word[1]])

    # print(simliar_result)
    # print("Change: ",results)

    # 对原查询语句进行实体命名替换
    replaced_query = text
    for result in results:
        if result[0] != result[1]:
            result[0] = result[0].replace(" | ", "|").replace(" .", ".").replace("( ", "(").replace(" )", ")").replace(" / ", "/").replace(" :", ":")
            if " - " not in result[1]:
                result[0] = result[0].replace(" - ", "-")
            if ". " not in result[1]:
                result[0] = result[0].replace(". ", ".")
            # print(result[0])
            replaced_query = replaced_query.replace(result[0], result[1])
            if plurelize(result[0]) == result[1] or plurelize(result[1]) == result[0]:      # 单复数问题
                if 4 not in output_flag:
                    output_flag.append(4)
            elif len(phrase_matcher(2, result[0])) != 0 and phrase_matcher(2, result[0])[-1] == result[0]:         # 类型问题
                if 5 not in output_flag:
                    output_flag.append(5)
            elif result[0].lower() == result[1].lower():        # 大小写问题
                if 3 not in output_flag:
                    output_flag.append(3)
            else:       # 不匹配
                if 2 not in output_flag:
                    output_flag.append(2)

    # print(replaced_query)
    # print(text)


    # if replaced_query == text and output_flag == 0:
    #     output_flag = 2
    #     # print("     The query originally contained only one spatial entity.")
    return text, query_category, replaced_query, output_flag

# print(replace_entity("How do I determine the travel direction from Rosenfelder Str. to Müggelwerderweg1?"))
# print(replace_entity("Identify the nearest Fahre to Barby."))


'''
    对查询语句进行检测和修复
    输入 path 文件路径 例如./work/file1.csv
'''
def query_detection(path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)   # 表头
        rows = list(reader)     # 查询语句

    # 存储全部query的实体识别结果
    # result = []                 # 存储每个查询内的实体
    error_match_query = []
    right_match_query = []
    # test_query = []

    print("Start detecting queries...Please wait for a minute...")
    
    start_detection = time.time()

    for row in rows[0:3000]:     # 检测语料范围
        # test_query.append([row])
        query_category = predict_type(row[1])
        if row[0] != query_category:
            # error_match_query.append([query_category, row[1], row[2], row[3]])
            error_match_query.append(row)
            continue
        # print(query_category)
        if query_category in ("Range Query", "Nearest Neighbor Query"):
            obtained_result = phrase_matcher(2, row[1])
            if len(obtained_result) >= 2:       # 实体数大于等于二
                right_match_query.append(row)
            else:
                error_match_query.append(row)
        # result.append(row_result)
        elif query_category in ("Basic-distance Query", "Basic-direction Query"):
            obtained_result = phrase_matcher(1, row[1])
            if len(obtained_result) >= 2:       # 实体数大于等于二
                right_match_query.append(row)
            else:
                error_match_query.append(row)
        elif query_category in ("Basic-area Query", "Basic-length Query"):
            obtained_result_0 = phrase_matcher(0, row[1])       # 识别到的关系
            obtained_result_1 = phrase_matcher(1, row[1])       # 识别到的实体
            if len(obtained_result_1) == 0:     # 没有识别到实体
                error_match_query.append(row)
            else:
                if len(obtained_result_0) == 0 and len(obtained_result_1) >= 1:
                    right_match_query.append(row)
                elif len(obtained_result_0) >= 1:         # LINE in RELI
                    ele_relation = max(obtained_result_0, key=len)  # 关系
                    ele_entity = max(obtained_result_1, key=len)    # 实体
                    if relation_file[relation_file['name'] == ele_relation]['GeoData'].iloc[0] in ("line", "region"):   # 关系为 line / region
                        rel_id = relation_file[relation_file['name'] == ele_relation]['id'].iloc[0]
                        if entity_file[(entity_file['rel_id'] == rel_id) & (entity_file['name'] == ele_entity)].empty:  # 关系与实体不对应
                            error_match_query.append(row)
                        else:
                            right_match_query.append(row)
                    else:
                        error_match_query.append(row)
                else:
                    error_match_query.append(row)
        elif query_category in ('Aggregation-count Query', 'Aggregation-max Query'):
            obtained_result_0 = phrase_matcher(0, row[1])   # 识别到的关系
            if len(obtained_result_0) == 0:     # 没有识别到关系
                error_match_query.append(row)
            else:
                right_match_query.append(row)
        elif query_category in 'Aggregation-sum Query':
            obtained_result_1 = phrase_matcher(1, row[1])   # 识别到的实体
            if len(obtained_result_1) == 0:
                error_match_query.append(row)
            else:
                right_match_query.append(row)
        elif query_category in 'Distance Join Query':   # 两种可能 RR EER
            obtained_result_0 = phrase_matcher(0, row[1])   # R
            obtained_result_1 = phrase_matcher(1, row[1])   # E
            if len(obtained_result_1) == 0:     # RR
                if len(obtained_result_0) >= 2:
                    right_match_query.append(row)
                else:
                    error_match_query.append(row)
            elif len(obtained_result_1) >= 2:   # EER
                if len(obtained_result_0) < 1:
                    error_match_query.append(row)
                else:
                    ele_entity = phrase_matcher2(1, row[1])[-1][0]
                    ele_relation = max(obtained_result_0, key=len)  # 关系
                    rel_id = relation_file[relation_file['name'] == ele_relation]['id'].iloc[0]
                    if entity_file[(entity_file['rel_id'] == rel_id) & (entity_file['name'] == ele_entity)].empty:
                        error_match_query.append(row)
                    else:
                        right_match_query.append(row)
            else:
                error_match_query.append(row)
        elif query_category in 'Spatial Join Query':    # 三种可能 RE RR RRE
            obtained_result_0 = phrase_matcher(0, row[1])   # R
            obtained_result_1 = phrase_matcher(1, row[1])   # E
            if len(obtained_result_0) == 1:     # RE
                if len(obtained_result_1) >= 1:
                    right_match_query.append(row)
                else:
                    error_match_query.append(row)
            elif len(obtained_result_0) >= 2:   # RR / RRE
                if len(obtained_result_1) == 0:
                    right_match_query.append(row)
                elif len(obtained_result_1) == 1:
                    ele_relation = phrase_matcher2(0, row[1])[-1][0]
                    ele_entity = max(obtained_result_1, key=len)    # 实体
                    rel_id = relation_file[relation_file['name'] == ele_relation]['id'].iloc[0]
                    if entity_file[(entity_file['rel_id'] == rel_id) & (entity_file['name'] == ele_entity)].empty:
                        error_match_query.append(row)
                    else:
                        right_match_query.append(row)
                else:
                    error_match_query.append(row)
            else:
                error_match_query.append(row)
        else:
            error_match_query.append(row)


    end_detection = time.time()
    detect_time = end_detection - start_detection

    print(f'There are {len(error_match_query)} sentences identifying errors.')

    if len(error_match_query):
        print("The error sentences in modified as follows:")
        print("------------------------------------------------------------")

    start_repair = time.time()

    # 如果有错误的语句
    if len(error_match_query):
        # 则分析为什么错
        for index, query in enumerate(error_match_query):
            # print(query)
            # print(len(query))
            print(f'{index + 1}-Error query:   {query[0]}: {query[1]}')
            flag , replaced_query = replace_entity(query[1])
            ptype = predict_type(query[1])
            if query[0] != ptype:
                flag.append(6)
            print(f'{index + 1}-Correct query: {ptype}: {replaced_query}')
            # right_match_query.append([ptype, replaced_query, query[2], query[3], query[4], query[5], query[6]])
            right_match_query.append([ptype, replaced_query, query[2], query[3]])
            for i, typeid in enumerate(flag):
                if typeid == 1:
                    print(f"    提示{i + 1}: 描述不准确（使用同义词或别名）")
                elif typeid == 2:
                    print(f"    提示{i + 1}: 虚构空间实体或关系")
                elif typeid == 3:
                    print(f"    提示{i + 1}: 描述不准确（大小写错误）")
                elif typeid == 4:
                    print(f"    提示{i + 1}: 描述不准确（单复数错误）")
                elif typeid == 5:
                    print(f"    提示{i + 1}: 查询地点类型错误")
                elif typeid == 6:
                    print(f"    提示{i + 1}: 查询语句类型错误")
            print("------------------------------------------------------------")

    end_repair = time.time()
    repair_time = end_repair - start_repair
    print(f"检测花费 {detect_time:.2f}s.")
    print(f"修复花费 {repair_time:.2f}s.")


    # # 输出所有正确的查询
    # receivekey = input("If you want to see all the correct queries, please enter 'yes'. Or enter enter anything else, the dection ends. Waiting for input... ")
    # if receivekey == 'yes':
    #     print("The correct senetences as follows:")
    #     print("------------------------------------------------------------")
    #     for index, query in enumerate(right_match_query):
    #         print(f'{index + 1}-{query[0]}: {query[1]}')

    # 修复后的输出地址
    file_path = 'SpaCor\knowledge_base\DROutput.csv'
    output_csv_file(right_match_query, file_path)
    sort_csv(file_path)

    print('The modified query is saved to DROutput.csv')


    return right_match_query


if __name__ == "__main__":
    nlq = "Identify the nearest Fahre to Barby."
    
    if len(sys.argv) > 1:
        nlq = sys.argv[1]
    
    result = replace_entity(nlq)
    
    if result[0] == result[2]:
        print("The NLQ is right.")
    else:
        output_str = f"Input:  {result[0]}\nOutput: {result[1]}, {result[2]}\nError message:\n"
        if result[3]:
            for index, flag in enumerate(result[3], start=1):
                if flag == 1:
                    output_str += f"   ({index}) Inaccurate description (using synonyms or aliases)\n"
                elif flag == 2:
                    output_str += f"   ({index}) Fictitious spatial entities or relationships\n"
                elif flag == 3:
                    output_str += f"   ({index}) Inaccurate description (case error)\n"
                elif flag == 4:
                    output_str += f"   ({index}) Inaccurate description (single and plural errors)\n"
                elif flag == 5:
                    output_str += f"   ({index}) The location type is incorrect\n"
                elif flag == 6:
                    output_str += f"   ({index}) The query statement type is incorrect\n"
        else:
            output_str += "It is NULL.\n"

        print(output_str)