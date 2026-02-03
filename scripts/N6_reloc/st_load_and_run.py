###################################################################################
#   Copyright (c) 2025 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Utility function to deploy a relocatable model
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import time

from misc import Params, create_logger
from tools import STM32CubeIDEResources, CExecutable
from target import BoardPropertyDesc
from binary_mgr import RelocBinaryImage
from exceptions import ExcToolsErr


#
# History
#
#   v1.0 - initial version
#   v1.1 - add llvm/(st-)clang support
#   v1.2 - add support for usbc test firmware
#


__title__ = 'NPU Utility - ST Load and run (dev environment)'
__version__ = '1.2'
__author__ = 'STMicroelectronics'


_DEFAULT_INPUT = 'build/network_rel.bin'
_GDB_SERVER_PORTNO = 36789
_DEFAULT_BOARD = 'stm32n6570-dk'
_DEFAULT_DEST_ADDR = '0x71000000,0x71800000'


def _get_params_file(net_file) -> str:
    """."""
    pfile_ = Path(net_file)
    stem_ = pfile_.stem
    suffix_ = pfile_.suffix
    if stem_.endswith('_rel'):
        nstem_ = stem_ + '_params' + suffix_
        npfile_ = pfile_.parent / nstem_
        return str(npfile_)
    return ''


def st_load_and_run(params: Params, no_banner: bool = False):
    """Post-Process the elf file"""

    logger = logging.getLogger()
    binary_file = Path(params.input)

    mode_params = params.mode.split(',')
    install_mode = 'xip' if 'xip' in mode_params else 'copy'
    if 'ext' in mode_params:
        install_mode = f'{install_mode}-ext'
    no_flash = bool('no-flash' in mode_params)
    no_run = bool('no-run' in mode_params)
    baudrate = '5529600' if 'max-speed' in mode_params else '921600'
    if 'usbc' in mode_params:
        baudrate = 'usbc'
        com_desc = 'serial'
    else:
        com_desc = f'serial:{baudrate}'

    if not no_banner:
        logger.info('%s (version %s)', __title__, __version__)
        logger.info('Creating date : %s', datetime.now().ctime())
        logger.info('')

    logger.info('Entry point    : \'%s\'', binary_file)
    logger.info('Board          : \'%s\'', params.board)
    logger.info('mode           : %s', mode_params)

    bin_img = RelocBinaryImage(binary_file)
    bin_img.check()
    bin_rt_ctx = bin_img.get_rt_context()
    params_off = bin_img.PARAMS_offset()
    use_clang = bin_img.toolchain.is_clang()

    if params_off == 0:
        params_file = _get_params_file(binary_file)
        if Path(params_file).is_file():
            logger.info('split model    : \'%s\'', params_file)
        else:
            msg_ = f'File \'{params_file}\' is requested.'
            raise ExcToolsErr(msg_)
    else:
        logger.info('split model    : %s', False)
    logger.info('clang mode     : %s', use_clang)
    logger.info('exec sz        : XIP=%s COPY=%s', f'{bin_img.XIP_size():,}', f'{bin_img.COPY_size():,}')
    logger.info('acts/params sz : acts=%s params=%s', f'{bin_rt_ctx["acts_sz"]:,}', f'{bin_rt_ctx["params_sz"]:,}')
    logger.info('ext ram sz     : %s', f'{bin_rt_ctx["ext_ram_sz"]:,}')

    if 'xip' in mode_params and use_clang:
        logger.warning('XIP mode is not supported with CLANG toolchain, COPY mode is forced')
        install_mode = 'copy' if 'ext' not in mode_params else 'copy-ext'

    logger.info('')

    board = BoardPropertyDesc(params.board)
    cube_ide = STM32CubeIDEResources(params.cube_ide_dir)

    logger.info('board size     : exec=(int=%s, ext=%s), ext=%s',
                f'{board.max_exec_ram_size():,}',
                f'{board.max_exec_ram_size(ext=True):,}',
                f'{board.max_ext_ram_size():,}')

    if bin_rt_ctx['ext_ram_sz'] > board.max_ext_ram_size():
        msg_ = 'Model requires more external RAM than available '
        msg_ += f'{bin_rt_ctx["ext_ram_sz"]:,} > {board.max_ext_ram_size():,}'
        raise ExcToolsErr(msg_)

    if 'xip' in install_mode and board.max_exec_ram_size() < bin_img.XIP_size():
        if 'ext' not in install_mode:
            logger.warning('COPY mode in external RAM is used')
            install_mode = 'xip-ext'
    elif 'copy' in install_mode and board.max_exec_ram_size() < bin_img.COPY_size():
        if 'ext' not in install_mode:
            logger.warning('Model will be installed in external RAM')
            install_mode = 'copy-ext'

    logger.info('install mode   : \'%s\'', install_mode)
    logger.info('')

    validation_fw_, dst_addr_, param_addr_ = board.validation_fw_name(f'{install_mode}',
                                                                      baudrate)

    cube_prg: CExecutable = cube_ide.cube_programmer
    logger.info("Resetting the board.")
    cmds = ['-q', '-c', 'port=SWD', 'mode=powerdown', 'freq=2000', 'ap=1']
    cube_prg.run(cmds, assert_on_error=False)

    time.sleep(1)

    if not no_flash:
        file_stats = os.stat(binary_file)
        size = file_stats.st_size
        logger.info("Flashing \'%s\' at address %s (size=%s)..", binary_file, dst_addr_, size)
        el = cube_prg.parent / "ExternalLoader" / board.ext_loader_name()
        cmds = ['-q', '-c', 'port=SWD', 'mode=hotplug', 'freq=2000', 'ap=1', '--extload',
                el, '--download', str(binary_file), str(dst_addr_)]
        cube_prg.run(cmds, assert_on_error=True, verbosity=params.verbosity > 1)
        if params_off == 0:
            file_stats = os.stat(params_file)
            size = file_stats.st_size

            logger.info("Resetting the board.")
            cmds = ['-q', '-c', 'port=SWD', 'mode=powerdown', 'freq=2000', 'ap=1']
            cube_prg.run(cmds, assert_on_error=False)

            logger.info("Flashing \'%s\' at address %s (size=%s)..", params_file, param_addr_, size)
            el = cube_prg.parent / "ExternalLoader" / board.ext_loader_name()
            cmds = ['-q', '-c', 'port=SWD', 'mode=hotplug', 'freq=2000', 'ap=1', '--extload',
                    el, '--download', str(params_file), str(param_addr_)]
            cube_prg.run(cmds, assert_on_error=True, verbosity=params.verbosity > 1)

        time.sleep(1)
    else:
        logger.warning('\'%s\' is not flashed', binary_file)
        if params_off == 0:
            logger.warning('\'%s\' is not flashed', params_file)

    logger.debug("Starting GDB server port=%s..", _GDB_SERVER_PORTNO)
    cmds = ["-d", "--frequency", "2000", "--apid", "1", "-v",
            "--port-number", str(_GDB_SERVER_PORTNO), "-cp",
            cube_prg.parent]
    cube_ide.gdb_server.run_detached(cmds, verbosity=params.verbosity > 1)

    time.sleep(1)

    logger.info("Loading & start the validation application \'%s\'..", validation_fw_.stem)
    cmds = [
        "-ex", f"target remote :{_GDB_SERVER_PORTNO}",
        "-ex", "monitor reset",
        "-ex", "load",
        "-ex", "set $pc = Reset_Handler",
        "-ex", "detach",
        "-ex", "quit",
        str(validation_fw_)]
    cube_ide.gdb_client.run(cmds, verbosity=params.verbosity > 1)
    cube_ide.gdb_server.kill()

    logger.info("Deployed model is started and ready to be used.")

    if no_run:
        logger.info('')
        return 0

    time.sleep(1)

    logger.info("Executing the deployed model (desc=%s)..", com_desc)
    logger.info('')

    try:
        from stm_ai_runner import AiRunner
    except ImportError:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_runner'))
        try:
            from stm_ai_runner import AiRunner
        except ImportError:
            logger.error('Update the \'PYTHONPATH\' to find the stm_ai_runner Python module.')
            return -1

    runner = AiRunner(debug=params.debug)
    runner.connect(desc=com_desc)
    if not runner.is_connected:
        logger.error(runner.get_error())
        return -1

    runner.summary(print_fn=logger.info)

    inputs = runner.generate_rnd_inputs(batch_size=2)
    mode = AiRunner.Mode.PER_LAYER
    if params.debug:
        mode |= AiRunner.Mode.DEBUG
    outputs, profiler = runner.invoke(inputs,  # disable_pb=True,
                                      mode=mode)
    runner.print_profiling(inputs, profiler, outputs,
                           print_fn=logger.info,
                           tensor_info=False)

    runner.disconnect()

    return 0


def main():
    """Script entry point."""

    parser = argparse.ArgumentParser(description=f'{__title__} v{__version__}')

    parser.add_argument('--input', '-i', metavar='STR', type=str,
                        help='location of the binary files (default: %(default)s)',
                        default=_DEFAULT_INPUT)

    parser.add_argument('--board', metavar='STR', type=str,
                        help='ST development board (default: %(default)s)',
                        default=_DEFAULT_BOARD)

    parser.add_argument('--address', metavar='STR', type=str,
                        help='destination address - model(,params) (default: %(default)s)',
                        default=_DEFAULT_DEST_ADDR)

    parser.add_argument('--mode', metavar='STR', type=str,
                        help='fw variants: copy,xip[no-flash,no-run,usbc,ext,max-speed]',
                        default='copy')

    parser.add_argument('--cube-ide-dir', metavar='STR', type=str,
                        help='installation directory of STM32CubeIDE tools (ex. ~/ST/STM32CubeIDE_1.18.0/STM32CubeIDE)',
                        default='')

    parser.add_argument('--log', metavar='STR', type=str, nargs='?',
                        default='no-log',
                        help='log file')

    parser.add_argument('--verbosity', '-v',
                        nargs='?', const=1, type=int, choices=range(0, 3),
                        default=1, help="set verbosity level")

    parser.add_argument('--debug', action='store_const', const=1,
                        help='enable internal log (DEBUG PURPOSE)')

    parser.add_argument('--no-color', action='store_const', const=1,
                        help='disable log color support')

    params: Params = Params(parser.parse_args())

    logger = create_logger(params, Path(__file__).stem)

    try:
        res = st_load_and_run(params)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e, stack_info=False, exc_info=params.debug)
        return -1

    return res


if __name__ == '__main__':
    sys.exit(main())
