from django.contrib.staticfiles.storage import CachedFilesMixin
from django.core.files.base import ContentFile

from storages.backends.s3boto import S3BotoStorage

from require.storage import OptimizedFilesMixin


class OptimizedCachedS3BotoStorage(OptimizedFilesMixin, CachedFilesMixin, S3BotoStorage):
    
    # HACK: The chunks implementation in S3 files appears broken when gzipped!
    def hashed_name(self, name, content=None):
        if content is None:
            content = ContentFile(self.open(name).read(), name=name)
        return super(OptimizedCachedS3BotoStorage, self).hashed_name(name, content)