import pandas as pd

csv_path = r"C:\Users\BrunoSoda\Documents\Scripts Python\magic_formula\apps\magic_formula_nyse_07012026.csv"

df = pd.read_csv(csv_path)

# Criar colunas de rank
df['rank_EY'] = df['EY'].rank(ascending=False)
df['rank_ROC'] = df['ROC'].rank(ascending=False)

# Score final
df['score'] = df['rank_EY'] + df['rank_ROC']

# Out / In (critério Joel Greenblatt)
df['out_in'] = df.apply(
    lambda row: 'out' if row['EBIT'] <= 0 or row['EV'] <= 0 else 'in',
    axis=1
)

# Ordenar: primeiro os válidos ("in"), depois pelo score
df_sorted = df.sort_values(by=['out_in', 'score']).reset_index(drop=True)

# Salvar ranking
output_path = r"C:\Users\BrunoSoda\Documents\Scripts Python\magic_formula\apps\ranking_magic_formula_nyse.csv"
df_sorted.to_csv(output_path, index=False)

print(df_sorted.head(20))
