import mmh3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, size, num_hash):
        self.size = size
        self.num_hash = num_hash
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        for seed in range(self.num_hash):
            index = mmh3.hash(item, seed) % self.size
            self.bit_array[index] = 1

    def contains(self, item):
        for seed in range(self.num_hash):
            index = mmh3.hash(item, seed) % self.size
            if self.bit_array[index] == 0:
                return False
        return True

