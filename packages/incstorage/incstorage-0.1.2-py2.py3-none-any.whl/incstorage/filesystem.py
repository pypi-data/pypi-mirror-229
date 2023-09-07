"""
Virtual FileSystem support.
"""
import os
import re

from uswarm.tools import parse_uri


# ----------------------------------------------------------
# Virtual File System
# ----------------------------------------------------------
class iVFS:  # noqa: R0903
    """Virtual File System interface"""

    def __init__(self, url: str):
        self.url = url

    def list(self, *tags, **filters):
        """a simple demo function"""
        raise NotImplementedError()

    def open(self, tags, lbound, rbound, ext='db', mode='a'):
        """a simple demo function"""
        raise NotImplementedError()

    def rename(self):
        """a simple demo function"""
        raise NotImplementedError()

    def delete(self):
        """a simple demo function"""
        raise NotImplementedError()


class FileSystem(iVFS):
    """Implementation of iVFS based on File System."""

    def __init__(self, url: str):
        super().__init__(url)
        self._uri = parse_uri(url)
        self.path = self._uri['path']

    def list(self, *tags, **filters):
        def match(tags, local_tags):
            for tag in tags:
                for ltag in local_tags:
                    if re.match(tag, ltag):
                        break
                else:
                    return False
            return True

        lroot = len(self.path.split(os.path.sep))
        for top, folders, files in os.walk(self.path):
            for name in files:
                path = os.path.join(top, name)
                name, ext = os.path.splitext(path)
                assert name[0] == os.path.sep
                local_tags = name.split(os.path.sep)
                local_tags = local_tags[lroot:] + [ext]
                if match(tags, local_tags):
                    yield local_tags, path

    def open(self, tags, lbound, rbound, ext='db', mode='a'):
        """a simple demo function"""
        ptags = '/'.join(tags)
        path = f"{self.path}/{ptags}/{lbound}-{rbound}.{ext}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fp = open(path, mode)
        return fp
