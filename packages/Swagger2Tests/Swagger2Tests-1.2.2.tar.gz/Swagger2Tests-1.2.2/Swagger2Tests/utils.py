import random

class FuncHelper():
    @staticmethod
    def get_random_int(start: int = -100, end: int = 100):
        return random.randint(start, end)
    
    @classmethod
    def get_random_float(cls, start: int = -100, end: int = 100):
        return random.random() * cls.get_random_int(start, end)

    @staticmethod
    def get_random_bool():
        return random.choice([True, False])