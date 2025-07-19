from kybra import ic
from tester import Tester  # noqa: E402

from kybra_simple_db import *  # noqa: E402


class StressTestEntity(Entity):
    __alias__ = "name"
    name = String(min_length=1, max_length=100)
    value = Integer()


class TestStress:
    def bulk_insert(self, quantity: str):
        quantity = int(quantity)
        actual_count = StressTestEntity.count()

        for i in range(quantity):
            v = i + actual_count
            StressTestEntity(name=f"Entity_{v}", value=v)

        actual_count = StressTestEntity.count() - actual_count
        if actual_count == quantity:
            ic.print(
                f"Successfully inserted {quantity} entities. Total entities = {actual_count}"
            )
        else:
            raise Exception(
                "Expected %d entities inserted, instead got %d"
                % (quantity, actual_count)
            )

    def query(self, name: str):
        ic.print("Name lookup: name = %s" % name)
        entity = StressTestEntity[name]
        ic.print("Name lookup: entity = %s" % entity.to_dict())
        assert entity is not None


def run(test_name: str = None, test_var: str = None):
    tester = Tester(TestStress)
    return tester.run_test(test_name, test_var)


if __name__ == "__main__":
    exit(run())
