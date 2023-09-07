import os
import random

import numpy as np
import torch
import subprocess
import tensorflow as tf


def get_device(mode="pt"):
    if mode == "pt":
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    else:
        return tf.config.list_logical_devices()[0]


def set_seed(seed):
    # Set global seeds to for reproducibility
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_labels(class_ix, class_list, probs=None, max_num_labels=10):
    labels = []
    for il, l in enumerate(class_ix):
        lab = None
        if type(l) == list:
            if len(l) <= max_num_labels:
                if probs is not None:
                    lab = " ".join(
                        ["{}:{}".format(class_list[i], probs[il][i])
                         for i in l]
                    )
                else:
                    lab = " ".join([class_list[c] for c in l])
            else:
                labels.append("Multiple classes")
        else:
            if probs is not None:
                lab = "{}:{}".format(class_list[l], probs[il])
            else:
                lab = class_list[l]
        labels.append(lab)
    return labels


def entropy(matrix, r=2):
    flat_matrix = matrix.flatten()
    binned = torch.round(flat_matrix, decimals=r)
    # Calculate probability of each value
    _, counts = torch.unique(binned, return_counts=True)
    probabilities = counts / counts.sum()

    # Calculate entropy
    entropy = -(probabilities * torch.log2(probabilities)).sum()

    return entropy


def calc_entanglement(baseline, logits):
    max_logit = np.amax(logits, axis=-1, keepdims=True)
    e = (logits - baseline) / (max_logit - baseline)
    return e


def flatten_dict(d, parent_key="", sep="_"):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.update(flatten_dict(
                    {f"{k}{sep}{i}": item}, parent_key, sep=sep))
        else:
            items[new_key] = v
    return items


def normalise(x):
    if (x.max() - x.min()) == 0:
        return x
    x = (x - x.min()) / (x.max() - x.min())
    return x
