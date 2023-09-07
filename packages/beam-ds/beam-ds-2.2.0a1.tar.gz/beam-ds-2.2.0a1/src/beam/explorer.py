from pathlib import PurePath


class BeamPath(PurePath):

    def __init__(self, *pathsegments):
        super(BeamPath, self).__init__(*pathsegments)

    def samefile(self, other):
        raise NotImplementedError

    def is_file(self):
        raise NotImplementedError

    def is_dir(self):
        raise NotImplementedError

    def joinpath(self, *other):
        raise NotImplementedError

    def mkdir(self, *args, **kwargs):
        raise NotImplementedError

    def exists(self):
        raise NotImplementedError

    def glob(self, *args, **kwargs):
        raise NotImplementedError


class HDFSPath(BeamPath):

    def __init__(self, *pathsegments, client=None, skip_trash=False):
        super(HDFSPath, self).__init__(*pathsegments)
        self.client = client
        self.skip_trash = skip_trash

    def exists(self):
        return self.client.status(str(self), strict=False) is not None

    def rename(self, target):
        self.client.rename(str(self), str(target))

    def replace(self, target):

        self.client.rename(str(self), str(target))
        return HDFSPath(target, client=self.client)

    def unlink(self, missing_ok=False):
        if not missing_ok:
            self.client.delete(str(self), skip_trash=self.skip_trash)
        self.client.delete(str(self), skip_trash=self.skip_trash)

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        if not exist_ok:
            if self.exists():
                raise FileExistsError
            self.client.makedirs(str(self))
        self.client.makedirs(str(self), permission=mode)

    def rmdir(self):
        self.client.delete(str(self), skip_trash=self.skip_trash)

    def iterdir(self):
        files = self.client.list(str(self))
        for f in files:
            yield HDFSPath(self.joinpath(f), client=self.client)

    def samefile(self, other):
        raise NotImplementedError

    def is_file(self):
        raise NotImplementedError

    def is_dir(self):
        raise NotImplementedError

    def joinpath(self, *other):
        raise NotImplementedError

    def mkdir(self, *args, **kwargs):
        raise NotImplementedError

    def exists(self):
        raise NotImplementedError

    def glob(self, *args, **kwargs):
        raise NotImplementedError
