#!/usr/bin/python3
# coding:utf-8

from errno import EAGAIN
from errno import EBUSY
from errno import ENOENT
import os
from queue import Empty
from queue import Queue
import shutil
from tempfile import TemporaryDirectory
from threading import Thread
from threading import current_thread
import time
from typing import List
from typing import Optional
import uuid

from xarg import commands

from .abstract import backup_description
from .checker import backup_check_item
from .checker import backup_check_pack
from .checker import calculate_md5
from .definer import COMPRESS_TYPE
from .definer import DEFAULT_COMPRESS_TYPE
from .definer import THDNUM_BAKPREP
from .package import backup_tarfile
from .scanner import backup_scanner

__version__ = "0.1.beta.1"
__prog__ = "xbackup"
__prog_check__ = f"{__prog__}-check"
__prog_desc__ = f"{__prog__}-desc"
__prog_list__ = f"{__prog__}-list"

URL_PROG = "https://github.com/bondbox/xbackup"


def backup_check(backup_path: str, fast: bool = False) -> bool:
    assert isinstance(backup_path, str)
    assert isinstance(fast, bool)
    cmds = commands()

    try:
        check_file = backup_tarfile(backup_path, True)
        assert check_file.readonly

        if not backup_check_pack(tarfile=check_file, fast=fast):
            cmds.logger.warn("Check backup failed.")
            check_file.close()
            return False
        check_file.close()
    except Exception as error:
        cmds.logger.error(f"Exception when check backup: {error}.")
        return False

    cmds.logger.info("Check backup ok.")
    return True


def backup_pack(scanner: backup_scanner,
                backup_path: str,
                comptype: Optional[str] = None,
                check: bool = True) -> int:
    cmds = commands()

    # create temp file
    with TemporaryDirectory(dir=None) as tempdir:
        cmds.logger.debug(f"Create the temp directory: {tempdir}.")
        backup_file = backup_tarfile(path=backup_path,
                                     readonly=False,
                                     comptype=comptype)
        assert not backup_file.readonly
        cmds.logger.info(f"Create a temp backup file: {backup_file.path}, "
                         f"compress type: {comptype}.")

        class task_stat:

            def __init__(self):
                self.exit = False
                self.q_bak = Queue()
                self.q_obj = Queue()

        backup_stat = task_stat()
        desc = backup_description(backup_file.path)

        def backup_object(desc: backup_description,
                          object: backup_scanner.object) -> bool:
            assert isinstance(desc, backup_description)
            assert isinstance(object, backup_scanner.object)
            assert not (object.isdir and not object.islink)

            def copy_file(source: str, item: backup_check_item) -> bool:
                assert isinstance(source, str)
                assert isinstance(item, backup_check_item)
                assert item.isfile and not item.islink
                assert isinstance(item.md5, str)

                # copy file and check md5
                tempname = uuid.uuid1().hex
                temppath = os.path.join(tempdir, tempname)
                shutil.copy(source, temppath)
                md5 = calculate_md5(temppath)
                if md5 != item.md5:
                    return False
                backup_stat.q_bak.put((temppath, item, True))
                return True

            item = backup_check_item(name=object.relpath,
                                     size=object.size,
                                     isdir=object.isdir,
                                     isfile=object.isfile,
                                     islink=object.islink,
                                     md5=object.md5 if object.isfile else None,
                                     linkname=os.readlink(object.abspath)
                                     if object.islink else None)

            if item.isfile and not item.islink:
                if copy_file(source=object.abspath, item=item) is not True:
                    return False
            else:
                backup_stat.q_bak.put((object.abspath, item, False))

            return True

        def task_archive():
            name = current_thread().name
            cmds.logger.debug(f"Task archive thread[{name}] start.")
            while not backup_stat.exit:
                try:
                    path, item, delete = backup_stat.q_bak.get(timeout=0.01)
                except Empty:
                    continue

                assert isinstance(path, str)
                assert isinstance(item, backup_check_item)
                assert isinstance(delete, bool)
                cmds.logger.debug(f"Archive {item.name}.")
                backup_file.wrap.add(name=path, arcname=item.name)
                desc.checklist.add(item)
                if delete:
                    os.remove(path=path)
                backup_stat.q_bak.task_done()
            cmds.logger.debug(f"Task archive thread[{name}] exit.")

        def task_prepare():
            name = current_thread().name
            cmds.logger.debug(f"Task prepare thread[{name}] start.")
            while not backup_stat.exit:
                try:
                    object = backup_stat.q_obj.get(timeout=0.01 *
                                                   THDNUM_BAKPREP)
                except Empty:
                    continue

                assert isinstance(object, backup_scanner.object)
                cmds.logger.debug(f"Prepare {object.relpath}.")
                while True:
                    try:
                        if backup_object(desc=desc, object=object) is True:
                            break
                        time.sleep(0.1)
                    except Exception as e:
                        cmds.logger.error(
                            f"Prepare {object.relpath} error: {e}.")
                backup_stat.q_obj.task_done()
            cmds.logger.debug(f"Task prepare thread[{name}] exit.")

        # archive backup object
        task_threads: List[Thread] = []
        task_threads.append(Thread(target=task_archive, name="xbak-arch"))
        task_threads.extend([
            Thread(target=task_prepare, name=f"xbak-prep{i}")
            for i in range(THDNUM_BAKPREP)
        ])

        for thread in task_threads:
            thread.start()

        for object in scanner:
            backup_stat.q_obj.put(object)

        backup_stat.q_obj.join()
        backup_stat.q_bak.join()

        backup_stat.exit = True
        for thread in task_threads:
            thread.join()

        # create backup checklist
        cmds.logger.debug("Dump checklist.")
        checklist_path = os.path.join(tempdir, "checklist")
        with open(checklist_path, "wb") as tempfd:
            # dump check item to temp
            desc.checklist.dump(tempfd)

        # create backup description
        cmds.logger.debug("Dump description.")
        description_path = os.path.join(tempdir, "description")
        with open(description_path, "w") as tempfd:
            tempfd.write(desc.dump())

        # archive temp files and close tarfile
        backup_file.description = description_path
        backup_file.checklist = checklist_path
        backup_file.close()

        # check after backup
        if check and not backup_check(backup_path=backup_file.path, fast=True):
            return EAGAIN

        cmds.logger.info("Backup is complete.")
        return 0

    return ENOENT
