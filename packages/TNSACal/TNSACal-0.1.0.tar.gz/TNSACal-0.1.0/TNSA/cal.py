import math

class MyAdvancedArray:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    def __add__(self, other):
        if len(self.data) != len(other.data):
            raise ValueError("Arrays must have the same length.")
        result = [x + y for x, y in zip(self.data, other.data)]
        return MyAdvancedArray(result)

    def __sub__(self, other):
        if len(self.data) != len(other.data):
            raise ValueError("Arrays must have the same length.")
        result = [x - y for x, y in zip(self.data, other.data)]
        return MyAdvancedArray(result)

    def __mul__(self, scalar):
        result = [x * scalar for x in self.data]
        return MyAdvancedArray(result)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def mean(self):
        return sum(self.data) / len(self.data)

    def std_deviation(self):
        mean_val = self.mean()
        variance = sum((x - mean_val) ** 2 for x in self.data) / len(self.data)
        return math.sqrt(variance)

    def normalize(self):
        mean_val = self.mean()
        std_dev = self.std_deviation()
        result = [(x - mean_val) / std_dev for x in self.data]
        return MyAdvancedArray(result)
