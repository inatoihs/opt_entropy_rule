import codecs as cd
import pandas as pd

df=pd.read_csv('diabetes.csv')
df['BMI_Bin'] = pd.qcut(df['BMI'], q=10)



# 'Outcome' 列が 1 と 0 の場合に分割して集計
result = df.groupby(['BMI_Bin', 'Outcome']).size().unstack(fill_value=0)

# タプルのリストを作成
result_tuples = [(index, row[1], row[0]) for index, row in result.iterrows()]

print(result_tuples[0][0])

#バケツから実際の範囲に変換する
lower_val, _ = result_tuples[0][0].left, result_tuples[0][0].right
_, upper_val = result_tuples[3][0].left, result_tuples[3][0].right
print("the range of bucket 0 to 3", "(", lower_val, upper_val, "]") 