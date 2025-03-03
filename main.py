from tests.m_tests import *
from tests.config import *
from tests.yuma_tests import *

from unittest.mock import patch, MagicMock


run_bat_and_wait_for_output("run_yuma.bat", "Entering main loop.")


if __name__ == "__main__":
    test_check_moves()
    
    find_yuma_on_screen(confidence=0.7)