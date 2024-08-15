from ..core import block
import pytest

def test_block_connection():

    block1 = block.FunctionBlock(name="AddictionBlock",
                                 display_name="더하기 블럭",
                                 function=lambda x, y: x + y,
                                 num_inputs=2,
                                 num_outputs=1)




