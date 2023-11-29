import sys


class Region:
    def __init__(self, length):
        self.gsum = 0.0
        self.l = 0
        self.r = 0
        self.top = [0] * length
        self.bot = [0] * length

    def print_region(self):
        print("gsum =", self.gsum)
        print("xoff =", self.l)
        for x in range(self.l, self.r + 1):
            print(f"[{self.bot[x]}, {self.top[x]}]")


class Matrix:
    def __init__(self, x, y=None):
        if y is None:
            self.load_from_file(x)
        else:
            self.xsize = x
            self.ysize = y
            self.val = [0.0] * (self.xsize * self.ysize)

    def set(self, x, y, v):
        self.val[y + x * self.ysize] = v

    def ref(self, x, y):
        if y < 0:
            return 0.0
        return self.val[y + x * self.ysize]

    def load_from_file(self, file_name):
        with open(file_name, "r") as file:
            lines = file.readlines()
            self.xsize, self.ysize = map(int, lines[0].split())
            self.val = [0] * (self.xsize * self.ysize)
            data_lines = lines[1:]
            for y in range(self.ysize):
                values = map(float, data_lines[y].split())
                for x, value in enumerate(values):
                    self.set(x, y, value)


def main():
    if len(sys.argv) != 2:
        print("Usage : opt_region [matrix file]")
        print("e.x. python ppt_region.py g.txt")
        sys.exit(-1)

    matrix_file = sys.argv[1]

    grid = Matrix(matrix_file)
    grid_cumsum = Matrix(grid.xsize, grid.ysize)  # 累積和
    t = Matrix(grid.xsize, grid.ysize)  # top
    b = Matrix(grid.xsize, grid.ysize)  # bot
    f = Matrix(grid.xsize, grid.ysize)
    fj = Matrix(grid.xsize, grid.ysize)
    ft = Matrix(grid.xsize, grid.ysize)
    fb = Matrix(grid.xsize, grid.ysize)

    x = 0
    y = 0

    # compute top and bot
    maxv = 0.0
    maxi = 0

    for x in range(grid.xsize):
        v = grid.ref(x, 0)
        grid_cumsum.set(x, 0, v)
        for y in range(1, grid.ysize):
            v = grid_cumsum.ref(x, y - 1) + grid.ref(x, y)
            grid_cumsum.set(x, y, v)
        # find top
        maxv = grid_cumsum.ref(x, grid.ysize - 1)
        maxi = grid.ysize - 1
        for y in range(grid.ysize - 1, -1, -1):
            if grid_cumsum.ref(x, y) > maxv:
                maxv = grid_cumsum.ref(x, y)
                maxi = y
            t.set(x, y, maxi)
        # find bot
        maxv = grid_cumsum.ref(x, grid.ysize - 1)
        maxi = 0
        b.set(x, 0, 0)
        for y in range(1, grid.ysize):
            v = grid_cumsum.ref(x, grid.ysize - 1) - grid_cumsum.ref(x, y - 1)
            if v > maxv:
                maxv = v
                maxi = y
            b.set(x, y, maxi)

    gmax = -float("inf")
    gmaxi = -1
    gmaxm = -1

    # compute f(i, m)
    # m = 0
    for y in range(grid.ysize):
        fj.set(0, y, -1)
        ft.set(0, y, t.ref(0, y))
        fb.set(0, y, b.ref(0, y))
        # cover
        f.set(
            0,
            y,
            grid_cumsum.ref(0, int(ft.ref(0, y)))
            - grid_cumsum.ref(0, int(fb.ref(0, y)) - 1),
        )
        if f.ref(0, y) > gmax:
            gmax = f.ref(0, y)
            gmaxi = y
            gmaxm = 0

    # m >= 1
    for x in range(1, grid.xsize):
        # examine (i > j)
        maxj = 0
        fval = f.ref(x - 1, 0)  # f(j, <= m-1)
        fj.set(x, 0, 0)
        if fval < 0:
            fval = 0.0
            fj.set(x, 0, -1)
        cval = grid_cumsum.ref(x, int(t.ref(x, 0))) - grid_cumsum.ref(
            x, int(b.ref(x, 0)) - 1
        )
        # print(x, f.val)
        f.set(x, 0, fval + cval)
        # print(x, f.val)
        ft.set(x, 0, t.ref(x, 0))
        fb.set(x, 0, b.ref(x, 0))
        for i in range(1, grid.ysize):
            # i=j
            fval = f.ref(x - 1, i)  # f(j, <= m-1)
            cval = grid_cumsum.ref(x, int(t.ref(x, i))) - grid_cumsum.ref(
                x, int(b.ref(x, i)) - 1
            )
            if fval < 0:
                dval = cval
            else:
                dval = fval + cval
            # examine maxj
            fval2 = f.ref(x - 1, maxj)  # f(j, <= m-1)
            cval2 = grid_cumsum.ref(x, int(t.ref(x, i))) - grid_cumsum.ref(
                x, int(b.ref(x, maxj)) - 1
            )
            if fval2 < 0:
                dval2 = cval2
            else:
                dval2 = fval2 + cval2
            if dval > dval2:
                if fval < 0:
                    fj.set(x, i, -1)
                else:
                    fj.set(x, i, i)
                f.set(x, i, dval)
                ft.set(x, i, t.ref(x, i))
                fb.set(x, i, b.ref(x, i))
                maxj = i
            else:
                fj.set(x, i, maxj)
                f.set(x, i, dval2)
                ft.set(x, i, t.ref(x, i))
                fb.set(x, i, b.ref(x, maxj))

        # examine (i < j)
        maxj = grid.ysize - 1
        for i in range(grid.ysize - 1, -1, -1):
            # i=j
            fval = f.ref(x - 1, i)  # f(j, <= m-1)
            cval = grid_cumsum.ref(x, int(t.ref(x, i))) - grid_cumsum.ref(
                x, int(b.ref(x, i)) - 1
            )
            if fval < 0:
                dval = cval
            else:
                dval = fval + cval
            # examine maxj
            fval2 = f.ref(x - 1, maxj)  # f(j, <= m-1)
            cval2 = grid_cumsum.ref(x, int(t.ref(x, maxj))) - grid_cumsum.ref(
                x, int(b.ref(x, i)) - 1
            )
            if fval2 < 0:
                dval2 = cval2
            else:
                dval2 = fval2 + cval2
            if dval > dval2:
                maxj = i
            else:
                if dval2 > f.ref(x, i):
                    fj.set(x, i, maxj)
                    f.set(x, i, dval2)
                    ft.set(x, i, t.ref(x, maxj))
                    fb.set(x, i, b.ref(x, i))

        for i in range(grid.ysize):
            if f.ref(x, i) > gmax:
                gmax = f.ref(x, i)
                gmaxi = i
                gmaxm = x

    # output optimal region
    r = Region(grid.xsize)
    r.r = gmaxm
    r.gsum = gmax
    r.top[gmaxm] = int(ft.ref(gmaxm, gmaxi))
    r.bot[gmaxm] = int(fb.ref(gmaxm, gmaxi))
    for x in range(gmaxm - 1, -1, -1):
        if fj.ref(x + 1, gmaxi) < 0:
            r.l = x + 1
            break
        gmaxi = int(fj.ref(x + 1, gmaxi))
        r.top[x] = int(ft.ref(x, gmaxi))
        r.bot[x] = int(fb.ref(x, gmaxi))

    r.print_region()


if __name__ == "__main__":
    main()
