import xml.etree.ElementTree as ET
import pandas as pd

file_path = 'example_xml.xml'
tree = ET.parse(file_path)
root = tree.getroot()
print(f"Root tag: {root.tag}")

########################### GET TABLE OF FENCERS ##########################

tireurs = root.find('Tireurs')

# Create a list to store tireur data
tireur_data = []

# Loop through each Tireur element and extract the relevant attributes
for tireur in tireurs.findall('Tireur'):
    tireur_data.append({
        'ID': tireur.get('ID'),
        'Nom': tireur.get('Nom'),
        'Prenom': tireur.get('Prenom'),
        'DateNaissance': tireur.get('DateNaissance'),
        'Sexe': tireur.get('Sexe'),
        'Lateralite': tireur.get('Lateralite'),
        'Nation': tireur.get('Nation'),
        'Club': tireur.get('Club'),
        'Licence': tireur.get('Licence'),
        'Classement': tireur.get('Classement'),
        'Statut': tireur.get('Statut')
    })

df_tireurs = pd.DataFrame(tireur_data)

################### GET POULES SUMMARY DATA , WHO QUALIFIED ################

phases = root.find('Phases')
tour_de_poules_data = []

# Loop through each 'TourDePoules' element and extract relevant information
for tour_de_poules in phases.findall('TourDePoules'):
    for poule in tour_de_poules.findall('Poule'):
        for tireur in poule.findall('Tireur'):
            tour_de_poules_data.append({
                'PhaseID': tour_de_poules.get('PhaseID'),
                'PouleID': poule.get('ID'),
                'TireurREF': tireur.get('REF'),
                'NbVictoires': tireur.get('NbVictoires'),
                'NbMatches': tireur.get('NbMatches'),
                'TD': tireur.get('TD'),
                'TR': tireur.get('TR'),
                'RangPoule': tireur.get('RangPoule')
            })

# Convert the extracted data into a DataFrame
df_poules_qualify = pd.DataFrame(tour_de_poules_data)


################ TABLEAUX SUMMARY ##############################

tableaux_data = []

# Loop through each 'PhaseDeTableaux' element and extract the relevant data
for phase in phases.findall('PhaseDeTableaux'):
    for tireur in phase.findall('Tireur'):
        tableaux_data.append({
            'PhaseID': phase.get('PhaseID'),
            'Tireur_REF': tireur.get('REF'),
            'RankInitial': tireur.get('RangInitial'),
            'RankFinal': tireur.get('RangFinal')
        })

# Convert the extracted data into a DataFrame
df_tableaux_summary = pd.DataFrame(tableaux_data)

################### GET POULES MATCHES #################
poule_match_data = []
phases = root.find('Phases')

# Loop through each 'TourDePoules' element and extract the matches
for tour_de_poules in phases.findall('TourDePoules'):
    for poule in tour_de_poules.findall('Poule'):
        for match in poule.findall('Match'):
            tireurs = match.findall('Tireur')
            poule_match_data.append({
                'MatchID': match.get('ID'),
                'MatchSourceID': poule.get('ID'),
                'Fencer_REF': tireurs[0].get('REF'),
                'Fencer_Score': tireurs[0].get('Score'),
                'Fencer_Status': tireurs[0].get('Statut'),
                'Opponent_REF': tireurs[1].get('REF'),
                'Opponent_Score': tireurs[1].get('Score'),
                'Opponent_Status': tireurs[1].get('Statut'),
                'MatchType': 'Poule'
            })

df_poule_matches = pd.DataFrame(poule_match_data)

################### GET TABLEAU MATCHES #################
tableau_match_data = []
# Loop through each 'SuiteDeTableaux' element and extract the matches
for suite in root.findall('.//SuiteDeTableaux'):
    for tableau in suite.findall('Tableau'):
        for match in tableau.findall('Match'):
            tireurs = match.findall('Tireur')
            tableau_match_data.append({
                'MatchID': match.get('ID'),
                'MatchSourceID': tableau.get('ID'),
                'Fencer_REF': tireurs[0].get('REF'),
                'Fencer_Score': tireurs[0].get('Score'),
                'Fencer_Status': tireurs[0].get('Statut'),
                'Opponent_REF': tireurs[1].get('REF'),
                'Opponent_Score': tireurs[1].get('Score'),
                'Opponent_Status': tireurs[1].get('Statut'),
                'MatchType': 'Tableau'
            })

df_tableau_matches = pd.DataFrame(tableau_match_data)

################### COMBINE POULES AND TABLEAU MATCHES ###################
# Concatenate the poule and tableau matches into one DataFrame
df_combined_matches = pd.concat([df_poule_matches, df_tableau_matches], ignore_index=True)

################### ADD FENCERS NAMES ###################
# Create a lookup dictionary for Fencers from the df_tireurs DataFrame
tireurs_lookup = df_tireurs.set_index('ID')[['Nom', 'Prenom']].to_dict('index')

# Define a function to lookup and return the full name
def get_fencer_name(ref):
    fencer = tireurs_lookup.get(ref)
    if fencer:
        return f"{fencer['Prenom']} {fencer['Nom']}"
    else:
        return None

# Apply the lookup function to add Fencer names in the combined DataFrame
df_combined_matches['Fencer_Name'] = df_combined_matches['Fencer_REF'].apply(get_fencer_name)
df_combined_matches['Opponent_Name'] = df_combined_matches['Opponent_REF'].apply(get_fencer_name)

# Display the final combined DataFrame
print(df_combined_matches)

del df_poule_matches
del df_tableau_matches


