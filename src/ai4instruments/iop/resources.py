"""Atomic, counted allocation of instruments, shared objects and compute capacity."""
from collections import Counter


class QueueFull(RuntimeError):
    pass


def quantities(value, capacities):
    if not isinstance(value, dict):
        raise ValueError('Requirements must be an object of resource names and quantities')
    result = {}
    for name, count in value.items():
        if name not in capacities:
            raise ValueError('Configure resource capacity first: ' + str(name))
        if type(count) is not int or count < 1 or count > capacities[name]:
            raise ValueError('Resource quantity must be within its capacity: ' + name)
        result['pool:' + name] = count
    return result


def capacities(value):
    if not isinstance(value, dict):
        raise ValueError('Capacities must be an object')
    for name, count in value.items():
        if not isinstance(name, str) or not name or type(count) is not int or count < 1:
            raise ValueError('Resource capacities need names and positive integer quantities')
    return dict(value)


class Allocator:
    """A reservation covers its own operations without counting the quantity twice.

    The engine owns the lock. Allocation and release cost O(requested resources).
    Every request is accepted in full or left waiting; no partial allocations.
    """
    def __init__(self):
        self.limits = {}
        self.used = Counter()
        self.reserved = {}
        self.claims = {}
        self.inside = {}

    def limit(self, name):
        return self.limits.get(name, 1)

    def can_reserve(self, amounts, blocked=()):
        return all(name not in blocked and self.used[name] + count <= self.limit(name)
                   for name, count in amounts.items())

    def reserve(self, owner, amounts):
        self.reserved[owner] = dict(amounts)
        self.inside[owner] = Counter()
        self.used.update(amounts)

    def can_claim(self, owner, amounts, blocked=()):
        reserved = self.reserved.get(owner, {})
        inside = self.inside.get(owner, {})
        for name, count in amounts.items():
            if name in reserved:
                if inside.get(name, 0) + count > reserved[name]:
                    return False
            elif name in blocked or self.used[name] + count > self.limit(name):
                return False
        return True

    def claim(self, identifier, owner, amounts):
        reserved = self.reserved.get(owner, {})
        self.claims[identifier] = (owner, dict(amounts))
        for name, count in amounts.items():
            if name in reserved:
                self.inside[owner][name] += count
            else:
                self.used[name] += count

    def release(self, identifier):
        owner, amounts = self.claims.pop(identifier)
        reserved = self.reserved.get(owner, {})
        for name, count in amounts.items():
            target = self.inside[owner] if name in reserved else self.used
            target[name] -= count
            if not target[name]:
                del target[name]

    def finish(self, owner):
        if any(self.inside.get(owner, {}).values()):
            raise RuntimeError('Operations still use the experiment reservation')
        self.used.subtract(self.reserved.pop(owner, {}))
        self.used += Counter()  # remove zero entries
        self.inside.pop(owner, None)

    def snapshot(self):
        names = self.limits.keys() | self.used.keys()
        return [{'resource': name, 'capacity': self.limit(name), 'used': self.used[name]}
                for name in sorted(names)]
