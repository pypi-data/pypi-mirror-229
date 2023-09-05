from torch.utils import data

from MetDL.utils.config import Config
from MetDL.dataset.dataset import Dataset


class DataLoader(data.dataloader.DataLoader):
    """
    AIWA AI 확장 라이브러리 DataLoader class
    """
    def __init__(self, *args, **kwargs):
        """
        클래스 초기화

        - 멤버 변수 선언

        Args:
        """
        super(DataLoader, self).__init__(*args, **kwargs)

    @staticmethod
    def initialize(config, batchSize=1, *args, **kwargs):
        config = Config(config)
        executeConfig = config["EXECUTE"]
        del config.config["EXECUTE"]
        dataset = Dataset.initialize(config, executeConfig, *args, **kwargs)
        return DataLoader(dataset=dataset, batch_size=batchSize, shuffle=False)


if __name__ == "__main__":
    pass
