import yaml


def makeNormalizedConfig(config):
    noUnique = ["TYPE", "DATA_FOLDER", "USE_CONDITIONAL_PIXEL", "USE_PHYSICAL_VALUE", "PRODUCTS", "FILE_NAMING_RULE",
                "BANDS", "ITEM_PATH", "REPLACE_NAN_VALUE", "EXECUTE", "GEOCODING", "LEFT_UPPER_PIXELX", "LEFT_UPPER_PIXELY",
                "RIGHT_LOWER_PIXELX", "RIGHT_LOWER_PIXELY", "TARGET", "ORDER", "INDEX", "ABBR", "LEVEL"]
    upperCaseConfig = {}
    for key in config:
        if type(config[key]) == dict:
            if key.upper() == "EXECUTE":
                upperCaseConfig["EXECUTE"] = makeNormalizedConfig(config[key])
            else:
                upperCaseConfig[key] = makeNormalizedConfig(config[key])
                if key.upper() in noUnique:
                    upperCaseConfig[key.upper()] = makeNormalizedConfig(config[key])
                    upperCaseConfig[key.lower()] = makeNormalizedConfig(config[key])
        else:
            upperCaseConfig[key] = config[key]
            if key.upper() in noUnique:
                upperCaseConfig[key.upper()] = config[key]
                upperCaseConfig[key.lower()] = config[key]
    return upperCaseConfig


def makeGroupedConfig(config):
    groupedConfig = {}
    for key in config:
        if type(config[key]) == dict:
            if "FILE_NAMING_RULE" in config[key]:
                if "PRODUCTS" in groupedConfig:
                    groupedConfig["PRODUCTS"][key] = makeGroupedConfig(config[key])
                else:
                    groupedConfig["PRODUCTS"] = {}
                    groupedConfig["PRODUCTS"][key] = makeGroupedConfig(config[key])
            elif "ITEM_PATH" in config[key] or \
                 "INDEX" in config[key] or \
                 "ABBR" in config[key] or \
                 "LEVEL" in config[key]:
                if "BANDS" in groupedConfig:
                    groupedConfig["BANDS"][key] = makeGroupedConfig(config[key])
                else:
                    groupedConfig["BANDS"] = {}
                    groupedConfig["BANDS"][key] = makeGroupedConfig(config[key])
            else:
                groupedConfig[key] = makeGroupedConfig(config[key])
        else:
            groupedConfig[key] = config[key]
    return groupedConfig


def checkConfig(test_config):
    config = test_config.copy()
    assert "EXECUTE" in config, "execute not in config"
    assert "geocoding" in config["EXECUTE"], "geocoding not in config/execute"
    assert (("left_upper_pixelY" in config["EXECUTE"]["geocoding"] and
             "left_upper_pixelX" in config["EXECUTE"]["geocoding"] and
             "right_lower_pixelY" in config["EXECUTE"]["geocoding"] and
             "right_lower_pixelX" in config["EXECUTE"]["geocoding"]) or
            ("left_upper_lat" in config["EXECUTE"]["geocoding"] and
             "left_upper_lon" in config["EXECUTE"]["geocoding"] and
             "right_lower_lat" in config["EXECUTE"]["geocoding"] and
             "right_lower_lon" in config["EXECUTE"]["geocoding"])), "geocoding info not in config/execute/geocoding."
    assert "order" in config["EXECUTE"], "order not in config/execute"
    del config["EXECUTE"]

    # dataset check
    assert len(config) > 0, "dataset not in config"
    for dataset in config:
        # dataset/type check
        assert "type" in config[dataset], f"type not in config/{dataset}"
        del config[dataset]["type"]
        # dataset/data_folder check
        assert "data_folder" in config[dataset], f"data_folder not in config/{dataset}"
        del config[dataset]["data_folder"]
        # dataset/product check
        assert "PRODUCTS" in config[dataset], f"no products in config/{dataset}"
        assert len(config[dataset]["PRODUCTS"]) > 0, f"no products in config/{dataset}"
        for product in config[dataset]["PRODUCTS"]:
            # dataset/products/file_naming_rule check
            assert "file_naming_rule" in config[dataset]["PRODUCTS"][product], \
                f"file_naming_rule not in config/{dataset}/{product}"
            del config[dataset]["PRODUCTS"][product]["file_naming_rule"]
            # dataset/products/bands check
            assert "BANDS" in config[dataset]["PRODUCTS"][product], f"no band in config/{dataset}/{product}"
            assert len(config[dataset]["PRODUCTS"][product]["BANDS"]) > 0, f"no band in config/{dataset}/{product}"
            for band in config[dataset]["PRODUCTS"][product]["BANDS"]:
                assert ("item_path" in config[dataset]["PRODUCTS"][product]["BANDS"][band] or
                        (("index" in config[dataset]["PRODUCTS"][product]["BANDS"][band] or
                          "abbr" in config[dataset]["PRODUCTS"][product]["BANDS"][band]) and
                         "level" in config[dataset]["PRODUCTS"][product]["BANDS"][band])), \
                    f"item_path not in config/{dataset}/{product}/{band} or index, abbr, level not in config/{dataset}/{product}/{band}"


class Config:
    def __init__(self, path=None):
        self.config = None
        try:
            with open(path, 'r') as f:
                self.config = yaml.load(f, yaml.FullLoader)
        except:
            with open(path, 'rt', encoding='utf-8') as f:
                self.config = yaml.load(f, yaml.FullLoader)
        self.config = makeNormalizedConfig(self.config)
        # include PRODUCTS & BANDS or not
        self.config = makeGroupedConfig(self.config)
        checkConfig(self.config)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def __getitem__(self, item):
        return self.get(item)

    @staticmethod
    def getItem(dic, path):
        l_path = [x for x in path.split('/') if x]
        d = dic
        for p in l_path:
            if p in d:
                d = d[p]
            else:
                return None
        return d

    def get(self, path='', no_error=False):
        value = self.getItem(self.config, path)
        if not value:
            if not no_error:
                raise RuntimeError('{} is not in configuration'.format(path))
            else:
                return {}
        return value


if __name__ == "__main__":
    pass
