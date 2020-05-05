import timeit

def main():
    for i in range(1, 7):
        t = timeit.timeit(number=30, stmt=f"solver = MineSAT(_BLANK_16x16, num_solver_threads={i}); safe_tiles = solver.find_tiles();", setup="from solver import MineSAT; _BLANK_16x16 = ['????????????????','????????????????','????????????????','????????????????','????????????????','????????????????','????????????????','????????????????','????????????????', '????????????????', '????????????????', '????????????????', '????????????????', '????????????????', '????????????????', '????????????????']")
        print(f'Number of threads: {i}  Time: {t}')

if __name__ == "__main__":
    main()