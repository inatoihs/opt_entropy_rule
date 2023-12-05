import pandas as pd
from region_entropy import find_optimal_region, sum_in_region
from region_visualizer import visualizer, create_bar_chart


def main():
    filename = "data/diabetes.csv"

    # CSVファイルからデータを読み込む
    df = pd.read_csv(filename)

    column_x = "Glucose"
    # x_bucket_num = len(df[column_x].unique())
    x_bucket_num = 10
    # df["x_Bin"] = df[column_x]
    while x_bucket_num > 0:
        try:
            df["x_Bin"], xbins = pd.qcut(df[column_x], q=x_bucket_num, retbins=True)
            break
        except ValueError:
            x_bucket_num -= 1
            continue

    column_y = "BMI"
    # y_bucket_num = len(df[column_y].unique())
    y_bucket_num = 10
    # df["y_Bin"] = df[column_y]
    while y_bucket_num > 0:
        try:
            df["y_Bin"], ybins = pd.qcut(df[column_y], q=y_bucket_num, retbins=True)
            break
        except ValueError:
            y_bucket_num -= 1
            continue

    objective_column = "Outcome"

    # 二次元タプルを初期化
    positive = [[0] * y_bucket_num for _ in range(x_bucket_num)]
    negative = [[0] * y_bucket_num for _ in range(x_bucket_num)]

    # objective_num 列が 1 と 0 の場合にデータを分割して集計
    # key=lambda x: x_custom_sort_order.index(x)は対象が文字列の時だけ書く
    for i, x_bin in enumerate(sorted(df["x_Bin"].unique().tolist())):
        for j, y_bin in enumerate(sorted(df["y_Bin"].unique().tolist())):
            subset = df[(df["x_Bin"] == x_bin) & (df["y_Bin"] == y_bin)]
            positive_count = len(subset[subset[objective_column] == 1])
            negative_count = len(subset[subset[objective_column] == 0])
            positive[i][j] = positive_count
            negative[i][j] = negative_count

    result = (
        df.groupby(["x_Bin", "y_Bin", objective_column]).size().unstack(fill_value=0)
    )

    # タプルのリストを作成
    result_tuples = [
        (index[0], index[1], row[1], row[0]) for index, row in result.iterrows()
    ]

    # summary[i][j]にはx_Binがi番目のBinである範囲、y_Binがj番目のBinである範囲、
    # 'Outcome'が1であるデータ数、'Outcome'が０であるデータ数が格納されています。
    summary = []

    for i in range(x_bucket_num):
        summary.append(result_tuples[i * y_bucket_num : (i + 1) * y_bucket_num])

    point, v, region = find_optimal_region(positive, negative)

    # objective_num列が1であるデータの数を数える
    positive_all = (df[objective_column] == 1).sum()

    # objective_num列が0であるデータの数を数える
    negative_all = (df[objective_column] == 0).sum()

    positive_in_region = sum_in_region(region, positive)
    negative_in_region = sum_in_region(region, negative)

    positive_out_region = positive_all - positive_in_region
    negative_out_region = negative_all - negative_in_region

    xbins, ybins = [round(num, 1) for num in xbins], [round(num, 1) for num in ybins]

    points = positive
    barlabel = "positive"
    visualizer(
        points,
        region.bot,
        region.top,
        region.l,
        region.r,
        y_bucket_num,
        x_bucket_num,
        column_y,
        column_x,
        barlabel,
        ybins,
        xbins,
    )

    points = negative
    barlabel = "negative"
    visualizer(
        points,
        region.bot,
        region.top,
        region.l,
        region.r,
        y_bucket_num,
        x_bucket_num,
        column_y,
        column_x,
        barlabel,
        ybins,
        xbins,
    )

    create_bar_chart(
        positive_all,
        negative_all,
        "Original Data Distribution",
    )

    create_bar_chart(
        positive_in_region,
        negative_in_region,
        "Data Distribution inside the Region",
    )
    create_bar_chart(
        positive_out_region,
        negative_out_region,
        "Data Distribution outside the Region",
    )


def compute_region(
    df,
    column_x,
    column_y,
    x_bucket_num=10,
    y_bucket_num=10,
    objective_column="Predicted",
    x_round=1,
    y_round=1,
):
    # x_bucket_num = len(df[column_x].unique())
    df["x_Bin"] = df[column_x]
    while x_bucket_num > 0:
        try:
            df["x_Bin"], xbins = pd.qcut(df[column_x], q=x_bucket_num, retbins=True)
            break
        except ValueError:
            x_bucket_num -= 1
            continue

    # y_bucket_num = len(df[column_y].unique())
    df["y_Bin"] = df[column_y]
    while y_bucket_num > 0:
        try:
            df["y_Bin"], ybins = pd.qcut(df[column_y], q=y_bucket_num, retbins=True)
            break
        except ValueError:
            y_bucket_num -= 1
            continue

    # 二次元タプルを初期化
    positive = [[0] * y_bucket_num for _ in range(x_bucket_num)]
    negative = [[0] * y_bucket_num for _ in range(x_bucket_num)]
    posandneg = [[0] * y_bucket_num for _ in range(x_bucket_num)]

    # objective_num 列が 1 と 0 の場合にデータを分割して集計
    # key=lambda x: x_custom_sort_order.index(x)は対象が文字列の時だけ書く
    for i, x_bin in enumerate(sorted(df["x_Bin"].unique().tolist())):
        for j, y_bin in enumerate(sorted(df["y_Bin"].unique().tolist())):
            subset = df[(df["x_Bin"] == x_bin) & (df["y_Bin"] == y_bin)]
            positive_count = len(subset[subset[objective_column] == 1])
            negative_count = len(subset[subset[objective_column] == 0])
            positive[i][j] = positive_count
            negative[i][j] = negative_count
            posandneg[i][j] = positive_count + negative_count

    result = (
        df.groupby(["x_Bin", "y_Bin", objective_column]).size().unstack(fill_value=0)
    )

    point, v, region = find_optimal_region(positive, negative)

    xbins, ybins = [round(num, x_round) for num in xbins], [
        round(num, y_round) for num in ybins
    ]
    return (
        df,
        region,
        v,
        xbins,
        ybins,
        positive,
        negative,
        posandneg,
        x_bucket_num,
        y_bucket_num,
    )


if __name__ == "__main__":
    main()

"""
# 'Outcome' 列が 1 と 0 の場合に分割して集計
result = df.groupby(["x_Bin", "Outcome"]).size().unstack(fill_value=0)

# タプルのリストを作成
result_tuples = [(index, row[1], row[0]) for index, row in result.iterrows()]

print(result_tuples[0])

# バケツから実際の範囲に変換する
lower_val, _ = result_tuples[0][0].left, result_tuples[0][0].right
_, upper_val = result_tuples[3][0].left, result_tuples[3][0].right
print("the range of bucket 0 to 3", "(", lower_val, upper_val, "]")


全ての組み合わせを試すには以下
column_list = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]
v_list = []
for i in range(len(column_list)):
    for j in range(len(column_list)):
        if i == j:
            continue
        column_x = column_list[i]
        column_y = column_list[j]
        x_bucket_num = 10
        y_bucket_num = 10
        while x_bucket_num > 0:
            try:
                df["x_Bin"], xbins = pd.qcut(df[column_x], q=x_bucket_num, retbins=True)
                break
            except ValueError:
                x_bucket_num -= 1
                continue

        while y_bucket_num > 0:
            try:
                df["y_Bin"], ybins = pd.qcut(df[column_y], q=y_bucket_num, retbins=True)
                break
            except ValueError:
                y_bucket_num -= 1
                continue

        objective_column = "Outcome"

        # 二次元タプルを初期化
        positive = [[0] * y_bucket_num for _ in range(x_bucket_num)]
        negative = [[0] * y_bucket_num for _ in range(x_bucket_num)]

        # objective_num 列が 1 と 0 の場合にデータを分割して集計
        # key=lambda x: x_custom_sort_order.index(x)は対象が文字列の時だけ書く
        for ii, x_bin in enumerate(sorted(df["x_Bin"].unique().tolist())):
            for jj, y_bin in enumerate(sorted(df["y_Bin"].unique().tolist())):
                subset = df[(df["x_Bin"] == x_bin) & (df["y_Bin"] == y_bin)]
                positive_count = len(subset[subset[objective_column] == 1])
                negative_count = len(subset[subset[objective_column] == 0])
                positive[ii][jj] = positive_count
                negative[ii][jj] = negative_count

        point, v, region = find_optimal_region(positive, negative)
        print("column_x:", column_x, "column_y:", column_y)
        print("エントロピー：", v)
        print("")
        v_list.append((column_x, column_y, v))

v_list.sort(key=lambda x: x[2])
print(v_list[:10])
Out: [('Age', 'Glucose', 0.5127452362273281), 
    ('Glucose', 'BMI', 0.515130279769151),
    ('BMI', 'Glucose', 0.5165017267492149), 
     ('Glucose', 'Age', 0.5167451646829311),
      ('Glucose', 'BloodPressure', 0.524783124932096),
     ('Glucose', 'DiabetesPedigreeFunction', 0.5369065024623783),
       ('Pregnancies', 'Glucose', 0.537696314321605), 
       ('Glucose', 'Pregnancies', 0.537696314321605), 
       ('BloodPressure', 'Glucose', 0.5390333472417089), 
       ('Age', 'BMI', 0.540477539689918)]
"""
