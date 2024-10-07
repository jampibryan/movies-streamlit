import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título de la aplicación
st.title('Aplicación de Películas')

# Cargar el dataset de películas
data = pd.read_csv('movies.csv')

# Imprimir el número de películas cargadas
st.write("Datos cargados:", data.shape[0], "películas.")

# Convertir 'release_date' a tipo datetime para manejar años fácilmente
data['release_date'] = pd.to_datetime(data['release_date'], errors='coerce')

# Eliminar filas con valores faltantes en la columna de fechas
data = data.dropna(subset=['release_date'])

# Convertir budget y revenue a numérico
data['budget'] = pd.to_numeric(data['budget'], errors='coerce')
data['revenue'] = pd.to_numeric(data['revenue'], errors='coerce')

# Eliminar películas donde el presupuesto y los ingresos son cero
data = data[(data['budget'] != 0) | (data['revenue'] != 0)]

# Añadir una columna 'year' para filtrar por año
data['year'] = data['release_date'].dt.year

# Filtro por año
años = data['year'].dropna().unique()
año_seleccionado = st.sidebar.selectbox("Selecciona un año:", sorted(años, reverse=True))

# Filtro por género
if 'genres' in data.columns:
    géneros = set([g.strip() for sublist in data['genres'].dropna().str.split(',') for g in sublist])
    género_seleccionado = st.sidebar.multiselect("Selecciona géneros:", sorted(géneros))
else:
    género_seleccionado = []

# Filtrar los datos por año
peliculas_filtradas = data[data['year'] == año_seleccionado]

# Filtrar por género
if género_seleccionado:
    peliculas_filtradas['genres'] = peliculas_filtradas['genres'].fillna('')  # Usar .loc para evitar SettingWithCopyWarning
    peliculas_filtradas = peliculas_filtradas[peliculas_filtradas['genres'].apply(lambda x: any(g in x for g in género_seleccionado))]

# Mostrar las películas filtradas
st.subheader(f"Películas del año {año_seleccionado} ({', '.join(género_seleccionado) if género_seleccionado else 'Todos los géneros'}):")
st.write(f"Número de películas filtradas: {len(peliculas_filtradas)}")  # Imprimir el número de películas
st.dataframe(peliculas_filtradas[['title', 'release_date', 'genres', 'vote_average', 'revenue']])

# Mostrar una película específica
if not peliculas_filtradas.empty:
    pelicula_seleccionada = st.selectbox("Selecciona una película para ver detalles:", peliculas_filtradas['title'])
    detalles = peliculas_filtradas[peliculas_filtradas['title'] == pelicula_seleccionada]
    st.subheader(f"Detalles de la película: {pelicula_seleccionada}")
    st.write(detalles)

    # Mostrar gráfica de presupuesto y ganancias de la película seleccionada
    if 'budget' in detalles.columns and 'revenue' in detalles.columns:
        st.subheader(f"Presupuesto y Ganancias de {pelicula_seleccionada}")
        
        presupuesto = detalles['budget'].values[0]
        ganancias = detalles['revenue'].values[0]
        
        # Crear un dataframe para la gráfica con el orden correcto
        presupuesto_ganancias = pd.DataFrame({
            'Monto ($)': [presupuesto, ganancias]
        }, index=['Presupuesto', 'Ganancias'])

        # Mostrar la gráfica de barras
        st.bar_chart(presupuesto_ganancias)

# Lista de películas donde el presupuesto es mayor que los ingresos
if not peliculas_filtradas.empty:
    peliculas_perdedoras = peliculas_filtradas[peliculas_filtradas['budget'] > peliculas_filtradas['revenue']]
    st.subheader("Películas con presupuesto mayor a ingresos:")
    st.write(f"Número de películas con presupuesto mayor a ingresos: {len(peliculas_perdedoras)}")
    st.dataframe(peliculas_perdedoras[['title', 'budget', 'revenue']])

# Gráfica: Comparación de ingresos (revenue) de las películas filtradas
if not peliculas_filtradas.empty:
    st.subheader("Comparación de ingresos:")
    
    # Filtrar las 10 películas con mayores ingresos
    top_peliculas_ingresos = peliculas_filtradas.sort_values(by='revenue', ascending=False).head(10)

    # Mostrar la gráfica de barras
    st.bar_chart(top_peliculas_ingresos.set_index('title')['revenue'])

# Gráfica: Las 10 películas más populares (vote_average)
if not peliculas_filtradas.empty:
    st.subheader("Las 10 películas más populares:")
    
    # Filtrar las 10 películas más populares
    top_peliculas_populares = peliculas_filtradas.sort_values(by='vote_average', ascending=False).head(10)

    # Crear un gráfico de barras horizontal
    plt.figure(figsize=(10, 6))
    plt.barh(top_peliculas_populares['title'], top_peliculas_populares['vote_average'], color='skyblue')
    plt.xlabel('Popularidad (vote_average)')
    plt.title('Las 10 películas más populares')
    plt.gca().invert_yaxis()  # Invertir el eje y para que la película más popular esté en la parte superior

    # Mostrar la gráfica
    st.pyplot(plt)
    plt.clf()  # Limpiar la figura para evitar sobreposiciones en futuras gráficas

# Mostrar los desarrolladores en la barra lateral
st.sidebar.markdown("### Desarrolladores:")
st.sidebar.markdown("- Bryan Amaya\n- Karen Perez")

#streamlit run movies.py
