#!/usr/bin/env python3
from typing import Dict, List, Tuple

from classifiercluster import Classifiers

from premium.classifiers.bases import TreeModel


class Xgboost(TreeModel):

    def __init__(self, vectorizer='tfidf',tokenizer=None):
        super().__init__(vectorizer,tokenizer)
        self.model = Classifiers().xgb
        self.name = 'xgboost:{}'.format(vectorizer)

    def run(self, train, test, threshold=0.5):
        return self.inner_run(train, test, threshold=threshold)


class Catboost(TreeModel):

    def __init__(self, vectorizer='tfidf',tokenizer=None):
        super().__init__(vectorizer,tokenizer)
        self.model = Classifiers().cat
        self.name = 'catboost:{}'.format(vectorizer)

    def run(self, train, test):
        return self.inner_run(train, test)


class Lightgbm(TreeModel):

    def __init__(self, vectorizer='tfidf',tokenizer=None):
        super().__init__(vectorizer,tokenizer)
        self.model = Classifiers().gbm
        self.name = 'lightgbm:{}'.format(vectorizer)

    def run(self, train, test):
        return self.inner_run(train, test)
