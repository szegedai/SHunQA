import pandas as pd

short_i = pd.read_csv("milqa_dataset/short_impossible.csv", sep=";", encoding="utf-8")
short = pd.read_csv("milqa_dataset/short.csv", sep=";", encoding="utf-8")
long_i = pd.read_csv("milqa_dataset/long_impossible.csv", sep=";", encoding="utf-8")
long = pd.read_csv("milqa_dataset/long.csv", sep=";", encoding="utf-8")

print(len(short_i))
print(len(short))
print(len(long_i))
print(len(long))
