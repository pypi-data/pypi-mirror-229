import pkg_resources
import pandas as pd
import numpy as np

from .netcdf_reader import NetCDFReader


class GK2AAMIReader(NetCDFReader):
    """
    GK2A AMI L1B Data를 열람하기 위한 클래스
    """
    def __init__(self, DQFIsUseConditional: bool, usePhysicalValue: bool, calibrationTablePath=None, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            dataPath_list: 데이터 저장 폴더 경로
        """
        super(GK2AAMIReader, self).__init__(*args, **kwargs)
        self.DQFIsUseConditional = DQFIsUseConditional
        self.usePhysicalValue = usePhysicalValue
        self.cacheGeophysicalData = {}

        if calibrationTablePath is None:
            self.calibrationTablePath = '../../metadata/META_GK2A_AMI_L1B_calibration_table.xlsx'
            calibrationTablePath = pkg_resources.resource_stream(__name__, self.calibrationTablePath)
        else:
            self.calibrationTablePath = calibrationTablePath

        self.calibrationTable = pd.read_excel(calibrationTablePath, engine="openpyxl", sheet_name="coeff.& equation_WN")

    def getData(self, band_data):
        ncdata = self.open(band_data["dataPath"])
        data = ncdata[band_data["itemPath"]][:]
        realData = data & 0x3FFF
        dqfData = data >> 14
        if not self.DQFIsUseConditional:
            realData[dqfData == 1] = np.ma.masked
        realData[dqfData == 2] = np.ma.masked
        realData[dqfData == 3] = np.ma.masked
        realData = self.calibration(band_data["dataPath"], realData)

        cfac = ncdata.cfac
        lfac = ncdata.lfac
        coff = ncdata.coff
        loff = ncdata.loff
        sublon = ncdata.sub_longitude

        pixelX = np.tile(np.arange(0, ncdata.number_of_lines), (ncdata.number_of_columns, 1))
        pixelY = np.tile(np.arange(0, ncdata.number_of_lines).reshape(-1, 1),
                         (1, ncdata.number_of_columns))
        [longitude, latitude] = self.colLineElemToLatLon(pixelX, pixelY, cfac, lfac, coff, loff, sublon)
        longitude[np.where(longitude > 180)] -= 360
        longitude[np.where(longitude < -180)] += 360
        return realData, latitude, longitude

    def colLineElemToLatLon(self, pixelX, pixelY, cfac, lfac, coff, loff, sublon):
        """
        GK2A AMI L1B product Latitude, Longitude 계산

        Args:
            pixelX: X 좌표
            pixelY: Y 좌표
            cfac: Column scaling factor
            lfac: Line scaling factor
            coff: Column offset
            loff: Line offset
            sublon: Longitude of Sub Satellite Point(degree)
        """
        key = (pixelX.shape, cfac, lfac, coff, loff, sublon)
        if key not in self.cacheGeophysicalData.keys():
            deg2rad = np.pi / 180
            x = (pixelX - coff) * np.power(2, 16) / cfac * deg2rad
            y = (pixelY - loff) * np.power(2, 16) / lfac * deg2rad
            yCos = np.cos(y)
            ySin = np.sin(y)
            xCos = np.cos(x)
            xSin = np.sin(x)
            v1 = xCos * yCos
            v2 = 42164 * v1
            v3 = (yCos ** 2) + 1.006803 * (ySin ** 2)
            sn = (v2 - np.sqrt((v2 ** 2) - v3 * 1737121856)) / v3
            s1 = 42164 - sn * v1
            s2 = sn * xSin * yCos

            lat = (np.arctan(s2 / s1) + sublon) / deg2rad
            lon = -np.arctan(1.006803 * (-sn * ySin) / (np.sqrt((s1 ** 2) + (s2 ** 2)))) / deg2rad
            self.cacheGeophysicalData[key] = [lat, lon]
        return self.cacheGeophysicalData[key]

    def calibration(self, dataPath, data):
        gain = 1
        offset = 0
        if "vi004" in dataPath:
            gain = self.calibrationTable.iloc[2, 3]
            offset = self.calibrationTable.iloc[2, 5]
        if "vi005" in dataPath:
            gain = self.calibrationTable.iloc[3, 3]
            offset = self.calibrationTable.iloc[3, 5]
        if "vi006" in dataPath:
            gain = self.calibrationTable.iloc[4, 3]
            offset = self.calibrationTable.iloc[4, 5]
        if "vi008" in dataPath:
            gain = self.calibrationTable.iloc[5, 3]
            offset = self.calibrationTable.iloc[5, 5]
        if "nr013" in dataPath:
            gain = self.calibrationTable.iloc[6, 3]
            offset = self.calibrationTable.iloc[6, 5]
        if "nr016" in dataPath:
            gain = self.calibrationTable.iloc[7, 3]
            offset = self.calibrationTable.iloc[7, 5]
        if "sw038" in dataPath:
            gain = self.calibrationTable.iloc[11, 3]
            offset = self.calibrationTable.iloc[11, 5]
        if "wv063" in dataPath:
            gain = self.calibrationTable.iloc[12, 3]
            offset = self.calibrationTable.iloc[12, 5]
        if "wv069" in dataPath:
            gain = self.calibrationTable.iloc[13, 3]
            offset = self.calibrationTable.iloc[13, 5]
        if "wv073" in dataPath:
            gain = self.calibrationTable.iloc[14, 3]
            offset = self.calibrationTable.iloc[14, 5]
        if "ir087" in dataPath:
            gain = self.calibrationTable.iloc[15, 3]
            offset = self.calibrationTable.iloc[15, 5]
        if "ir096" in dataPath:
            gain = self.calibrationTable.iloc[16, 3]
            offset = self.calibrationTable.iloc[16, 5]
        if "ir105" in dataPath:
            gain = self.calibrationTable.iloc[17, 3]
            offset = self.calibrationTable.iloc[17, 5]
        if "ir112" in dataPath:
            gain = self.calibrationTable.iloc[18, 3]
            offset = self.calibrationTable.iloc[18, 5]
        if "ir123" in dataPath:
            gain = self.calibrationTable.iloc[19, 3]
            offset = self.calibrationTable.iloc[19, 5]
        if "ir133" in dataPath:
            gain = self.calibrationTable.iloc[20, 3]
            offset = self.calibrationTable.iloc[20, 5]

        if self.usePhysicalValue:
            calibrationData = np.array(data) * gain + offset
            data = np.ma.masked_array(calibrationData, data.mask)
        return data