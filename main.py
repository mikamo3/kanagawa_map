import folium
from folium.plugins import HeatMap
import pandas as pd


def import_data(s: str):
    years = ['2018', '2019', '2020', '2021']
    d = [pd.read_csv(
        "./data/kanagawa_"+year+s+".csv") for year in years]
    return pd.concat(d).loc[:, ['市区町村（発生地）', '町丁目（発生地）', '手口']]


def convert_data(df: pd.DataFrame):

    df = df.rename(columns={'市区町村（発生地）': '市区町村名', '町丁目（発生地）': '大字・丁目名'})
    df = df.groupby(['市区町村名', '大字・丁目名']).size().reset_index(name='counts')
    df = pd.merge(df, data_lat_lon)
    return df


def make_layer(df: pd.DataFrame, target: str,):
    group = folium.FeatureGroup(name=target)

    folium.plugins.HeatMap(
        data=[[row['緯度'], row['経度'], row['counts']]
              for idx, row in convert_data(df.query('手口 =="'+target+'"')).iterrows()],
        radius=7, blur=5
    ).add_to(group)
    return group


data_lat_lon = pd.read_csv(
    "./data/14_2021.csv"
)

data_lat_lon = data_lat_lon[['市区町村名', '大字・丁目名', '緯度', '経度']]

conv_table = [["一", "１"], ["二", "２"], ["三", "３"],
              ["四", "４"], ["五", "５"], ["六", "６"],
              ["七", "７"], ["八", "８"], ["九", "９"]]

for conv in conv_table:
    data_lat_lon['大字・丁目名'] = data_lat_lon["大字・丁目名"].str.replace(
        conv[0]+"丁目", conv[1]+"丁目")


m = folium.Map(location=[35.532161806053644, 139.6973609301159], zoom_start=10)

data_hittakuri = import_data('hittakuri')
data_syazyou = import_data('syazyounerai')
data_buhin = import_data('buhinnerai')
data_zidouhanbaiki = import_data('zidouhanbaikinerai')
data_ootobaitou = import_data('ootobaitou')
data_zidousyatou = import_data('zidousyatou')
data_zitensyatou = import_data('zitensyatou')

data = pd.concat([data_hittakuri, data_syazyou, data_buhin,
                 data_zidouhanbaiki, data_ootobaitou, data_zidousyatou, data_zitensyatou])

make_layer(data, 'ひったくり').add_to(m)
make_layer(data, '車上ねらい').add_to(m)
make_layer(data, '部品ねらい').add_to(m)
make_layer(data, '自動販売機ねらい').add_to(m)
make_layer(data, '自動車盗').add_to(m)
make_layer(data, 'オートバイ盗').add_to(m)
make_layer(data, '自転車盗').add_to(m)
folium.LayerControl().add_to(m)
m.save('output.html')
