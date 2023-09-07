import random
import time
import os
import yaml

from datetime import timedelta

from .filesystem import iVFS, FileSystem
from .fixbounded import TimeBoundedBook


# ----------------------------------------------------------
# Library
# ----------------------------------------------------------
class Library:
    """Main Library class.

    - classify *books* based on tags.
    - user provide tags ordered by relevance (more relevant first).
    - tags order is used for creating the path of the *book*.
    - tags inventory are automatically maintained.
    - user can modify the preference of found tags and reorganize folders.
    - Library needs a *workspace* to store preferences and *books*.

    """

    VFS_FACTORY = FileSystem
    URL_PATTERN = 'file://{root}'
    BOOK_FACTORY = TimeBoundedBook

    def __init__(self, root: str):
        self.root = root

        # TODO: review VFS Factory but FS
        url = self.URL_PATTERN.format_map(self.__dict__)
        self.fs = self.VFS_FACTORY(url)

        self.config_file = os.path.join(root, 'config.yaml')
        self.config = {}
        try:
            self.config = yaml.load(open(self.config_file), Loader=yaml.Loader)
        except:
            pass

    def save(self):
        yaml.dump(self.config, open(self.config_file, 'w'), Dumper=yaml.Dumper)

    def create(self, *tags):
        """Create a *book* storage based on tags"""
        bind = timedelta(seconds=3600)
        book = TimeBoundedBook(bind, self.fs, tags, flush_rate=1)

        # update library tags
        libtags = self.config.setdefault('tags', {})
        for relevance, tag in enumerate(tags):
            info = libtags.setdefault(tag, {})
            info[relevance] = info.get(relevance, 0) + 1

        self.save()
        return book

    def list(self, *tags, **filters):
        """list a *books* that match all tags given patterns."""
        result = {}
        for ltags, path in self.fs.list(*tags, **filters):
            result[path] = ltags
        return result
