"""
config.py

"""

class Config:
    """
    Config Class

    Description:
        이 클래스는 정 정보(name, block_type등)을 저장하고 관리합니다

    Example:
        cfg = Config(
            in_channels=3,
            kernel_size=[7, 1, 2],
            stride=1,
            padding=1
        )
        cfg.name = "TestConfig"
        cfg.description = "ABC"
    """
    def __init__(self, **kwargs):
        self.config = kwargs

    def __str__(self):
        attributes = ', '.join(f"{key}={value}" for key, value in self.config.items())
        return f"Config({attributes})"

    def __getattr__(self, item):
        return self.config.get(item, None)

    def __setattr__(self, key, value):
        if key == "config":
            super().__setattr__(key, value)
        else:
            self.config[key] = value