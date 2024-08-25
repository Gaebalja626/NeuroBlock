"""
config.py

"""

class Config:
    """
    Config Class

    Description:
        이 클래스는 config 객체를 정의합니다.
        config 객체는 dictionary 형태로 각 attribution을 저장하고 __getattr__ 메소드를 통해 접근합니다.
        cfg.key = value 또는 cfg.config["key"] = value 형태로 설정 정보를 추가할 수 있습니다.
        이 객체를 상속 받아서 추가적으로 필요한 config 기능을 구현합니다.

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