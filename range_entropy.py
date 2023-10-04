# print文はdebug用なので消して良い

import random
import numpy as np


def to_normal_vector(vector):
    """convert vector to normal vector"""
    y, x = vector
    y = -y
    return (x, y)


def is_point_on_edge(x1, y1, x2, y2, x, y, abXat, bcXbt):
    """check if the point is on the edge"""
    # 点が直線上にあるかどうかを判定
    is_on_line = abXat * bcXbt == 0.0

    # 点が始点を含まない辺の始点と終点の間にあるかどうかを判定
    is_between_points = (
        (x1 <= x <= x2 or x1 >= x >= x2)
        and (y1 <= y <= y2 or y1 >= y >= y2)
        and not (x1 == x and y1 == y)
        and not (x2 == x and y2 == y)
    )

    return is_on_line and is_between_points


def find_intersection(vector1, vector2, point1, point2) -> (float, float):
    """find the intersection of two lines"""
    # 法線ベクトルの成分を抽出し、方向ベクトルに変換
    vector1 = to_normal_vector(vector1)
    vector2 = to_normal_vector(vector2)
    x1, y1 = vector1
    x2, y2 = vector2

    # 直線の方程式を求める
    # 直線1: y = mx + c1
    # 直線2: y = nx + c2
    m = y1 / x1 if x1 != 0 else float("inf")  # 傾き m
    n = y2 / x2 if x2 != 0 else float("inf")  # 傾き n

    # 切片 c1, c2 を計算
    c1 = point1[1] - m * point1[0] if x1 != 0 else None
    c2 = point2[1] - n * point2[0] if x2 != 0 else None

    # 両方の直線が垂直な場合
    if x1 == 0 and x2 == 0:
        return point1

    # どちらかの直線が垂直な場合
    if x1 == 0:
        x = point1[0]
        y = n * x + c2
    elif x2 == 0:
        x = point2[0]
        y = m * x + c1
    else:
        # 通常の場合、連立方程式を解く
        if m == n:
            return point1
        x = (c2 - c1) / (m - n)
        y = m * x + c1

    return (x, y)


def compute_entropy(X, A):
    """compute entropy of X"""
    x1, x2 = X
    a1, a2 = A
    total_X = x1 + x2
    total_A = a1 + a2
    if x1 < 0 or x2 < 0:
        entropy_X = -float("inf")
    elif x1 == 0 and x2 == 0:
        entropy_X = 0
    elif x1 == 0:
        entropy_X = -(1 / total_A) * x2 * np.log(x2 / total_X)
    elif x2 == 0:
        entropy_X = -(1 / total_A) * x1 * np.log(x1 / total_X)
    else:
        entropy_X = -(1 / total_A) * (
            x1 * np.log(x1 / total_X) + x2 * np.log(x2 / total_X)
        )
    if abs(x1 - a1) < 0.00000001 and abs(x2 - a2) < 0.00000001:
        entropy_A_X = 0
    elif total_A - total_X == 0:
        entropy_A_X = -float("inf")
    elif (a1 - x1) / (total_A - total_X) < 0 or (a2 - x2) / (total_A - total_X) < 0:
        entropy_A_X = -float("inf")
    elif abs(x1 - a1) < 0.00000001:
        entropy_A_X = (
            -(1 / total_A) * (a2 - x2) * np.log((a2 - x2) / (total_A - total_X))
        )
    elif abs(x2 - a2) < 0.00000001:
        entropy_A_X = (
            -(1 / total_A) * (a1 - x1) * np.log((a1 - x1) / (total_A - total_X))
        )
    else:
        entropy_A_X = -(1 / total_A) * (
            (a1 - x1) * np.log((a1 - x1) / (total_A - total_X))
            + (a2 - x2) * np.log((a2 - x2) / (total_A - total_X))
        )
        if a1 - x1 < 0 or a2 - x2 < 0:
            print("a1-x1:", a1 - x1, "a2-x2:", a2 - x2)
    entropy = entropy_X + entropy_A_X

    return entropy


def touching_oracle(atomic_points: list, theta: (float, float)):
    """Touching Oracle function"""
    # 内積を計算して最大部分和を求める
    current_sum = 0
    max_so_far = float("-inf")
    max_index_l = 0
    max_index_r = 0
    index_l = 0

    for i, point in enumerate(atomic_points):
        point = atomic_points[i]
        dot_product = point[0] * theta[0] + point[1] * theta[1]

        if current_sum < 0:
            current_sum = dot_product
            index_l = i
        else:
            current_sum = dot_product + current_sum

        if max_so_far < current_sum:
            max_so_far = current_sum
            max_index_l = index_l
            max_index_r = i

        elif max_so_far == current_sum:  # 最大部分和が複数ある時
            pass  # TODO

    # 最大部分和の範囲内のデータを合計
    max_range_data = atomic_points[max_index_l : max_index_r + 1]
    total_sum = tuple(map(sum, zip(*max_range_data)))

    return (total_sum, max_index_l, max_index_r)


# Main algorithm
def find_optimal_range(data):
    """function for one dimensional optimal rule"""
    atomic_points = data
    A = (sum(item[0] for item in atomic_points), sum(item[1] for item in atomic_points))
    v_best_sofar = float("inf")
    tangent_points = []
    entropies = []
    theta_list = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    point_rule = {}  # スタンプポイントとルールの関係
    thetas = []

    # Step 1
    """ステップ１
    法線ベクトルΘ1=(1,1), Θ2 =(1,-1), Θ3 =(-1,-1), Θ4 =(-1,1)を持つ直線
    に対してtouching_oracleを用いて、4つのスタンプポイントP1,P2,P3,P4を求めます。
    そしてcompute_entropyを用いてそれらのエントロピーもそれぞれ求めます。
    そのうち、最もエントロピーの低いものをvbestsofarとおきます。"""
    for theta in theta_list:
        current_tangent_point, left, right = touching_oracle(atomic_points, theta)
        tangent_points.append(current_tangent_point)
        entropy = compute_entropy(current_tangent_point, A)
        entropies.append(entropy)
        point_rule[current_tangent_point] = (left, right)

    best_index = entropies.index(min(entropies))
    v_best_sofar = entropies[best_index]
    point_of_v = tangent_points[best_index]

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
    # print("tangent_points",tangent_points)  # for debug

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
            return (point_of_v, v_best_sofar)

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
        Pmid, left, right = touching_oracle(atomic_points, theta)

        entropy = compute_entropy(Pmid, A)
        point_rule[Pmid] = (left, right)
        if entropy < v_best_sofar:
            v_best_sofar = entropy
            point_of_v = Pmid
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


def test_opt_range():
    """function for testing optimal range rule function"""
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

    point_and_entropy = []
    points = []
    A = (sum(item[0] for item in atomic_points), sum(item[1] for item in atomic_points))
    for i in range(len(atomic_points)):
        x = 0
        y = 0
        for j in range(i, len(atomic_points)):
            x += atomic_points[j][0]
            y += atomic_points[j][1]
            point_and_entropy.append(((x, y), compute_entropy((x, y), A)))
            points.append((x, y))
    point_and_entropy.sort(key=lambda x: x[1])
    computed_ans = find_optimal_range(atomic_points)
    print("atomic points:\n", atomic_points)
    print(computed_ans)
    if computed_ans[1] != point_and_entropy[0][1]:
        print(
            "Computed solution:   ",
            computed_ans,
            "\nCorrect solution: ",
            point_and_entropy[0],
        )
        print("atomic points:\n", atomic_points)
        print("points: \n", points)
        exit(1)


# for i in range(1):
#    test_opt_range()
# print("Test Passed")
