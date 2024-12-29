import streamlit as st
import pandas as pd
import os
import plotly.express as px
from functools import lru_cache

# Configurer la page Streamlit
st.set_page_config(page_title="Dashboard Bonheur des Pays", layout="wide", initial_sidebar_state="expanded")

# Ajouter un en-tête
st.title("Dashboard World Happiness ")

# Chemin vers le dossier contenant les fichiers CSV
data_folder = 'archive'

# Définir le mapping des colonnes pour chaque dataset
column_mapping = {
    '2017': {
        'Happiness.Score': 'Happiness Score',
        'Economy..GDP.per.Capita.': 'Economy (GDP per Capita)',
        'Health..Life.Expectancy.': 'Health (Life Expectancy)',
        'Trust..Government.Corruption.': 'Trust (Government Corruption)',
        'Family': 'Family',
        'Freedom': 'Freedom',
        'Generosity': 'Generosity',
        'Country': 'Country'
    },
    '2018': {
        'Score': 'Happiness Score',
        'GDP per capita': 'Economy (GDP per Capita)',
        'Healthy life expectancy': 'Health (Life Expectancy)',
        'Perceptions of corruption': 'Trust (Government Corruption)',
        'Social support': 'Family',
        'Freedom to make life choices': 'Freedom',
        'Generosity': 'Generosity',
        'Country or region': 'Country'
    },
    '2019': {
        'Score': 'Happiness Score',
        'GDP per capita': 'Economy (GDP per Capita)',
        'Healthy life expectancy': 'Health (Life Expectancy)',
        'Perceptions of corruption': 'Trust (Government Corruption)',
        'Social support': 'Family',
        'Freedom to make life choices': 'Freedom',
        'Generosity': 'Generosity',
        'Country or region': 'Country'
    }
}

# Récupérer la liste des datasets disponibles
available_years = sorted([file.split('.')[0] for file in os.listdir(data_folder) if file.endswith('.csv')])

# Barre latérale : Sélection de l'année
st.sidebar.title("Filtres")
selected_year = st.sidebar.selectbox("Sélectionnez l'année :", available_years)

# Charger les données pour l'année sélectionnée
file_path = os.path.join(data_folder, f"{selected_year}.csv")
df = pd.read_csv(file_path)

# Appliquer le mapping des colonnes pour les années spécifiques
if selected_year in column_mapping:
    df.rename(columns=column_mapping[selected_year], inplace=True)

# Vérification des colonnes nécessaires
required_columns = ['Country', 'Happiness Score', 'Economy (GDP per Capita)', 'Family', 
                    'Health (Life Expectancy)', 'Freedom', 'Trust (Government Corruption)', 
                    'Generosity']
if not all(col in df.columns for col in required_columns):
    st.error("Le dataset sélectionné ne contient pas les colonnes nécessaires.")
else:
    # Afficher les données
    st.subheader(f"Données pour l'année {selected_year}")
    st.write(df.head())

    # KPI globaux
    average_happiness = df['Happiness Score'].mean()
    max_happiness = df.loc[df['Happiness Score'].idxmax()]
    min_happiness = df.loc[df['Happiness Score'].idxmin()]

    # Mettre les KPI dans des cartes élégantes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score Moyen de Bonheur", f"{average_happiness:.2f}")
    with col2:
        st.metric("Pays le Plus Heureux", max_happiness['Country'], f"Score: {max_happiness['Happiness Score']:.2f}")
    with col3:
        st.metric("Pays le Moins Heureux", min_happiness['Country'], f"Score: {min_happiness['Happiness Score']:.2f}")

    # Sélection d'un pays spécifique
    countries = df['Country'].unique()
    selected_country = st.sidebar.selectbox("Sélectionnez un pays :", sorted(countries))

    # Filtrer les données pour le pays sélectionné
    country_data = df[df['Country'] == selected_country]

    if country_data.empty:
        st.warning(f"Aucune donnée disponible pour {selected_country}.")
    else:
        st.subheader(f"Analyse pour {selected_country}")
        happiness_score = country_data['Happiness Score'].values[0]
        st.metric("Score de Bonheur", f"{happiness_score:.2f}")

        # Diagramme à barres des facteurs contribuant au bonheur
        factors = ['Economy (GDP per Capita)', 'Family', 'Health (Life Expectancy)',
                   'Freedom', 'Trust (Government Corruption)', 'Generosity']
        factors_data = country_data[factors].transpose().reset_index()
        factors_data.columns = ['Facteur', 'Contribution']
        fig_factors = px.bar(factors_data, x='Facteur', y='Contribution',
                             title=f"Facteurs contribuant au bonheur pour {selected_country}",
                             labels={'Contribution': 'Contribution au Score de Bonheur'},
                             color='Facteur', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_factors, use_container_width=True)

    # Carte des scores de bonheur
    st.subheader("Carte des Scores de Bonheur")
    fig_map = px.choropleth(
        df,
        locations="Country",
        locationmode="country names",
        color="Happiness Score",
        title="Carte des Scores de Bonheur par Pays",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Classement des Pays par Score de Bonheur
    st.subheader("Classement des Pays par Score de Bonheur")
    st.markdown("Voici le classement des pays selon leur Score de Bonheur pour l'année sélectionnée.")

    # Trier les pays par Score de Bonheur
    ranked_df = df[['Country', 'Happiness Score']].sort_values(by='Happiness Score', ascending=False)

    # Afficher les 10 premiers pays (classement global)
    top_n = st.slider("Nombre de pays à afficher :", min_value=5, max_value=10, value=10)
    st.write(ranked_df.head(top_n))

    # Visualisation du Classement
    fig_ranking = px.bar(
        ranked_df.head(top_n),
        x='Happiness Score',
        y='Country',
        orientation='h',  # Orientation horizontale pour une meilleure lisibilité
        title=f"Top {top_n} Pays par Score de Bonheur en {selected_year}",
        labels={'Happiness Score': 'Score de Bonheur', 'Country': 'Pays'},
        color='Happiness Score',
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig_ranking.update_layout(yaxis={'categoryorder': 'total ascending'})  # Classement ascendant
    st.plotly_chart(fig_ranking, use_container_width=True)

    # Distribution des Scores de Bonheur
    st.subheader("Distribution des Scores de Bonheur")
    fig_hist = px.histogram(
        df,
        x='Happiness Score',
        nbins=20,
        title="Distribution des Scores de Bonheur",
        labels={'Happiness Score': 'Score de Bonheur'},
        marginal='box',  # Ajouter une boîte à moustaches
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Corrélation entre les facteurs explicatifs
    st.subheader("Corrélation entre les facteurs explicatifs")
    selected_factors = st.multiselect(
        "Choisissez des facteurs à comparer avec le Score de Bonheur :",
        options=factors,
        default=factors[:2]
    )
    if selected_factors:
        fig_corr = px.scatter_matrix(
            df,
            dimensions=selected_factors,
            color="Happiness Score",
            title="Corrélations entre les Facteurs Sélectionnés",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_corr, use_container_width=True)