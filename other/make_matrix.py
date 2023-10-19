import sys
import random

def main():
    if len(sys.argv) != 3:
        print("Usage: python make_matrix.py [xsize] [ysize]")
        print("e.g. python make_matrix.py 20 20")
        sys.exit(-1)

    xsize = int(sys.argv[1])
    ysize = int(sys.argv[2])
    print(f"{xsize} {ysize}")

    for _ in range(ysize):
        row = [int(random.uniform(-10, 10)) for _ in range(xsize)]
        row_str = ' '.join(f"{val:2}" for val in row)  # Adjust the width as needed
        print(row_str)

if __name__ == "__main__":
    main()
