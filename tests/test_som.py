"""Self-organizing map: it organizes (quantization error drops) and maps inputs."""
import numpy as np

from hrl import SelfOrganizingMap


def _two_clusters(seed=0):
    rng = np.random.default_rng(seed)
    a = rng.normal([-1.0, 0.0], 0.12, size=(40, 2))
    b = rng.normal([1.0, 0.0], 0.12, size=(40, 2))
    return np.vstack([a, b])


def test_som_organizes():
    data = _two_clusters()
    som = SelfOrganizingMap(grid=(5, 5), dim=2, seed=1)
    before = som.quantization_error(data)
    som.train(data, epochs=40)
    after = som.quantization_error(data)
    assert after < before * 0.5          # training tightens the map substantially


def test_bmu_in_range_and_history():
    data = _two_clusters()
    som = SelfOrganizingMap(grid=(4, 6), dim=2, seed=2)
    hist = som.train(data, epochs=10, record=True)
    assert len(hist) == 11               # one snapshot per epoch + final
    i, j = som.bmu(np.array([1.0, 0.0]))
    assert 0 <= i < som.gw and 0 <= j < som.gh


if __name__ == "__main__":
    test_som_organizes()
    test_bmu_in_range_and_history()
    print("ok  som tests")
