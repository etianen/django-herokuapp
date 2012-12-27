from cStringIO import StringIO
from gzip import GzipFile

from django.core.files.base import File
from django.contrib.staticfiles.storage import CachedFilesMixin

from storages.backends.s3boto import S3BotoStorage

from require.storage import OptimizedFilesMixin


class GzipFixS3BotoStorageMixin(object):
    
    # Decompresses previously compressed content, essential for correct hash calculation.
    def _open(self, name, mode="rb"):
        """Opens the given file."""
        file = super(GzipFixS3BotoStorageMixin, self)._open(name, mode)
        if file.key.content_encoding == "gzip":
            file = GzipFile(mode=mode, compresslevel=9, fileobj=file)
            file_size = len(file.read())
            file.seek(0)
            file = File(file, name=name)
            file.size = file_size
        return file
    
    # Patch for bug in django-storages with compressed content.
    def _compress_content(self, content):
        """Gzip a given string."""
        zbuf = StringIO()
        zfile = GzipFile(mode='wb', compresslevel=9, fileobj=zbuf)
        zfile.write(content.read())
        zfile.close()
        zbuf.seek(0) # i was missing!
        content.file = zbuf
        return content


class OptimizedCachedS3BotoStorage(OptimizedFilesMixin, GzipFixS3BotoStorageMixin, CachedFilesMixin, S3BotoStorage):
    
    pass