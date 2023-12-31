import matplotlib.pyplot as plt
import numpy as np
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
    highlight=False,
    highlight_x=None,
    highlight_y=None,
    square=False,
):
    # グラフのサイズを設定
    plt.figure(figsize=(5, 5))

    if not square:
        xticks_placement = [-0.5]
        for i in range(x_max):
            xticks_placement.append(i + 0.5)
        yticks_placement = [-0.5]
        for i in range(y_max):
            yticks_placement.append(i + 0.5)

        # x軸とy軸の目盛りを設定
        plt.xticks(xbins[::2], xbins[::2])
        plt.yticks(ybins[::2], ybins[::2])
        plt.xticks(rotation=50)

        X, Y = np.meshgrid(xbins, ybins)

        plt.pcolormesh(X, Y, data)

        # 領域の線を描画するための座標を定義
        region_coords = []

        x_shift_width = (xbins[-1] - xbins[0]) / 200  # 領域の端っこ線をずらすための値
        y_shift_width = (ybins[-1] - ybins[0]) / 200  # 領域の端っこ線をずらすための値
        for i in range(left_index, right_index + 1):
            region_coords.append([xbins[i], ybins[bot[i]]])
            region_coords.append([xbins[i + 1], ybins[bot[i]]])
            if i == 0:
                region_coords[-2][0] += x_shift_width
            elif i == x_max - 1:
                region_coords[-1][0] -= x_shift_width
            if bot[i] == 0:
                region_coords[-2][1] += y_shift_width
                region_coords[-1][1] += y_shift_width
            elif bot[i] == y_max - 1:
                region_coords[-2][1] -= y_shift_width
                region_coords[-1][1] -= y_shift_width
        for i in range(right_index, left_index - 1, -1):
            region_coords.append([xbins[i + 1], ybins[top[i] + 1]])
            region_coords.append([xbins[i], ybins[top[i] + 1]])
            if i == 0:
                region_coords[-1][0] += x_shift_width
            elif i == x_max - 1:
                region_coords[-2][0] -= x_shift_width
            if top[i] == 0:
                region_coords[-2][1] += y_shift_width
                region_coords[-1][1] += y_shift_width
            elif top[i] == y_max - 1:
                region_coords[-2][1] -= y_shift_width
                region_coords[-1][1] -= y_shift_width
        # Polygonオブジェクトを作成
        region_polygon = Polygon(
            region_coords,
            closed=True,
            edgecolor="red",
            facecolor="none",
            linewidth=2,
        )

        if highlight:
            highlight_coords = [
                [xbins[highlight_x], ybins[highlight_y]],
                [xbins[highlight_x + 1], ybins[highlight_y]],
                [xbins[highlight_x + 1], ybins[highlight_y + 1]],
                [xbins[highlight_x], ybins[highlight_y + 1]],
            ]
            highlight_polygon = Polygon(
                highlight_coords,
                closed=True,
                edgecolor="magenta",
                facecolor="none",
                linewidth=1.5,
            )
    else:
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

        if highlight:
            highlight_coords = [
                [highlight_x + 0.5, highlight_y - 0.5],
                [highlight_x + 0.5, highlight_y + 0.5],
                [highlight_x - 0.5, highlight_y + 0.5],
                [highlight_x - 0.5, highlight_y - 0.5],
            ]
            highlight_polygon = Polygon(
                highlight_coords,
                closed=True,
                edgecolor="magenta",
                facecolor="none",
                linewidth=2.5,
            )

    # グラフにPolygonを追加
    plt.gca().add_patch(region_polygon)
    if highlight:
        plt.gca().add_patch(highlight_polygon)

    # カラーバーを追加
    plt.colorbar().set_label("Number of " + barlabel)

    # x軸とy軸のラベルを設定
    plt.xlabel(column_x)
    plt.ylabel(column_y)

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
