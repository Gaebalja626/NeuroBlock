from typing import Any

from .block_validation import validate_block_name
from .block import *
import inspect
from collections import deque, defaultdict
import copy


class BlockManager:
    """
    BlockManager Class

    Description:
        이 클래스는 NeuroBricks 의 블록 매니저 객체를 정의합니다.\n
        블록 객체 리스트, 블록 연결 정보를 관리합니다 \n

    Attributes:
        - block_registry(dict): key: 블록 이름 (str), value: 블록 객체 (block)
        - connection_registry(dict): "블록 이름" -> "포트" -> ("연결된 블록 이름", "포트") (연결 정보)

    Methods:
        - __init__: 블록 매니저 객체 초기화
        - create_block: 블록 객체 생성
        - add_block: 블록 객체 추가
        - remove_block: 블록 객체 삭제
        - add_connection: 블록 객체 연결
        - remove_connection: 블록 객체 연결 해제

    Attributes Example:
        block_registry = {
            "AddictionBlock": Block,
            "SubtractionBlock": Block,
            "SplitInputBlock": Block,
            "DisconnectedBlock": Block
        }

        connection_registry = {
            "AddictionBlock": {
                "in0": [("SplitInputBlock", "out0")],
                "in1": [("SplitInputBlock", "out1")],
                "out0": [],
            },
        }
    """

    def __init__(self, block_registry=None, connection_registry=None) -> None:
        """
        BlockManager 객체 초기화

        Description:
            BlockManager 객체를 초기화합니다.

        Args:
            :param block_registry: block_registry(기본값: None)
            :param connection_registry: connection_registry(기본값: None)
        """

        self.BLOCK_TYPES = {
            "Block": Block,
            "FunctionBlock": FunctionBlock,
        }

        if block_registry is None:
            block_registry = {}
        if connection_registry is None:
            connection_registry = {}

        self.block_registry = block_registry
        self.connection_registry = connection_registry
        self.levels = {}

    def create_block(self, cfg: BlockConfig, **kwargs) -> Block:
        """
        블록 객체 생성

        Description:
            BlockConfig 객체를 받아서 블록 객체를 생성합니다.
            블록 객체를 생성할때, block registry에 블록 객체가 이미 있다면, ValueError를 발생합니다.
            TODO: ( Block Manager에서 이름을 알아서 지어주도록 수정)
        Returns:
            :return: 생성된 블록 객체
        """

        for key, value in kwargs.items():
            cfg.config[key] = value

        if cfg.name in self.block_registry or not validate_block_name(cfg.name):
            raise ValueError("Invalid block name")

        if cfg.block_type not in self.BLOCK_TYPES.keys():
            raise ValueError("Invalid block type")

        return self.BLOCK_TYPES[cfg.block_type](name=cfg.name, cfg=cfg, **cfg.config)

    def add_block(self, block: Block) -> None:
        """
        블록 객체 추가

        Description:
            블록 객체를 block registry에 추가합니다.
            connection_registry에도 추가합니다.
        Args:
            :param block: 추가할 블록 객체
        """
        if block.name in self.block_registry.keys():
            raise ValueError("Block already exists")

        self.block_registry[block.name] = block
        self.connection_registry[block.name] = {port: [] for port in block.ports}

    def remove_block(self, block_name: str) -> None:
        """
        블록 객체 삭제

        Description:
            블록 객체를 block registry에서 삭제합니다.
            connections registry에서도 삭제합니다
        Args:
            :param block_name: 삭제할 블록 객체의 이름
        """
        if block_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        _target_block = self.block_registry[block_name]

        for port in _target_block.ports:
            _tmp = []
            for (connected_block, connected_port) in self.connection_registry[block_name][port]:
                _tmp.append((connected_block, connected_port))
            for connected_block, connected_port in _tmp:
                self.remove_connection(f"{block_name}/{port}", f"{connected_block}/{connected_port}")

        del self.block_registry[block_name]
        del self.connection_registry[block_name]

    def add_connection(self, source_address, target_address):
        """
        블록 객체 연결

        Description:
            블록 객체를 연결합니다.
        Args:
            :param source_address: 연결할 블록 객체의 주소
            :param target_address: 연결될 블록 객체의 주소
        """
        source_name, source_port = source_address.split("/")
        target_name, target_port = target_address.split("/")

        if source_name not in self.block_registry.keys():
            raise ValueError(f"Block '{source_name}' does not exist")
        if target_name not in self.block_registry.keys():
            raise ValueError(f"Block '{target_name}' does not exist")

        if source_port not in self.block_registry[source_name].ports:
            raise ValueError(f"Port '{source_port}' does not exist")
        if target_port not in self.block_registry[target_name].ports:
            raise ValueError(f"Port '{target_port}' does not exist")

        if (target_name, target_port) in self.connection_registry[source_name][source_port]:
            raise ValueError("Connection already exists")

        self.connection_registry[source_name][source_port].append((target_name, target_port))
        self.connection_registry[target_name][target_port].append((source_name, source_port))

    def remove_connection(self, source_address, target_address):
        """
        블록 객체 연결 해제

        Description:
            블록 객체의 연결을 해제합니다.
        Args:
            :param source_address: 연결할 블록 객체의 주소
            :param target_address: 연결될 블록 객체의 주소
        """
        source_name, source_port = source_address.split("/")
        target_name, target_port = target_address.split("/")

        if source_name not in self.block_registry.keys() or target_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        if source_port not in self.block_registry[source_name].ports or target_port not in self.block_registry[
            target_name].ports:
            raise ValueError("Port does not exist")

        if (target_name, target_port) not in self.connection_registry[source_name][source_port]:
            raise ValueError("Connection does not exist")

        self.connection_registry[source_name][source_port].remove((target_name, target_port))
        print(f"Remove connection: {source_name}/{source_port} -> {target_name}/{target_port}")
        self.connection_registry[target_name][target_port].remove((source_name, source_port))
        print(f"Remove connection: {source_name}/{source_port} <- {target_name}/{target_port}")

    def get_block(self, block_name) -> Block | None:
        """
        블록 객체 반환
        :param block_name:
        :return: block
        """
        if block_name not in self.block_registry.keys():
            return None
        return self.block_registry[block_name]

    def get_connections(self, block_name) -> {}:
        """
        블록 객체 연결 정보 반환
        :param block_name:
        :return: list
        """
        if block_name not in self.connection_registry.keys():
            return {}
        return self.connection_registry[block_name]

    def get_connected_blocks(self, block_name: str, in_port=False, out_port=False) -> list:
        """
        블록과 연결되어있는 블록들의 이름을 반환합니다

        :param block_name:
        :param in_port: Boolean, in port에 연결된 블록들을 반환할건지
        :param out_port: Boolean, out port에 연결된 블록들을 반환할건지
        :return: str
        """
        if block_name not in self.block_registry.keys():
            raise ValueError(f"Block '{block_name}' does not exist")

        _connected_blocks = []
        for port in self.connection_registry[block_name]:
            for connected_block in self.connection_registry[block_name][port]:
                if in_port and "in" in port:
                    _connected_blocks.append(connected_block[0])
                if out_port and "out" in port:
                    _connected_blocks.append(connected_block[0])

        return list(set(_connected_blocks))

    def get_selected_group(self, block_name: str) -> list:
        """
        블록 하나를 선택하고, 연결되어있는 블록들을 그룹으로 묶어주고
        start block, end block, validation 정보를 반환

        Description:
            선택된 블럭이 포함된 그래프를 찾아서 그룹을 선택해줍니다.
            이걸 이제 실행가능하게 Block Graph에서 검사하고 실행가능하게 변경해줘야함

        Args:
            :param block_name: 반환할 블록 객체의 이름
        Returns:
            :return: 블록 객체의 연결 정보
        """

        if block_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        _connected_blocks = {}

        _queue = deque([block_name])

        while _queue:
            _current_block = _queue.popleft()
            _connected_blocks[_current_block] = True

            _current_connected_blocks = self.get_connected_blocks(_current_block, in_port=True, out_port=True)
            for connected_block in _current_connected_blocks:
                if connected_block not in _connected_blocks:
                    _queue.append(connected_block)

        return list(_connected_blocks.keys())


class BlockGraph:
    """
    """

    def __init__(self, block_registry=None, connection_registry=None) -> None:
        """
        BlockGraph 객체 초기화

        Description:
            BlockGroup 객체를 초기화합니다.

        Args:
            :param block_registry: block_registry(기본값: None)
            :param connection_registry: connection_registry(기본값: None)
        """

        if block_registry is None:
            block_registry = {}
        if connection_registry is None:
            connection_registry = {}

        self.block_registry = block_registry
        self.connection_registry = connection_registry
        self.start_blocks = []
        self.end_blocks = []
        self.levels = {}

    @staticmethod
    def find_start_end_blocks(block_names: list, connection_registry: dict, return_degree=False) -> Any:
        """
        시작 블럭과 끝 블럭을 찾아주는 함수

        Description:
            시작 블럭과 끝 블럭을 찾아주는 함수입니다.
            시작 블럭은 inport가 없는 블럭이며, 끝 블럭은 outport가 없는 블럭입니다.

        Args:
            :param block_names: 블록 이름 리스트
            :param connection_registry: 블록 연결 정보
            :param return_degree: in_degree, out_degree 반환 여부
        Returns:
            :return: 시작 블럭, 끝 블럭
        """

        in_degree = {node: 0 for node in block_names}
        out_degree = {node: 0 for node in block_names}

        for node in block_names:
            for port in connection_registry[node]:
                if "out" in port:
                    for connected_block, connected_port in connection_registry[node][port]:
                        in_degree[connected_block] += 1
                if "in" in port:
                    for connected_block, connected_port in connection_registry[node][port]:
                        out_degree[connected_block] += 1

        start_blocks = [node for node in in_degree if in_degree[node] == 0]
        end_blocks = [node for node in out_degree if out_degree[node] == 0]

        if return_degree:
            return start_blocks, end_blocks, in_degree, out_degree
        return start_blocks, end_blocks

    @staticmethod
    def validate_connections(block_names, start_blocks, end_blocks, connection_registry: dict) -> Any:
        validate_value = True
        invalid_blocks = []

        for node in block_names:
            for port in connection_registry[node]:
                if len(connection_registry[node][port]) == 0:
                    if (node in start_blocks and "out" in port) or \
                            (node in end_blocks and "in" in port) or (
                            node not in start_blocks and node not in end_blocks):
                        validate_value = False
                        invalid_blocks.append(node)

        return validate_value, invalid_blocks

    def create_graph(self, block_names: list, block_registry: dict, connection_registry: dict) -> Any:
        """
        블록 그래프 객체 생성

        Description:
            block manager에서 block_names들을 받고 블럭 그래프를 생성합니다.
            만약, 실행이 불가능하다면 블럭 그래프를 생성하지 않고 ValueError를 발생합니다.
        """

        self.start_blocks, self.end_blocks, in_degree, out_degree = (
            self.find_start_end_blocks(block_names, connection_registry,
                                       return_degree=True))

        if len(self.start_blocks) == 0:
            raise Exception("No start block")

        validate_value, error_blocks = self.validate_connections(block_names,
                                                                 self.start_blocks,
                                                                 self.end_blocks,
                                                                 connection_registry)
        if not validate_value:
            raise ValueError(f"Invalid connection: {list(set(error_blocks))}")

        # 진입 차수가 0인 노드를 큐에 삽입
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        levels = defaultdict(list)
        level = 0

        while queue:
            next_queue = deque()
            while queue:
                current = queue.popleft()
                levels[level].append(current)
                for port in connection_registry[current]:
                    if "out" in port:
                        for connected_block, connected_port in connection_registry[current][port]:
                            in_degree[connected_block] -= 1
                            if in_degree[connected_block] == 0:
                                next_queue.append(connected_block)
            queue = next_queue
            level += 1

        # 그래프에 사이클이 있는 경우
        if sum(len(nodes) for nodes in levels.values()) != len(block_names):
            raise Exception("Graph has at least one cycle")

        # 여기까지 통과했으면 이제 완전히 잘 연결된 그래프임
        # 1. start block, end block 잘 정의딤
        # 2. middle block들은 전부 잘 연결되어있음
        # 3. DAG임
        # 4. levels에는 레벨별로 잘 정리됨

        for block_name in block_names:
            self.block_registry[block_name] = block_registry[block_name]
            self.connection_registry[block_name] = connection_registry[block_name]

        self.levels = levels

        return levels, self.start_blocks, self.end_blocks

    def __call__(self, input_dict=dict) -> tuple:
        """
        Input Example:
        input = {
            "StartBlock1": {
                "in0": 1,
                "in1": 2,
            },
            "StartBlock2": {
                "in0": 3,
                "in1": 4,
            }
        }
        """

        if set(input_dict.keys()) != set(self.start_blocks):
            raise ValueError(f"Invalid input {input_dict.keys()} != {self.start_blocks}")

        output = {}

        for level in self.levels.values():
            for block_name in level:
                block = self.block_registry[block_name]
                block_input = {}
                if block_name in self.start_blocks:
                    block_input = input_dict[block_name]
                else:
                    for port in self.connection_registry[block_name]:
                        if "in" in port:
                            for connected_block, connected_port in self.connection_registry[block_name][port]:
                                block_input[port] = output[connected_block][connected_port]

                output[block_name] = block(**block_input)

        return {key: output[key] for key in self.end_blocks}, output
