import numpy as np


def testLatitude(latitude):
    assert isinstance(latitude, np.ndarray), 'latitude data type must be numpy array'
    latitudeRange = np.where((latitude > 90) | (latitude < -90))
    assert len(latitudeRange) == 2, 'latitude data must be 2d array'
    assert len(latitudeRange[0]) == 0, 'latitude data must be in 90 ~ -90'


def testLongitude(longitude):
    assert isinstance(longitude, np.ndarray), 'longitude data type must be numpy array'
    longitudeRange = np.where((longitude > 180) | (longitude < -180))
    assert len(longitudeRange) == 2, 'longitude data must be 2d array'
    assert len(longitudeRange[0]) == 0, 'longitude data must be in 180 ~ -180'
