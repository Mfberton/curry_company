#Libraries
from haversine import haversine
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
  page_title='Visão Restaurantes',
  page_icon='🍽️',
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

def top_delivers( df1, top_asc ):
  cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
  cities = df1['City'].unique()
  df_filtered_cities = df1.loc[df1['City'].isin(cities), cols]
  df2 = df_filtered_cities.groupby( ['City', 'Delivery_person_ID'] ).max().reset_index()
  df2 = df2.sort_values( ['City', 'Time_taken(min)'], ascending=top_asc )
  df3 = df2.groupby('City').head(10)
  return df3

def distance(df1, fig):
  if fig == False:
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df1['distance'] = df1.loc[:, cols].apply( lambda x:
                          haversine(
                              (x['Restaurant_latitude'], x['Restaurant_longitude']),
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
    avg_distance = df1['distance'].mean().round(2)
    return avg_distance

  else:
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x:
                          haversine(
                              (x['Restaurant_latitude'], x['Restaurant_longitude']),
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
    fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0]) ] )
    return fig

def avg_std_time_delivery( df1, festival, op ):
  """
    Esta Função calculao tempo médio e o desvio padrão do tempo de entrega.
    Parametros:
      Input:
      - df: Dataframe com os dados necessários para o cálculo
      - festival: Tipo de festival (Yes ou No)
      - op: Tipo de operação (mean ou std)
    Output:
      - df: Dataframe com 2 colunas e 1 linha.
  """
  cols = ['Time_taken(min)', 'Festival']
  df_aux = df1.loc[:, cols].groupby( ['Festival'] )['Time_taken(min)'].agg( ['mean', 'std'] ).reset_index().round(2)
  linhas_selecionadas = df_aux['Festival'] == festival
  df_aux = df_aux.loc[linhas_selecionadas, op]
  return df_aux

def avg_std_time_graph( df1 ):
  cols = ['City', 'Time_taken(min)']
  df_aux = df1.loc[:, cols].groupby( ['City'] )['Time_taken(min)'].agg( ['mean', 'std'] ).reset_index().round(2)
  fig = go.Figure()
  fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['mean'], error_y=dict( type='data', array=df_aux['std'] ) ) )
  fig.update_layout( barmode='group' )
  return fig

def avg_std_time_on_traffic(df1):
  cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
  df_aux = df1.loc[:, cols].groupby( ['City', 'Road_traffic_density'] )['Time_taken(min)'].agg( ['mean', 'std'] ).reset_index().round(2)
  fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='mean', color='std', color_continuous_scale='RdBu', color_continuous_midpoint=px.np.average( df_aux['std'] ) )
  return fig

# =================================================================
#Inicio da estrutura lógica do código
# =================================================================

df = pd.read_csv('dataset/train.csv')

df1 = clean_code( df )


# =================================================================
# Barra lateral
# =================================================================
st.header( 'Marketplace - Visão Restaurante' )

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

weather_conditions_options = list(df1['Weatherconditions'].unique())

Weather_options = st.sidebar.multiselect(
    'Quais as condições do clima',
    weather_conditions_options,
    default=weather_conditions_options )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

#Filtro de datas
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin( Weather_options )
df1 = df1.loc[linhas_selecionadas, :]

# =================================================================
# Layout do Streanlit
# =================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''] )

with tab1:
  with st.container():
    st.title( 'Overal Metrics' )

    col1, col2, col3, col4, col5, col6 = st.columns( 6 )

    with col1:
      delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
      col1.metric( 'Entregadores únicos', delivery_unique )

    with col2:
      avg_distance = distance( df1, fig=False )
      col2.metric( 'Distância média das entregas', avg_distance )

    with col3:
      df_aux = avg_std_time_delivery( df1, 'Yes', 'mean' )
      col3.metric( 'tempo médio de entrega c/ festival', df_aux )

    with col4:
      df_aux = avg_std_time_delivery( df1, 'Yes', 'std' )
      col4.metric( 'desvio padrão do tempo de entrega c/ festival', df_aux )

    with col5:
      df_aux = avg_std_time_delivery( df1, 'No', 'mean' )
      col5.metric( 'tempo médio de entrega c/ festival', df_aux )

    with col6:
      df_aux = avg_std_time_delivery( df1, 'No', 'std' )
      col6.metric( 'desvio padrão do tempo de entrega c/ festival', df_aux )

  with st.container():
    st.markdown( """---""" )

    col1, col2 = st.columns( 2 )

    with col1:
      fig = avg_std_time_graph( df1 )
      st.plotly_chart( fig, use_container_width=True, key='bar_time_by_city' )

    with col2:
      cols = ['City', 'Time_taken(min)', 'Type_of_order']
      df_aux = df1.loc[:, cols].groupby( ['City', 'Type_of_order'] )['Time_taken(min)'].agg( ['mean', 'std'] ).reset_index().round(2)
      st.dataframe( df_aux )

  with st.container():
    st.markdown( """---""" )
    st.title( 'Distribuição do tempo' )

    col1, col2 = st.columns( 2 )

    with col1:
      fig = distance( df1, fig=True )
      st.plotly_chart( fig, use_container_width=True, key='bar_avg_distance_by_city' )

    with col2:
      fig = avg_std_time_on_traffic( df1 )
      st.plotly_chart( fig, use_container_width=True, key='sunburst_time_by_city_traffic' )
