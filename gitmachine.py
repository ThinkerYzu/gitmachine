import zlib

class git(object):
    def __init__(self, dirname):
        super(git, self).__init__()
        self.rootpath = self.__find_gitrootpath(dirname)
        pass

    def __find_gitrootpath(self, dirname):
        import os.path
        path = os.path.abspath(dirname)
        gitdir = os.path.join(path, '.git')
        while not os.path.lexists(gitdir):
            newpath = os.path.abspath(os.path.join(path, os.path.pardir))
            if newpath == path:
                return
            path = newpath
            gitdir = os.path.join(path, '.git')
            pass
        return path

    def get_objectpath(self, hashcode):
        import os.path
        p1 = hashcode[:2]
        p2 = hashcode[2:]
        return os.path.join(self.rootpath, '.git', 'objects', p1, p2)

    def get_objectfd(self, hashcode, mode):
        path = self.get_objectpath(hashcode)
        fd = file(path, mode)
        return fd

    def make_objectrw(self, hashcode):
        import os, os.path
        path = self.get_objectpath(hashcode)
        st = os.stat(path)
        mode = st.st_mode | os.path.stat.S_IWUSR
        os.chmod(path, mode)
        pass

    def make_objectro(self, hashcode):
        import os, os.path
        path = self.get_objectpath(hashcode)
        st = os.stat(path)
        mode = st.st_mode & ~os.path.stat.S_IWUSR
        os.chmod(path, mode)
        pass

    def rm_object(self, hashcode):
        import os
        path = self.get_objectpath(hashcode)
        os.remove(path)
        pass

    def get_commit(self, hashcode):
        fd = self.get_objectfd(hashcode, 'rb')
        raw = fd.read()
        plain = zlib.decompress(raw)
        head_stop = plain.index('\x00')
        content = plain[head_stop + 1:]
        return content

    def write_commit(self, hashcode, content):
        self.rm_object(hashcode)
        fd = self.get_objectfd(hashcode, 'wb')
        data = 'commit %d\x00%s' % (len(content), content)
        compressed = zlib.compress(data)
        fd.write(compressed)
        fd.close()
        self.make_objectro(hashcode)
        pass

    def rm_logs(self):
        import os.path, shutil, sys
        path = os.path.join(self.rootpath, '.git', 'logs')
        if os.path.lexists(path):
            shutil.rmtree(path)
            pass
        pass

    def discard_before(self, hashcode):
        import time
        try:
            commit = self.get_commit(hashcode)
        except:
            print >>sys.stderr, 'invalid commit!'
            return
        lines = commit.split('\n')
        lines = lines[:lines.index('')]
        parents = [line[len('parent '):].strip()
                   for line in lines
                   if line.startswith('parent ')]
        tree = [line.split()[1]
                for line in lines
                if line.startswith('tree ')][0]
        for parent in parents:
            content = 'tree %s\nauthor gitmachine <gitmachine@invalid.org> %d +0800\ncommiter gitmachine <gitmachine@invalid.org> 1411795367 %+03d00\n\nCommits earlier than %s were removed.\n' % (tree, int(time.time()), time.timezone / -3600, hashcode)
            self.write_commit(parent, content)
            pass
        self.rm_logs()
        pass
    pass

if __name__ == '__main__':
    import sys
    hashcode = sys.argv[1]
    gitobj = git('.')
    gitobj.discard_before(hashcode)
    pass
