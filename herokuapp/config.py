"""Access to the heroku config."""

from collections import Mapping

from django.utils.functional import cached_property

from herokuapp import commands
from herokuapp.settings import HEROKU_CONFIG_BLACKLIST


class HerokuConfig(Mapping):
    
    """A lazy lookup of heroku config parameters."""
    
    @cached_property
    def _unsafe(self):
        """All Heroku config params, included blacklisted ones."""
        config_str = commands.call("config", "--shell").decode("utf-8")
        return dict(line.split("=", 1) for line in config_str.splitlines())
        
    @cached_property
    def _safe(self):
        """All safe Heroku config params."""
        return {
            key: value
            for key, value
            in self._unsafe.items()
            if not key in HEROKU_CONFIG_BLACKLIST
        }
        
    def __getitem__(self, *args, **kwargs):
        return self._safe.__getitem__(*args, **kwargs)
    
    def __len__(self, *args, **kwargs):
        return self._safe.__len__(*args, **kwargs)
    
    def __iter__(self, *args, **kwargs):
        return self._safe.__iter__(*args, **kwargs)
    
    def __contains__(self, *args, **kwargs):
        return self._safe.__contains__(*args, **kwargs)
    
    
config = HerokuConfig()