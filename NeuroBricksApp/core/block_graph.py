from .block_validation import validate_block_name
from .block import *
from collections import deque, defaultdict
import copy


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

    def get_start_blocks(self):
        return self.start_blocks

    def get_end_blocks(self):
        return self.end_blocks

    def get_block(self, block_name):
        return self.block_registry[block_name]

    def get_connection(self, block_name):
        return self.connection_registry[block_name]

    def get_num_inputs(self):
        return sum([self.block_registry[block].num_inputs for block in self.start_blocks])

    def get_num_outputs(self):
        return sum([self.block_registry[block].num_outputs for block in self.end_blocks])

    def get_input_dict(self):
        input_dict = {}
        for block_name in self.start_blocks:
            input_dict[block_name] = {}
            for port in self.connection_registry[block_name]:
                if "in" in port:
                    input_dict[block_name][port] = None
        return input_dict