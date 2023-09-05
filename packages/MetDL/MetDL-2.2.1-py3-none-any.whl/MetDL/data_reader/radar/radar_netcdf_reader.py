import netCDF4 as nc

from .radar_reader import RadarReader


class RadarNetCDFReader(RadarReader):
    """
    Radar Data를 열람하기 위한 클래스
    """
    def __init__(self, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            data_path_list: 데이터 저장 폴더 경로
        """
        super(RadarNetCDFReader, self).__init__(*args, **kwargs)

    def readHeader(self, data_path, start=0):
        """
        헤더 파싱

        - 멤버 변수 선언

        Args:
            idx: 읽어올 product의 index
        """
        ncdata = nc.Dataset(data_path)
        header = {}
        header["grid"] = ncdata.grid_size / 1000
        header["ny"] = ncdata.ny
        header["nx"] = ncdata.nx
        header["olat"] = ncdata.map_slat
        header["olon"] = ncdata.map_slon
        header["yo"] = ncdata.map_sy
        header["xo"] = ncdata.map_sx

        return header, 0

    def readData(self, data_path, RDR_CMP_HEAD, start):
        ncdata = nc.Dataset(data_path)
        return ncdata


if __name__ == "__main__":
    pass
