import pandas as pd
import numpy as np

import joblib
import os
import regex

from robusta import utils


__all__ = ['save_result', 'load_result', 'remove_result', 'check_result']




def save_result(result, idx, name, detach_preds=True, path='./output',
                rewrite=False):

    result = dict(result)

    try:
        float(idx)
    except:
        raise ValueError("<save_result> version has changed!")

    if check_result(idx, path):
        if rewrite:
            remove_result(idx, path)
        else:
            raise IOError("Model {} already exists!".format(idx))


    if idx is None:
        # If not specified, use last + 1
        idx = last_result_idx(path) + 1

    for key in ['new_pred', 'oof_pred']:
        if detach_preds and key in result:

            # Detach predictions & delete from result
            y = result[key]
            del result[key]

            # Save predictions in separate files
            prefix = key.split('_')[0] # "new" or "oof" prefix
            fpath = os.path.join(path, '{} {} {}.csv'.format(idx, prefix, name))

            y.to_csv(fpath, header=True)

            # Logging
            print('{}  ({})'.format(fpath, utils.sizeof(y)))

    # Save main result
    fpath = os.path.join(path, '{} res {}.pkl'.format(idx, name))
    _ = joblib.dump(result, fpath)

    # Logging
    print('{}  ({})'.format(fpath, utils.sizeof(result)))



def load_result(idx, path='./output'):

    # Load main result
    for fname in os.listdir(path):
        if regex.match('{} res .*.pkl'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            result = joblib.load(fpath)
            break

    # Load predictions
    for fname in os.listdir(path):
        for prefix in ['new', 'oof']:
            if regex.match('{} {} .*.csv'.format(idx, prefix), fname) is not None:
                fpath = os.path.join(path, fname)
                result['{}_pred'.format(prefix)] = pd.read_csv(fpath, index_col=0)

    return result


def check_result(idx, path='./output'):

    fpaths = []

    for fname in os.listdir(path):

        if regex.match('{} res .*.pkl'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            fpaths.append(fpath)

        elif regex.match('{} new .*.csv'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            fpaths.append(fpath)

        elif regex.match('{} oof .*.csv'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            fpaths.append(fpath)

    return fpaths


def remove_result(idx, path='./output'):

    fpaths = check_result(idx, path)

    if fpaths:
        print('Deleting model {}...'.format(idx))
        raise FileNotFoundError('Model {} was not found!'.format(idx))

    for fname in os.listdir(path):

        if regex.match('{} res .*.pkl'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            print('{}  ({})'.format(fpath, utils.sizeof(y)))
            os.remove(fpath)

        elif regex.match('{} new .*.csv'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            print('{}  ({})'.format(fpath, utils.sizeof(y)))
            os.remove(fpath)

        elif regex.match('{} oof .*.csv'.format(idx), fname) is not None:
            fpath = os.path.join(path, fname)
            print('{}  ({})'.format(fpath, utils.sizeof(y)))
            os.remove(fpath)

    print()



def last_result_idx(path='./output'):
    fnames = os.listdir(path)
    str_indices = [fname.split(' ')[0] for fname in fnames]
    int_indices = [int(idx) for idx in str_indices if idx.isdigit()]
    last_idx = max(int_indices) if len(int_indices) > 0 else 0
    return last_idx
