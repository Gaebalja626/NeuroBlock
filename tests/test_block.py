from NeuroBricksApp.core import block, block_validation
import unittest


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
        manager = block.BlockManager()
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


if __name__ == "__main__":
    unittest.main()
