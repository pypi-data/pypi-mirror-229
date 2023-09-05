import struct
import gzip

from .radar_reader import RadarReader


class TIME_SS:
    """
    Radar Data에서 시간 정보를 파싱하기 위한 클래스
    """
    def __init__(self, seven_byte):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
            seven_byte: 7바이트 길이의 Byte 데이터
        """
        self.year = struct.unpack("<h", seven_byte[:2])[0]
        self.month = seven_byte[2]
        self.day = seven_byte[3]
        self.hour = seven_byte[4]
        self.minute = seven_byte[5]
        self.second = seven_byte[6]

    def get(self):
        return "{0:04d}{1:02d}{2:02d}_{3:02d}{4:02d}".format(self.year, self.month, self.day, self.hour, self.minute)


class RadarCMPReader(RadarReader):
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
        super(RadarCMPReader, self).__init__(*args, **kwargs)

        self.RDR_CMP_HEAD_keys = ["version", "ptype", "tm", "tm_in", "num_stn", "map_code", "map_etc",
                                  "nx", "ny", "nz", "dxy", "dz", "z_min", "num_data", "data_code", "etc"]
        self.RDR_CMP_HEAD_bytes = [1, 2, 7, 7, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 16, 15]
        self.RDR_CMP_STN_LIST_keys = ["stn_cd", "tm", "tm_in"]
        self.RDR_CMP_STN_LIST_bytes = [6, 7, 7]

    def readHeader(self, data_path, start=0):
        """
        헤더 파싱

        - 멤버 변수 선언

        Args:
            idx: 읽어올 product의 index
        """
        RDR_CMP_HEAD = {}
        with gzip.open(data_path, "rb") as f:
            f.seek(start)
            for i, b in enumerate(self.RDR_CMP_HEAD_bytes):
                byte = f.read(b)
                if "tm" in self.RDR_CMP_HEAD_keys[i]:
                    tm = TIME_SS(byte)
                    tm_list = tm.get()
                    RDR_CMP_HEAD[self.RDR_CMP_HEAD_keys[i]] = tm_list
                else:
                    if b == 1:
                        byte_result = struct.unpack("<b", byte)[0]
                    elif b == 2:
                        byte_result = struct.unpack("<h", byte)[0]
                    else:
                        byte_result = []
                        for j in range(b):
                            byte_result.append(byte[j])
                    RDR_CMP_HEAD[self.RDR_CMP_HEAD_keys[i]] = byte_result

            RDR_CMP_HEAD["grid"] = RDR_CMP_HEAD["dxy"] / 1000

            if RDR_CMP_HEAD["map_code"] == 1:
                RDR_CMP_HEAD["olon"] = 126.0
                RDR_CMP_HEAD["olat"] = 38.0
                RDR_CMP_HEAD["xo"] = 1121
                RDR_CMP_HEAD["yo"] = 1681
            elif RDR_CMP_HEAD["map_code"] == 2:
                RDR_CMP_HEAD["olon"] = 126.0
                RDR_CMP_HEAD["olat"] = 38.0
                RDR_CMP_HEAD["xo"] = 801
                RDR_CMP_HEAD["yo"] = 1101

            return RDR_CMP_HEAD, f.tell()

    def readStandardHeader(self, data_path, RDR_CMP_HEAD, start):
        RDR_CMP_STN_LIST = []
        with gzip.open(data_path, "rb") as f:
            f.seek(start)

            for _ in range(RDR_CMP_HEAD["num_stn"]):
                STN_LIST = {}
                for i, b in enumerate(self.RDR_CMP_STN_LIST_bytes):
                    byte = f.read(b)
                    if "tm" in self.RDR_CMP_STN_LIST_keys[i]:
                        tm = TIME_SS(byte)
                        tm_list = tm.get()
                        STN_LIST[self.RDR_CMP_STN_LIST_keys[i]] = tm_list
                    else:
                        byte_result = []
                        for j in range(b):
                            byte_result.append(byte[j])
                        STN_LIST[self.RDR_CMP_STN_LIST_keys[i]] = byte_result
                RDR_CMP_STN_LIST.append(STN_LIST)
            _ = f.read(20 * (48 - RDR_CMP_HEAD["num_stn"]))

            return RDR_CMP_STN_LIST, f.tell()


if __name__ == "__main__":
    pass
