import numpy as np

position = (3, 3)


first_part = []
for i in range(1, 8):
    first_part.append((position[0] - i, position[1] - i))
    first_part.append((position[0] - i, position[1] + i))
    first_part.append((position[0] + i, position[1] - i))
    first_part.append((position[0] + i, position[1] + i))
first_part = np.array(first_part)
first_part = first_part[first_part[:, 0] >= 0]
first_part = first_part[first_part[:, 0] < 8]
first_part = first_part[first_part[:, 1] >= 0]
first_part = first_part[first_part[:, 1] < 8]

second_part = []
for i in range(1, 8):
    second_part.append((position[0] - i, position[1]))
    second_part.append((position[0] + i, position[1]))
    second_part.append((position[0], position[1] - i))
    second_part.append((position[0], position[1] + i))
second_part = np.array(second_part)
second_part = second_part[second_part[:, 0] >= 0]
second_part = second_part[second_part[:, 0] < 8]
second_part = second_part[second_part[:, 1] >= 0]
second_part = second_part[second_part[:, 1] < 8]


print(f"First part: {first_part}")
print(f"Second part: {second_part}")



