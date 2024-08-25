import os
import re
import json
from collections import defaultdict
from rasa_sdk.events import SlotSet


p = 'Diseases_dic.txt'
disease_names = [i.strip() for i in open(p, 'r', encoding='UTF-8').readlines()]

class TireNode:
    def __init__(self):
        self.word_finish = False
        self.count = 0
        self.word = None
        self.entity_class = defaultdict(set)
        self.child = defaultdict(TireNode)


def read_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


class Tire:
    def __init__(self):
        self.root = TireNode()

    def add(self, word, entity_class):
        curr_node = self.root
        for char in str(word).strip():
            curr_node = curr_node.child[char]
        curr_node.count += 1
        curr_node.word = word
        curr_node.entity_class[word].add(entity_class)
        curr_node.word_finish = True

    def search(self, words):
        entity_dic = {}
        for i in range(len(words)):
            word = words[i:]
            curr_node = self.root
            for char in word:
                curr_node = curr_node.child.get(char)
                if curr_node is not None and curr_node.word_finish == True:
                    entity_dic[curr_node.word] = curr_node.entity_class.get(curr_node.word)
                elif curr_node is None or len(curr_node.child) == 0:
                    break
        return entity_dic if entity_dic else ''


class MatchEntity:
    def __init__(self):
        self.tire = Tire()
        self.entity_dic = {}
        self.cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1]) + '/entity_dict/'
        for file_name in [file for file in os.listdir(self.cur_dir) if file != '.DS_Store']:
            entity_name = file_name.split('.')[0]
            self.entity_dic[entity_name] = self.read_data(self.cur_dir + file_name)

        for name, entity_lis in self.entity_dic.items():
            for entity in entity_lis:
                self.tire.add(entity, name)

    def read_data(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return [word.strip() for word in file.readlines() if word.strip()]

    def match(self, words):
        entity_dic = self.tire.search(words)
        slot_list = []
        if entity_dic:
            for entity, class_set in entity_dic.items():
                for class_ in class_set:
                    slot_list.append(SlotSet(class_, entity))
                    return slot_list, entity_dic
        else:
            return slot_list, entity_dic


def retrieve_disease_name(name):
    names = []
    name = '.*' + '.*'.join(list(name)) + '.*'
    pattern = re.compile(name)
    for i in disease_names:
        candidate = pattern.search(i)
        if candidate:
            names.append(candidate.group())
    return names


if __name__ == '__main__':
    input_word = ""
    match = MatchEntity()
    slot_list, entity_dic = match.match(input_word)
    possible_diseases = retrieve_disease_name("百日咳")