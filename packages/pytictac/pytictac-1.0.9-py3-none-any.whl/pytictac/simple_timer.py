import torch
import time


class CpuTimer:
    def __init__(self, name="", verbose=True) -> None:
        self.name = name
        self.verbose = verbose

    def __enter__(self):
        if self.verbose:
            self.tic()

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.verbose:
            print(f"Time {self.name}: ", self.toc(), "ms")

    def tic(self):
        self.start = time.perf_counter()

    def toc(self):
        self.end = time.perf_counter()
        return (self.end - self.start)*1000


class Timer:
    def __init__(self, name="", verbose=True) -> None:
        self.name = name
        self.verbose = verbose
        if verbose:
            self.start = torch.cuda.Event(enable_timing=True)
            self.end = torch.cuda.Event(enable_timing=True)
        
    def __enter__(self):
        if self.verbose:
            self.tic()

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.verbose:
            print(f"Time {self.name}: ", self.toc(), "ms")

    def tic(self):
        self.start.record()

    def toc(self):
        self.end.record()
        torch.cuda.synchronize()
        return self.start.elapsed_time(self.end)


if __name__ == "__main__":

    print("Start timing using context manager")

    with Timer("Test1"):
        s1, s2 = 1000, 1000
        a = torch.zeros((s1, s2))
        for x in range(s1):
            for y in range(s2):
                a[x, y] = x * y
    with CpuTimer("Test2"):
        s1, s2 = 1000, 1000
        a = torch.zeros((s1, s2))
        for x in range(s1):
            for y in range(s2):
                a[y, x] = x * y
