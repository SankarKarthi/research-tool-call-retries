from faults.injector import FaultInjector, stable_unit


def test_stable_unit_is_deterministic():
    a = stable_unit(1, "T012", "order_lookup", 0)
    b = stable_unit(1, "T012", "order_lookup", 0)
    c = stable_unit(1, "T012", "order_lookup", 1)
    assert a == b
    assert a != c


def test_same_seed_same_faults():
    rates = {"transient": 0.10, "validation": 0.08, "permission": 0.04}

    def collect():
        inj = FaultInjector(seed=1, rates=rates, sleep_fn=lambda _: None)
        cats = []
        for i in range(40):
            err = inj.maybe_fail("T012", "order_lookup", i)
            cats.append(None if err is None else err.category)
        return cats

    assert collect() == collect()
