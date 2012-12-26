from cStringIO import StringIO
from gzip import GzipFile

from django.core.files.base import File
from django.contrib.staticfiles.storage import CachedFilesMixin

from storages.backends.s3boto import S3BotoStorage

from require.storage import OptimizedFilesMixin


class GzipFixS3BotoStorageMixin(object):
    
    def _open(self, name, mode="rb"):
        file = super(GzipFixS3BotoStorageMixin, self)._open(name, mode)
        if self.gzip:
            file = GzipFile(mode=mode, compresslevel=6, fileobj=file)
            file.size = len(file.read())
            file.seek(0)
            file = File(file, name=name)
        return file
    
    # Patch for bug in django-storages with compressed content.
    def _compress_content(self, content):
        """Gzip a given string."""
        zbuf = StringIO()
        zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        zfile.write(content.read())
        zfile.close()
        zbuf.seek(0) # i was missing!
        content.file = zbuf
        return content


class OptimizedCachedS3BotoStorage(OptimizedFilesMixin, GzipFixS3BotoStorageMixin, CachedFilesMixin, S3BotoStorage):
    
    pass