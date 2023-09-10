from masoniteorm.models import Model
from masoniteorm.scopes import UUIDPrimaryKeyMixin

class Audio(Model, UUIDPrimaryKeyMixin):
    __fillable__ = ["id", "hash_id", "hash_count"]

    def get_by_hash(self, hash: str):
        return self.query().where("hash_id", hash).first()
    
    def get_by_id(self, id):
        return self.query().find(id)
    
    def update_hash_count(self, hash_count):
        self.hash_count = hash_count
        self.save()
        return self