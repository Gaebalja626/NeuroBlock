from NeuroBricksApp.core import block, block_validation, block_group
import unittest
import math

class TestBlock(unittest.TestCase):
    def test_FunctionBlock(self):
        block1 = block.FunctionBlock(name="AddictionBlock",
                                     display_name="더하기 블럭",
                                     function=lambda x, y: x + y,
                                     num_inputs=2,
                                     num_outputs=1)
        assert block1.name == "AddictionBlock"
        assert block1(1, 2) == 3
        assert block1(block1(1, 2), 3) == 6

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

        assert "SubtractionBlock/in0" in manager.get_connection("AddictionBlock/out0")
        assert "SubtractionBlock/in1" in manager.get_connection("AddictionBlock/out0")

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

        manager = block_group.BlockManager()
        manager.add_block(block0)
        manager.add_block(block1)
        manager.add_block(block2)
        manager.add_connection("SplitInputBlock/out0", "AddictionBlock/in0")
        manager.add_connection("SplitInputBlock/out1", "AddictionBlock/in1")
        manager.add_connection("AddictionBlock/out0", "SubtractionBlock/in0")

        selected_group = manager.select_group("AddictionBlock")  # 연결되어있는 블록들을 그룹으로 묶어줌


        assert len(selected_group) ==  3





if __name__ == "__main__":
    unittest.main()
