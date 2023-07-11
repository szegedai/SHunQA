import pandas as pd

df_pos_lemma = pd.read_csv('q_wPoS_wLemma_c_wLemma_c_wOfficial.csv',
                           names=['question', 'context'],
                           header=1,
                           encoding='utf-8')

df_lemma = pd.read_csv('q_wLemma_c_wLemma.csv',
                 names=['question', 'context'],
                 header=1,
                 encoding='utf-8')

print(len(df_pos_lemma), len(df_lemma))
