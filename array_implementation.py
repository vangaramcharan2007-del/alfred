# === 1-D & 2-D ARRAY IMPLEMENTATION ===
# Generated and typed live by Alfred OS

class DynamicArray:
    def __init__(self):
        self.data = []

    def append(self, value):
        self.data.append(value)

    def get(self, index):
        return self.data[index]

    def display(self):
        print('Array Content:', self.data)


if __name__ == '__main__':
    arr = DynamicArray()
    for x in [10, 20, 30, 40, 50]:
        arr.append(x)
    arr.display()
    print('Element at index 2 =', arr.get(2))
