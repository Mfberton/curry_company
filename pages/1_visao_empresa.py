#Libraries
# from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessarias
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(
  page_title='Visão Empresa',
  page_icon='📈',
  layout='wide'
)

# =================================================================
#Funções
# =================================================================
def clean_code( df1 ):
  """ Esta função tem a responsabilidade de limpar o dataframe
      Tipos de limpeza:
      1. Remoção dos dados NaN
      2. Mudança do tipo da coluna de dados
      3. Remoção dos espaços dentro de strings/texto/object
      4. Formatação da coluna de datas
      5. Limpeza da coluna de tempo ( remoção do texto e conversão para número )
      Input: Dataframe
      Output: Dataframe
  """
  # Excluir as linhas com a idade dos entregadores vazia
  # ( Conceitos de seleção condicional )
  linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
  df1 = df1.loc[linhas_vazias, :].copy()

  linhas_vazias = df1['Road_traffic_density'] != 'NaN '
  df1 = df1.loc[linhas_vazias, :].copy()

  linhas_vazias = df1['City'] != 'NaN '
  df1 = df1.loc[linhas_vazias, :].copy()

  linhas_vazias = df1['Festival'] != 'NaN '
  df1 = df1.loc[linhas_vazias, :].copy()


  # Conversao de texto/categoria/string para numeros inteiros
  df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

  # Conversao de texto/categoria/strings para numeros decimais
  df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

  # Conversao de texto para data
  df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

  #
  linhas_vazias = df1['multiple_deliveries'] != 'NaN '
  df1 = df1.loc[linhas_vazias, :]
  df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

  # removendo os espaços dentro de strings/texto/object
  df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
  df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
  df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
  df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
  df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
  df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

  # Limpando a coluna de time taken
  df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.split(' ').str[1]
  # df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
  df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

  return df1

def order_metric( df1 ):
  df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
  df_aux.columns = ['order_date', 'qtde_entregas']
  # gráfico
  fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
  return fig


def traffic_order_share( df1 ):
  columns = ['ID', 'Road_traffic_density']
  df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()

  df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
  df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )

  fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
  return fig

def traffic_order_city( df1 ):
  columns = ['ID', 'City', 'Road_traffic_density']
  df_aux = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()

  df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
  fig = px.scatter( df_aux, x='City', y='Road_traffic_density', color='City', size='ID')
  return fig

def order_by_week( df1 ):
  df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
  df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
  # gráfico
  fig = px.line( df_aux, x='week_of_year', y='ID' )
  return fig

def order_share_by_week( df1 ):
  df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
  df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
  df_aux = pd.merge( df_aux1, df_aux2, how='inner' )

  df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

  fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
  return fig

def country_maps( df1 ):
  columns = [ 'City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
  columns_groupby = ['City', 'Road_traffic_density']
  data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
  # Desenhar o mapa
  map_ = folium.Map( zoom_start=11 )

  for index, location_info in data_plot.iterrows():
    folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )

  folium_static( map_, width=1024, height=600 )

# =================================================================
#Inicio da estrutura lógica do código
# =================================================================

df = pd.read_csv('dataset/train.csv')

df1 = clean_code( df )


# =================================================================
# Barra lateral
# =================================================================
st.header( 'Marketplace - Visão Cliente' )

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )

st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),

    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

#Filtro de datas
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# =================================================================
# Layout do Streanlit
# =================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
  with st.container():
    # Order Metric
    st.markdown( '# Quantidade de pedidos por dia' )
    fig = order_metric( df1 )
    st.plotly_chart( fig, use_container_width=True, key='bar_orders_by_day' )

  with st.container():
    col1, col2 = st.columns( 2 )
    with col1:
        st.markdown( '# Distribuição dos pedidos por tipo de tráfego' )
        fig = traffic_order_share( df1 )
        st.plotly_chart( fig, use_container_width=True, key='pie_traffic_distribution' )

    with col2:
        st.markdown( '## Comparação do volume de pedidos por cidade e tipo de tráfego' )
        fig = traffic_order_city( df1 )
        st.plotly_chart( fig, use_container_width=True, key='scatter_city_traffic' )

with tab2:
  with st.container():
    st.markdown( '# Pedidos por semana' )
    fig = order_by_week( df1 )
    st.plotly_chart( fig, use_container_width=True, key='line_orders_by_week' )

  with st.container():
    st.markdown( '# Pedidos por entregador por semana' )
    fig = order_share_by_week( df1 )
    st.plotly_chart( fig, use_container_width=True, key='line_orders_by_delivery' )

with tab3:
  st.markdown( '# Pedidos por cidade' )
  country_maps( df1 )
