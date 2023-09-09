# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 生成仿真评论
"""
import os
from jieba import analyse
from loguru import logger
from textgen.unsup_generation.tgls_util import (
    load_list,
    caculate_word_idf,
    text2review,
    find_word_phrase,
    get_seg_pos,
    text2seg_pos,
    get_aspect_express,
    get_candidate_aspect,
    merge_aspect_express,
    fake_review_filter,
    generate_reviews,
    NSDict,
    PairPattSort,
)

pwd_path = os.path.abspath(os.path.dirname(__file__))
default_stopwords_path = os.path.join(pwd_path, '../data/stopwords.txt')
default_pos_adj_word_path = os.path.join(pwd_path, '../data/HowNetPOSWord.txt')


class TglsModel:
    def __init__(self, docs=None, stopwords_path=default_stopwords_path, pos_adj_word_path=default_pos_adj_word_path):
        """
        Initialize the model with the given docs
        """
        # Load stop words
        self.stopwords = set(load_list(stopwords_path))
        if docs is None:
            # Use jieba IDF
            tfidf = analyse.TFIDF()
            self.word_idf = tfidf.idf_freq
        else:
            logger.debug(f'Docs size: {len(docs)}')
            # 计算除去停用词的每个词的idf值
            self.word_idf, self.seg_pos_text = caculate_word_idf(docs, self.stopwords)
            review_list, all_word = text2review(self.seg_pos_text)
            phrase_list = find_word_phrase(all_word, review_list)
            logger.debug(f'Find {len(phrase_list)} new words, top10: {phrase_list[:10]}')
        logger.debug(f'Load {len(self.word_idf)} words idf, top10: {list(self.word_idf.items())[:10]}')
        # 加载正向情感词典
        self.pos_adj_word = load_list(pos_adj_word_path)

    def generate(self, doc, num_steps=1000, is_uniq=True):
        """
        Generate similar texts from a given doc
        """
        seg_pos_text = [get_seg_pos(l) for l in doc]
        seg_list, pos_list, seg_review_list = text2seg_pos(seg_pos_text, pattern='[。！？，～]')
        raw_aspect_list = get_candidate_aspect(seg_list, pos_list, self.pos_adj_word, self.stopwords, self.word_idf)

        # 构建候选集合
        N = NSDict(seg_list, pos_list, raw_aspect_list)
        ns_dict = N.build_nsdict()
        # 候选集合排序
        P = PairPattSort(ns_dict)
        pair_score = P.sort_pair()

        # 得到正确的观点表达候选
        pair_useful = {}
        baseline = 0.1 * len(pair_score)
        for i, item in enumerate(pair_score):
            if i <= baseline:
                aspect, opinion = item[0].split('\t')
                if aspect in pair_useful:
                    pair_useful[aspect].append(opinion)
                else:
                    pair_useful[aspect] = [opinion]

        # 从原始评论中抽取观点表达
        aspect_express = get_aspect_express(seg_review_list, pair_useful)
        # 字符匹配合并aspect
        merged_aspect_express, opinion_set = merge_aspect_express(aspect_express, pair_useful)
        # 生成相似评论
        generated_raw_reviews = generate_reviews(merged_aspect_express, num_steps=num_steps)
        if len(generated_raw_reviews) == 0:
            logger.warning(f'generated is empty, given doc min size: 100, now doc size: {len(doc)}, please add data.')
        # 去除低质量评论
        results = fake_review_filter(generated_raw_reviews, opinion_set, is_uniq=is_uniq)

        return results
