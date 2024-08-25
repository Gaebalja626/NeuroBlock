"""
block.py

Description:
    이 모듈은 NeuroBricks 의 블록 객체와 필요한 객체를 정의합니다.

Classes:
    - Block: 블록 객체
    - Connector: 블록 연결 정보 객체
"""
from typing import Any

from ..utils.config import Config
from .block_graph import BlockGraph
import inspect
from collections.abc import Iterable


class BlockConfig(Config):
    """
    BlockConfig Class

    Description:
        이 클래스는 Config 객체를 상속받아 Block 객체의 설정 정보를 저장합니다.\n
        각 Block는 BlockConfig 객체를 생성하여 Block 객체의 설정 정보를 저장합니다.
        이때
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

    def __call__(self, *args, **kwargs):
        """
        kwargs 로
        in0=value1, in1=value2, ... 형태로 받은다음
        input_dict 로 변환해서 처리

        return 으로
        {out0:value1, out1:value2, ...} 형태로
        dict로 반환

        :param args:
        :param kwargs:
        :return:
        """
        if args and kwargs:
            raise ValueError("You must use only args or kwargs")
        if args:
            input_dict = {f"in{i}": args[i] for i in range(self.num_inputs)}
        else:
            input_dict = kwargs
        return input_dict

    def get_config(self):
        return self.cfg


class FunctionBlock(Block):
    block_type = "FunctionBlock"
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
        if set(inspect.signature(function).parameters) != \
                set([f"in{i}" for i in range(self.cfg.num_inputs)]):
            res = set([f"in{i}" for i in range(self.cfg.num_inputs)]) - set(inspect.signature(function).parameters)
            raise ValueError(f"Function '{function.__name__}' must have parameters {list(res)}")

    def __call__(self,*args, **kwargs):
        if args and kwargs:
            raise ValueError("You must use only args or kwargs")
        if args:
            result = self.function(*args)
        else:
            result = self.function(**kwargs)

        if isinstance(result, Iterable) and hasattr(result, "__getitem__"):
            return {f"out{i}": result[i] for i in range(len(result))}
        else:
            return {"out0": result}


class MergedBlock(Block):
    block_type = "MergedBlock"

    def __init__(self, name: str, *,
                 graph: BlockGraph,
                 cfg: BlockConfig = None,
                 **kwargs
                 ) -> None:
        """
        MergedBlock 객체 초기화

        Args:
        -blocks(Block): 병합할 블록 객체

        :param blocks: Block
        """
        self.inner_graph = graph
        super().__init__(name=name, block_type="MergedBlock",
                         num_inputs=graph.get_num_inputs(),
                         num_outputs=graph.get_num_outputs(), **kwargs)

        self.num_inputs = graph.get_num_inputs()
        self.num_outputs = graph.get_num_outputs()
        self.input_connections = {}
        self.output_connections = {}

        i = 0
        for block_name in graph.get_start_blocks():
            for port in graph.get_connection(block_name):
                if "in" in port:
                    self.input_connections[f"in{i}"] = (block_name, port)
                    i += 1

        i = 0
        for block_name in graph.get_end_blocks():
            for port in graph.get_connection(block_name):
                if "out" in port:
                    self.output_connections[f"{block_name}/{port}"] = f"out{i}"
                    i += 1

    def __call__(self, **kwargs):
        """

        input은 dict 형태로 받아질거임
        """

        input_dict = self.inner_graph.get_input_dict()

        for key, value in kwargs.items():  # key = in0, in1, in2, ...
            connected_block, connected_port = self.input_connections[key]
            input_dict[connected_block][connected_port] = value

        for block_name in input_dict:
            if None in input_dict[block_name].values():
                raise ValueError(f"Invalid input '{block_name}', {input_dict[block_name]}")

        end_output, _ = self.inner_graph(input_dict)

        output_dict = {port.split('/')[1]: None for port in self.output_connections.keys()}

        for block, values in end_output.items():
            for port, value in values.items():
                output_dict[self.output_connections[f"{block}/{port}"]] = value

        return output_dict
