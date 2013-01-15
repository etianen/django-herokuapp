from django.contrib.staticfiles.storage import CachedFilesMixin

from storages.backends.s3boto import S3BotoStorage

from require.storage import OptimizedFilesMixin


class OptimizedCachedS3BotoStorage(OptimizedFilesMixin, CachedFilesMixin, S3BotoStorage):
    
    # HACK: Don't use the local file for content hashing, ever!
    def hashed_name(self, name, content=None):
        return super(OptimizedCachedS3BotoStorage, self).hashed_name(name)