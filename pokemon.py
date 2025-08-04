import streamlit as st
import pandas as pd
import plotly.express as px
import random
import requests
from PIL import Image
from io import BytesIO

# Set the title of the app
st.title("Pokemon App (Team 2)")

# Load data
df = pd.read_csv("pokemon.csv")

# Define URL and extension
base_url = "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/"
im_ext = ".png"

# F to generate a link based on user input
def generate_link (base_url, pokedex):
    return base_url + pokedex + im_ext

# F to generate str from int input
def input_handle (input):
    if input < 10:
        return "00" + str(input)
    elif input < 100:
        return "0" + str(input)
    else:
        return str(input)

# F to get lowest valid input
def get_min_value(column_name):
    return df[column_name].min()

# F to get highest valid input
def get_max_value(column_name):
    return df[column_name].max()


# Create two columns
#col1, col2 = st.columns([1, 1])

#with col1:
# Input box for Pokémon number
st.write(f"Enter a Pokémon number ({get_min_value('pokedex_number')}–{get_max_value('pokedex_number')})")
pokemon_number_input = st.number_input(
    "",
    min_value=get_min_value('pokedex_number'),
    max_value=get_max_value('pokedex_number'),
    step=1,
    value=None) #making sure that no image is rendered before user input

#with col2:
# Button to generate a random Pokémon number
st.write("Or pick randomly")
st.write("")
if st.button("Generate Random Pokémon", use_container_width=True):
    pokemon_number_input = random.randint(get_min_value('pokedex_number'), get_max_value('pokedex_number'))

# Display pokemon image based on user input
if pokemon_number_input is not None:
    # Fetch the image
    response = requests.get(generate_link(base_url,(input_handle(pokemon_number_input))))
    image = Image.open(BytesIO(response.content))

    # Display in Streamlit
    st.image(image, width=300) # width in pixels / use_column_width=True can be used


    # Visualizations
    selected_number = pokemon_number_input
    pokemon = df[df['pokedex_number'] == selected_number].iloc[0]

    df['is_selected'] = df['pokedex_number'] == selected_number
    
    if pokemon['height_m'] > 12:
        max_height = 21
    else:
        max_height = 12

    # Scatter plot of all Pokémon
    fig1 = px.scatter(
        df,
        x='height_m',
        y='weight_kg',
        hover_name='name',
        color='is_selected',
        color_discrete_map={True: 'red', False: 'lightblue'},
        title="Height vs weight of all Pokémon"
    )

    fig1.add_annotation(
        x=pokemon['height_m'],
        y=pokemon['weight_kg'],
        text=pokemon['name'],
        showarrow=True,
        arrowhead=1,
        font=dict(color='black'),
        bgcolor='white'
    )
    
    
    fig1.update_layout(
        yaxis=dict(
            title = 'Weight (kg)',
            range=[0, (get_max_value('weight_kg')+100)]),
        xaxis=dict(
            title = 'Height (m)',
            range=[0, max_height]),
        showlegend=False
    )

    # Show the bar chart in Streamlit
    st.plotly_chart(fig1)


    # get against_ columns
    against_cols = [col for col in df.columns if col.startswith('against_')]

    selected_pokemon = df[df['pokedex_number'] == selected_number].iloc[0]

    # effectiveness dataframe
    effectiveness = pd.DataFrame({
        'type': [col.replace('against_', '') for col in against_cols],
        'effectiveness': [selected_pokemon[col] for col in against_cols]
    })

    # Sort by effectiveness
    effectiveness = effectiveness.sort_values('effectiveness', ascending=False)
    
    # Create color column based on effectiveness
    effectiveness['color'] = effectiveness['effectiveness'].apply(
        lambda x: 'green' if x > 1 else 'blue' if x == 1 else 'red'
    )
 
    # Plot bar chart
    fig2 = px.bar(
        effectiveness,
        x='effectiveness',
        y='type',
        orientation='h',
        title=f"{selected_pokemon['name']} effectiveness against each type:",
        color='color',  # Use the color column
        color_discrete_map={
            'green': '#2ecc71',
            'blue': '#add8e6',
            'red': '#e74c3c'
        },
        labels={'Effectiveness': 'Damage Multiplier'}
    )

    fig2.update_layout(
        yaxis=dict(
            title = 'Type'),
        xaxis=dict(
            title = 'Effectiveness'),
        showlegend=False
    )
    
    # Show the bar chart in Streamlit
    st.plotly_chart(fig2)