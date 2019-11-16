import hashlib
import os
import random
import re
import json
import ftfy


import tensorflow as tf


class Sampler(object):
    def __init__(self, mode, data_path, enc, n_ctx):
        self.mode = mode
        self.data_path = data_path
        self.enc = enc
        with open(self.data_path + '/coqa-{}-v1.0.json'.format(mode), 'r') as f:
            self.data = json.load(f)["data"]
        self.num_samples = len(self.data)
        self.n_ctx = n_ctx

    def sample(self,):
        for i, x in enumerate(self.data):

            len_sample = 0

            story = x['story']
            questions = x['questions']
            answers = x['answers']

            story = ftfy.fix_text(story)
            story = story.strip()
            enc_story = self.enc.encode(story)

            for q, a in zip(questions, answers):
                enc_qq = self.enc.encode(
                    ftfy.fix_text("\nQ: " + q['input_text']).strip())
                enc_aa = self.enc.encode(
                    ftfy.fix_text("\nA: " + a['input_text']).strip())

                if len(enc_story) + len(enc_qq) + len(enc_aa) <= self.n_ctx:
                    enc_story = enc_story + enc_qq + enc_aa
                else:
                    break

            if len(enc_story) < self.n_ctx:
                yield enc_story, enc_story[1:]


def create_dataset(enc, length, dataset_path, batch_size, steps_per_epoch):
    
    data_sampler = Sampler('train', dataset_path, enc, length)

    ds = tf.data.Dataset.from_generator(
        data_sampler.sample,
        (tf.int32, tf.int32),
        (tf.TensorShape([None]), tf.TensorShape([None]))
        )

    ds = ds.shuffle(buffer_size=steps_per_epoch).batch(batch_size, drop_remainder=True)

    return ds