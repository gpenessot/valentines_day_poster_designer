import datetime
import io
import warnings

# import os
import cv2
import folium
import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Temporarily suppress all warnings
warnings.filterwarnings("ignore")

API_KEY = st.secrets["token"]
URL = "https://api-adresse.data.gouv.fr/search/?q="
TILE_URL = "https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png?api_key=" + str(API_KEY)
ICON_PATH = "assets/heart.png"

# Paramètres poster
A3_WIDTH = 3508
A3_HEIGHT = 4961
MASK_RADIUS = 1500
MAP_RADIUS = 3200
FONT_1 = ImageFont.truetype("assets/Fashion Script.otf", 650)
FONT_2 = ImageFont.truetype("assets/CaviarDreams.ttf", 160)
ICON = folium.features.CustomIcon(ICON_PATH, icon_size=(120, 120))

st.sidebar.header("Générateur de poster St Valentin")
name1 = st.sidebar.text_input("Prénom 1", "Roméo")
name2 = st.sidebar.text_input("Prénom 2", "Juliette")
date_meet = st.sidebar.date_input(
    "Date de rencontre", datetime.date.today(), format="DD/MM/YYYY"
)
address = st.sidebar.text_input("Lieu de recontre", "Paris")
generate_button = st.sidebar.button("Générer le poster")

if generate_button:
    with st.spinner(text="Création en cours..."):
        with requests.Session() as session:
            r = session.get(URL + "{}".format(address.replace(" ", "+")))
            coords = tuple(r.json()["features"][0]["geometry"]["coordinates"])

        # Create a map centered at the coordinates
        map_ = folium.Map(
            location=[coords[1], coords[0]],
            width=MAP_RADIUS,
            height=MAP_RADIUS,
            tiles=TILE_URL,
            attr="made in python with love <3",
            zoom_start=17,
        )

        # Add a marker for the location
        folium.Marker([coords[1], coords[0]], icon=ICON).add_to(map_)

        # Display the map in the Streamlit app
        # folium_static(map_)
        img_data = map_._to_png()
        img = Image.open(io.BytesIO(img_data))
        img = np.array(img)
        center = (img.shape[1] // 2, img.shape[0] // 2)

        # Create a mask with the same dimensions as the image, initially all zeros (black)
        mask = np.zeros_like(img)

        # Draw a filled white circle in the mask at the center with the given radius
        cv2.circle(mask, center, MASK_RADIUS, (255, 255, 255), -1)

        # Invert the mask to get a black circle on a white background
        inverted_mask = cv2.bitwise_not(mask)

        # Apply the inverted mask to the original image
        result = cv2.bitwise_and(img, mask)
        result += inverted_mask

        image_originale = Image.fromarray(result)  # Image.open('cropped_circle_image.jpg')

        # Créer une nouvelle image avec une hauteur de 2000 et une largeur de 1000
        nouvelle_image = Image.new("RGB", (A3_WIDTH, A3_HEIGHT), color="white")

        # Coller l'image originale dans la partie haute de la nouvelle image
        nouvelle_image.paste(image_originale, (int((A3_WIDTH - 3200) / 2), 100))

        # Ajouter un titre dans la partie basse de la nouvelle image
        draw = ImageDraw.Draw(nouvelle_image)

        texte1 = f"{name1} & {name2}"
        texte2 = f"{date_meet.strftime('%d/%m/%Y')}\n\n{coords[1]}, {coords[0]}"

        _, _, font_width1, font_height1 = FONT_1.getbbox(texte1)
        new_width1 = (A3_WIDTH - font_width1) / 2
        new_height1 = (A3_HEIGHT - font_height1) / 2

        font_width2, font_height2 = FONT_2.getsize_multiline(texte2)
        new_width2 = (A3_WIDTH - font_width2) / 2
        new_height2 = (A3_HEIGHT - font_height2) / 2

        draw.text(
            (new_width1, A3_HEIGHT * 5 / 7 - 300),
            texte1,
            fill="black",
            font=FONT_1,
            align="center",
        )
        draw.text(
            (new_width2, A3_HEIGHT * 5 / 7 + 500),
            texte2,
            fill="black",
            font=FONT_2,
            align="center",
        )
        col1, col2 = st.columns([2, 1])

        with col1:
            st.image(nouvelle_image, 
                     width=500, 
                     caption='Image générée', 
                     use_column_width=True)

        with col2:
            image_bytes_io = io.BytesIO()
            nouvelle_image.save(
                image_bytes_io, format="PNG"
            )  # You can change the format as needed
            image_bytes = image_bytes_io.getvalue()
            buffered_reader = io.BytesIO(image_bytes)

            # Export button
            export_button = st.download_button(
                label="Télécharger image",
                data=buffered_reader,
                file_name="poster.png",
                mime="image/png",
            )

        st.markdown("---")
        st.markdown("Made with 💘 & 🐍 | [Gaël Penessot](https://www.linkedin.com/in/gael-penessot/) | [data-decision.io](https://data-decision.io/)")
        