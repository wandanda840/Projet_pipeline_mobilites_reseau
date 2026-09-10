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
def get_vehicle_positions(): # cette fonction retourne un objet FeedMessage contenant les positions des véhicules
    url = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"
    try:
        response = requests.get(url, timeout=5, headers=headers)  # Timeout de 5 secondes
        response.raise_for_status()  # Vérifie si la requête a réussi
        
        
        #je suavegarde la reponse en local 
        
        ts = datetime.now().strftime("%Y%m%dT%H%M%S") #pour l'horodatage du fichier
        filename = f"../../local_data/gtfs_rt_vehicle_positions_{ts}.pb"  # Nom du fichier avec horodatage
        
        
        with open(filename, "wb") as f:
            f.write(response.content)  # Écriture du contenu binaire dans le fichier
        print(f"Flux GTFS-RT sauvegardé dans le fichier : {filename}")
        
        #J'affiche le content type le content lenght et le content encoding pour vérifier que le flux est bien en binaire
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
        
        
        # #Je vérifie les entetes HTTP de validation de contenu client serveur
        
        # #j'affhiche aussi le LastMofified pour savoir quand le flux a été mis à jour pour la dernière fois
        # print(f"Last-Modified: {response.headers.get('Last-Modified')}")
        
        # #Etag
        # print(f"Etag: {response.headers.get('Etag')}")
        
        # #cache control
        # print(f"Cache-Control: {response.headers.get('Cache-Control')}")
        
        
        #je vérifie ce qui se passe quand je lis la reponse comme du texte
        #print(f"Response text: {response.text[:100]}")  # Affiche les 100 premiers caractères du texte de la réponse
        #effectivement c'est illisible car la réponse est un binaire
        
        
        
        feed = gtfs_realtime_pb2.FeedMessage() # initialisation de l'objet FeedMessage
        feed.ParseFromString(response.content) # je mets le contenu binaire de la réponse dans l'objet FeedMessage
        return feed
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API : {e}")
        return None


def get_vehicle_positions_from_file(filename): # cette fonction retourne un objet FeedMessage contenant les positions des véhicules
    try:
        with open(filename, "rb") as f:
            feed = gtfs_realtime_pb2.FeedMessage() # initialisation de l'objet FeedMessage
            feed.ParseFromString(f.read()) # je mets le contenu binaire du fichier dans l'objet FeedMessage
            return feed
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
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

    #liste des écarts calculés entre les horodatages STAR de deux appels successifs
    #et dernier horodatage vu
    horodatages_vehicules = []
    last_timestamp = None
    
    #En vue d'anticiper le dimensionnement du stockage je vais aussi quatifier la taille moyennes des appels successifs
    sizes = []
    initial_size = 0
    
    
    #je vais faire la jointure du df des voiture avec le df des trips car c'est comme ça que je peux avoir les horaires théoriques à coté des horaires temps réel
    #juste faire attention au GTFS statique que j'utilise
    
    
    # GTFS STATIQUE POUR COMPARAISON
    #son df
    df_trips = pd.read_csv("../../local_data/trips.txt", dtype="str")
    
    
    

    # Boucle pour récupérer les données toutes les 10 secondes
    while True:
        feed = get_vehicle_positions()

        if feed is not None:
            # Convertir les données en DataFrame pandas
            df_vehicules = feed_to_dataframe(feed)
            
            
            
            
            
            
            
            #Je suis en train de faire les jointure entre le vehicules et le trips
            
            
            df_jointure = df_vehicules.merge(
                df_trips,
                on="trip_id",
                how="left",
                indicator=True   # ça ajoute une colonne qui dit si la jointure a réussi
                )
            

            
            
            
            
            
            
            
            
            
            #calculd du volume de l'appel actuelle en octets
            current_size = len(feed.SerializeToString())
            sizes.append(current_size)

            print(f"Taille de l'appel actuel : {current_size} octets")
            print(f"Taille totale des appels : {sum(sizes)} octets")
            
            #moyenne actuelle de la taille des appels successifs
            average_size = sum(sizes) / len(sizes)
            print(f"Taille moyenne des appels successifs : {average_size} octets")
            
            
            #Apres lancement je relève un taille moyenne des appels d'environs 29352.25 octets, soit 29.35 Ko.
            #sur la base d'appels toutes les 10 secondes, cela fait 6 appels par minute, soit 360 appels par heure, soit 8640 appels par jour.
            #Donc le volume de données journalier est d'environ 29352.25 * 8640 = 253.7 Mo par jour, soit 7.6 Go par mois   
            #soit 91.2 Go par an. Donc le stockage n'est pas un problème pour ce flux, même sur une longue période. je note dans data-source.md


            if df_vehicules.empty:
                print("Aucun véhicule dans ce flux, on passe à l'appel suivant.")
                continue

            timestamp_actuel = df_vehicules['vehicle_timestamp'].max()

            # on ne calcule l'écart qu'à partir du 2e appel (pas de "précédent" au premier tour)
            if last_timestamp is not None:
                ecart_actuel = timestamp_actuel - last_timestamp
                horodatages_vehicules.append(ecart_actuel)

            last_timestamp = timestamp_actuel


            # Ajouter un horodatage pour savoir quand les données ont été récupérées
            df_vehicules['timestamp'] = datetime.now()


            # je convertis l'horodatage en format lisible fuseau horaire de paris
            df_vehicules['vehicle_timestamp'] = pd.to_datetime(df_vehicules['vehicle_timestamp'], unit='s', utc=True).dt.tz_convert('Europe/Paris')
            print(df_vehicules.head(20))  # Affiche les premières lignes du DataFrame

            #j'affiche le nombre de véhicules récupérés
            print(f"Nombre de véhicules récupérés : {len(df_vehicules)}")



            #calcul de la distribution des écarts de timestamp des véhicules entre les appels successifs
            #à la fin je fait la moyenne des ecarts des horodatages de la liste
            if horodatages_vehicules:
                ecart_moyen = sum(horodatages_vehicules) / len(horodatages_vehicules)
                print(f"Écart moyen des horodatages des véhicules entre les appels successifs : {ecart_moyen} secondes")



            # Je vais maintenant faire une jointure entre le GTFS TR et le GTFS statique pour récupérer les informations sur les lignes et les arrêts
            
            resultat = df_vehicules.merge(
            df_trips,
            on="trip_id",   # nom de la colonne de jointure, si identique des deux côtés
            how="left"              # quel type de jointure
            )
            
            #mesure du taux d'appariement entre les deux dataset
            taux = (df_jointure["_merge"] == "both").mean()
            print(f"Taux d'appariement trip_id : {taux:.1%}")
            
            
            #pour voir les éléments non appariés
            # voir les non-appariés
            non_apparies = df_jointure[df_jointure["_merge"] == "left_only"]
            
            

            print("#####################   AFFICHAGE DES ELEMENTS NON APPARIES  ######################## \n \n \n ”")
            
            
            print(non_apparies.drop_duplicates())
            
            
            

        else:
            print("Aucune donnée récupérée.")

        time.sleep(10)  # Attendre 10 secondes avant la prochaine récupération
    
    
    
    # #lecture du fichier local pour tester la fonction get_vehicle_positions_from_file
    # filename = "../../local_data/gtfs_rt_vehicle_positions_20260902T202031.pb"
    # feed = get_vehicle_positions_from_file(filename)
    
    # #Faisons un print de l'objet feed pour voir ce qu'il contient
    # print(feed)
    
    
    
    # df_vehicules = feed_to_dataframe(feed)
    # print(df_vehicules.head(1000))  # Affiche les premières lignes du DataFrame
    
    # #j'affiche maitenant l'id , la lagitude longitue et l'horodatage
    # print(df_vehicules[['entity_id', 'latitude', 'longitude', 'vehicle_timestamp']].head(1000))  # Affiche les premières lignes du DataFrame
    # #maintant en convetissant l'horadatage en format lisible fuseau horaire de paris
    # df_vehicules['vehicle_timestamp'] = pd.to_datetime(df_vehicules['vehicle_timestamp'], unit='s', utc=True).dt.tz_convert('Europe/Paris')
    # print(df_vehicules[['entity_id', 'latitude', 'longitude', 'vehicle_timestamp']].head(1000))  # Affiche les premières lignes du DataFrame



