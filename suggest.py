import re

def update(narrative_scores, i, update):
    '''update a score index: disqualify or change its numeric value'''
    if narrative_scores[i] != "DQ":
        if update == "DQ":
            narrative_scores[i] = "DQ"
        else:
            assert isinstance(update, (float, int)), f"{update} is not a number"
            narrative_scores[i] += update

def make_suggestion(genres, characters, topics, all_data):
    all_characters = all_data['characters']
    character_names = [character.split(":", 1)[0] for character in characters]
    all_topics = all_data['topics']
    topic_names = [topic.split(":", 1)[0] for topic in topics]
    all_genres = all_data['genres']

    # PROCESS CHARACTER INFO

    input_characters = []
    input_character_types = []
    for character in all_characters:
        if character['NAME'] in character_names:
            input_characters.append(character)
            input_character_types.append(character['TYPE'].split('/'))
    print("input character types:", input_character_types)

    # PROCESS TOPIC INFO
    input_topics = []
    for topic in all_topics:
        if topic['NAME'] in topic_names:
            input_topics.append(topic['NAME'])
    print("input topics:", input_topics)

    # PROCESS GENRE INFO

    input_genres = []
    for genre in all_genres:
        if genre['NAME'] in genres:
            input_genres.append(genre)

    # SCORE EACH NARRATIVE BASED ON CHARACTER, TOPIC, AND GENRE MATCH W/ USER INPUT

    all_narratives = all_data['narratives']
    narrative_scores = [0] * len(all_narratives)
    for i in range(len(all_narratives)):
        narrative = all_narratives[i]
        print("narrative:", narrative['NAME'])
        total_weight = 100

        min_characters = 0 if narrative['MIN CHARACTERS'] == "NA" else int(narrative['MIN CHARACTERS'])
        max_characters = 100 if narrative['MAX CHARACTERS'] == "NA" else int(narrative['MAX CHARACTERS'])

        # min characters: can't have too few
        if min_characters > len(input_characters):
            update(narrative_scores, i, "DQ")
            print("DQ based on min characters")
        
        # max characters: can't have too money
        if max_characters < len(input_characters):
            update(narrative_scores, i, "DQ")
            print("DQ based on max characters")

        # up to 40 pts for character overlaps (compare input characters to CHARACTER TYPES)
        character_score = 0
        narrative_characters = re.split('[/,]', narrative['CHARACTER TYPES'])
        print("narrative characters:", narrative_characters)
        if len(input_characters) != 0 and narrative_characters[0] != "NA":
            weight = 40 / sum(len(sublist) for sublist in input_characters) # type should be equally important for all character combos, regardless of their # of possible types
            total_weight -= 40
            for character_types in input_character_types:
                for character in character_types:
                    if character in narrative_characters:
                        character_score += weight
            update(narrative_scores, i, character_score)
        print("character score:", character_score)

        # up to 30 pts for topic overlaps (compare input topics to RELEVANT TOPICS)
        topic_score = 0
        narrative_topics = narrative['RELEVANT TOPICS'].split('/')
        print("narrative topics:", narrative_topics)
        if len(input_topics) != 0 and len(narrative_topics) != 0:
            weight = (total_weight * 0.5) / len(input_topics)
            total_weight *= 0.5
            for topic in input_topics:
                if topic in narrative_topics:
                    topic_score += weight
            update(narrative_scores, i, topic_score)
        print("topic score:", topic_score)

        # remaining points for genre overlaps (compare input genres to genres of RELEVANT TOPICS)
        genre_score = 0
            

                    
    print("narrative scores:", narrative_scores)
    # CREATE DECISION EXPLANATION
    # {narrative_scores[i]}% match

    # shuffle characters before picking character_0


    return None