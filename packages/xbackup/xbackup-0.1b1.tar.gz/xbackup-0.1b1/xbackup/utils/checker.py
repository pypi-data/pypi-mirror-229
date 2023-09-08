#!/usr/bin/python3
# coding:utf-8

import enum
import hashlib
import os
import pickle
from queue import Empty
from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from threading import current_thread
from typing import Dict
from typing import IO
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple

from xarg import commands

from .definer import THDNUM_BAKCHK
from .package import backup_tarfile


def calculate_md5(path: str) -> str:
    assert isinstance(path, str)
    with open(path, "rb") as file:
        md5_hash = hashlib.md5()
        while True:
            data = file.read(1024**2)
            if not data:
                break
            md5_hash.update(data)
    return md5_hash.hexdigest()


class backup_check_item:

    @enum.unique
    class item_flag(enum.IntFlag):
        none = 0
        isdir = 1 << 0
        isfile = 1 << 1
        islink = 1 << 2

    def __init__(self, name: str, size: int, isdir: bool, isfile: bool,
                 islink: bool, md5: Optional[str], linkname: Optional[str]):
        assert isinstance(name, str)
        assert isinstance(size, int) and size >= 0
        assert isinstance(isdir, bool)
        assert isinstance(isfile, bool)
        assert isinstance(islink, bool)

        flag = self.item_flag.none

        if isdir:
            assert not isfile
            flag |= self.item_flag.isdir

        if isfile:
            assert size >= 0 and not isdir
            assert md5 is None if islink else isinstance(md5, str)
            flag |= self.item_flag.isfile

        if islink:
            assert isinstance(linkname, str)
            flag |= self.item_flag.islink
        else:
            assert linkname is None

        self.__name = name
        self.__size = size
        self.__flag = flag
        self.__md5 = md5
        self.__linkname = linkname

    def __str__(self):
        return " ".join([str(i) for i in self.dump()])

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> int:
        return self.__size

    @property
    def flag(self) -> item_flag:
        return self.__flag

    @property
    def isdir(self) -> bool:
        return self.item_flag.isdir in self.__flag

    @property
    def isfile(self) -> bool:
        return self.item_flag.isfile in self.__flag

    @property
    def islink(self) -> bool:
        return self.item_flag.islink in self.__flag

    @property
    def md5(self) -> Optional[str]:
        return self.__md5

    @property
    def linkname(self) -> Optional[str]:
        return self.__linkname

    def dump(self) -> Tuple:
        data = [self.name, int(self.flag)]

        if self.islink:
            data.append(self.linkname)
        elif self.isfile:
            data.extend([self.size, self.md5])

        return tuple(data)

    @classmethod
    def load(cls, data: Sequence):
        data = list(data)
        name = data.pop(0)
        flag = data.pop(0)
        assert isinstance(flag, int)
        isdir = True if flag & backup_check_item.item_flag.isdir else False
        isfile = True if flag & backup_check_item.item_flag.isfile else False
        islink = True if flag & backup_check_item.item_flag.islink else False
        size = data.pop(0) if isfile and not islink else 0
        md5 = data.pop(0) if isfile and not islink else None
        linkname = data.pop(0) if islink else None

        return backup_check_item(name=name,
                                 size=size,
                                 isdir=isdir,
                                 isfile=isfile,
                                 islink=islink,
                                 md5=md5,
                                 linkname=linkname)


class backup_check_list:

    class item_counter:

        def __init__(self):
            self.__sizes = 0
            self.__items = 0
            self.__dirs = 0
            self.__files = 0
            self.__links = 0

        def __str__(self):
            return "\n\t".join([
                f"{self.items} backup items:", f"{self.dirs} dirs",
                f"{self.files} files", f"{self.links} symbolic links"
            ])

        @property
        def sizes(self) -> int:
            return self.__sizes

        @property
        def items(self) -> int:
            return self.__items

        @property
        def dirs(self) -> int:
            return self.__dirs

        @property
        def files(self) -> int:
            return self.__files

        @property
        def links(self) -> int:
            return self.__links

        ITEM = "items"
        SIZE = "sizes"
        DIR = "dirs"
        FILE = "files"
        LINK = "links"

        def dump_dict(self) -> Dict:
            return {
                self.ITEM: self.items,
                self.SIZE: self.sizes,
                self.DIR: self.dirs,
                self.FILE: self.files,
                self.LINK: self.links,
            }

        def inc(self, item):
            assert isinstance(item, backup_check_item)
            self.__sizes += item.size
            self.__items += 1

            if item.isdir:
                self.__dirs += 1

            if item.isfile:
                self.__files += 1

            if item.islink:
                self.__links += 1

    def __init__(self):
        self.__items: Set[backup_check_item] = set()
        self.__counter = self.item_counter()

    def __iter__(self):
        return iter(self.__items)

    @property
    def counter(self) -> item_counter:
        return self.__counter

    def add(self, item: backup_check_item):
        assert isinstance(item, backup_check_item)
        self.__items.add(item)
        self.counter.inc(item)

    def dump(self, file: IO[bytes]):
        pickle.dump(obj=[item.dump() for item in self.__items], file=file)

    @classmethod
    def load(cls, file: IO[bytes]):
        check_list = backup_check_list()
        for data in pickle.load(file=file):
            assert isinstance(data, tuple)
            check_list.add(backup_check_item.load(data))
        return check_list


def backup_check_pack(tarfile: backup_tarfile, fast: bool = False) -> bool:
    assert isinstance(tarfile, backup_tarfile)
    assert isinstance(fast, bool)
    assert tarfile.readonly
    checklist = tarfile.checklist
    assert checklist is not None

    chklist = backup_check_list.load(checklist)
    assert isinstance(chklist, backup_check_list)

    cmds = commands()

    if set([i.name for i in chklist]) - set([m.name for m in tarfile.members]):
        cmds.logger.error("Check members failed.")
        return False

    with TemporaryDirectory(dir=None) as tempdir:

        def check_file(item: backup_check_item,
                       tarfile: backup_tarfile,
                       fast: bool = False) -> bool:
            assert isinstance(item, backup_check_item)
            assert isinstance(tarfile, backup_tarfile)
            assert isinstance(fast, bool)

            def file_md5(name: str,
                         tarfile: backup_tarfile,
                         fast: bool = False) -> Optional[str]:

                if not fast:
                    tarf = tarfile.wrap.extractfile(name)
                    if not tarf:
                        return None

                    try:
                        hash_md5 = hashlib.md5()
                        while True:
                            data = tarf.read(1024**2)
                            if not data:
                                break
                            hash_md5.update(data)
                        return hash_md5.hexdigest()
                    except Exception:
                        return None
                    finally:
                        tarf.close()

                else:
                    path = os.path.join(tempdir, name)
                    md5 = calculate_md5(path=path)
                    return md5

            md5 = file_md5(name=item.name, tarfile=tarfile, fast=fast)
            if md5 == item.md5:
                return True

            cmds.logger.debug(f"Check {item.name} md5 is {md5}, "
                              f"expected {item.md5}.")
            return False

        def check_item(item: backup_check_item,
                       tarfile: backup_tarfile,
                       fast: bool = False) -> bool:
            assert isinstance(item, backup_check_item)
            assert isinstance(tarfile, backup_tarfile)
            member = tarfile.wrap.getmember(item.name)
            assert isinstance(fast, bool)

            if member.isdir() and item.isdir != member.isdir():
                cmds.logger.error(f"Check {item.name} isdir failed.")
                return False

            if member.isfile():
                if item.isfile != member.isfile():
                    cmds.logger.error(f"Check {item.name} isfile failed.")
                    return False

                if not member.issym() and check_file(
                        item=item, tarfile=tarfile, fast=fast) is not True:
                    cmds.logger.error(f"Check {item.name} file md5 failed.")
                    return False

            if member.issym():
                if item.islink != member.issym():
                    cmds.logger.error(f"Check {item.name} islink failed.")
                    return False

                # check symbolic link
                if item.linkname != member.linkname:
                    cmds.logger.debug(
                        f"Check {item.name} linkname is {member.linkname}, "
                        f"expected {item.linkname}.")
                    cmds.logger.error(f"Check {item.name} linkname failed.")
                    return False

            # if member.islnk():
            #     cmds.logger.error(f"Check {item.name} hard link failed.")
            #     return False

            # if member.isdev():
            #     cmds.logger.error(f"Check {item.name} device failed.")
            #     return False

            # if member.isreg():
            #     cmds.logger.error(f"Check {item.name} regular file failed.")
            #     return False

            # if member.chksum:
            #     cmds.logger.error(f"Check {item.name} regular file failed.")
            #     return False

            cmds.logger.debug(f"Check {item.name} ok.")
            return True

        def check_main() -> bool:
            for item in chklist:
                if check_item(item=item, tarfile=tarfile) is not True:
                    return False
            return True

        def check_fast() -> bool:

            class task_stat:

                def __init__(self):
                    self.fail = False
                    self.exit = False
                    self.q_item = Queue()

            check_stat = task_stat()

            def check_error():
                cmds.logger.debug("Check waiting error exit.")
                check_stat.fail = True
                while not check_stat.q_item.empty():
                    try:
                        check_stat.q_item.get(timeout=0.1)
                        check_stat.q_item.task_done()
                    except Empty:
                        cmds.logger.debug("Check queue empty.")
                        pass
                assert check_stat.fail is True
                cmds.logger.debug("Check error exit.")

            def task_check_item():
                name = current_thread().name
                cmds.logger.debug(f"Task check thread[{name}] start.")
                while not check_stat.exit and not check_stat.fail:
                    try:
                        item = check_stat.q_item.get(timeout=0.01 *
                                                     THDNUM_BAKCHK)
                    except Empty:
                        continue

                    assert isinstance(item, backup_check_item)
                    if check_item(item=item, tarfile=tarfile,
                                  fast=True) is not True:
                        check_error()
                    check_stat.q_item.task_done()
                cmds.logger.debug(f"Task check thread[{name}] exit.")

            def task_check():
                name = current_thread().name
                cmds.logger.debug(f"Task check thread[{name}] start.")

                members = [
                    m for m in tarfile.members
                    if m.isreg() and not m.issym() and m.name[:2] != ".."
                ]
                tarfile.wrap.extractall(path=tempdir, members=members)

                for item in chklist:
                    if check_stat.fail:
                        break

                    if item.isfile and item.name[:2] == "..":
                        if check_item(item=item, tarfile=tarfile) is not True:
                            check_error()

                    check_stat.q_item.put(item)

                if not check_stat.fail:
                    check_stat.q_item.join()
                check_stat.exit = True
                assert check_stat.exit is True
                cmds.logger.debug(f"Task check thread[{name}] exit.")

            task_threads: List[Thread] = []
            task_threads.append(Thread(target=task_check, name="xbak-check"))
            task_threads.extend([
                Thread(target=task_check_item, name=f"xbak-chk{i}")
                for i in range(THDNUM_BAKCHK)
            ])

            for thread in task_threads:
                thread.start()

            for thread in task_threads:
                thread.join()

            return not check_stat.fail

        return check_main() if not fast else check_fast()
