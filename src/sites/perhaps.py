class Perhaps:
    
    def __init__(self, l: list):
        self.l = l

    def is_empty(self) -> bool:
        return len(self.l) == 0

    def exists(self) -> bool:
        return len(self.l) != 0

    def get(self):
        if len(self.l) == 0:
            print('no elements error')

        return self.l[0]
