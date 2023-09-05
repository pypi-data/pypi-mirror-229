import os
import re
import shutil
import warnings

import numpy as np
import netCDF4 as Nc
from scipy import interpolate

from MetDL.utils.geotest import testLatitude, testLongitude


class DataReader:
    """
    AIWA AI 확장 라이브러리 DataReader class
    """
    def __init__(self, cacheQueue, cache, useCache, saveCache):
        if not os.path.isdir(cache) and saveCache:
            os.makedirs(cache)
            warnings.warn("cache path not exist: {} \ncache path made by AI Library".format(cache))
        self.cachePath = cache
        self.useCache = useCache
        self.saveCache = saveCache

        self.cachedData = [None]
        self.cachedKey = [{"bandData": None,
                           "interpolateMethod": None}]
        self.cacheQueue = cacheQueue

    @staticmethod
    def initialize(cacheQueue, cache, useCache, saveCache):
        return DataReader(cacheQueue, cache, useCache, saveCache)

    def get(self, datetime, bandData, dstLatitude, dstLongitude, interpolateMethod):
        key = {"bandData": bandData,
               "interpolateMethod": interpolateMethod}

        if key in self.cachedKey:
            data = self.cachedData[self.cachedKey.index(key)]
        else:
            cacheName = f"{bandData['dataPath'].split('/')[-1]}_{bandData['itemPath']}.nc"
            cacheName = re.sub('[\/:*?"<>|]','_', cacheName)
            cacheDirectory = f"{datetime['year']}/{datetime['month']}/{datetime['day']}"
            cachePath = os.path.join(self.cachePath, cacheDirectory, cacheName)
            if os.path.isfile(cachePath):
                if self.useCache:
                    try:
                        cacheData = Nc.Dataset(cachePath)
                        data = cacheData["/data"][:]
                        mask = cacheData["/mask"][:]
                        lat = cacheData["/lat"][:]
                        lon = cacheData["/lon"][:]
                        if lat != dstLatitude or lon != dstLongitude:
                            raise Exception
                        data = np.ma.masked_array(data, mask)
                        cacheData.close()
                    except Exception as e:
                        data, lat, lon = self.getData(bandData)
                        data, dstLatitude, dstLongitude = self.bilinearInterpolate(data, lat, lon, dstLatitude, dstLongitude,
                                                                           method=interpolateMethod)
                        replaceNanValue = DataReader.getFillvalue(data, replaceNanValue=bandData["replaceNanValue"])
                        data = np.ma.masked_invalid(data)
                        data.data[data.mask] = replaceNanValue
                        self.saveCacheData(cachePath, bandData, data, dstLatitude, dstLongitude)
                else:
                    data, lat, lon = self.getData(bandData)
                    data, dstLatitude, dstLongitude = self.bilinearInterpolate(data, lat, lon, dstLatitude, dstLongitude,
                                                                       method=interpolateMethod)
                    replaceNanValue = DataReader.getFillvalue(data, replaceNanValue=bandData["replaceNanValue"])
                    data = np.ma.masked_invalid(data)
                    data.data[data.mask] = replaceNanValue
                    self.saveCacheData(cachePath, bandData, data, dstLatitude, dstLongitude)
            else:
                data, lat, lon = self.getData(bandData)
                data, dstLatitude, dstLongitude = self.bilinearInterpolate(data, lat, lon, dstLatitude, dstLongitude,
                                                                   method=interpolateMethod)
                replaceNanValue = DataReader.getFillvalue(data, replaceNanValue=bandData["replaceNanValue"])
                data = np.ma.masked_invalid(data)
                data.data[data.mask] = replaceNanValue
                self.saveCacheData(cachePath, bandData, data, dstLatitude, dstLongitude)

            self.cachedData.append(data)
            self.cachedKey.append(key)
            if len(self.cachedKey) > self.cacheQueue:
                self.cachedData = self.cachedData[1:]
                self.cachedKey = self.cachedKey[1:]

            testLatitude(lat)
            testLongitude(lon)
            testLatitude(dstLatitude)
            testLongitude(dstLongitude)
        if isinstance(data.mask, np.bool8):
            data.mask = np.full(data.shape, False)
        return data.data, data.mask

    def getData(self, bandData):
        raise NotImplementedError

    def saveCacheData(self, path, bandData, data, lat, lon):
        if self.saveCache:
            try:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                shape = data.shape
                cacheFile = Nc.Dataset(path, "w")
                cacheFile.type = bandData["type"]
                cacheFile.dataPath = bandData["dataPath"]
                cacheFile.itemPath = bandData["itemPath"]
                cacheFile.createDimension("lineNumber", shape[0])
                cacheFile.createDimension("pixelNumber", shape[1])
                cacheFile.createVariable("data", np.float32, ("lineNumber", "pixelNumber", ),
                                          complevel=1, chunksizes=shape, zlib=True)
                cacheFile.createVariable("mask", np.int8, ("lineNumber", "pixelNumber", ),
                                          complevel=1, chunksizes=shape, zlib=True)
                cacheFile.createVariable("lat", np.float32, ("lineNumber", "pixelNumber",),
                                          complevel=1, chunksizes=shape, zlib=True)
                cacheFile.createVariable("lon", np.float32, ("lineNumber", "pixelNumber",),
                                          complevel=1, chunksizes=shape, zlib=True)

                maxIndex = np.unravel_index(lat.argmax(), lat.shape)

                if maxIndex[len(maxIndex)//3] > maxIndex[-len(maxIndex)//3]:
                    cacheFile["/data"][:] = data.data[::-1, :]
                    cacheFile["/mask"][:] = data.mask[::-1, :]
                    cacheFile["/lat"][:] = lat[::-1, :]
                    cacheFile["/lon"][:] = lon[::-1, :]
                else:
                    cacheFile["/data"][:] = data.data
                    cacheFile["/mask"][:] = data.mask
                    cacheFile["/lat"][:] = lat
                    cacheFile["/lon"][:] = lon
                cacheFile.close()
            except BaseException as e:
                warnings.warn("cache save failed: {} \n{}".format(path, e))
                shutil.rmtree(path, ignore_errors=True)

    def bilinearInterpolate(self, src, srcLatitude, srcLongitude, dstLatitude, dstLongitude, replaceNanValue=None, method='nearest'):
        """
        원본 Data Array를 입력한 latitude, longitude에 맞춰 subset & interpolate

        Args:
            src: 원본 Data Array
            srcLatitude: 원본 Data Array의 latitude
            srcLongitude: 원본 Data Array의 longitude
            dstLatitude: 목표 latitude
            dstLongitude: 목표 longitude
            method: interpolate method
        """
        if method == "skip":
            if not isinstance(src, np.ma.masked_array):
                src = np.ma.masked_array(src, np.full(src.shape, False))
            return src, srcLatitude, srcLongitude

        srcMask = np.full(dstLatitude.shape, False)

        dstLatitudeNan = np.isnan(dstLatitude)
        dstLongitudeNan = np.isnan(dstLongitude)
        dstLatitude[dstLatitudeNan] = np.nanmedian(dstLatitudeNan)
        dstLongitude[dstLongitudeNan] = np.nanmedian(dstLongitudeNan)

        if isinstance(src, np.ma.masked_array):
            if np.sum(src.mask) > 0:
                srcMask, _, _ = self.bilinearInterpolate(src.mask, srcLatitude, srcLongitude, dstLatitude, dstLongitude)

        srcMask[dstLatitudeNan] = True
        srcMask[dstLongitudeNan] = True

        src = np.array(src)
        srcLatitude = np.array(srcLatitude)
        srcLongitude = np.array(srcLongitude)
        if len(np.where(dstLongitude > 180)) > 0:
            srcLongitude[np.where(srcLongitude < np.min(dstLongitude))] += 360

        points = np.concatenate((srcLongitude.flatten()[:, np.newaxis], srcLatitude.flatten()[:, np.newaxis]), axis=1)
        areaSrcToDst, points, src = DataReader.getDstAreaFromSrc(dstLatitude, dstLongitude, points, src)

        src = np.ma.masked_array(src)

        result = interpolate.griddata(points, src, (dstLongitude, dstLatitude), method=method)
        result = np.ma.masked_array(result, srcMask, fill_value=replaceNanValue)

        return result, dstLatitude, dstLongitude

    @staticmethod
    def getDstAreaFromSrc(lat, lon, points, src):
        """
        Himawari-8 파일 attribute overwrite

        Args:
            lat: 원본 Data Array를 자를 latitude
            lon: 원본 Data Array를 자를 longitude
            points: 원본 Data Array의 latitude, longitude
            src: 원본 Data Array
        """
        min_lon = np.nanmin(lon)
        max_lon = np.nanmax(lon)
        min_lat = np.nanmin(lat)
        max_lat = np.nanmax(lat)
        areaSrcToDst = np.where((points[:, 0] >= min_lon) &
                                   (points[:, 0] <= max_lon) &
                                   (points[:, 1] >= min_lat) &
                                   (points[:, 1] <= max_lat))
        if len(areaSrcToDst[0]) > 0:
            points = points[areaSrcToDst]
            src = src[:].ravel()[areaSrcToDst]
        else:
            areaSrcToDst = np.where(points[:, 0])
            src = src[:].ravel()
        return areaSrcToDst, points, src

    @staticmethod
    def getFillvalue(data, replaceNanValue):
        if replaceNanValue is None:
            replaceNanValue = 'median'

        if isinstance(replaceNanValue, str):
            if replaceNanValue not in ['median', 'mean']:
                raise Exception("replaceNanValue should be one of ['median', 'mean'] or specific numeric value")

        if replaceNanValue == 'median':
            replaceNanValue = np.median(data[~data.mask])
        elif replaceNanValue == 'mean':
            replaceNanValue = np.nanmean(data[~data.mask])

        return replaceNanValue


if __name__ == "__main__":
    pass
