from __future__ import annotations
import logging
import argparse
from pathlib import Path
from typing import List
import subprocess
import shutil
import sys
from n6_utils_pkg.config_reader import ConfigReader, N6LoaderConfig
from n6_utils_pkg.compilers import CompilerType, IARCompiler, GCCCompiler
from n6_utils_pkg.intel_hex import IHex
from n6_utils_pkg.c_file import CFile

## Current script variable 
TEMPLATE_PATH = "./cspy_n6_template.mac"

#default logger
logger = logging.getLogger(__name__)
log_filename = "n6_loader.log"

def set_logger():
    global logger
    global log_indent
    if "run_validate_on_target" in {name for name in logging.root.manager.loggerDict}:
        logger = logging.getLogger("run_validate_on_target").getChild(__name__)
        log_indent = " "*5 + "- "
    else:
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter
        formatter = logging.Formatter('%(asctime)s  %(name)s -- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)
        log_indent = ""
                # create file handler and set level to debug
        fh = logging.FileHandler(log_filename, mode='w')
        fh.setLevel(logging.DEBUG)
        # add formatter to fh
        fh.setFormatter(formatter)
        # add fh to logger
        logger.addHandler(fh)

def log(level, msg):
    logger.log(level, f"{log_indent}{msg}")

def find_while_line(main_c: Path) -> int:
    i = 1
    f = main_c.read_text(encoding=None, errors=None)
    for curline in f.splitlines():
        #print(curline)aiValidationInit();
        #if "USER CODE BEGIN WHILE" in curline:
        if "aiValidationInit();" in curline: #  TODO: Adapt for the current main.c structure !
            return i
        else:
            i = i + 1
    return 

def convert_mem_files(memdir:Path, c_file:CFile, objcopy_path:Path=None) -> List[Path]:
    """Converts memory files to hex using the offsets defined in the C-file"""
    rv = []
    memprefix = "*"
    mempool_offsets = c_file.get_all_offsets()
    mempool_suffixes = list(mempool_offsets.keys())
    file_pfx = c_file.get_cname()
    
    for mf in memdir.glob(f"**/{file_pfx}_{memprefix}"):
        # 폴더거나 확장자 없으면 건너뛰기
        if not mf.is_file() or not mf.suffixes:
            continue

        mem_file_type = mf.suffixes[0][1:].upper()  # get memory pool from file extension
        
        if mem_file_type not in mempool_suffixes:
            continue

        offset = mempool_offsets[mem_file_type]

        if mf.suffix == '.raw':
            obj = objcopy_path.resolve()
            output_name = mf.with_suffix('.hex')
            # --start-address  doesnt work
            cmd = [obj, "--change-addresses", offset, "-Ibinary", "-Oihex", mf, output_name]
            cmd_str = " ".join([str(k) for k in cmd]).replace(str(mf.parent / mf.stem), mf.stem).replace(str(obj), obj.name)
            log(logging.INFO, cmd_str)
            #print(f"+ {mf} found -> converting to hex : {cmd}")
            v = subprocess.run(cmd, capture_output=True, shell=False)
            if (IHex(output_name).get_data_size() != 0):
                rv.append(output_name)
            #print(v.returncode)
        # elif mf.suffix == '.hex':
        #     if (IHex(mf).get_data_size() != 0):
        #         rv.append(mf)
            #print(f"+ {mf} found")
        else:
            pass
            #print(f"- {mf} ignored")
    return rv

def set_project_path(s:str, projdir: Path) -> str:
    exe_path = (projdir / "EWARM").resolve().as_posix()
    exe_path = exe_path.replace("/", "\\\\")
    return s.replace("$PROJ_DIR$", exe_path)


def show_returncode(desc:str, rv:int):
    """Logs return code value and logs it"""
    if rv == 0:
        # log(logging.INFO, f"{desc} successful")
        pass
    else:
        log(logging.ERROR, f"{desc} failed")


def safe_copy(src: Path, dst: Path):
    """Copy file only if the source exists, raise a FileNotFoundError otherwise"""
    if Path(src).exists():
        shutil.copy2(src, str(dst))
    else:
        log(logging.ERROR, f"Copying {str(src)} failed (file does not exist)")
        raise FileNotFoundError(f"{str(src)} does not exists")


def main_n6_loader(path_to_network_c:List[Path] = None,
                   path_to_memorydumps:Path = None,
                   clean_before_build:bool = False,
                   stlink_sn:str = None,
                   port:str = 'SWD',
                   args:Mapping[str,Any]=None):
    """
    Main n6 loader entry point:
    :param path_to_network_c: List of Path objects [0] is the network.c file, other indices (optional) are extra files to be copied into the project
    :param path_to_memorydumps: Path to the memory dumps directory
    :param clean_before_build: If True, clean the project before building it
    :param stlink_sn: ST-Link serial number
    :param port: Port to use when calling CubeProgrammer
    :param args: Arguments from the command line if any
    """
    set_logger()
    # Get info from config file
    o = Path(__file__).with_name("config.json").resolve()
    c = ConfigReader(o)
    c.add_n6_loader_config(args)
    path_to_c_project = c.get_project_path()
    
    path_to_main = path_to_c_project / "Core" / "Src" / "main.c"
    path_to_network_in_project = path_to_c_project / "X-CUBE-AI" / "App"
    path_to_compiler = c.get_compiler_binary_path()
    path_to_cube = c.get_cubeprogrammer_path()
    path_to_objcopy = c.get_objcopy_path()
    build_conf = c.get_project_build_conf()
    if "nucleo" in build_conf.lower():
        path_to_stldr = c.get_stldr_path(board_type="NUCLEO")
    else:
        path_to_stldr = c.get_stldr_path(board_type="DK")
    skip_extflash_prog = c.get_skip_prog_flash()
    skip_ramdata_prog = c.get_skip_prog_ramdata()
    compiler_type = c.get_compiler_type()
    if compiler_type == CompilerType.IAR:
        log(logging.INFO, f"Preparing compiler IAR")
        compiler = IARCompiler(path_to_compiler_binary=path_to_compiler/"iarbuild", 
                               path_to_debugger_binary=path_to_compiler/"CSpyBat",
                               path_to_project=path_to_c_project,
                               path_to_debugger_template=Path(__file__).with_name("cspy_n6_template.mac"),
                               project_config_name=build_conf, 
                               st_link_sn=stlink_sn, 
                               logger=log)
    elif compiler_type == CompilerType.GCC:
        log(logging.INFO, f"Preparing compiler GCC")
        compiler = GCCCompiler(path_to_compiler_binary=path_to_compiler/"arm-none-eabi-gcc", 
                        path_to_debugger_binary=path_to_compiler/"arm-none-eabi-gdb",
                        path_to_project=path_to_c_project,
                        path_to_debugger_template=Path(__file__).with_name("gdb_n6_template.gdb"),
                        project_config_name=build_conf,
                        st_link_sn=stlink_sn,
                        logger=log,
                        path_to_gdb_server=c.get_gdb_path(), 
                        path_to_cube_programmer=c.get_cubeprogrammer_path(),
                        path_to_make=c.get_make_path())

    skip_build=c.get_skip_build()

    # If no arguments, read contents from the config file
    if not path_to_network_c:
        path_to_network_c = [c.get_n6ldr_network()]
    
    if path_to_memorydumps is None:
        path_to_memorydumps = c.get_n6ldr_memdump_path()

    # Add breakpoint
    lineno = find_while_line(path_to_main)
    log(logging.INFO, f"Setting a breakpoint in main.c at line {lineno} (before the infinite loop)")
    compiler.add_breakpoint_to_main_macro(lineno)
    
    # Copy network .c to & extra files to project
    net_c = path_to_network_c.pop(0)  
    pout = path_to_network_in_project / net_c.name
    try:
        log(logging.INFO, f"Copying {net_c.name} to project: -> {pout}")
        safe_copy(net_c, pout)
        if net_c.with_suffix(".h").exists():
            safe_copy(net_c.with_suffix(".h"), pout.with_suffix(".h"))
        # Copy blobs if any (and more recent than the .c file)
        blob_expected_file = net_c.with_name(net_c.stem + "_ecblobs.h")
        if blob_expected_file.exists() and (blob_expected_file.stat().st_mtime >= net_c.stat().st_mtime):
            log(logging.INFO, f"Copying {blob_expected_file.name} to project: {blob_expected_file} -> {pout.parent}")
            safe_copy(blob_expected_file, pout.parent)
        
        # Copy extra files if any
        if path_to_network_c is not None:
            for k in path_to_network_c:
                # 1. C 파일 복사
                log(logging.INFO, f"Copying {k.name} to project")
                safe_copy(k, path_to_network_in_project / k.name)
                
                # 2. 헤더 파일(.h) 복사
                k_header = k.with_suffix(".h")
                if k_header.exists():
                    safe_copy(k_header, path_to_network_in_project / k_header.name)

                # 3. Blob 헤더(_ecblobs.h) 복사
                k_blob = k.with_name(k.stem + "_ecblobs.h")
                if k_blob.exists():
                    safe_copy(k_blob, path_to_network_in_project / k_blob.name)
    except FileNotFoundError:
        return 1
    
    # Extract memory pool info from ALL c-files
    log(logging.INFO, f"Extracting information from c-files")

    # 1. 처리할 모든 C 파일 리스트 구성
    target_c_files = [pout] # 첫 번째 파일
    
    if path_to_network_c:
        for k in path_to_network_c:
            target_c_files.append(path_to_network_in_project / k.name)

    all_mem_hex_dumps = []
    mp = None

    # 2. 루프를 돌며 모든 모델의 가중치 파일 변환
    for c_file_path in target_c_files:
        log(logging.INFO, f"Processing metadata from: {c_file_path.name}")
        cf = CFile(str(c_file_path))

        # Loader 정보는 한 번만 로드
        if mp is None:
            mp = cf.get_mpools()
            mp.add_loaders(path_to_stldr)

        log(logging.INFO, f"Converting memory files for prefix: {c_file_path.stem}")
        
        dumps = convert_mem_files(path_to_memorydumps, cf, path_to_objcopy)
        all_mem_hex_dumps.extend(dumps)
        
    mem_hex_dumps = all_mem_hex_dumps
    
    if not mem_hex_dumps: 
        log(logging.ERROR, f"No memory file converted")
    
    # Reset the complete board
    log(logging.INFO, f"""Resetting the board...""")
    cmd = [str(path_to_cube), '-q', '-c', 'port='+port, 'mode=powerdown', 'freq=2000', 'ap=1']
    if stlink_sn:
        cmd.insert(cmd.index("port=SWD")+1, f"sn={stlink_sn}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log(logging.DEBUG, f"Launching command: {' '.join(cmd)}")
    log(logging.DEBUG, result.stdout.decode('utf-8').replace("\r\n","\n"))
    
    # Add memories
    for mf in mem_hex_dumps:
        mem_file_type = mf.suffixes[0][1:]
        flshl = mp.get_loader(mem_file_type)
        hx = IHex(mf)
        size_kb = hx.get_data_size() / 1000
        if flshl:
            cmd = [str(path_to_cube), '-q', '-c', 'port='+port, 'mode=hotplug', 'ap=1', '--extload', flshl, '--download', str(mf), "--verify"]
            if stlink_sn:
                cmd.insert(cmd.index("port=SWD")+1, f"sn={stlink_sn}")
            
            if skip_extflash_prog:
                log(logging.INFO, f"Skipping flashing memory {mem_file_type} -- {size_kb:,.3f} kB")
            else:
                log(logging.INFO, f"Flashing memory {mem_file_type} -- {size_kb:,.3f}".replace(',', ' ') + " kB")
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                log(logging.DEBUG, f"Flashing memory command: {' '.join(cmd)}")
                log(logging.DEBUG, result.stdout.decode('utf-8').replace("\r\n","\n"))

                if result.returncode:
                    log(logging.INFO, f"Flashing memory {mem_file_type} -- return code ERROR")
                    return result.returncode
        else:
            if skip_ramdata_prog:
                log(logging.INFO, f"""Not planning to load ram data {mem_file_type} -- {size_kb:,.3f}kB""")
            else:
                log(logging.INFO, f"""Loading {mem_file_type} after program start -- {size_kb:,.3f}kB""")
                compiler.add_memory_file_to_load(mem_file_type, Path(mf).resolve())

    compiler.dump_macro_file()
    
    if not skip_build:
        step_s = f"Building project (conf= {build_conf})"
        if clean_before_build is True:
            step_s = f"Cleaning and {step_s}"
        log(logging.INFO, step_s)
        rv = compiler.compile_project(clean=clean_before_build)
        show_returncode("Compilation", rv)
        if rv:
            return rv

    log(logging.INFO, f"Loading internal memories & Running the program")
    rv = compiler.load_and_run()
    show_returncode("Loading memories", rv)
    return rv


class PathConverter(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
            if values:
                values = Path(values)
            setattr(args, self.dest, values)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Program to load data to the N6",
                                     epilog="Only temporary, for internal use...")
    parser.add_argument("-sn", "--serial-number", dest="st_link_serialnr",
                    default=None, help="Force the ST-Link serial number to use for communication with the N6"
                    )
    parser.add_argument("--port", dest="st_link_port", default='SWD', help="Force the use of CubeProgrammer port (default: SWD)")
    parser.add_argument("--clean", action="store_true", dest="project_clean",
                    default=False, help="Clean the project before building it (default: False)")
    N6LoaderConfig.add_args(parser=parser)
    args = parser.parse_args()

    # [수정] 로드할 네트워크 C 파일들의 경로
    my_network_files = [
        Path("C:/Users/user/.stm32cubemx/kws_output/kws.c"),    # 1번 모델 (Prefix: kws)
        Path("C:/Users/user/.stm32cubemx/img_output/img.c")  # 2번 모델 (Prefix: img)
    ]

    # [수정] 덤프 파일들이 있는 폴더들의 "공통 상위 경로"
    common_dump_path = Path("C:/Users/user/.stm32cubemx/")

    rv = main_n6_loader(path_to_network_c=my_network_files, 
                    path_to_memorydumps=common_dump_path, 
                    clean_before_build=True, 
                    stlink_sn=args.st_link_serialnr,
                    port=args.st_link_port,
                    args=args)
    if rv == 0:
        log(logging.INFO, "Start operation achieved successfully")
    else:
        log(logging.ERROR, "Start operation did not achieve successfully")
    sys.exit(rv)