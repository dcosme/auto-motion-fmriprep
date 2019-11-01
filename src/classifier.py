from sklearn.ensemble import RandomForestClassifier
import numpy


class Classifier:
    # Wrapper around RandomForestClassifier
    def __init__(self, x: numpy.ndarray, y: numpy.ndarray):
        self._x = x
        self._y = y
        self._classifier = RandomForestClassifier()

    def train(self):
        self._classifier.fit(self._x, self._y)

    def predict(self, x):
        return self._classifier.predict(x)
