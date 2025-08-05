import streamlit as st
import pandas as pd
import plotly.express as px
import random
import requests
from PIL import Image
from io import BytesIO
import plotly.graph_objects as go

st.sidebar.image("https://blog.logomyway.com/wp-content/uploads/2021/05/pokemon-logo-png.png", width=300)

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


# Define type colors for Pokemon type
type_colors = {
    "Grass": "#78C850",
    "Poison": "#A040A0",
    "Fire": "#F08030",
    "Water": "#6890F0",
    "Electric": "#F8D030",
    "Psychic": "#F85888",
    "Normal": "#A8A878",
    "Ground": "#E0C068",
    "Flying": "#A890F0",
    "Bug": "#A8B820",
    "Rock": "#B8A038",
    "Ghost": "#705898",
    "Ice": "#98D8D8",
    "Dragon": "#7038F8",
    "Dark": "#705848",
    "Steel": "#B8B8D0",
    "Fairy": "#EE99AC"
}

st.sidebar.title("Pokémon Options")

# Add some explanatory text
st.sidebar.markdown("Choose a Pokémon manually or generate one randomly.")


# Input box for Pokémon number
pokemon_number_input = st.sidebar.number_input(
    f"Enter a Pokémon number ({get_min_value('pokedex_number')}–{get_max_value('pokedex_number')})",
    min_value=get_min_value('pokedex_number'),
    max_value=get_max_value('pokedex_number'),
    step=1,
    value=None) #making sure that no image is rendered before user input


# Button to generate a random Pokémon number
if st.sidebar.button("Generate Random Pokémon", use_container_width=True):
    pokemon_number_input = random.randint(get_min_value('pokedex_number'), get_max_value('pokedex_number'))



# Display pokemon image based on user input
if pokemon_number_input is not None:
    
    # Fetch the image
    response = requests.get(generate_link(base_url,(input_handle(pokemon_number_input))))
    image = Image.open(BytesIO(response.content))

    # Assume this returns multiple rows
    pokemon_row = df[df['pokedex_number'] == pokemon_number_input]

    # Take only the first matching row
    first_pokemon = pokemon_row.iloc[0]
    
    st.header(first_pokemon['name'].title())
    
    st.markdown("""
    <hr style="border: 1px solid #ccc; margin: 20px 0;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])  # 25%, 12.5%, 62.5%
    
    # Column 1: Name and Image
    with col1:
        #st.header(first_pokemon['name'].title())
        st.image(image)

    # Column 2: Type, Height, Weight
    with col2:
        st.subheader("Type")
        
        # Example: types as a list (in case more than 1)
        types = [first_pokemon['type_1']]
        if first_pokemon['type_number'] == 2 and pd.notna(first_pokemon['type_2']): # In case there is more than one type
            types.append(first_pokemon['type_2']) 

        # Generate styled buttons for each type
        styled_types = ""
        for t in types:
            color = type_colors.get(t.title(), "#CCCCCC")
            styled_types += f"""
            <span style="
                display: inline-block;
                background-color: {color};
                color: white;
                padding: 0.3em 0.8em;
                margin-right: 0.5em;
                border-radius: 10px;
                font-weight: bold;
                font-size: 0.9em;
            ">
                {t.title()}
            </span>
            """

        # Display it
        st.markdown(styled_types, unsafe_allow_html=True)

        # Show stats
        st.subheader("Stats")
        st.metric("Height", f"{first_pokemon['height_m']} m")
        st.metric("Weight", f"{first_pokemon['weight_kg']} kg")

    # Column 3: Species and Abilities
    with col3:
        st.subheader("Species")
        st.markdown(f"**{first_pokemon['species']}**")

        st.subheader("Abilities")
        abilities = []
        if first_pokemon['ability_1']:
            abilities.append(first_pokemon['ability_1'])
        if pd.notna(first_pokemon['ability_2']) and first_pokemon['ability_2']:
            abilities.append(first_pokemon['ability_2'])
        if pd.notna(first_pokemon['ability_hidden']) and first_pokemon['ability_hidden']:
            abilities.append(f"{first_pokemon['ability_hidden']} *(Hidden)*")

        for ability in abilities:
            st.markdown(f"- {ability}")

    st.markdown("""
    <hr style="border: 1px solid #ccc; margin: 20px 0;">
    """, unsafe_allow_html=True)
    
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
        title="Height vs weight of All Pokémon"
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
        title=f"{selected_pokemon['name']} Effectiveness Against Each Type:",
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
    
    # Sample 19 random Pokémon 
    sample_df = df.sample(19)

    # Add the selected Pokémon to the sample
    hp_comparison_df = pd.concat([sample_df, df[df['pokedex_number'] == selected_number]])

    # Sort by value
    hp_comparison_df = hp_comparison_df.sort_values(by='hp', ascending=False)
    
    # Highlight the selected Pokémon
    colors = ['#e74c3c' if pid == selected_number else '#FFCB05' for pid in hp_comparison_df['pokedex_number']]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
    x=hp_comparison_df['name'],
    y=hp_comparison_df['hp'],
    marker_color=colors,
    name='HP'
    ))

    fig3.update_layout(
        barmode='group',
        title='HP Comparison: Selected Pokémon vs 19 Random Others',
        xaxis_title='Pokémon',
        yaxis_title='HP',
        xaxis_tickangle=-45,
        showlegend=False
    )

    st.plotly_chart(fig3)