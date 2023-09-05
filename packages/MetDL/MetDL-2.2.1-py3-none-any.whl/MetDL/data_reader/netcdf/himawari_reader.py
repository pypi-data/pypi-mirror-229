import numpy as np

from .netcdf_reader import NetCDFReader


class HimawariReader(NetCDFReader):
    """
    Himawari-8 Data를 열람하기 위한 클래스
    """
    def __init__(self, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            dataPath_list: 데이터 저장 폴더 경로
        """
        super(HimawariReader, self).__init__(*args, **kwargs)

    def getData(self, bandData):
        ncdata = self.open(bandData["dataPath"])
        data = ncdata[bandData["itemPath"]][:]
        latitude = ncdata['/latitude'][:]
        longitude = ncdata['/longitude'][:]
        longitude, latitude = np.meshgrid(longitude, latitude)
        longitude[np.where(longitude > 180)] -= 360
        longitude[np.where(longitude < -180)] += 360
        return data, latitude, longitude
