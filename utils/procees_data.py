import os
from tqdm import tqdm
from random import choice
import random


def read_txt(data_path, save_path, name):
    increase_text1 = ["", "", "", "", "", "", "呐", "呢", "", "呢", "呀", "哦", "？", "。", "！", "，", "~"]
    increase_text2 = ["", "", "", "那", "如果是", "要是", "", "是", "", "我问的是", "问的是", "那么"]
    with open(data_path, "r", encoding="utf8") as fr, open(save_path, "w", encoding="utf-8") as intent_out:
        intent_out.write("version: \"3.1\"\n")
        intent_out.write("nlu:" + "\n")
        intent_out.write("  - intent: {}_name".format(name) + "\n")
        intent_out.write("    examples: |" + "\n")
        data = fr.readlines()
        random.shuffle(data)
        k = 1000 if len(data) >= 1000 else len(data)
        for line in tqdm(data[:k], total=len(data[:k]), desc=name):
            if len(line) > 0:
                result = "      - " + choice(increase_text2) + "[" + line.strip() + "]" + \
                         "({})".format(name) + choice(increase_text1)
                intent_out.write(result + "\n")


if __name__ == '__main__':
    data_paths = ["../pipeline/jieba_userdict/disease.txt", "../pipeline/jieba_userdict/drug.txt",
                  "../pipeline/jieba_userdict/check.txt", "../pipeline/jieba_userdict/symptom.txt",
                  "../pipeline/jieba_userdict/food.txt", "../pipeline/jieba_userdict/department.txt"]
    save_paths = ["../data/disease/disease_intent.yml", "../data/disease/drug_intent.yml",
                  "../data/disease/check_intent.yml", "../data/disease/symptom_intent.yml",
                  "../data/disease/food_intent.yml", "../data/disease/department_intent.yml"]
    for data_path, save_path in zip(data_paths, save_paths):
        name = data_path.strip().split("/")[-1].strip().split(".txt")[0]
        read_txt(data_path, save_path, name)
