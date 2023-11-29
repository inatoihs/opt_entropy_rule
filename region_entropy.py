import random
from range_entropy import (
    compute_entropy,
    find_intersection,
    to_normal_vector,
    find_optimal_range,
)


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
            self.data_load(x)
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

    def data_load(self, data):
        self.xsize = len(data[0])
        self.ysize = len(data)
        self.val = [0] * (self.xsize * self.ysize)
        for y in range(self.ysize):
            values = map(float, data[y])
            for x, value in enumerate(values):
                self.set(x, y, value)


def touching_oracle(positive: tuple, negative: tuple, theta: (float, float)):
    rows, cols = len(positive), len(positive[0])
    dotted_matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            dotted_matrix[i][j] = positive[i][j] * theta[0] + negative[i][j] * theta[1]

    grid = Matrix(dotted_matrix)
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

    # r.print_region()

    return r


def sum_in_region(region: Region, matrix: tuple):
    """sum of matrix in region"""
    result = 0
    for i in range(region.l, region.r + 1):
        for j in range(region.bot[i], region.top[i] + 1):
            result += matrix[j][i]
    return result


# Main algorithm
def find_optimal_region(positive, negative):
    """function for two dimensional optimal rule"""
    A = (
        sum(number for row in positive for number in row),
        sum(number for row in negative for number in row),
    )
    v_best_sofar = float("inf")
    tangent_points = []
    entropies = []
    theta_list = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    thetas = []
    regions = []

    # Step 1
    """ステップ１
    法線ベクトルΘ1=(1,1), Θ2 =(1,-1), Θ3 =(-1,-1), Θ4 =(-1,1)を持つ直線
    に対してtouching_oracleを用いて、4つのスタンプポイントP1,P2,P3,P4を求めます。
    そしてcompute_entropyを用いてそれらのエントロピーもそれぞれ求めます。
    そのうち、最もエントロピーの低いものをvbestsofarとおきます。"""
    for theta in theta_list:
        region = touching_oracle(positive, negative, theta)
        current_tangent_point = (
            sum_in_region(region, positive),
            sum_in_region(region, negative),
        )
        tangent_points.append(current_tangent_point)
        entropy = compute_entropy(current_tangent_point, A)
        entropies.append(entropy)
        regions.append(region)

    best_index = entropies.index(min(entropies))
    v_best_sofar = entropies[best_index]
    point_of_best_v = tangent_points[best_index]
    best_region = regions[best_index]

    # Step 2
    """P1,P2,P3,P4に対応する接線L1,L2,L3,L4の交点をそれぞれ求めます。
    なお、L1はP1を通り法線ベクトルが(1,1)である直線です。
    ここで求めた交点をI_12, I_23, I_34, I_41としましょう。I_12はL1とL2の交点です。"""
    intersections = []
    for i in range(4):
        intersections.append(
            find_intersection(
                theta_list[i % 4],
                theta_list[(i + 1) % 4],
                tangent_points[i % 4],
                tangent_points[(i + 1) % 4],
            )
        )
        thetas.append((theta_list[i % 4], theta_list[(i + 1) % 4]))

    # Step 3
    """I_12, I_23, I_34, I_41のエントロピーを求める。"""
    intersection_entropies = []
    for i in intersections:
        intersection_entropies.append(compute_entropy(i, A))

    tangent_point_pairs = []
    for i in range(4):
        tangent_point_pairs.append((tangent_points[i % 4], tangent_points[(i + 1) % 4]))
    subchains = list(
        zip(intersections, tangent_point_pairs, intersection_entropies, thetas)
    )
    # print("tangent_points", tangent_points)  # for debug

    # Step 4
    """交点Iのエントロピーがvbestsofarよりも高いなら、その交点に対応するsub-chainを枝刈りする。
    もしもsub-chainがひとつもない場合、ここで探索を終了しvbestsofarに対応するルール（範囲）を出力します。"""
    while True:
        # print("subchain:", subchains, "\nentropy", v_best_sofar) # for debug
        for current_subchain in subchains:
            if current_subchain[2] > v_best_sofar:
                subchains.remove(current_subchain)
        if not subchains:
            # for debug
            # print("convex hull:\n", tangent_points)

            # output the best rule
            return (point_of_best_v, v_best_sofar, best_region)

        # Step 5
        """エントロピーが最も低いIを選択します。ここで、I_ijが選択されたとします。θ=(iからj)
        点iと点jを結ぶ直線の傾きをθijとし、θijの法線ベクトルをtouching oracleに与えてPmidを計算します。
        もしPmidのエントロピーがvbestsofarよりも低ければvbestsofar, point_of_vを更新します。"""
        subchains.sort(key=lambda x: x[2])  # ループ内でソートさせるのまずい？|subchains|は十分小さい？
        selected_subchain = subchains.pop(0)
        x1, y1 = selected_subchain[1][0]
        x2, y2 = selected_subchain[1][1]
        if x1 == x2 and y1 == y2:
            continue
        theta = to_normal_vector((x1 - x2, y1 - y2))
        region = touching_oracle(positive, negative, theta)
        Pmid = (
            sum_in_region(region, positive),
            sum_in_region(region, negative),
        )
        entropy = compute_entropy(Pmid, A)
        if entropy < v_best_sofar:
            v_best_sofar = entropy
            point_of_best_v = Pmid
            best_region = region
        # print("Pmid: ", Pmid, (x1, y1), (x2, y2), (theta[0], theta[1]))  # for debug

        # Step 6
        """Pmidが新たなスタンプポイントであれば、Iijに対応するsub-chainをIimid,Imidjに対応する2つのsub-chainに分割します。
        Pimdが新たなスタンポイントでないならば、そのsub-chainを削除します。
        ステップ４に戻ります"""
        if Pmid not in tangent_points:
            tangent_points.append(Pmid)
            # print("selected:",selected_subchain) #for debug
            left_mid_intersection = find_intersection(
                selected_subchain[3][0], theta, (x1, y1), Pmid
            )
            right_mid_intersection = find_intersection(
                selected_subchain[3][1], theta, (x2, y2), Pmid
            )
            left_mid_entropy = compute_entropy(left_mid_intersection, A)
            right_mid_entropy = compute_entropy(right_mid_intersection, A)
            subchains.append(
                (
                    left_mid_intersection,
                    ((x1, y1), Pmid),
                    left_mid_entropy,
                    (selected_subchain[3][0], theta),
                )
            )
            subchains.append(
                (
                    right_mid_intersection,
                    (Pmid, (x2, y2)),
                    right_mid_entropy,
                    (theta, selected_subchain[3][1]),
                )
            )


def test_opt_region():  # range_entropy.pyと差が出ないか確認
    """function for testing optimal region rule function"""
    # 生成するタプルの個数
    num_tuples = random.randint(1, 10)

    # タプル内の要素の範囲
    min_value = 0
    max_value = 10

    # ランダムなタプルを生成
    atomic_points = [
        (random.randint(min_value, max_value), random.randint(min_value, max_value))
        for _ in range(num_tuples)
    ]
    positive = [[]]
    negative = [[]]
    for i in range(len(atomic_points)):
        positive[0].append(atomic_points[i][0])
        negative[0].append(atomic_points[i][1])

    point_v, v, _ = find_optimal_region(positive, negative)
    if (point_v, v) != find_optimal_range(atomic_points):
        print("incorrect")
        print("atomic points:\n", atomic_points)
        exit(1)


# for i in range(10000):
#    test_opt_region()
# print("Test Passed")
