import math
import gzip
import struct
import numpy as np

from MetDL.data_reader.data_reader import DataReader


class RadarReader(DataReader):
    """
    Radar Data를 열람하기 위한 클래스
    """
    def __init__(self, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            dataPath_list: 데이터 저장 폴더 경로
        """
        super(RadarReader, self).__init__(*args, **kwargs)
        self.Re = 6371.00877    ##  지도반경
        slat1 = 30.0            ##  표준위도 1
        slat2 = 60.0            ##  표준위도 2

        self.PI = math.asin(1.0) * 2.0
        self.DEGRAD = self.PI / 180.0
        self.RADDEG = 180.0 / self.PI

        slat1 = slat1 * self.DEGRAD
        slat2 = slat2 * self.DEGRAD

        sn = math.tan(self.PI * 0.25 + slat2 * 0.5) / math.tan(self.PI * 0.25 + slat1 * 0.5)
        self.sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
        sf = math.tan(self.PI * 0.25 + slat1 * 0.5)
        self.sf = math.pow(sf, self.sn) * math.cos(slat1) / self.sn

        self.maskValue = {("CCP", "PPI", "CMX", "PTY", "LNG", "PCP", "NUM", "OTH", "PUB"):
                               [-20000, -25000, -30000],
                           ("HCI", "HAIL", "HSR"): [-200, -250, -300],
                           ("WD", "_____"): [-30000]}

    def getData(self, bandData):
        header, headerEnd = self.readHeader(bandData["dataPath"])
        standardHeader, standardHeaderEnd = self.readStandardHeader(bandData["dataPath"], header, headerEnd)
        data = self.readData(bandData["dataPath"], header, standardHeaderEnd)

        grid = header["grid"]
        NY = header["ny"]
        NX = header["nx"]
        olat = header["olat"]
        olon = header["olon"]
        yo = header["yo"]
        xo = header["xo"]

        itemPath = bandData["itemPath"].split("_")
        dataCode, nzIndex = "_".join(itemPath[:-1]), itemPath[-1]
        if dataCode.isdigit():
            dataCode = int(dataCode)
        data = data[dataCode][int(nzIndex)]

        re = self.Re / grid
        olon = olon * self.DEGRAD
        olat = olat * self.DEGRAD
        ro = math.tan(self.PI * 0.25 + olat * 0.5)
        ro = re * self.sf / math.pow(ro, self.sn)

        colGrid, rowGrid = np.meshgrid(np.arange(NX), np.arange(NY))
        lat, lon = self.gridToMap(colGrid, rowGrid, re, ro, xo, yo, olon)

        if "WD" not in bandData["dataPath"]:
            lat = np.flipud(lat)
            lon = np.flipud(lon)

        maskValues = []
        for radarTypes in self.maskValue:
            for radarType in radarTypes:
                if radarType in bandData["dataPath"].split("/")[-1]:
                    maskValues = self.maskValue[radarTypes]

        maskArray = np.full((NY, NX), False)
        for maskValue in maskValues:
            maskArray[data == maskValue] = True

        data = np.ma.masked_array(data, maskArray)

        return data, lat, lon

    def readHeader(self, dataPath, start=0):
        raise NotImplementedError

    def readStandardHeader(self, dataPath, RDR_CMP_HEAD, start):
        return [], start

    def readData(self, dataPath, RDR_HEAD, start):
        NZ = RDR_HEAD["nz"]
        NY = RDR_HEAD["ny"]
        NX = RDR_HEAD["nx"]
        with gzip.open(dataPath, "rb") as f:
            f.seek(0, 2)
            fileSize = f.tell() - start
            f.seek(start)
            dataNum = fileSize // (2 * NZ * NY * NX)

            data = np.zeros((dataNum, NZ, NY, NX), dtype=np.float32)
            subData = np.zeros((NY, NX), dtype=np.float32)
            for b in range(dataNum):
                for v in range(NZ):
                    for h in range(NY):
                        for w in range(NX):
                            byte = f.read(2)
                            subData[h, w] = struct.unpack("<h", byte)[0] / 100
                    subData = np.flipud(subData)
                    data[b, v] = subData

            return data

    def mapToGrid(self, lat, lon, re, ro, xo, yo, olon):
        ra = np.tan(self.PI * 0.25 + lat * self.DEGRAD * 0.5)
        ra = re * self.sf / np.power(ra, self.sn)
        theta = lon * self.DEGRAD - olon
        theta[theta > self.PI] -= 2.0 * self.PI
        theta[theta < -self.PI] += 2.0 * self.PI
        theta *= self.sn
        x = (ra * np.sin(theta)) + xo
        y = (ro - ra * np.cos(theta)) + yo
        return x, y

    def gridToMap(self, x, y, re, ro, xo, yo, olon):
        xn = x - xo
        yn = ro - y + yo
        ra = np.sqrt(xn * xn + yn * yn)
        if self.sn < 0.0:
            ra = -ra
        alat = np.power((re * self.sf / ra), (1.0 / self.sn))
        alat = 2.0 * np.arctan(alat) - self.PI * 0.5
        theta = np.arctan2(xn, yn)
        theta[np.fabs(xn) <= 0] = 0.0
        theta[np.fabs(yn) <= 0] = self.PI * 0.5
        theta[(np.fabs(yn) <= 0) & (np.fabs(xn) < 0)] = -1 * self.PI * 0.5
        alon = theta / self.sn + olon
        lat = alat * self.RADDEG
        lon = alon * self.RADDEG
        return lat, lon


if __name__ == "__main__":
    pass
