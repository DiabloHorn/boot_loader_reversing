#!/usr/bin/env python
# Original code from: https://github.com/skorokithakis/python-fuse-sample
# Used to debug disk encryption and other file system reading applications 
# added some print statements - https://diablohorn.com

from __future__ import with_statement

import os
import sys
import errno
import argparse

from fuse import FUSE, FuseOSError, Operations

G_DATADIR = "/tmp/datadir_storage"

class Passthrough(Operations):
    def __init__(self, root, datadir, emulate):
        self.root = root
        self.datadir = datadir
        self.emulate = emulate

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path
        
    def _savesector(self, data, offset, length):
        """Save sector data to file
        file will be overwritten if written to
        use cases not supported:
            - same sector being written in between reads
        """
        sectorname = "{}.{}.r".format(offset,length)
        sectorpath = os.path.join(self.datadir,sectorname)
        handle_sector = open(sectorpath,"wb")
        handle_sector.write(data)
        handle_sector.close()

    def _readsector(self, offset, length):
        """return sector data from files
        """
        sectorname = "{}.{}.r".format(offset,length)
        sectorpath = os.path.join(self.datadir,sectorname)
        with open(sectorpath, 'rb') as sectordata_file:
            sectordata = sectordata_file.read()
        return sectordata
        

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        """read sectors from disk or from saved files
        following use cases not implemented:
            - when emulating read sector from disk if not previously saved
            - emulate sectors that are also written and read
        """
        sectordata = ''
        if self.emulate:
            print "r {} {} {} emulated".format(path,offset,length)
            sectordata = self._readsector(offset,length)
        else:
            print "r {} {} {}".format(path,offset,length)
            os.lseek(fh, offset, os.SEEK_SET)
            sectordata = os.read(fh, length)
            self._savesector(sectordata, offset, length)
        return sectordata

    def write(self, path, buf, offset, fh):
        print "w {} {} {}".format(path,offset,len(buf))
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)
    

def main(mountpoint, root, datadir,emulate):
    FUSE(Passthrough(root, datadir, emulate), mountpoint, nothreads=True, foreground=True, **{'allow_other': True})

def createdatadir(name):
    if not name:
        name = G_DATADIR

    try:
        os.mkdir(name)
    except:
        print "{} already exists".format(name)
    
    return name

if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="target directory to be mounted")
    parser.add_argument("mountpoint",help="directory on which the target is mounted")
    parser.add_argument("--datadir",help="directory where the data will be saved, default /tmp/datadir_storage")
    parser.add_argument("--emulate",help="enable playback of previously stored data", action="store_true")
    args = parser.parse_args()
    
    args.datadir = createdatadir(args.datadir)

    if args.target and args.mountpoint:
        main(args.mountpoint, args.target, args.datadir, args.emulate)
