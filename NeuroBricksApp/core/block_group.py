from typing import Any

from .block_validation import validate_block_name
from .block import *
import inspect
from collections import deque, defaultdict

class BlockGraph:
    """
    """

    def __init__(self, block_registry=None, connection_registry=None) -> None:
        """
        BlockManager 객체 초기화

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

    def get_selected_group(self, block_name: str, block_register=None, connection_register=None) -> list:
        """
        블록 하나를 선택하고, 연결되어있는 블록들을 그룹으로 묶어주고
        start block, end block, validation 정보를 반환

        Description:
            블록 객체의 연결 정보를 반환합니다.

        Args:
            :param block_name: 반환할 블록 객체의 이름
        Returns:
            :return: 블록 객체의 연결 정보
        """
        if block_register is None:
            block_register = self.block_registry
        if connection_register is None:
            connection_register = self.connection_registry

        if block_name not in block_register.keys():
            raise ValueError("Block does not exist")

        _connected_blocks = {}

        _queue = deque([block_name])

        while _queue:
            _current_block = _queue.popleft()
            _connected_blocks[_current_block] = True

            _connected_block_set = set([connected_block for connected_block, _ in connection_register[_current_block].values()])
            for connected_block in list(_connected_block_set):
                if connected_block not in _connected_blocks:
                    _queue.append(connected_block)

        return list(_connected_blocks.keys())


class BlockManager:
    """
    BlockManager Class

    Description:
        이 클래스는 NeuroBricks 의 블록 매니저 객체를 정의합니다.\n
        블록 객체 리스트, 블록 연결 정보를 관리합니다

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

        if source_name not in self.block_registry.keys() or target_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        if source_port not in self.block_registry[source_name].ports or target_port not in self.block_registry[target_name].ports:
            raise ValueError("Port does not exist")

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

        if source_port not in self.block_registry[source_name].ports or target_port not in self.block_registry[target_name].ports:
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

    def get_selected_group(self, block_name: str, block_register=None, connection_register=None) -> list:
        """
        블록 하나를 선택하고, 연결되어있는 블록들을 그룹으로 묶어주고
        start block, end block, validation 정보를 반환

        Description:
            블록 객체의 연결 정보를 반환합니다.

        Args:
            :param block_name: 반환할 블록 객체의 이름
        Returns:
            :return: 블록 객체의 연결 정보
        """
        if block_register is None:
            block_register = self.block_registry
        if connection_register is None:
            connection_register = self.connection_registry

        if block_name not in block_register.keys():
            raise ValueError("Block does not exist")

        _connected_blocks = {}

        _queue = deque([block_name])

        while _queue:
            _current_block = _queue.popleft()
            _connected_blocks[_current_block] = True

            _connected_block_set = set([connected_block[0][0]
                                        for connected_block in connection_register[_current_block].values() if len(connected_block) > 0])
            for connected_block in list(_connected_block_set):
                if connected_block not in _connected_blocks:
                    _queue.append(connected_block)

        return list(_connected_blocks.keys())