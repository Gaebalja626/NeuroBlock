"""
block.py

Description:
    이 모듈은 NeuroBricks 의 블록 객체와 필요한 객체를 정의합니다.

Classes:
    - Block: 블록 객체
    - Connector: 블록 연결 정보 객체
"""
from typing import Any

from .block_validation import validate_block_name
import inspect


class BlockConfig:
    """
    BlockConfig Class

    Description:
        이 클래스는 블록 객체의 설정 정보(name, block_type등)을 저장하고 관리합니다
        이 객체는 dictionary 형태로 각 attribution을 저장하고 __getattr__ 메소드를 통해 접근합니다.
        cfg.key = value 또는 cfg.config["key"] = value 형태로 설정 정보를 추가할 수 있습니다.

    Example:
        cfg = BlockConfig(
            in_channels=3,
            kernel_size=[7, 1, 2],
            stride=1,
            padding=1
        )
        cfg.name = "TestConfig"
        cfg.description = "ABC"

        print(cfg.name)
        print(cfg.description)
    """

    def __init__(self, **kwargs):
        self.config = kwargs

    def __str__(self):
        attributes = ', '.join(f"{key}={value}" for key, value in self.config.items())
        return f"BlockConfig({attributes})"

    def __getattr__(self, item):
        return self.config.get(item, None)

    def __setattr__(self, key, value):
        if key == "config":
            super().__setattr__(key, value)
        else:
            self.config[key] = value


class Block:
    """
    Block Class

    Description:
        이 클래스는 NeuroBricks 의 블록 객체를 정의합니다.\n
        블록코딩 환경에서 블록 객체의 속성 및 연결 정보를 저장합니다.\n
        각 블럭은 BlockManager 객체에 의해 생성 및 관리됩니다.

    Attributes:
        - name(str): 블록의 이름
        - display_name(str): 블록의 표시 이름
        - block_type(Any): 블록의 타입
        - num_inputs(int): 블록의 입력부 개수
        - num_outputs(int): 블록의 출력부 개수
        - ports(dict): 블록의 입력 & 출력 포트 정보
        - position(tuple): 블록의 위치 정보 저장

    Attribution Annotation:
        ports = {
            "in0": {
                "name": "in0",
                "connected_port": ["Block2/out1"]
            },
            "in1": {
                "name": "in1",
                "connected_port": []
            },
            "out0": {
                "name": "out0",
                "connected_port": ["Block3/in0", "Block3/in1"]
            },
        }
        ex) Block.ports["in0"]["connected_port"] = "Block2/out1"

    Methods:
        - __init__: 블록 객체 초기화
        - get_connections: 입력 & 출력 포트 정보 반환
    """

    def __init__(self, *,
                 name: str,
                 block_type: object,
                 display_name: str = None,
                 num_inputs: int = 0,
                 num_outputs: int = 0,
                 position: tuple = None,
                 cfg: BlockConfig = None,
                 **kwargs
                 ) -> None:
        """
        Block 객체 초기화

        Description:
            Block 객체를 초기화합니다.

        Args:
            -name(str): 블록의 이름 (필수)
            -block_type(Any): 블록의 타입, ex) 'BatchNorm1D', 'Conv3D' (필수)
            -display_name(str): block_type 에 따른 속성 정보 (선택)
            -num_inputs(int): 블록의 입력부 개수 (선택)
            -num_outputs(int): 블록의 출력부 개수 (선택)
            -position(tuple): 블록의 위치 정보 (선택)
            -cfg(BlockConfig): BlockConfig 객체

        :param name: 블록의 이름 (필수)
        :param block_type: 블록의 타입, ex) 'BatchNorm1D', 'Conv3D' (필수)
        :param display_name: block_type 에 따른 속성 정보 (선택)
        :param num_inputs: 블록의 입력부 개수 (선택)
        :param num_outputs: 블록의 출력부 개수 (선택)
        :param position: 블록의 위치 정보 (선택)
        :param cfg: BlockConfig 객체
        """
        self.name = name
        self.display_name = display_name
        if display_name is None:
            self.display_name = name

        self.block_type = block_type

        if num_inputs < 0 or num_outputs < 0:
            raise ValueError("num_inputs & num_outputs must be positive integer")
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self.ports = []
        for i in range(num_inputs):
            self.ports.append(f"in{i}")
        for i in range(num_outputs):
            self.ports.append(f"out{i}")

        self.position = position

        if cfg:
            self.cfg = cfg
        else:
            self.cfg = BlockConfig()

        self.cfg.name = name
        self.cfg.display_name = display_name
        self.cfg.block_type = block_type
        self.cfg.num_inputs = num_inputs
        self.cfg.num_outputs = num_outputs
        self.cfg.position = position
        for key, value in kwargs.items():
            self.cfg.config[key] = value

        # self.cfg.ports = self.ports

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("You must implement __call__ method in subclass of Block")


class FunctionBlock(Block):
    def __init__(self, name: str,
                 *, function: callable,
                 cfg: BlockConfig = None,
                 **kwargs) -> None:
        """
        FunctionBlock 객체 초기화

        Args:\n
        -name(str): 블록 이름 (필수)\n
        -function(callable): 대상함수\n
        함수 파라미터 수가 input port 수랑 반드시 일치해야함\n
        -cfg(BlockConfig): BlockConfig 객체

        :rtype: object
        :param name: str
        :param function: callable
        :param cfg: BlockConfig
        :param kwargs: **kwargs
        """
        super().__init__(name=name, block_type="FunctionBlock", cfg=cfg, **kwargs)

        self.function = function

        # 블럭의 input 개수랑 함수의 파라미터 개수가 일치하는지 확인
        if len(inspect.signature(function).parameters) != self.cfg.num_inputs:
            raise ValueError(f"Function parameter count({len(inspect.signature(function).parameters)})"
                             f" must be equal to num_inputs({self.cfg.num_inputs})")

    def __call__(self, *args):
        return self.function(*args)