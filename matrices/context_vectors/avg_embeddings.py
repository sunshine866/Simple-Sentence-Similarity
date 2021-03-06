import math
from collections import Counter

import numpy as np
from flair.data import Sentence
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


def run_context_avg_benchmark(sentences1, sentences2, model=None, use_stoplist=False, doc_freqs=None):
    if doc_freqs is not None:
        N = doc_freqs["NUM_DOCS"]

    sims = []
    for (sent1, sent2) in tqdm(zip(sentences1, sentences2), total=len(sentences1)):

        tokens1 = sent1.tokens_without_stop if use_stoplist else sent1.tokens
        tokens2 = sent2.tokens_without_stop if use_stoplist else sent2.tokens

        flair_tokens1 = sent1.tokens
        flair_tokens2 = sent2.tokens

        flair_sent1 = Sentence(" ".join(flair_tokens1))
        flair_sent2 = Sentence(" ".join(flair_tokens2))

        model.embed(flair_sent1)
        model.embed(flair_sent2)

        embeddings_map1 = {}
        embeddings_map2 = {}

        for token in flair_sent1:
            embeddings_map1[token.text] = np.array(token.embedding.data.tolist())

        for token in flair_sent2:
            embeddings_map2[token.text] = np.array(token.embedding.data.tolist())

        if len(tokens1) == 0 or len(tokens2) == 0:
            sims.append(0)
            continue

        tokfreqs1 = Counter(tokens1)
        tokfreqs2 = Counter(tokens2)

        weights1 = [tokfreqs1[token] * math.log(N / (doc_freqs.get(token, 0) + 1))
                    for token in tokfreqs1 if token in embeddings_map1] if doc_freqs else None
        weights2 = [tokfreqs2[token] * math.log(N / (doc_freqs.get(token, 0) + 1))
                    for token in tokfreqs2 if token in embeddings_map2] if doc_freqs else None

        embedding1 = np.average([embeddings_map1[token] for token in tokfreqs1 if token in embeddings_map1], axis=0, weights=weights1).reshape(1, -1)
        embedding2 = np.average([embeddings_map2[token] for token in tokfreqs2 if token in embeddings_map2], axis=0, weights=weights2).reshape(1, -1)

        sim = cosine_similarity(embedding1, embedding2)[0][0]
        sims.append(sim)

    return sims
