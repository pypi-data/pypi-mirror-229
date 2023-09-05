from .grib2_reader import GRIB2Reader


class GDAPSReader(GRIB2Reader):
    def __init__(self, *args, **kwargs):
        super(GDAPSReader, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    pass
