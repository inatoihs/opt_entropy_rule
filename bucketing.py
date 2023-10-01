import codecs as cd
import pandas as pd

df=pd.read_csv('diabetes.csv')
df['BMI_Bin'] = pd.qcut(df['BMI'], q=10)



# 'Outcome' 列が 1 と 0 の場合に分割して集計
result = df.groupby(['BMI_Bin', 'Outcome']).size().unstack(fill_value=0)

# タプルのリストを作成
result_tuples = [(index, row[1], row[0]) for index, row in result.iterrows()]

print(result_tuples)

#TODO: これに加えて、バケツから実際の範囲に変換する