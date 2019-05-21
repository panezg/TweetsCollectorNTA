import requests
import os
import json
import logging
import secrets
import urllib.parse
import datetime
from hashlib import sha1
from requests_oauthlib import OAuth1
import sys
import pandas as pd
from afinn import Afinn


class SentimentAnalyzer:
    def __init__(self):
        # initialize afinn sentiment analyzer
        self.af = Afinn()

    def analyze(self, text):
        article = text
        # compute sentiment scores (polarity) and labels
        #sentiment_scores = [af.score(article) for article in corpus]
        sentiment_score = self.af.score(article)
        #sentiment_category = ['positive' if score > 0 else 'negative' if score < 0 else 'neutral' for score in sentiment_scores]
        sentiment_category = 'positive' if sentiment_score > 0 else 'negative' if sentiment_score < 0 else 'neutral'

        return sentiment_score, sentiment_category
