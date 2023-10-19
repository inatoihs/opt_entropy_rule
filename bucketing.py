import pandas as pd
from region_entropy import find_optimal_region, sum_in_region
from region_visualizer import visualizer, create_bar_chart

filename = "data/diabetes.csv"

# CSVファイルからデータを読み込む
df = pd.read_csv(filename)

column_x = "Age"
# x_bucket_num = len(df[column_x].unique())
x_bucket_num = 10
# df["x_Bin"] = df[column_x]
df["x_Bin"], xbins = pd.qcut(df[column_x], q=x_bucket_num, retbins=True)
x_custom_sort_order = ["Unhealthy", "Average", "Healthy"]

column_y = "BMI"
# y_bucket_num = len(df[column_y].unique())
y_bucket_num = 10
# df["y_Bin"] = df[column_y]
df["y_Bin"], ybins = pd.qcut(df[column_y], q=y_bucket_num, retbins=True)
y_custom_sort_order = ["Unhealthy", "Average", "Healthy"]

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


result = df.groupby(["x_Bin", "y_Bin", objective_column]).size().unstack(fill_value=0)

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

# グラフに表示するデータを決定
posneg = [positive, negative]
points = posneg[0]

if points == positive:
    barlabel = "positive"
elif points == negative:
    barlabel = "negative"

# objective_num列が1であるデータの数を数える
positive_all = (df[objective_column] == 1).sum()

# objective_num列が0であるデータの数を数える
negative_all = (df[objective_column] == 0).sum()

positive_in_region = sum_in_region(region, positive)
negative_in_region = sum_in_region(region, negative)

positive_out_region = positive_all - positive_in_region
negative_out_region = negative_all - negative_in_region

xbins, ybins = [round(num, 1) for num in xbins], [round(num, 1) for num in ybins]


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
"""
