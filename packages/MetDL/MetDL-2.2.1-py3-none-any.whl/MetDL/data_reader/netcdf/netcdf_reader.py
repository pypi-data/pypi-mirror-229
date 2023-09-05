import netCDF4 as Nc

from MetDL.data_reader.data_reader import DataReader


class NetCDFReader(DataReader):
    """
    NetCDF Data를 열람하기 위한 클래스
    """
    def __init__(self, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            dataPath_list: 데이터 저장 폴더 경로
        """
        super(NetCDFReader, self).__init__(*args, **kwargs)

    def open(self, dataPath):
        return Nc.Dataset(dataPath)
