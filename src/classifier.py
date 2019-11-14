from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy


class Classifier:
    # Wrapper around RandomForestClassifier
    def __init__(self, x: numpy.ndarray, y: numpy.ndarray):
        self._scale = StandardScaler().fit(x)
        self._x = self._scale.transform(x)
        self._y = y
        self._classifier = RandomForestClassifier()

    def train(self):
        self._classifier.fit(self._x, self._y)

    def predict(self, x):
        return self._classifier.predict(self._scale.transform(x))
