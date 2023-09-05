import os
import warnings
import datetime
from glob import glob

import numpy as np
from torch.utils import data

from MetDL.utils.geotest import testLatitude, testLongitude

warnings.filterwarnings("ignore")


class Dataset(data.dataset.Dataset):
    """
    AIWA AI 확장 라이브러리 Dataset class
    """

    def __init__(self, config, timeStart, timeEnd, timeDelta, timeParser, geocoding_info,
                 windowWidth, windowHeight, windowStride, sequenceLength, interpolateMethod,
                 preprocess_fn, cacheQueue, cacheDirectory, useCache, saveCache, replaceNanValue,
                 targetGeocoding, order, timeInterpolate, gk2aAmiCalibrationTable, dapsAbbrIdxLevelTable,
                 *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            config: Dataset 실행 정보를 담은 python dictionary
        """
        super(Dataset, self).__init__(*args, **kwargs)
        self.config = config

        self.data = []
        self.datafile = []

        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.timeDelta = timeDelta
        self.timeParser = timeParser

        self.targetGeocoding = targetGeocoding

        if self.targetGeocoding:
            leftUpperPixelY, leftUpperPixelX, rightLowerPixelY, rightLowerPixelX, target, pixelNumber, lineNumber = geocoding_info
            self.dstDataset = {}
            self.leftUpperPixelY = leftUpperPixelY
            self.leftUpperPixelX = leftUpperPixelX
            self.rightLowerPixelY = rightLowerPixelY
            self.rightLowerPixelX = rightLowerPixelX
            self.target = target
            self.dstLatitude, self.dstLongitude = None, None
        else:
            rl_lat, lu_lat, lu_lon, rl_lon, pixelNumber, lineNumber = geocoding_info
            dstLatitude = (np.linspace(rl_lat, lu_lat, lineNumber))
            dstLongitude = (np.linspace(lu_lon, rl_lon, pixelNumber))
            dstLongitude[dstLongitude > 180] -= 360
            dstLatitude, dstLongitude = np.meshgrid(dstLatitude, dstLongitude)
            self.dstLatitude, self.dstLongitude = np.rot90(np.ma.masked_array(dstLatitude)), np.rot90(np.ma.masked_array(dstLongitude))
            testLatitude(self.dstLatitude)
            testLongitude(self.dstLongitude)

        self.processedShape = (lineNumber, pixelNumber)
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.stride = windowStride
        self.windowXNum = int((pixelNumber - self.windowWidth + self.stride) / self.stride)
        self.windowYNum = int((lineNumber - self.windowHeight + self.stride) / self.stride)
        self.minWindowX = pixelNumber - self.windowWidth
        self.minWindowY = lineNumber - self.windowHeight
        self.windowNum = self.windowXNum * self.windowYNum
        self.sequenceLength = sequenceLength
        self.interpolateMethod = interpolateMethod
        self.preprocessFunction = preprocess_fn

        self.cacheQueue = cacheQueue
        self.cacheDirectory = cacheDirectory
        self.useCache = useCache
        self.saveCache = saveCache

        self.replaceNanValue = replaceNanValue

        self.order = order

        self.timeInterpolate = timeInterpolate

        self.gk2aAmiCalibrationTable = gk2aAmiCalibrationTable
        self.dapsAbbrIdxLevelTable = dapsAbbrIdxLevelTable

        self.dataReaders = self.getDataReaders()
        self.datas = self.getDatasets()

    @staticmethod
    def initialize(config, execute_config, timeStart, timeEnd, timeDelta, timeParser,
                   windowWidth=0, windowHeight=0, windowStride=1, sequenceLength=1, interpolateMethod='nearest',
                   preprocess_fn=None, cacheQueue=1, cacheDirectory="", useCache=False, saveCache=False,
                   replaceNanValue='median', timeInterpolate='error', gk2aAmiCalibrationTable=None,
                   dapsAbbrIdxLevelTable=None, *args, **kwargs):

        targetGeocoding = False
        if "target" in execute_config["geocoding"]:
            targetGeocoding = True
            leftUpperPixelY = execute_config["geocoding"]["left_upper_pixelY"]
            leftUpperPixelX = execute_config["geocoding"]["left_upper_pixelX"]
            rightLowerPixelY = execute_config["geocoding"]["right_lower_pixelY"]
            rightLowerPixelX = execute_config["geocoding"]["right_lower_pixelX"]
            target = execute_config["geocoding"]["target"]
            pixelNumber = abs(rightLowerPixelX - leftUpperPixelX)
            lineNumber = abs(rightLowerPixelY - leftUpperPixelY)
            geocoding_info = [leftUpperPixelY, leftUpperPixelX, rightLowerPixelY, rightLowerPixelX, target,
                              pixelNumber, lineNumber]

        else:
            leftUpperLat = execute_config["geocoding"]["left_upper_lat"]
            leftUpperLon = execute_config["geocoding"]["left_upper_lon"]
            rightLowerLat = execute_config["geocoding"]["right_lower_lat"]
            rightLowerLon = execute_config["geocoding"]["right_lower_lon"]
            pixelNumber = abs(execute_config["geocoding"]["width"])
            lineNumber = abs(execute_config["geocoding"]["height"])
            geocoding_info = [rightLowerLat, leftUpperLat, leftUpperLon, rightLowerLon, pixelNumber, lineNumber]

            assert leftUpperLat <= 90, 'lu_lat must be smaller than 90'
            assert leftUpperLon >= -180, 'lu_lon must be bigger than -180'
            assert rightLowerLon <= 360, 'rl_lon must be smaller than 180'
            assert rightLowerLat >= -90, 'rl_lat must be bigger than -90'
            assert rightLowerLon > leftUpperLon, 'rl_lon must be bigger than lu_lon'
            assert leftUpperLat > rightLowerLat, 'lu_lat must be bigger than rl_lat'

        if preprocess_fn is None or not isinstance(preprocess_fn, list):
            preprocess_fn = []

        try:
            if type(pixelNumber) is not int:
                pixelNumber = int(pixelNumber)
            if type(lineNumber) is not int:
                lineNumber = int(lineNumber)
            if type(windowWidth) is not int:
                windowWidth = int(windowWidth)
            if windowWidth == 0:
                windowWidth = pixelNumber
            if type(windowHeight) is not int:
                windowHeight = int(windowHeight)
            if windowHeight == 0:
                windowHeight = lineNumber
            if type(windowStride) is not int:
                windowStride = int(windowStride)
            if type(sequenceLength) is not int:
                sequenceLength = int(sequenceLength)
        except ValueError:
            raise AssertionError("wrong argument type")

        methods = ['nearest', 'linear', 'cubic', 'skip']
        assert interpolateMethod in methods, "interpolatemethod must be in {}".format(str(methods))

        assert pixelNumber > 0, 'pixel number must be bigger than 0'
        assert lineNumber > 0, 'line number must be bigger than 0'
        assert windowWidth > 0, 'window width must be bigger than 0'
        assert windowHeight > 0, 'window height must be bigger than 0'
        assert windowWidth <= pixelNumber, 'window width must be smaller than pixel number'
        assert windowHeight <= lineNumber, 'window height must be smaller than line number'
        assert windowStride <= pixelNumber and windowStride <= lineNumber, \
            'window stride must be smaller than pixel number & line number'
        assert windowStride > 0, 'window stride must be bigger than 0'
        assert sequenceLength > 0, 'sequence length must be bigger than 0'

        if cacheDirectory == "":
            useCache = False
            saveCache = False

        order = execute_config["order"]

        if isinstance(timeInterpolate, type(glob)):
            timeInterpolateMethod = timeInterpolate
        elif isinstance(timeInterpolate, str):
            assert timeInterpolate == "error", "timeInterpolate must be 'error' or demical value"
            def error_timeInterpolate(pre_data, post_data):
                raise Exception("data file not exist")
            timeInterpolateMethod = error_timeInterpolate
        else:
            def fill_value_timeInterpolate(pre_data, post_data):
                return np.full(pre_data.shape, timeInterpolate)
            timeInterpolateMethod = fill_value_timeInterpolate

        return Dataset(config, timeStart, timeEnd, timeDelta, timeParser, geocoding_info,
                       windowWidth, windowHeight, windowStride, sequenceLength, interpolateMethod,
                       preprocess_fn, cacheQueue, cacheDirectory, useCache, saveCache, replaceNanValue,
                       targetGeocoding, order, timeInterpolateMethod, gk2aAmiCalibrationTable, dapsAbbrIdxLevelTable,
                       *args, **kwargs)

    def checkDataSize(self, dstLatitude):
        oldWindowShape = (abs(self.rightLowerPixelY - self.leftUpperPixelY),
                            abs(self.rightLowerPixelX - self.leftUpperPixelX))
        if self.leftUpperPixelY == -1:
            self.leftUpperPixelY = 0
        if self.leftUpperPixelX == -1:
            self.leftUpperPixelX = 0
        if self.rightLowerPixelY == -1:
            self.rightLowerPixelY = len(dstLatitude)
        if self.rightLowerPixelX == -1:
            self.rightLowerPixelX = len(dstLatitude[0])
        self.processedShape = (self.rightLowerPixelY - self.leftUpperPixelY,
                               self.rightLowerPixelX - self.leftUpperPixelX)
        if oldWindowShape == (self.windowHeight, self.windowWidth):
            self.windowHeight = self.processedShape[0]
            self.windowWidth = self.processedShape[1]
            self.windowXNum = int((self.windowWidth - self.windowWidth + self.stride) / self.stride)
            self.windowYNum = int((self.windowHeight - self.windowHeight + self.stride) / self.stride)
            self.minWindowX = self.windowWidth - self.windowWidth
            self.minWindowY = self.windowHeight - self.windowHeight
            self.windowNum = self.windowXNum * self.windowYNum
            return False
        return True

    def getDataShape(self, item):
        windowStartWidth = self.stride * (item // (len(self.datas) - self.sequenceLength + 1) % self.windowXNum)
        windowStartHeight = self.stride * (item // (len(self.datas) - self.sequenceLength + 1) // self.windowYNum)
        imageIndex = item // self.windowNum
        data = np.zeros((self.sequenceLength, len(self.datas[0]), self.windowHeight, self.windowWidth))
        mask = np.zeros((self.sequenceLength, len(self.datas[0]), self.windowHeight, self.windowWidth))
        return windowStartWidth, windowStartHeight, imageIndex, data, mask

    def getDataReaders(self):
        dataReaders = {}
        for dataset in self.config[""]:
            datasetType = self.config[dataset]["TYPE"]
            datasetType = datasetType.upper()
            if datasetType == "HIMAWARI_CLOUD":
                from MetDL.data_reader.netcdf.himawari_reader import HimawariReader
                dataReaders[datasetType] = HimawariReader(self.cacheQueue, self.cacheDirectory,
                                                          self.useCache, self.saveCache)
            elif datasetType == "RADAR_CMP":
                from MetDL.data_reader.radar.radar_cmp_reader import RadarCMPReader
                dataReaders[datasetType] = RadarCMPReader(self.cacheQueue, self.cacheDirectory,
                                                          self.useCache, self.saveCache)
            elif datasetType == "RADAR_NETCDF":
                from MetDL.data_reader.radar.radar_netcdf_reader import RadarNetCDFReader
                dataReaders[datasetType] = RadarNetCDFReader(self.cacheQueue, self.cacheDirectory,
                                                             self.useCache, self.saveCache)
            elif datasetType == "GK2A_AMI":
                from MetDL.data_reader.netcdf.gk2a_reader import GK2AAMIReader
                DQFIsUseConditional = False
                if "USE_CONDITIONAL_PIXEL" in self.config[dataset]:
                    DQFIsUseConditional = self.config[dataset]["USE_CONDITIONAL_PIXEL"]
                usdPhysicalValue = False
                if "USE_PHYSICAL_VALUE" in self.config[dataset]:
                    usdPhysicalValue = self.config[dataset]["USE_PHYSICAL_VALUE"]
                dataReaders[datasetType] = GK2AAMIReader(DQFIsUseConditional, usdPhysicalValue,
                                                         self.gk2aAmiCalibrationTable,
                                                         self.cacheQueue, self.cacheDirectory,
                                                         self.useCache, self.saveCache)
            elif datasetType == "LDAPS":
                from MetDL.data_reader.grib2.ldpas_reader import LDAPSReader
                dataReaders[datasetType] = LDAPSReader(self.dapsAbbrIdxLevelTable,
                                                       self.cacheQueue, self.cacheDirectory,
                                                       self.useCache, self.saveCache)
            elif datasetType == "GDAPS_UM":
                from MetDL.data_reader.grib2.gdaps_reader import GDAPSReader
                dataReaders[datasetType] = GDAPSReader(self.dapsAbbrIdxLevelTable,
                                                       self.cacheQueue, self.cacheDirectory,
                                                       self.useCache, self.saveCache)
            elif datasetType == "GDAPS_KIM":
                from MetDL.data_reader.grib2.gdaps_kim_reader import GDAPSReader
                dataReaders[datasetType] = GDAPSReader(self.dapsAbbrIdxLevelTable,
                                                       self.cacheQueue, self.cacheDirectory,
                                                       self.useCache, self.saveCache)
            else:
                raise Exception("unsupported product type {}\n"
                                "product type must be in [HIMAWARI_CLOUD, RADAR_CMP, RADAR_NETCDF, GK2A_AMI, "
                                "LDAPS, GDAPS_UM, GDAPS_KIM]".
                                format(datasetType))
        return dataReaders

    def getDataName(self, name, dateIdx):
        dateTime = self.dateTimes[dateIdx]
        name = name.replace("%Y", dateTime['year'])
        name = name.replace("%m", dateTime['month'])
        name = name.replace("%d", dateTime['day'])
        name = name.replace("%H", dateTime['hour'])
        name = name.replace("%M", dateTime['minute'])
        return name

    def getDatasets(self):
        timeStart = datetime.datetime.strptime(self.timeStart, self.timeParser)
        timeEnd = datetime.datetime.strptime(self.timeEnd, self.timeParser)
        timeDelta = datetime.timedelta(minutes=self.timeDelta)

        assert timeEnd >= timeStart, 'start_time is later than end_time'
        assert timeDelta.total_seconds() > 0, 'timedelta must be bigger than 0'

        self.dateTimes = []
        while True:
            self.dateTimes.append({'year': "{0:04d}".format(timeStart.year),
                                   'month': "{0:02d}".format(timeStart.month),
                                   'day': "{0:02d}".format(timeStart.day),
                                   'hour': "{0:02d}".format(timeStart.hour),
                                   'minute': "{0:02d}".format(timeStart.minute)})
            timeStart += timeDelta
            if timeStart > timeEnd:
                break

        datas = []
        for i, dateTime in enumerate(self.dateTimes):
            data_by_datetime_dict = {}
            for dataset in self.config[""]:
                dataType = self.config[dataset]["TYPE"]
                dataFolder = self.config[dataset]["DATA_FOLDER"]
                for product in self.config[dataset]["PRODUCTS"]:
                    name = self.config[dataset]["PRODUCTS"][product]["FILE_NAMING_RULE"]
                    availableList = glob(os.path.join(dataFolder, self.getDataName(name, i)))

                    if len(availableList) > 0:
                        dataPath = availableList[0]
                    else:
                        preAvailableList = glob(os.path.join(dataFolder, self.getDataName(name, i - 1)))
                        postAvailableList = glob(os.path.join(dataFolder, self.getDataName(name, i + 1)))
                        if len(postAvailableList) == 0:
                            raise Exception("more than 2 files not exist")
                        else:
                            dataPath = f"{preAvailableList[0]}:{postAvailableList[0]}"

                    for band in self.config[dataset]["PRODUCTS"][product]["BANDS"]:
                        if "item_path" in self.config[dataset]["PRODUCTS"][product]["BANDS"][band]:
                            itemPath = self.config[dataset]["PRODUCTS"][product]["BANDS"][band]["item_path"]
                        elif "INDEX" in self.config[dataset]["PRODUCTS"][product]["BANDS"][band]:
                            index = self.config[dataset]["PRODUCTS"][product]["BANDS"][band]["INDEX"]
                            level = self.config[dataset]["PRODUCTS"][product]["BANDS"][band]["LEVEL"]
                            itemPath = f"{index}::{level}"
                        elif "ABBR" in self.config[dataset]["PRODUCTS"][product]["BANDS"][band]:
                            abbr = self.config[dataset]["PRODUCTS"][product]["BANDS"][band]["ABBR"]
                            level = self.config[dataset]["PRODUCTS"][product]["BANDS"][band]["LEVEL"]
                            itemPath = f":{abbr}:{level}"

                        replaceNanValue = self.replaceNanValue
                        if 'replaceNanValue' in self.config[dataset]["PRODUCTS"][product]["BANDS"][band]:
                            replaceNanValue = self.config[dataset]["PRODUCTS"][product]["BANDS"][band][
                                "replaceNanValue"]

                        config_path = f"{dataset}/{product}/{band}"
                        data_by_datetime_dict[config_path] = {"type": dataType,
                                                              "dataPath": dataPath,
                                                              "itemPath": itemPath,
                                                              "datetime": dateTime,
                                                              "replaceNanValue": replaceNanValue}

                        if self.targetGeocoding:
                            if self.target in config_path:
                                dateTime_key = "".join(list(dateTime.values()))
                                self.dstDataset[dateTime_key] = {"type": dataType,
                                                                   "dataPath": dataPath,
                                                                   "itemPath": itemPath,
                                                                   "datetime": dateTime,
                                                                   "replaceNanValue": replaceNanValue}

            data_by_datetime = [data_by_datetime_dict[config_path] for config_path in self.order]
            datas.append(data_by_datetime)
        return datas

    def __len__(self):
        """
        pytorch Dataset 상속 메서드
        사용 가능한 Data 시간대의 길이를 반환
        """
        return (len(self.datas) - self.sequenceLength + 1) * self.windowNum

    def __getitem__(self, item, is_numpy=True):
        """
        pytorch Dataset 상속 메서드
        사용 가능한 Data에 preprocess_fn을 적용하고 반환

        Args:
            item: Data 시간대 index
            is_numpy: 반환 Data의 numpy array 사용 여부
        """
        window_start_width, window_start_height, img_idx, data, mask = self.getDataShape(item)

        for data_idx in range(img_idx, img_idx + self.sequenceLength):
            for band_idx, band_data in enumerate(self.datas[data_idx]):
                data_reader = self.dataReaders[band_data["type"]]

                if self.dstLatitude is None and self.dstLongitude is None:
                    if self.targetGeocoding:
                        dateTime = self.dateTimes[img_idx]
                        dateTime_key = "".join(list(dateTime.values()))
                        _, dstLatitude, dstLongitude = data_reader.getData(self.dstDataset[dateTime_key])

                        if not self.checkDataSize(dstLatitude):
                            window_start_width, window_start_height, img_idx, data, mask = self.getDataShape(item)

                        self.dstLatitude = dstLatitude[self.leftUpperPixelY:self.rightLowerPixelY,
                                  self.leftUpperPixelX:self.rightLowerPixelX]
                        self.dstLongitude = dstLongitude[self.leftUpperPixelY:self.rightLowerPixelY,
                                  self.leftUpperPixelX:self.rightLowerPixelX]
                dstLatitude = self.dstLatitude
                dstLongitude = self.dstLongitude

                if ":" in band_data["dataPath"]:
                    pre_band_data = band_data.copy()
                    pre_band_data["dataPath"] = band_data["dataPath"].split(":")[0]
                    pre_processed_data, _ = \
                        data_reader.get(self.dateTimes[img_idx], pre_band_data, dstLatitude, dstLongitude,
                                        self.interpolateMethod)
                    post_band_data = band_data.copy()
                    post_band_data["dataPath"] = band_data["dataPath"].split(":")[1]
                    post_processed_data, _ = \
                        data_reader.get(self.dateTimes[img_idx], post_band_data, dstLatitude, dstLongitude,
                                        self.interpolateMethod)
                    processed_data = self.timeInterpolate(pre_processed_data, post_processed_data)
                    processed_mask = np.full(processed_data.shape, 1)
                else:
                    processed_data, processed_mask = \
                        data_reader.get(self.dateTimes[img_idx], band_data, dstLatitude, dstLongitude, self.interpolateMethod)

                if processed_data.shape == self.processedShape:
                    data[data_idx - img_idx, band_idx, :, :] = (processed_data
                    [min(window_start_height, self.minWindowY):
                     (min(window_start_height, self.minWindowY) + self.windowHeight),
                                                                min(window_start_width, self.minWindowX):
                                                                (min(window_start_width,
                                                                     self.minWindowX) + self.windowWidth)])
                    mask[data_idx - img_idx, band_idx, :, :] = (processed_mask
                    [min(window_start_height, self.minWindowY):
                     (min(window_start_height, self.minWindowY) + self.windowHeight),
                                                                min(window_start_width, self.minWindowX):
                                                                (min(window_start_width,
                                                                     self.minWindowX) + self.windowWidth)])

                elif self.interpolateMethod == "skip":
                    raise Exception("interpolation method 'skip' cannot be used at different size datasets\n"
                                    "required shape {} but {}".format(self.processedShape, processed_data.shape))

        for preprocess_fn in self.preprocessFunction:
            data = preprocess_fn(data)
        return data, mask

    def preprocess_fn(self, func, test_data=None):
        """
        Data 변환에 사용될 메서드 추가

        Args:
            func: Data 변환에 사용될 메서드
            test_data: 메서드가 정상 작동하는지 확인하기 위한 numpy Data Array
        """
        if test_data is None:
            test_data = np.random.random((100, 100))
        try:
            func(test_data)
            self.preprocessFunction.append(func)
        except Exception as e:
            warnings.warn("processing function is not executable")
            raise e


if __name__ == "__main__":
    pass
