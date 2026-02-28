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
  page_title='Visão Entregadores',
  page_icon='🚚',
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

# =================================================================
#Inicio da estrutura lógica do código
# =================================================================

df = pd.read_csv('dataset/train.csv')

df1 = clean_code( df )


# =================================================================
# Barra lateral
# =================================================================
st.header( 'Marketplace - Visão Entregadores' )

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
    st.title( 'Overall Metrics' )
    col1, col2, col3, col4 = st.columns( 4, gap='large' )

    with col1:
      # st.subheader( 'Maior Idade' )
      maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
      col1.metric( 'Maior Idade', maior_idade )

    with col2:
      # st.subheader( 'Menor Idade' )
      menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
      col2.metric( 'Menor Idade', menor_idade )

    with col3:
      # st.subheader( 'Melhor Condição de Veiculos' )
      melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
      col3.metric( 'Melhor Condição', melhor_condicao )

    with col4:
      # st.subheader( 'Pior Condição de Veiculos' )
      pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
      col4.metric( 'Pior Condição', pior_condicao )

  with st.container():
    st.markdown( """---""" )
    st.title( 'Avaliações' )

    col1, col2 = st.columns( 2, gap='large' )

    with col1:
      st.markdown( '##### Avaliação Média por Entregador' )
      cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
      df_avg_rating_per_deliver = df1.loc[:, cols].groupby( 'Delivery_person_ID' ).mean().reset_index().round(2)
      st.dataframe( df_avg_rating_per_deliver )

    with col2:
      st.markdown( '##### Avaliação Média por Trânsito' )
      cols = ['Delivery_person_Ratings', 'Road_traffic_density']
      df_avg_rating_by_traffic = df1.loc[:, cols].groupby(['Road_traffic_density'])['Delivery_person_Ratings'].agg(['mean', 'std']).reset_index().round(2)
      st.dataframe( df_avg_rating_by_traffic )

      st.markdown( '##### Avaliação Média por Clima' )
      cols = ['Delivery_person_Ratings', 'Weatherconditions']
      df_avg_rating_by_weather = df1.loc[:, cols].groupby(['Weatherconditions'])['Delivery_person_Ratings'].agg(['mean', 'std']).reset_index().round(2)
      st.dataframe( df_avg_rating_by_weather )

  with st.container():
    st.markdown( """---""" )
    st.title( 'Velocidade de Entrega' )

    col1, col2 = st.columns( 2, gap='large' )

    with col1:
      st.markdown( '##### Top Entregadores mais Rápidos' )
      df3 = top_delivers( df1, top_asc=True )
      st.dataframe( df3 )

    with col2:
      st.markdown( '##### Top Entregadores mais Lentos' )
      df3 = top_delivers( df1, top_asc=False )
      st.dataframe( df3 )
