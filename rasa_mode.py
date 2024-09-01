#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rasa
import os
import warnings
import argparse
from server.start_services import run, interactive
import logging
import gc

gc.collect()
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
warnings.filterwarnings("ignore")

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="test", help="train or test mode")
parser.add_argument("--domain", type=str, default="domain/", help="domain file")
parser.add_argument("--config", type=str, default="config.yml", help="config file")
parser.add_argument("--output", type=str, default="models", help="output model path")
args = parser.parse_args()


def setup_logging():
    if not os.path.exists("log"):
        os.mkdir("log")
    # 设置日志的配置
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为 DEBUG，也可以设置为 INFO, WARNING, ERROR, CRITICAL
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
        filename='log/rasa.log',  # 日志输出到文件，不设置这个参数则输出到标准输出（控制台）
        filemode='w'  # 'w' 表示写模式，'a' 表示追加模式
    )

    # 如果还想要将日志输出到控制台，可以添加一个 StreamHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 设置控制台的日志级别
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)
    logging.debug('logging start...')


def train():
    rasa.train(
        domain="domain/",
        config="config.yml",
        training_files="data",
        output="models")


def test():
    # 启动服务
    run()


if __name__ == '__main__':
    setup_logging()
    if args.mode == "train":
        train()
    elif args.mode == "test":
        test()

