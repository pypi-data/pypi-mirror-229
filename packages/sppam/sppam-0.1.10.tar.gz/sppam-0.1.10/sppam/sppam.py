"""
The SPPAM (Saddle Point Problem for AUC Maximization)

===============================================================
Author: Rolf Carlson, Carlson Research, LLC <hrolfrc@gmail.com>
License: 3-clause BSD
===============================================================

Implements F in:

Natole Jr, Michael & Ying, Yiming & Lyu, Siwei. (2019).
Stochastic AUC Optimization Algorithms With Linear Convergence.
Frontiers in Applied Mathematics and Statistics. 5. 10.3389/fams.2019.00030.
https://www.frontiersin.org/articles/10.3389/fams.2019.00030/full#B5

"""
import time
from collections import Counter

import numpy as np
from ortools.linear_solver.pywraplp import Solver
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.datasets import make_classification
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import minmax_scale
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


def scaled_predict(X, w):
    return np.array(
        minmax_scale(
            predict(X, w),
            feature_range=(-1, 1)
        )
    )


def predict(X, w):
    return np.sum(np.multiply(X, w), 1)


def lp_weights(X, y):
    """
        Get the classification coefficients using LP.

    Parameters
    ----------
        X : array-like, shape (n_samples, n_features)
            The training input features and samples.

        y : ground truth vector

    Returns
    -------
        weights

    References
    ----------

        1.  Classification of patterns using LP
        https://www.stat.cmu.edu/~ryantibs/convexopt-F13/scribes/lec2.pdf

        2.  LP formulation evolving to regularization and SVM
        Calf looks similar to dual problem on slide 14
        https://people.eecs.berkeley.edu/~russell/classes/cs194/f11/lectures/CS194%20Fall%202011%20Lecture%2005.pdf

        3. Natole Jr, Michael & Ying, Yiming & Lyu, Siwei. (2019).
        Stochastic AUC Optimization Algorithms With Linear Convergence.
        Frontiers in Applied Mathematics and Statistics. 5. 10.3389/fams.2019.00030.

    Examples
    --------
        >>> from sklearn.datasets import make_classification
        >>> from sklearn.metrics import roc_auc_score

        # Make a classification problem
        >>> X_d, y_d = make_classification(
        ...    n_samples=100,
        ...    n_features=10,
        ...    n_informative=5,
        ...    n_redundant=3,
        ...    n_classes=2,
        ...    hypercube=True,
        ...    random_state=8
        ... )

        Low complexity throws an exception
        >>> w_d, status_d = lp_weights(X_d, y_d)

        >>> np.round(w_d, 2).tolist()
        [-1.0, -0.39, -0.7, 0.43, -0.24, 0.67, -0.56, -1.0, -1.0, -1.0]

        The lp solver identifies good initial weights.
        >>> auc = roc_auc_score(y_true=y_d, y_score=predict(X_d, w_d))
        >>> np.round(auc, 2)
        0.99

        Scaling the weights gives the same predicted score
        >>> auc = roc_auc_score(y_true=y_d, y_score=scaled_predict(X_d, w_d))
        >>> np.round(auc, 2)
        0.99

    """

    feature_range = list(range(X.shape[1]))
    sample_range = list(range(X.shape[0]))

    solver = Solver.CreateSolver('GLOP')

    # The following recommendation to improve GLOP performance degrades the AUC.
    # https: https://developers.google.com/optimization/lp/lp_advanced#choice_of_solvers_and_algorithms
    # uncomment to see the relative performance in calf_lp.ipynb
    # solver.use_dual_simplex = True

    if not solver:
        raise RuntimeError("GLOP solver unavailable")
    solver.SetTimeLimit(100000)

    # n_plus and n_minus are the numbers of samples of the positive and negative cases.
    # protect against division by zero.
    n_plus = max(Counter(y)[1], 1)
    n_minus = max(Counter(y)[0], 1)

    # w[i] is 0 if feature i is excluded
    # otherwise the weight is 1 or -1
    w = {}
    for j in feature_range:
        w[j] = solver.NumVar(-1, 1, 'w[%i]' % j)

    pos = (1 / n_plus) * sum([X[i][j] * w[j] for j in feature_range for i in sample_range if y[i] == 1])
    neg = (1 / n_minus) * sum([X[i][j] * w[j] for j in feature_range for i in sample_range if y[i] == 0])

    # the slack variables, p, significantly increase run-time.
    # if complexity == 'high':
    p = {}
    # sample probability constraints
    for i in sample_range:
        p[i] = solver.NumVar(0, solver.infinity(), 'p[%i]' % i)
        constraint_expr = sum([X[i][j] * w[j] for j in feature_range])
        if y[i] == 1:
            solver.Add(constraint_expr + p[i] >= 1)
        else:
            solver.Add(constraint_expr - p[i] <= -1)
    row_slack = sum([p[i] for i in sample_range])

    # Maximize the difference between the positive and negative cases
    # Minimizing the sum of the coefficient vector is a way to
    # include regularization of the weights, like LASSO.
    # Minimizing the weight sum does not seem to improve AUC.
    # https://scikit-learn.org/stable/modules/linear_model.html#:~:text=The%20lasso%20estimate,the%20coefficient%20vector.
    solver.Maximize(pos - neg - row_slack)

    # solve the classification problem
    status = solver.Solve()
    assert len(w) == len(feature_range)

    weights = [v.solution_value() for v in w.values()]
    return weights, status


# noinspection PyAttributeOutsideInit
class SPPAM(ClassifierMixin, BaseEstimator):
    """ The SPPAM (Saddle Point Problem for AUC Maximization) classifier

    Attributes
    ----------
        coef_ : array of shape (n_features, )
            Estimated coefficients for the linear fit problem.  Only
            one target should be passed, and this is a 1D array of length
            n_features.

        n_features_in_ : int
            Number of features seen during :term:`fit`.

        classes_ : list
            The unique class labels

        fit_time_ : float
            The number of seconds to fit X to y

    Examples
    --------
        >>> import numpy
        >>> from sklearn.datasets import make_classification as mc
        >>> X, y = mc(n_features=2, n_redundant=0, n_informative=2, n_clusters_per_class=1, random_state=42)
        >>> numpy.round(X[0:3, :], 2)
        array([[ 1.23, -0.76],
               [ 0.7 , -1.38],
               [ 2.55,  2.5 ]])

        >>> y[0:3]
        array([0, 0, 1])

        >>> cls = SPPAM().fit(X, y)
        >>> cls.score(X, y)
        0.95

        >>> np.round(cls.coef_, 4)
        array([-0.2463,  1.    ])

        >>> numpy.round(cls.score(X, y), 2)
        0.95

        >>> cls.fit_time_ > 0
        True

        >>> cls.predict(np.array([[3, 5]]))
        array([0])

        >>> cls.predict_proba(np.array([[3, 5]]))
        array([[1., 0.]])

        """

    def __init__(self):
        """ Initialize SPPAM """
        pass

    def fit(self, X, y):
        """ Fit the model according to the given training data.

        Parameters
        ----------
            X : {array-like, sparse matrix} of shape (n_samples, n_features)
                Training vector, where n_samples is the number of samples and n_features is the number of features.

            y : array-like of shape (n_samples,)
                Target vector relative to X.

        Returns
        -------
            self
                Fitted estimator.

        """
        if y is None:
            raise ValueError('requires y to be passed, but the target y is None')

        X, y = check_X_y(X, y, accept_sparse=False)
        self.n_features_in_ = X.shape[1]
        self.classes_ = unique_labels(y)
        self.X_ = X
        self.y_ = y

        start = time.time()
        self.w_, self.status_ = lp_weights(X, y)
        self.fit_time_ = time.time() - start
        self.coef_ = self.w_
        self.is_fitted_ = True
        return self

    def decision_function(self, X):
        """ Identify confidence scores for the samples

        Parameters
        ----------
            X : array-like, shape (n_samples, n_features)
                The training input features and samples

        Returns
        -------
            y_d : the decision vector (n_samples)

        """
        check_is_fitted(self, ['is_fitted_', 'X_', 'y_'])

        X = self._validate_data(X, accept_sparse="csr", reset=False)
        scores = np.array(
            minmax_scale(
                predict(X, self.w_),
                feature_range=(-1, 1)
            )
        )
        return scores

    def predict(self, X):
        """Predict class labels for samples in X.

        Parameters
        ----------
            X : {array-like, sparse matrix} of shape (n_samples, n_features)
                The data matrix for which we want to get the predictions.

        Returns
        -------
            y_pred : ndarray of shape (n_samples,)
                Vector containing the class labels for each sample.

        """
        check_is_fitted(self, ['is_fitted_', 'X_', 'y_'])
        X = check_array(X)

        if len(self.classes_) < 2:
            y_class = self.y_
        else:
            # and convert to [0, 1] classes.
            y_class = np.heaviside(self.decision_function(X), 0).astype(int)
            # get the class labels
            y_class = [self.classes_[x] for x in y_class]
        return np.array(y_class)

    def predict_proba(self, X):
        """Probability estimates for samples in X.

        Parameters
        ----------
            X : array-like of shape (n_samples, n_features)
                Vector to be scored, where n_samples is the number of samples and
                n_features is the number of features.

        Returns
        -------
            T : array-like of shape (n_samples, n_classes)
                Returns the probability of the sample for each class in the model,
                where classes are ordered as they are in `self.classes_`.

        """
        check_is_fitted(self, ['is_fitted_', 'X_', 'y_'])
        X = check_array(X)

        y_proba = np.array(
            minmax_scale(
                self.decision_function(X),
                feature_range=(0, 1)
            )
        )
        class_prob = np.column_stack((1 - y_proba, y_proba))
        return class_prob

    def transform(self, X):
        """ Reduce X to the features that contribute positive AUC.

        Parameters
        ----------
            X : array-like, shape (n_samples, n_features)
                The training input features and samples

        Returns
        -------
            X_r : array of shape [n_samples, n_selected_features]
                The input samples with only the selected features.

        """
        check_is_fitted(self, ['is_fitted_', 'X_', 'y_'])
        X = check_array(X)

        return X[:, np.asarray(self.coef_).nonzero()]

    def fit_transform(self, X, y):
        """ Fit to the data, then reduce X to the features that contribute positive AUC.

        Parameters
        ----------
            X : array-like, shape (n_samples, n_features)
                The training input features and samples

            y : array-like of shape (n_samples,)
                Target vector relative to X.

        Returns
        -------
            X_r : array of shape [n_samples, n_selected_features]
                The input samples with only the selected features.

        """
        return self.fit(X, y).transform(X)

    def _more_tags(self):
        return {
            'poor_score': True,
            'non_deterministic': True,
            'binary_only': True
        }
