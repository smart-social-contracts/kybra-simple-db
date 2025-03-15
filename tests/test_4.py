from pprint import pprint
from kybra_simple_db import *

class MyEntity(Entity, TimestampedMixin):
    pass

class Organization(MyEntity):
    name = String(min_length=2, max_length=50) 
    users = OneToMany(["User", "Robot"], "organization")

class User(MyEntity):
    name = String(min_length=2, max_length=50)
    age = Integer(min_value=0, max_value=150)
    organization = ManyToOne("Organization", "users")

    @classmethod
    def new(cls, name, age, **kwargs):
        new_user = cls(name=name, age=age)
        # new_user.name = name
        # new_user.age = age
        return new_user
        
class SuperUser(User):
    address = String(min_length=2, max_length=50)
    gender = String(min_length=1, max_length=1)

    @classmethod
    def new(cls, name, age, address, **kwargs):
        new_superuser = User.new(name, age, **kwargs)
        new_superuser.address = address
        return new_superuser


class Robot(MyEntity):
    name = String(min_length=2, max_length=50)
    organization = ManyToOne("Organization", "users")

    @classmethod
    def new(cls, name):
        new_user = cls(name=name)
        return new_user

# jesus = MyEntity.new(name="Nesus", age=33)

john = User.new("John", 30)
eva = SuperUser.new("Eva", 16, "f")
rob = Robot.new("Rob")
# print('john', pprint(john.to_dict()))

org = Organization(name="some org")
org.users = [john, eva, rob]
pprint(org.to_dict())
pprint(john.to_dict())
pprint(eva.to_dict())

# john.age = 31

# peter = SuperUser.new(
#     "Peter", 22, "Good st",
#     _id="peter",
#     gender='m')
# peter.address = 'Fair st'

# # Print storage contents
# print("\nStorage contents:")
# print(db.raw_dump_json(pretty=True))

# assert len(User.instances()) == 2

# print([d.age for d in User.find({'age': 31})])
# print([d.name for d in User.find({'name': 'Peter'})])