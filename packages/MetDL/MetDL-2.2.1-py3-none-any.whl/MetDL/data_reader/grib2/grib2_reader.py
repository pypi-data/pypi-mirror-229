import pkg_resources
import numpy as np
import yaml
from MetDL.data_reader.data_reader import DataReader


class GRIB2Reader(DataReader):
    def __init__(self, dapsAbbrIdxLevelTable=None, *args, **kwargs):
        self.latCoord = []
        self.lonCoord = []
        self.latGrid = []
        self.lonGrid = []
        self.rawData = []
        if dapsAbbrIdxLevelTable is None:
            self.dapsAbbrIdxLevelTablePath = '../../metadata/META_DAPS_ABBR_INDEX_LEVEL_Table.yaml'
            dapsAbbrIdxLevelTable = pkg_resources.resource_stream(__name__, self.dapsAbbrIdxLevelTablePath)
        else:
            self.dapsAbbrIdxLevelTablePath = dapsAbbrIdxLevelTable
            dapsAbbrIdxLevelTable = open(self.dapsAbbrIdxLevelTablePath, "r")

        self.readDapsAbbrIdxLevelTable(dapsAbbrIdxLevelTable)
        super(GRIB2Reader, self).__init__(*args, **kwargs)

    def readDapsAbbrIdxLevelTable(self, dapsAbbrIdxLevelTable):
        dapsAbbrIdxLevelTable = yaml.load(dapsAbbrIdxLevelTable, yaml.FullLoader)
        self.level = dapsAbbrIdxLevelTable["level"]
        self.fileType = dapsAbbrIdxLevelTable["fileType"]

    def getGeotable(self, lat, lon):
        self.latGrid, self.lonGrid = lat, lon
        height, width = self.lonGrid.shape[:2]

        self.data = [np.ma.masked_array(np.zeros((height, width)), np.full((height, width), True))]
        for i, data in enumerate(self.rawData):
            try:
                self.data.append(data.reshape(height, width))
            except Exception as e:
                self.data.append(self.data[0])

    def convertItemPath(self, dataPath, itemPath):
        try:
            index, abbr, level = itemPath.split(":")
            for fileType in self.fileType:
                if fileType in dataPath:
                    if len(index) == 0:
                        index = self.fileType[fileType]["ABBR"].index(abbr)
                    else:
                        index = int(index)

                    itemPath = 1
                    for i in range(index):
                        itemPath += len(self.level[self.fileType[fileType]["LEVEL"][i]])
                    if len(self.level[self.fileType[fileType]["LEVEL"][index]]) == 1:
                        itemPath += 0
                    else:
                        itemPath += self.level[self.fileType[fileType]["LEVEL"][index]].index(level)
        except:
            raise Exception("wrong INDEX, ABBR, LEVEL")
        return str(itemPath)

    def calcLatLon(self, upperLeftLat, lowerRightLat, height, upperLeftLon, lowerRightLon, width, over=False):
        lat = np.linspace(upperLeftLat, lowerRightLat, height)
        lon = np.linspace(upperLeftLon, lowerRightLon, width)
        if over:
            over = width // 2
            lon[:over] += 180
            lon[over:] -= 180
        lonGrid, latGrid = np.meshgrid(lon, lat)
        return lonGrid, latGrid

    def open(self, dataPath: str):
        exist = False
        for modules in __import__('pkg_resources').working_set.__dict__:
            if 'pygrib' in __import__('pkg_resources').working_set.__dict__[modules]:
                exist = True
        if exist:
            import pygrib
            grbs = pygrib.open(dataPath)
            self.rawData = []
            for grb in grbs:
                rawData = grb.values
                if not isinstance(rawData, np.ma.masked_array):
                    rawData = np.ma.masked_array(rawData, np.full(rawData.shape, False))
                self.rawData.append(rawData)
            lat, lon = grb.latlons()
            lon[lon > 180] -= 360
        else:
            raise NotImplementedError
        self.getGeotable(lat, lon)
        return self.data

    def close(self):
        self.dataPathList = None
        self.latCoord = None
        self.lonCoord = None

    def getData(self, bandData):
        if ":" in bandData["itemPath"]:
            bandData["itemPath"] = self.convertItemPath(bandData["dataPath"], bandData["itemPath"])
        assert bandData["itemPath"].isdigit(), 'LDAPS/GDAPS band path must be convertible as integer'
        data = self.open(bandData["dataPath"])
        assert int(bandData["itemPath"]) < len(data), 'LDAPS/GDAPS band path must be smaller than band count'
        data = data[int(bandData["itemPath"])]
        print(int(bandData["itemPath"]))
        return data, self.latGrid, self.lonGrid
