from NeuroBricksApp.core import block, block_validation
import unittest


class TestBlock(unittest.TestCase):
    def test_FunctionBlock(self):
        block1 = block.FunctionBlock(name="AddictionBlock",
                                     display_name="더하기 블럭",
                                     function=lambda x, y: x + y,
                                     num_inputs=2,
                                     num_outputs=1)
        print(block1(1, 2))
        print(block1(block1(1, 2), 3))
        print(block1)
        print(block1.get_connections())

        assert block1(1, 2) == 3
        assert block1(block1(1, 2), 3) == 6



if __name__ == "__main__":
    unittest.main()
