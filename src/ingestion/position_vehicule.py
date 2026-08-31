#script de premier contact avec le flux

#url : https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position

#je fait un appel avec des timeout determinés pour ne pas bloquer le script si le flux est indisponible
import requests
import time
import pandas as pd
from datetime import datetime
from google.transit import gtfs_realtime_pb2  #on importe le module gtfs-realtime-bindings pour décoder le flux binaire 
                                                #C'est cet objet là que le reseau de transport utilise pour encoder les données du flux GTFS-RT

#je fais un appel à l'API pour récupérer les données du flux GTFS-RT
#le flux est servi en Protocol Buffers (binaire), pas en JSON : il faut le décoder avec gtfs-realtime-bindings



#j'ajoute aussi un user-agent pour éviter d'être bloqué par le serveur distant
headers = {
    "User-Agent": "Projet Pipeline Mobilités Réseau - Étudiant"
}
def get_vehicle_positions():
    url = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"
    try:
        response = requests.get(url, timeout=5, headers=headers)  # Timeout de 5 secondes
        response.raise_for_status()  # Vérifie si la requête a réussi
        feed = gtfs_realtime_pb2.FeedMessage() # Initialisation de l'objet FeedMessage
        feed.ParseFromString(response.content) # Parse le contenu binaire de la réponse dans l'objet FeedMessage
        return feed
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API : {e}")
        return None


#fonction pour convertir le flux GTFS-RT en DataFrame pandas
def feed_to_dataframe(feed):
    rows = []
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue
        vehicle = entity.vehicle
        rows.append({
            "entity_id": entity.id,
            "vehicle_id": vehicle.vehicle.id,
            "trip_id": vehicle.trip.trip_id,
            "route_id": vehicle.trip.route_id,
            "latitude": vehicle.position.latitude,
            "longitude": vehicle.position.longitude,
            "bearing": vehicle.position.bearing,
            "speed": vehicle.position.speed,
            "current_stop_sequence": vehicle.current_stop_sequence,
            "stop_id": vehicle.stop_id,
            "vehicle_timestamp": vehicle.timestamp,
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # Boucle pour récupérer les données toutes les 10 secondes
    while True:
        feed = get_vehicle_positions()
        if feed is not None:
            # Convertir les données en DataFrame pandas
            df = feed_to_dataframe(feed)
            # Ajouter un horodatage pour savoir quand les données ont été récupérées
            df['timestamp'] = datetime.now()
            print(df.head())  # Affiche les premières lignes du DataFrame
        else:
            print("Aucune donnée récupérée.")

        time.sleep(10)  # Attendre 10 secondes avant la prochaine récupération


