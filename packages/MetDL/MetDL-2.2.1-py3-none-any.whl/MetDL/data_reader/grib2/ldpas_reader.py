from .grib2_reader import GRIB2Reader


class LDAPSReader(GRIB2Reader):
    def __init__(self, *args, **kwargs):
        super(LDAPSReader, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    pass
