from typing import Any

from .block_validation import validate_block_name
from .block import *
import inspect

class BlockGroup:
    """
    BlockManager Class

    Description:
        이 클래스는 NeuroBricks 의 블록 매니저 객체를 정의합니다.\n
        블록 객체 리스트, 블록 연결 정보를 관리합니다

    Attributes:
        - block_registry(dict): key: 블록 이름 (str), value: 블록 객체 (block)
        - connection_registry(dict): address -> address list (연결 정보)

    Methods:
        - __init__: 블록 매니저 객체 초기화
        - create_block: 블록 객체 생성
        - add_block: 블록 객체 추가
        - remove_block: 블록 객체 삭제
        - add_connection: 블록 객체 연결
        - remove_connection: 블록 객체 연결 해제
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
            (추후 이름을 알아서 지어주도록 수정)
        Returns:
            :return: 생성된 블록 객체
        """

        for key, value in kwargs.items():
            cfg.config[key] = value

        if cfg.name in self.block_registry or not validate_block_name(cfg.name):
            raise ValueError("Invalid block name")

        if cfg.block_type in self.BLOCK_TYPES.keys():
            return self.BLOCK_TYPES[cfg.block_type](name=cfg.name, cfg=cfg, **cfg.config)
        else:
            raise ValueError("Invalid block type")

    def add_block(self, block: Block) -> None:
        """
        블록 객체 추가

        Description:
            블록 객체를 block registry에 추가합니다.

        Args:
            :param block: 추가할 블록 객체
        """
        if block.name in self.block_registry.keys():
            raise ValueError("Block already exists")

        self.block_registry[block.name] = block

    def remove_block(self, block_name: str) -> None:
        """
        블록 객체 삭제

        Description:
            블록 객체를 block registry에서 삭제합니다.

        Args:
            :param block_name: 삭제할 블록 객체의 이름
        """
        if block_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        del self.block_registry[block_name]

    def add_connection(self, source_address: str, target_address: str) -> None:
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

        if (source_name not in self.block_registry.keys() or
                target_name not in self.block_registry.keys()):
            raise ValueError("Block does not exist")

        if (source_port not in self.block_registry[source_name].ports.keys() or
                target_port not in self.block_registry[target_name].ports.keys()):
            raise ValueError("Port does not exist")

        # connection_registry source_address 없으면 []로 초기화
        if source_address not in self.connection_registry.keys():
            self.connection_registry[source_address] = []

        if target_address in self.connection_registry[source_address]:
            raise ValueError("Connection already exists")

        self.connection_registry[source_address].append(target_address)
        self.block_registry[source_name].add_connection(source_port, target_address)
        self.block_registry[target_name].add_connection(target_port, source_address)

    def remove_connection(self, source_address: str, target_address: str) -> None:
        """
        블록 객체 연결 해제

        Description:
            블록 객체의 연결을 해제합니다.

        Args:
            :param source_address: 연결할 블록 객체의 주소
            :param target_address: 연결될 블록 객체의 주소
        """
        if source_address not in self.connection_registry.keys():
            raise ValueError("Source address does not exist")

        if target_address not in self.connection_registry[source_address]:
            raise ValueError("Connection does not exist")

        self.connection_registry[source_address].remove(target_address)

    def get_block(self, block_name: str) -> Any | None:
        """
        블록 객체 반환

        Description:
            블록 객체를 반환합니다.

        Args:
            :param block_name: 반환할 블록 객체의 이름
        Returns:
            :return: 블록 객체
        """
        if block_name not in self.block_registry.keys():
            return None

        return self.block_registry[block_name]

    def get_connection(self, source_address: str) -> list:
        """
        블록 객체 연결 정보 반환

        Description:
            블록 객체의 연결 정보를 반환합니다.

        Args:
            :param source_address: 반환할 블록 객체의 주소
        Returns:
            :return: 블록 객체의 연결 정보
        """
        if source_address not in self.connection_registry.keys()\
                or len(self.connection_registry[source_address]) == 0:
            return []

        return self.connection_registry[source_address]


class BlockManager:
    """
    BlockManager Class

    Description:
        이 클래스는 NeuroBricks 의 블록 매니저 객체를 정의합니다.\n
        블록 객체 리스트, 블록 연결 정보를 관리합니다

    Attributes:
        - block_registry(dict): key: 블록 이름 (str), value: 블록 객체 (block)
        - connection_registry(dict): address -> address list (연결 정보)

    Methods:
        - __init__: 블록 매니저 객체 초기화
        - create_block: 블록 객체 생성
        - add_block: 블록 객체 추가
        - remove_block: 블록 객체 삭제
        - add_connection: 블록 객체 연결
        - remove_connection: 블록 객체 연결 해제
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
            (추후 이름을 알아서 지어주도록 수정)
        Returns:
            :return: 생성된 블록 객체
        """

        for key, value in kwargs.items():
            cfg.config[key] = value

        if cfg.name in self.block_registry or not validate_block_name(cfg.name):
            raise ValueError("Invalid block name")

        if cfg.block_type in self.BLOCK_TYPES.keys():
            return self.BLOCK_TYPES[cfg.block_type](name=cfg.name, cfg=cfg, **cfg.config)
        else:
            raise ValueError("Invalid block type")

    def add_block(self, block: Block) -> None:
        """
        블록 객체 추가

        Description:
            블록 객체를 block registry에 추가합니다.

        Args:
            :param block: 추가할 블록 객체
        """
        if block.name in self.block_registry.keys():
            raise ValueError("Block already exists")

        self.block_registry[block.name] = block

    def remove_block(self, block_name: str) -> None:
        """
        블록 객체 삭제

        Description:
            블록 객체를 block registry에서 삭제합니다.

        Args:
            :param block_name: 삭제할 블록 객체의 이름
        """
        if block_name not in self.block_registry.keys():
            raise ValueError("Block does not exist")

        del self.block_registry[block_name]

    def add_connection(self, source_address: str, target_address: str) -> None:
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

        if (source_name not in self.block_registry.keys() or
                target_name not in self.block_registry.keys()):
            raise ValueError("Block does not exist")

        if (source_port not in self.block_registry[source_name].ports.keys() or
                target_port not in self.block_registry[target_name].ports.keys()):
            raise ValueError("Port does not exist")

        # connection_registry source_address 없으면 []로 초기화
        if source_address not in self.connection_registry.keys():
            self.connection_registry[source_address] = []

        if target_address in self.connection_registry[source_address]:
            raise ValueError("Connection already exists")

        self.connection_registry[source_address].append(target_address)
        self.block_registry[source_name].add_connection(source_port, target_address)
        self.block_registry[target_name].add_connection(target_port, source_address)

    def remove_connection(self, source_address: str, target_address: str) -> None:
        """
        블록 객체 연결 해제

        Description:
            블록 객체의 연결을 해제합니다.

        Args:
            :param source_address: 연결할 블록 객체의 주소
            :param target_address: 연결될 블록 객체의 주소
        """
        if source_address not in self.connection_registry.keys():
            raise ValueError("Source address does not exist")

        if target_address not in self.connection_registry[source_address]:
            raise ValueError("Connection does not exist")

        self.connection_registry[source_address].remove(target_address)

    def get_block(self, block_name: str) -> Any | None:
        """
        블록 객체 반환

        Description:
            블록 객체를 반환합니다.

        Args:
            :param block_name: 반환할 블록 객체의 이름
        Returns:
            :return: 블록 객체
        """
        if block_name not in self.block_registry.keys():
            return None

        return self.block_registry[block_name]

    def get_connection(self, source_address: str) -> list:
        """
        블록 객체 연결 정보 반환

        Description:
            블록 객체의 연결 정보를 반환합니다.

        Args:
            :param source_address: 반환할 블록 객체의 주소
        Returns:
            :return: 블록 객체의 연결 정보
        """
        if source_address not in self.connection_registry.keys()\
                or len(self.connection_registry[source_address]) == 0:
            return []

        return self.connection_registry[source_address]