"""Stress tests for querying and loading operations in kybra-simple-db."""

from .stress_test_base import (
    ic, 
    StressTestBase, 
    StressTestEntity, 
    RelatedEntity,
    SMALL_BATCH_SIZE, 
    MEDIUM_BATCH_SIZE, 
    LARGE_BATCH_SIZE, 
    Tester
)


class TestStressBulkLoad(StressTestBase):
    """Test class for bulk loading and querying performance."""
    
    def test_query_performance_after_bulk_insert(self):
        entities = StressTestEntity.instances()
        len_entities = len(entities)
        ic.print("len(entities) = %d" % len_entities)
        # ic.print("entities[0] = %s" % entities[0].to_dict())
        id = int(len_entities / 2)
        ic.print("Id lookup: id = %s" % id)
        entity = StressTestEntity[id]
        ic.print("Id lookup: entity = %s" % entity.to_dict())
        assert entity is not None
        name = 'Entity_%s' % id
        ic.print("Name lookup: name = %s" % name)
        entity = StressTestEntity[name]
        ic.print("Name lookup: entity = %s" % entity.to_dict())
        assert entity is not None

def run():
    tester = Tester(TestStressBulkLoad)
    return tester.run_tests()


if __name__ == "__main__":
    exit(run())
