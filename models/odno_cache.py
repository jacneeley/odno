'''Application Cache'''

from core.load_pref import get_prefs, update_prefs

class OdnoCache:
    '''OdnoCache'''
    def __init__(self, **kwargs):
        self.odno_cache = kwargs.get("odno_cache", {})

    def get_cache(self) -> dict:
        return self.odno_cache
    
    def init_cache(self) -> None:
        '''init the cache'''
        if not self.odno_cache:
            self.odno_cache = get_prefs()

    def update_cache(self, odno_cache:str) -> dict:
        '''update the cache'''
        self.odno_cache = odno_cache
        update_prefs(odno_cache)
        return self.odno_cache

    def __str__(self):
        cache_str = ""
        if self.odno_cache:
            for k,v in self.odno_cache.items():
                cache_str += f"{k} : {v}"

        return cache_str

    def __repr__(self):
        return self.__str__()


odno_cache = OdnoCache()
