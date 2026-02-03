from __future__ import annotations
from dataclasses import dataclass, field
import itertools
from pathlib import Path
from typing import Mapping, Optional
import json
import re


@dataclass
class MPool():
    """
    Memory pool file object
    with the associated utilities to extract info from it
    NOTE: this can be replaced by data in the network.c BUT network.c does not allow to find the name of the memory dump files... :(
    """
    filename: str = None
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.data["mem_file_prefix"] = None
        self.data["mempools"] = {}
        if self.filename is not None:
            self.data = Path(self.filename).read_text()
            # Sanitize badly written json.
            self.data = re.sub("\},(\s+)\]", r"}\1]", self.data, flags = re.MULTILINE | re.DOTALL)
            self.data = re.sub("\],(\s+)\}", r"]\1}", self.data, flags = re.MULTILINE | re.DOTALL)
            self.data = json.loads(self.data)
            self.data["mempools"] = {k["fname"].upper():k for k in self.data["memory"]["mempools"]}
            self.data["mem_file_prefix"] = self.data["memory"]["mem_file_prefix"]
            del self.data["memory"]
    
    @classmethod
    def from_string(cls, data:str):
        obj = cls()
        mpools = obj.data["mempools"]
        rex = re.compile(r"""/\*\sglobal\spool\s(?P<NO>\d+)\sis\s(?P<SIZE>\?|\d+(?:\.\d+)?\s[KM]?B).*?
                        postfix=(?P<POSTFIX>.*?)
                        name=(?P<NAME>.*?)
                        \s
                        offset=(?P<OFFSET>0x[0-9A-Fa-f]+)
                        .*?
                        size=(?P<RAW_SIZE>\d+)\s+
                        (?P<TYPE>[A-Z_]+).*?
                        """, re.MULTILINE|re.VERBOSE|re.DOTALL)
        for m in rex.finditer(data):
            pool_pf = m.group("POSTFIX").strip().upper()
            mpools[pool_pf] = {
                                "fname" : pool_pf,
                                "name": m.group("NAME"),
                                "fformat": None,
                                "prop":{
                                        "rights": m.group("TYPE"),
                                        "throughput": None,     # to be added in the regexp if needed
                                        "latency": None,        # to be added in the regexp if needed
                                        "byteWidth": None,      # to be added in the regexp if needed
                                        "freqRatio": None,      # to be added in the regexp if needed
                                        "read_power": None,     # to be added in the regexp if needed
                                        "write_power": None,    # to be added in the regexp if needed
                                },
                                "offset":{
                                    "value": m.group("OFFSET"),
                                    "magnitude": "BYTES"
                                },
                                "size":{
                                    "value": m.group("RAW_SIZE"),
                                    "magnitude": "BYTES",
                                    "used_size": m.group("SIZE")
                                }
                                # "number": m.group("NO"), #Not used
                                }
        
        # filter out useless -in this context- pools
        # -> Remove pools without postfix (eg. cache in default config)
        if "" in mpools:
            del mpools[""]
        # -> Find virtual memory pools if applicable, and remove them.
        # Virtual mem pool name starts with a combination of the name of two other mempools
        li = list(mpools.keys())
        for v in li:
            ll = [k for k in li if k != v]
            c = ["_".join(c) for c in itertools.permutations(ll, 2)]
            if v.startswith(tuple(c)):
                del mpools[v]
        
        return obj

    def set_filename(self, fn: str):
        self.filename = fn
        
    def add_loaders(self, flashloader:str):
        """
        Add flashloader fields for each memory pool
        CAUTION: This is valid only for the current N6 embodiement (addresses are subject to future modifications)
        CAUTION: Flashloader is also valid only for the current N6 embodiement
        TODO: Ensure this data is ok
        """
        for k, mp in self.data["mempools"].items():
            # I don't know how to know if this is an external thing 
            # except using addresses but this is not generic at all...
            #if "External" in mp["name"] and "Flash" in mp["name"]:
            if (int(mp["offset"]["value"],16) > 0x60000000) and (int(mp["offset"]["value"],16) < 0x90000000):
                # ONLY FOR THE N6 WE HAVE HERE AND NOW
                mp["loader"] = str(flashloader)
            else:
                mp["loader"] = None
    
    def get_all_offsets(self) -> Mapping[str, str]:
        return {k.upper(): v["offset"]["value"] for k, v in self.data["mempools"].items()}
    
    def get_offset(self, offset_str:str) -> str:
        """ Returns offset of a bank (name is case-insensitive)"""
        for k, v in self.data["mempools"].items():
            if offset_str.upper() == k:
                return v["offset"]["value"]

    def get_prefix(self) -> str:
        """Retrieves the prefix of the memory-dump-files generated by this mempool"""
        return self.data["mem_file_prefix"]
    
    def get_loader(self, pool_name: str) -> Optional[str]:
        """Retrieves the flash loader string-path or None if no flashloader for this memory pool"""
        return self.data["mempools"][pool_name.upper()]["loader"]