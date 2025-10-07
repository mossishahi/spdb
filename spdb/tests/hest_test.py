import os
import pandas as pd
import numpy as np
from spdb.abs import get_abstract
from spdb.emb import get_embedding

hest = pd.read_csv(f'{os.getenv("HOME")}/HEST_v1_1_0.csv')
urls = hest['study_link'].tolist()[:7]
ids = hest['study_id'].tolist()[:7]

abstracts = []
embs = []
checked_urls = []
checked_ids = []

for i, v in enumerate(urls):
    if pd.isna(v):
        continue
    abs = get_abstract(v)
    emb = get_embedding(abs)
    abstracts.append(abs)
    embs.append(np.array(emb))
    checked_urls.append(v)
    checked_ids.append(ids[i])

abs_df = pd.DataFrame(abstracts, columns=['abstract'], index=checked_ids)
emb_df = pd.DataFrame(embs, columns=[f'emb_{i}' for i in range(len(embs[0]))], index=checked_ids)
emb_df.to_csv(f'{os.getenv("HOME")}/data/spdb/emb_df.csv')
abs_df.to_csv(f'{os.getenv("HOME")}/data/spdb/abs_df.csv')