from NeuroBricksApp.core import block, block_validation, block_group
import unittest
import math


class TestBlock(unittest.TestCase):
    def test_FunctionBlock(self):
        block1 = block.FunctionBlock(name="AddictionBlock",
                                     display_name="더하기 블럭",
                                     function=lambda in0, in1: (in1, in0),
                                     num_inputs=2,
                                     num_outputs=2)
        res = block1(**{
            "in0": 3,
            "in1": 5
        })
        print(res)


    def test_BlockConfig(self):
        cfg1 = block.BlockConfig(name="TestConfig",
                                 description="테스트용 Config",
                                 in_channels=3,
                                 kernel_size=[7, 1, 2],
                                 stride=1,
                                 padding=1)
        cfg1.name = "TestConfig"
        cfg1.description = "ABC"

        cfg1.test_attr = "test"
        cfg1.config["magic_attr"] = "test"
        print(cfg1.config)

        assert cfg1.name == "TestConfig"
        assert cfg1.description == "ABC"
        assert cfg1.in_channels == 3
        assert cfg1.kernel_size == [7, 1, 2]

    def test_BlockManager(self):
        manager = block_group.BlockManager()
        block1 = block.FunctionBlock(name="AddictionBlock",
                                     display_name="더하기 블럭",
                                     function=lambda x, y: x + y,
                                     num_inputs=2,
                                     num_outputs=1)

        block2 = block.FunctionBlock(name="SubtractionBlock",
                                     display_name="빼기 블럭",
                                     function=lambda x, y: x - y,
                                     num_inputs=2,
                                     num_outputs=1)
        manager.add_block(block1)
        manager.add_block(block2)

        manager.add_connection("AddictionBlock/out0", "SubtractionBlock/in0")
        manager.add_connection("AddictionBlock/out0", "SubtractionBlock/in1")

        assert ("SubtractionBlock", "in0") in manager.get_connections("AddictionBlock")["out0"]
        assert ("SubtractionBlock", "in1") in manager.get_connections("AddictionBlock")["out0"]

        assert manager.get_block("AddictionBlock") == block1
        assert manager.get_block("SubtractionBlock") == block2

    def test_block_group(self):
        block0 = block.FunctionBlock(name="SplitInputBlock",
                                     display_name="입력 블럭",
                                     function=lambda x: x,
                                     num_inputs=1,
                                     num_outputs=2)
        block1 = block.FunctionBlock(name="AddictionBlock",
                                     display_name="더하기 블럭",
                                     function=lambda x, y: math.sin(x + y),
                                     num_inputs=2,
                                     num_outputs=1)
        block2 = block.FunctionBlock(name="SubtractionBlock",
                                     display_name="빼기 블럭",
                                     function=lambda x: math.asin(x),
                                     num_inputs=1,
                                     num_outputs=1)

        block3 = block.FunctionBlock(name="DisconnectedBlock",
                                     display_name="연결되지 않은 블럭",
                                     function=lambda x: x,
                                     num_inputs=1,
                                     num_outputs=1)

        manager = block_group.BlockManager()
        manager.add_block(block0)
        manager.add_block(block1)
        manager.add_block(block2)
        manager.add_block(block3)
        manager.add_connection("SplitInputBlock/out0", "AddictionBlock/in0")
        manager.add_connection("SplitInputBlock/out1", "AddictionBlock/in1")
        manager.add_connection("AddictionBlock/out0", "SubtractionBlock/in0")

        print("!!")

        selected_group = manager.get_selected_group("AddictionBlock")  # 연결되어있는 블록들을 그룹으로 묶어줌
        print(selected_group)
        assert len(selected_group) == 3
        assert "AddictionBlock" in selected_group
        assert "SplitInputBlock" in selected_group
        assert "SubtractionBlock" in selected_group
        assert "DisconnectedBlock" not in selected_group

        selected_group = manager.get_selected_group("DisconnectedBlock")  # 연결되어있지 않은 블록들을 그룹으로 묶어줌
        assert len(selected_group) == 1
        assert "DisconnectedBlock" in selected_group

        manager.add_connection("AddictionBlock/out0", "DisconnectedBlock/in0")
        selected_group = manager.get_selected_group("DisconnectedBlock")
        print(selected_group)

        print(manager.get_connections("AddictionBlock"))


        manager.remove_block("AddictionBlock")
        selected_group = manager.get_selected_group("DisconnectedBlock")
        print(selected_group)
        assert len(selected_group) == 1

    def test_block_graph(self):
        block0 = block.FunctionBlock(name="입력분리블럭",
                                     display_name="입력 블럭",
                                     function=lambda x: (x, x),
                                     num_inputs=1,
                                     num_outputs=2)
        block1 = block.FunctionBlock(name="더하기블럭",
                                     display_name="증가 블럭",
                                     function=lambda x: x + 20,
                                     num_inputs=1,
                                     num_outputs=1)
        block2 = block.FunctionBlock(name="빼기블럭",
                                     display_name="감소 블럭",
                                     function=lambda x: x - 10,
                                     num_inputs=1,
                                     num_outputs=1)

        block3 = block.FunctionBlock(name="곱하기블럭",
                                     display_name="곱하기 블럭",
                                     function=lambda x, y: x*y,
                                     num_inputs=2,
                                     num_outputs=1)
        block4 = block.FunctionBlock(name="그냥블럭",
                                     display_name="그냥 블럭",
                                     function=lambda x: x,
                                     num_inputs=1,
                                     num_outputs=1)

        manager = block_group.BlockManager()
        manager.add_block(block0)
        manager.add_block(block1)
        manager.add_block(block2)
        manager.add_block(block3)
        manager.add_block(block4)
        manager.add_connection("입력분리블럭/out0", "더하기블럭/in0")
        manager.add_connection("입력분리블럭/out1", "빼기블럭/in0")
        manager.add_connection("더하기블럭/out0", "곱하기블럭/in0")
        manager.add_connection("빼기블럭/out0", "곱하기블럭/in1")
        manager.add_connection("곱하기블럭/out0", "그냥블럭/in0")
        selected_blocks = manager.get_selected_group("빼기블럭")
        # print(selected_blocks)
        assert len(selected_blocks) == 5  # 입력분리, 뺴기, 더하기, 곱하기
        graph = block_group.BlockGraph()
        levels, start_blocks, end_blocks = graph.create_graph(selected_blocks, manager.block_registry, manager.connection_registry)
        # print(levels)

        assert '입력분리블럭' in start_blocks
        assert '그냥블럭' in end_blocks


    def test_DAG(self):
        from collections import defaultdict, deque

        def topological_sort_with_levels(graph):
            # 각 노드의 진입 차수를 계산
            in_degree = {node: 0 for node in graph}
            for node in graph:
                for neighbor in graph[node]:
                    in_degree[neighbor] += 1

            # 진입 차수가 0인 노드를 큐에 삽입
            queue = deque([node for node in in_degree if in_degree[node] == 0])
            levels = defaultdict(list)
            level = 0

            while queue:
                next_queue = deque()
                while queue:
                    current = queue.popleft()
                    levels[level].append(current)
                    for neighbor in graph[current]:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            next_queue.append(neighbor)
                queue = next_queue
                level += 1

            # 그래프에 사이클이 있는 경우
            if sum(len(nodes) for nodes in levels.values()) != len(graph):
                raise Exception("Graph has at least one cycle")

            return levels

        # 예시 그래프 (DAG)
        graph = {
            '1': ['2'],
            '2': ['3', '7'],
            '3': ['4'],
            '4': ['5'],
            '5': ['6'],
            '7': ['9'],
            '6': ['8'],
            '8': [],
            '9': ['8'],
        }

        try:
            levels = topological_sort_with_levels(graph)
            for level, nodes in levels.items():
                print(f"Level {level}: {', '.join(nodes)}")
        except Exception as e:
            print(e)




if __name__ == "__main__":
    unittest.main()
