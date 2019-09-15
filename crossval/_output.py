import pandas as pd
import numpy as np

import datetime, time
import termcolor

from robusta.model import extract_model_name, extract_model
from robusta import utils




class CVLogger(object):

    def __init__(self, cv, verbose=1, prec=6):
        self.n_folds = cv.get_n_splits()
        self.verbose = verbose
        self.prec = prec

        self.messages = {}
        self.last_ind = -1

        self.busy = False


    def log(self, ind, result, n_digits=6):

        if ind is -1:
            return

        while True:
            if not self.busy:
                self.busy = True
                break
            else:
                time.sleep(0.1)

        # Fold index & score
        msg = 'FOLD{:>3}:   '.format(ind)
        msg += '{:.{prec}f}'.format(result['score'], prec=self.prec)

        # Save message
        self.messages[ind] = msg

        # If all previous folds are ready, print them
        for i in range(self.last_ind+1, self.n_folds):
            if i in self.messages.keys():
                if self.verbose >= 2 and i >= ind:
                    self._log_ind(i)
                    self.last_ind = i
            else:
                break

        self.busy = False


    def log_start(self, estimator, scorer):

        if self.verbose >= 2:
            msg = extract_model_name(estimator, short=False)
            utils.logmsg(msg)
            print()


    def log_final(self, results):

        if not self.verbose:
            return

        if self.verbose > 1:
            print()

        scores = results['score']

        m = '{:.{prec}f}'.format(np.mean(scores), prec=self.prec)
        s = '{:.{prec}f}'.format(np.std(scores), prec=self.prec)

        m = termcolor.colored(m, 'yellow')

        msg = 'AVERAGE:   {} ± {}'.format(m, s)
        utils.logmsg(msg)

        print()


    def _log_ind(self, ind):
        msg = self.messages[ind]
        utils.logmsg(msg)



def _extract_est_name(estimator, drop_type=False):
    """Extract name of estimator instance.

    Parameters
    ----------
    estimator : estimator object
        Estimator or Pipeline

    drop_type : bool (default=False)
        Whether to remove an ending of the estimator's name, contains
        estimator's type. For example, 'XGBRegressor' transformed to 'XGB'.


    Returns
    -------
    name : string
        Name of the estimator

    """
    name = estimator.__class__.__name__

    if name is 'Pipeline':
        last_step = estimator.steps[-1][1]
        name = _extract_est_name(last_step, drop_type=drop_type)

    elif name is 'TransformedTargetRegressor':
        regressor = estimator.regressor
        name = _extract_est_name(regressor, drop_type=drop_type)

    elif drop_type:
        for etype in ['Regressor', 'Classifier', 'Ranker']:
            if name.endswith(etype):
                name = name[:-len(etype)]

    return name
