#!/usr/bin/python3
# coding:utf-8

from errno import EAGAIN
from errno import EBUSY
from errno import ENOENT
import os
import shutil
from tempfile import TemporaryDirectory
from typing import Optional

from xarg import commands

from .abstract import backup_description
from .checker import backup_check_file
from .package import COMPRESS_TYPE
from .package import DEFAULT_COMPRESS_TYPE
from .package import backup_tarfile
from .scanner import backup_scanner

__version__ = "0.1.alpha.2"
__prog__ = "xbackup"
__prog_check__ = f"{__prog__}-check"
__prog_desc__ = f"{__prog__}-desc"
__prog_list__ = f"{__prog__}-list"

URL_PROG = "https://github.com/bondbox/xbackup"


def backup_check(backup_path: str) -> bool:
    cmds = commands()

    try:
        check_file = backup_tarfile(backup_path, True)
        assert check_file.readonly

        if not backup_check_file(check_file):
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
    with TemporaryDirectory(dir=os.path.dirname(backup_path)) as tempdir:
        cmds.logger.debug(f"Create the temp directory: {tempdir}.")
        backup_temp = backup_tarfile(os.path.join(tempdir, "xbackup-temp"),
                                     False, comptype)
        assert not backup_temp.readonly
        cmds.logger.info(f"Create a temp backup file: {backup_temp.path}, "
                         f"compress type: {comptype}.")

        desc = backup_description()

        # save backup object to tarfile
        for object in scanner:
            cmds.logger.debug(f"{object.relpath}: {object.abspath}")
            backup_temp.add(object.abspath, object.relpath)
            desc.checklist.add_object(object)

        # save backup checklist
        checklist_path = os.path.join(tempdir, "checklist")
        with open(checklist_path, "wb") as tempfd:
            # dump check item to temp
            desc.checklist.dump(tempfd)

        # save backup description
        description_path = os.path.join(tempdir, "description")
        with open(description_path, "w") as tempfd:
            tempfd.write(desc.dump())

        # archive temp files and close tarfile
        backup_temp.description = description_path
        backup_temp.checklist = checklist_path
        backup_temp.close()

        # check after backup
        if check and backup_check(backup_temp.path) is not True:
            return EAGAIN

        # move temp file to backup file
        try:
            cmds.logger.info(f"Move temp {backup_temp.path} to {backup_path}.")
            shutil.move(backup_temp.path, backup_path)
        except Exception as error:
            cmds.logger.error(f"Exception: {error}.")
            return EBUSY

        cmds.logger.info("Backup is complete.")
        return 0

    return ENOENT
