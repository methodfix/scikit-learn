import numpy as np

from numpy.testing import assert_array_almost_equal, assert_almost_equal
from scikits.learn import neighbors, manifold
from scikits.learn.utils.fixes import product

eigen_solvers = ['dense', 'arpack']

try:
    import pyamg
    eigen_solvers.append('lobpcg')
except ImportError:
    pass

#----------------------------------------------------------------------
# Test LLE by computing the reconstruction error on some manifolds.

def test_lle_simple_grid():
    # grid of equidistant points in 2D, out_dim = n_dim
    X = np.array(list(product(range(5), repeat=2)))
    out_dim = 2
    clf = manifold.LocallyLinearEmbedding(n_neighbors=5, out_dim=out_dim)
    tol = .1

    N = neighbors.kneighbors_graph(X, clf.n_neighbors, mode='barycenter').todense()
    reconstruction_error = np.linalg.norm(np.dot(N, X) - X, 'fro')
    assert reconstruction_error < tol

    for solver in eigen_solvers:
        clf.fit(X, eigen_solver=solver)
        assert clf.embedding_.shape[1] == out_dim
        reconstruction_error = np.linalg.norm(
            np.dot(N, clf.embedding_) - clf.embedding_, 'fro') ** 2
        # FIXME: ARPACK fails this test ...
        if solver != 'arpack':
            assert reconstruction_error < tol
            assert_almost_equal(clf.reconstruction_error_, reconstruction_error, decimal=4)
    noise = np.random.randn(*X.shape) / 100
    assert np.linalg.norm(clf.transform(X + noise) - clf.embedding_) < tol


def test_lle_manifold():
    # similar test on a slightly more complex manifold
    X = np.array(list(product(range(20), repeat=2)))
    X = np.c_[X, X[:, 0]**2 / 20]
    out_dim = 2
    clf = manifold.LocallyLinearEmbedding(n_neighbors=5, out_dim=out_dim)
    tol = .5

    N = neighbors.kneighbors_graph(X, clf.n_neighbors, mode='barycenter').todense()
    reconstruction_error = np.linalg.norm(np.dot(N, X) - X)
    assert reconstruction_error < tol

    for solver in eigen_solvers:
        clf.fit(X, eigen_solver=solver)
        assert clf.embedding_.shape[1] == out_dim
        reconstruction_error = np.linalg.norm(
            np.dot(N, clf.embedding_) - clf.embedding_, 'fro') ** 2
        assert reconstruction_error < tol
        assert_almost_equal(clf.reconstruction_error_, reconstruction_error)


def test_pipeline():
    # check that LocallyLinearEmbedding works fine as a Pipeline
    from scikits.learn import pipeline, datasets
    iris = datasets.load_iris()
    clf = pipeline.Pipeline(
        [('filter', manifold.LocallyLinearEmbedding()),
         ('clf', neighbors.NeighborsClassifier())])
    clf.fit(iris.data, iris.target)
    assert clf.score(iris.data, iris.target) > .7


if __name__ == '__main__':
    import nose
    nose.runmodule()
