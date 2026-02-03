###################################################################################
#   Copyright (c) 2024, 2025 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Utility functions to describe the STM32 target
"""

import os
from pathlib import Path
from typing import Tuple


from exceptions import ExcToolsErr, ExecutableNotFoundError


class DevicePropertyDesc():
    """Target descriptor"""

    def __init__(self, target: str = 'stm32n6'):
        """Constructor"""

        if target != 'stm32n6':
            raise ExcToolsErr('Only the \'stm32n6570-dk\' is supported')

        self._target: str = target

    @property
    def ext_base_address(self) -> int:
        """Return the base @ of the external memory"""

        return 0x60000000

    @property
    def mcu_core_type(self) -> str:
        """Return MCU core type"""

        return 'cortex-m55'


class BoardPropertyDesc():
    """Board descriptor"""

    def __init__(self, board: str = 'stm32n6570-dk'):
        """Constructor"""

        if board != 'stm32n6570-dk':
            raise ExcToolsErr('Only the \'stm32n6570-dk\' board is supported')

        self._board: str = board

    @property
    def name(self):
        """Return name of the board"""
        return self._board

    def ext_loader_name(self) -> str:
        """."""
        return "MX66UW1G45G_STM32N6570-DK.stldr"

    def max_exec_ram_size(self, ext: bool = False) -> int:
        """Return max executable ram size"""
        if ext:
            return 4 * 1024 * 1024
        return (512 + 128) * 1024

    def max_ext_ram_size(self) -> int:
        """Return max external ram size"""
        return 27 * 1024 * 1024

    def validation_fw_name(self,
                           mode: str = 'copy',
                           baudrate: str = '921600') -> Tuple[Path, str, str]:
        """."""
        current_ = Path(os.path.dirname(os.path.realpath(__file__))) / 'test'
        f_name = f'{self.name}-validation-reloc-{mode}.elf'
        if baudrate != '921600':
            f_name = f'{self.name}-validation-reloc-{mode}-{baudrate}.elf'
        app_ = current_ / f_name

        if not app_.is_file():
            msg_ = f'The \'{app_}\' is not available'
            raise ExecutableNotFoundError(msg_)

        return app_, '0x71000000', '0x71800000'
