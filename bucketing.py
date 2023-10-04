import pandas as pd
from region_entropy import find_optimal_region

filename = "diabetes.csv"

# CSVファイルからデータを読み込む
df = pd.read_csv(filename)

column_x = "BMI"
x_bucket_num = 10
df["x_Bin"] = pd.qcut(df[column_x], q=x_bucket_num)

column_y = "Age"
y_bucket_num = len(df["Age"].unique())
df["y_Bin"] = df[column_y]

# 二次元タプルを初期化
positive = [[0] * y_bucket_num for _ in range(x_bucket_num)]
negative = [[0] * y_bucket_num for _ in range(x_bucket_num)]

# 'Outcome' 列が 1 と 0 の場合にデータを分割して集計
for i, x_bin in enumerate(sorted(df["x_Bin"].unique().tolist())):
    for j, y_bin in enumerate(sorted(df["y_Bin"].unique().tolist())):
        subset = df[(df["x_Bin"] == x_bin) & (df["y_Bin"] == y_bin)]
        positive_count = len(subset[subset["Outcome"] == 1])
        negative_count = len(subset[subset["Outcome"] == 0])
        positive[i][j] = positive_count
        negative[i][j] = negative_count


result = df.groupby(["x_Bin", "y_Bin", "Outcome"]).size().unstack(fill_value=0)

# タプルのリストを作成
result_tuples = [
    (index[0], index[1], row[1], row[0]) for index, row in result.iterrows()
]

# summary[i][j]にはx_Binがi番目のBinである範囲、y_Binがj番目のBinである範囲、
#'Outcome'が1であるデータ数、'Outcome'が０であるデータ数が格納されています。
summary = []

for i in range(x_bucket_num):
    summary.append(result_tuples[i * y_bucket_num : (i + 1) * y_bucket_num])

print(find_optimal_region(positive, negative))

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
