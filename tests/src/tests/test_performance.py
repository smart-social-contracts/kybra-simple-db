import hashlib
import string

from kybra_simple_db import *


def random_string_from_seed(seed: int, length: int = 10) -> str:
    """Generate deterministic alphanumeric string from a seed"""
    chars = string.ascii_letters + string.digits
    hex_digest = hashlib.sha256(str(seed).encode()).hexdigest()
    # Map each hex character to our character set
    return "".join(chars[int(c, 16) % len(chars)] for c in hex_digest[:length])


total_num_records = 0


# Simple entity models with relationships
class Address(Entity):
    street = String(max_length=100)
    city = String(max_length=50)
    user = OneToOne("User", "addresses")


class Tag(Entity):
    name = String(max_length=50)
    favorited_by = OneToOne("User", "favorite_tag")
    tagged_users = ManyToMany("User", "tags")


class User(Entity):
    name = String(max_length=100)
    email = String(max_length=100)
    score = Integer()
    # Relationships
    addresses = OneToMany("Address", "user")
    favorite_tag = OneToOne("Tag", "favorited_by")
    tags = ManyToMany("Tag", "tagged_users")


def insert_0(num_records=100):
    global total_num_records
    for i in range(num_records):
        User(
            _id=random_string_from_seed(i + total_num_records, 32),
            name=f"User {i}",
            email=f"user{i}@example.com",
            score=i * 10,
        )
    total_num_records += num_records
    return total_num_records


def insert(num_records=100):
    global total_num_records

    # Create tag templates (don't reuse actual instances)
    tag_templates = [f"Tag {i}" for i in range(5)]

    for i in range(num_records):
        # Create 1-2 addresses per user
        address1 = Address(
            _id=f"addr_{i}_1_{total_num_records}",
            street=f"Street {i}",
            city=f"City {i % 5}",
        )

        address2 = None
        if i % 2 == 0:  # Half of users get a second address
            address2 = Address(
                _id=f"addr_{i}_2_{total_num_records}",
                street=f"Street {i} Apt B",
                city=f"City {i % 5}",
            )

        # Create unique tags for this user
        favorite_tag = Tag(
            _id=f"tag_fav_{i}_{total_num_records}", name=tag_templates[i % 5]
        )

        # Create user with relationships
        user = User(
            _id=random_string_from_seed(i + total_num_records, 32),
            name=f"User {i}",
            email=f"user{i}@example.com",
            score=i * 10,
        )

        # Add relationships
        user.addresses.add(address1)
        if address2:
            user.addresses.add(address2)

        # Set favorite tag (unique for this user)
        user.favorite_tag = favorite_tag

        # Add tags (1-3 tags per user)
        num_tags = (i % 3) + 1
        for j in range(num_tags):
            # Create unique tag for each relationship
            tag = Tag(_id=f"tag_{i}_{j}_{total_num_records}", name=tag_templates[j % 5])
            user.tags.add(tag)

    total_num_records += num_records
    return total_num_records


def read(from_id=0, to_id=100):
    count = 0
    for i in range(from_id, to_id):
        try:
            # Get the user
            user_id = random_string_from_seed(i, 32)
            user = User[user_id]

            # Access properties
            _ = user.name
            _ = user.score

            # Access relationships
            addresses = list(user.addresses)
            for addr in addresses:
                _ = addr.street

            favorite_tag = user.favorite_tag
            if favorite_tag:
                _ = favorite_tag.name

            tags = list(user.tags)
            for tag in tags:
                _ = tag.name

            count += 1
        except:
            pass  # Skip if entity doesn't exist

    return count


def get_record_as_dict(record_num=0):
    """Get a specific User record as a dictionary string"""
    try:
        # Get the user
        user_id = random_string_from_seed(record_num, 32)
        user = User[user_id]

        # Build the dictionary representation
        user_dict = {
            "_id": user._id,
            "name": user.name,
            "email": user.email,
            "score": user.score,
            "addresses": [],
            "tags": [],
            "favorite_tag": None,
        }

        # Add addresses
        for addr in user.addresses:
            user_dict["addresses"].append(
                {"_id": addr._id, "street": addr.street, "city": addr.city}
            )

        # Add favorite tag
        if user.favorite_tag:
            user_dict["favorite_tag"] = {
                "_id": user.favorite_tag._id,
                "name": user.favorite_tag.name,
            }

        # Add tags
        for tag in user.tags:
            user_dict["tags"].append({"_id": tag._id, "name": tag.name})

        return str(user_dict)
    except Exception as e:
        return f"Error retrieving record {record_num}: {str(e)}"
