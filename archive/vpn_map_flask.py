from flask import Flask, render_template_string
import folium
import geojson

app = Flask(__name__)

# Charger les données des pays
with open('countries.geojson', 'r', encoding='utf-8') as f:
    countries = geojson.load(f)

@app.route('/')
def index():
    # Créer une carte centrée sur le monde
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Ajouter des pays à la carte
    for feature in countries.features:
        country = feature['properties'].get('name', 'Unknown')
        geom = feature['geometry']

        # Ajouter un polygone pour chaque pays
        folium.GeoJson(
            geom,
            name=country,
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 1},
            tooltip=country
        ).add_to(m)

        # Ajouter un Popup avec un lien pour se connecter
        folium.Popup(f'<a href="/connect/{country}">Connect to {country}</a>').add_to(m)

    # Convertir la carte en HTML
    m.save('templates/map.html')
    return render_template_string(open('templates/map.html').read())

@app.route('/connect/<country>')
def connect(country):
    # Logique pour se connecter au pays
    return f"Connecting to {country}..."

if __name__ == '__main__':
    app.run(debug=True)
