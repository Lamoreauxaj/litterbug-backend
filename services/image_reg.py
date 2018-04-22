from math import sqrt
import os
from os.path import join
from random import sample
import _pickle as pickle

from scipy import spatial
from PIL import Image
import numpy as np
import indicoio

indicoio.config.api_key = '9abbc6fbda605c77c14c9d2b3493eb0b'

def make_paths_list(location):
    print(__file__)
    d = []
    i = 0
    for root, dirs, files in os.walk(location):
        for image in files:
            if image.endswith(".jpg"):
                d.append(os.path.join(root, image))
                i += 1
    return d


def make_feat(image):
    return indicoio.image_features(image)


def make_feats(paths):
    feats = []
    for i in range(0, len(paths), 5):
        if i + 5 > len(paths):
            feats.extend(indicoio.image_features(paths[i:], batch=True))
        else:
            feats.extend(indicoio.image_features(paths[i:i+5], batch=True))
    return feats


def calculate_similarity_distance(image_feat1, image_feat2):
    d = 0
    for i in range(len(image_feat1)):
        d += pow(image_feat1[i] - image_feat2[i], 2)
    return sqrt(d)


def average_similarity(image_feat, other_feats):
    d = 0
    for i in range(len(other_feats)):
        d += calculate_similarity_distance(image_feat, other_feats[i])
    return d / len(other_feats)


def get_trash_can_feats():
    pkl_trash_can_path = join(os.path.dirname(__file__), 'trash_can_feats.pkl')
    try:
        feats = pickle.load(open(pkl_trash_can_path, 'rb'))
    except IOError:
        feats = make_feats(make_paths_list(join(os.path.dirname(__file__), 'trash_cans')))
        pickle.dump(feats, open(pkl_trash_can_path, 'wb'))
    return feats


def is_trash_can(path):
    trash_can_feats = get_trash_can_feats()
    image_feat = make_feat(path)
    similarity = average_similarity(image_feat, trash_can_feats)
    return similarity <= 25, similarity

