import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def visualizer(
    data,
    bot,
    top,
    left_index,
    right_index,
    x_max,
    y_max,
    column_x,
    column_y,
    barlabel,
    xbins,
    ybins,
):
    # グラフのサイズを設定
    plt.figure(figsize=(5, 5))

    # カラーマップを選択（ここでは'viridis'を使用）
    cmap = plt.get_cmap("viridis")

    # データをimshowを使用して描画
    plt.imshow(data, cmap=cmap, origin="lower", interpolation="nearest")

    # 領域の線を描画するための座標を定義
    region_coords = []

    shift_width = 0.0035 * x_max  # 領域の端っこ線をずらすための値
    for i in range(left_index, right_index + 1):
        region_coords.append([i - 0.5, bot[i] - 0.5])
        region_coords.append([i + 0.5, bot[i] - 0.5])
        if i == 0:
            region_coords[-2][0] += shift_width
        elif i == x_max - 1:
            region_coords[-1][0] -= shift_width
        if bot[i] == 0:
            region_coords[-2][1] += shift_width
            region_coords[-1][1] += shift_width
        elif bot[i] == y_max - 1:
            region_coords[-2][1] -= shift_width
            region_coords[-1][1] -= shift_width
    for i in range(right_index, left_index - 1, -1):
        region_coords.append([i + 0.5, top[i] + 0.5])
        region_coords.append([i - 0.5, top[i] + 0.5])
        if i == 0:
            region_coords[-1][0] += shift_width
        elif i == x_max - 1:
            region_coords[-2][0] -= shift_width
        if top[i] == 0:
            region_coords[-2][1] += shift_width
            region_coords[-1][1] += shift_width
        elif top[i] == y_max - 1:
            region_coords[-2][1] -= shift_width
            region_coords[-1][1] -= shift_width

    # Polygonオブジェクトを作成
    region_polygon = Polygon(
        region_coords,
        closed=True,
        edgecolor="red",
        facecolor="none",
        linewidth=3,
    )

    # グラフにPolygonを追加
    plt.gca().add_patch(region_polygon)

    # カラーバーを追加
    plt.colorbar().set_label("Number of " + barlabel)

    # x軸とy軸のラベルを設定
    plt.xlabel(column_x)
    plt.ylabel(column_y)

    xticks_placement = [-0.5]
    for i in range(x_max):
        xticks_placement.append(i + 0.5)
    yticks_placement = [-0.5]
    for i in range(y_max):
        yticks_placement.append(i + 0.5)

    plt.xticks(xticks_placement[::2], xbins[::2])
    plt.yticks(yticks_placement[::2], ybins[::2])

    # グラフを表示
    plt.show()


def create_bar_chart(data1, data2, chart_label):
    # データとラベルを設定
    data = [data1, data2]
    labels = ["positive", "negative"]

    # 棒グラフを作成
    plt.bar(labels, data)

    # グラフにラベルを追加
    plt.title(chart_label)

    # グラフを表示
    plt.show()
