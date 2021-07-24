"""
Skript vytvářející nový csv soubor, který rozšiřuje vstupní soubor o nové sloupce, získané "dekumulaci" daných kumulovaných sloupců.
Například sloupec "pocet_nakazenych" se získá ze slopce "kumulativni_pocet_nakazenych" tak, že:
- pocet_nakazenych[0] := kumulativni_pocet_nakazenych[0]
- pocet_nakazenych[n] := kumulativni_pocet_nakazenych[n] - kumulativni_pocet_nakazenych[n-1], kde 0 < n <= celkový počet řádek

(pocet_nakazenych[n] znamená n-tá řádka sloupce "pocet_nakazenych")
"""

import pandas as pd

df = pd.read_csv('logstash\datasets\kraj-okres-nakazeni-vyleceni-umrti.csv')

okres_df_dict = {}
for okres in df['okres_lau_kod'].unique():
    okres_df_dict[okres] = df.loc[df['okres_lau_kod'] == okres].reset_index().drop(columns=['index'])
    okres_df_dict[okres]['index'] = okres_df_dict[okres].apply(lambda row: row.name, axis=1)

def uncummulate(row, column_name):
    okres_df = okres_df_dict[row['okres_lau_kod']]
    okres_row = okres_df.loc[okres_df['datum'] == row['datum']]
    if int(okres_row['index']) == 0:
        return int(row[column_name])
    else:
        okres_row_prev = okres_df.loc[okres_df['index'] == int(okres_row['index']) - 1]
        return int(okres_row[column_name]) - int(okres_row_prev[column_name])

df['pocet_nakazenych'] = df.apply(lambda row: uncummulate(row, 'kumulativni_pocet_nakazenych'), axis=1)
df['pocet_vylecenych'] = df.apply(lambda row: uncummulate(row, 'kumulativni_pocet_vylecenych'), axis=1)
df['pocet_umrti'] = df.apply(lambda row: uncummulate(row, 'kumulativni_pocet_umrti'), axis=1)

df.to_csv('logstash\datasets\kraj-okres-nakazeni-vyleceni-umrti-extended.csv', index=False)
