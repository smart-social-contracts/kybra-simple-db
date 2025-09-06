from kybra_simple_db import (
    Entity,
    ManyToMany,
    OneToMany,
    OneToOne,
    String,
    TimestampedMixin,
)


class User(Entity):
    __alias__ = "name"
    name = String()


class User2(Entity):
    __alias__ = "id"
    id = String()



user = User(name="anna")
print('*** (user.to_dict())', user.to_dict())
print('*** (User.count()', User.count())
print('*** (len(User.instances())', len(User.instances()))
print('*' * 20)

user2 = User2(id="bob")
print('*** (user2.to_dict())', user2.to_dict())
print('*** (User2.count()', User2.count())
print('*** (len(User2.instances())', len(User2.instances()))

