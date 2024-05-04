import re, random
from collections import defaultdict

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
        if character['NAME'] != 'None' and character['NAME'] in character_names:
            input_characters.append(character)
            input_character_types.append(character['TYPE'].split('/'))
    print("input characters:", input_characters)
    print("input character types:", input_character_types)
    num_input_characters = len(input_characters)

    # PROCESS TOPIC INFO

    input_topics = []
    for topic in all_topics:
        if topic['NAME'] != 'None' and topic['NAME'] in topic_names:
            input_topics.append(topic['NAME'])
    print("input topics:", input_topics)

    # PROCESS GENRE INFO

    input_genres = []
    for genre in all_genres:
        if genre['NAME'] != 'No selection' and genre['NAME'] in genres:
            input_genres.append(genre)

    # add characters derived from genre

    # SCORE EACH NARRATIVE BASED ON CHARACTER, TOPIC, AND GENRE MATCH W/ USER INPUT

    all_narratives = all_data['narratives']
    narrative_scores = [0] * len(all_narratives)
    for i in range(len(all_narratives)):
        narrative = all_narratives[i]
        # print("narrative:", narrative['NAME'])
        total_weight = 100

        min_characters = 0 if narrative['MIN CHARACTERS'] == "NA" else int(narrative['MIN CHARACTERS'])
        max_characters = 100 if narrative['MAX CHARACTERS'] == "NA" else int(narrative['MAX CHARACTERS'])

        # min characters: can't have too few
        if min_characters > num_input_characters:
            update(narrative_scores, i, "DQ")
        
        # max characters: can't have too money
        if max_characters < num_input_characters:
            update(narrative_scores, i, "DQ")

        # up to 50 pts for character overlaps (compare input characters to CHARACTER TYPES)
        character_score = 0
        narrative_characters = re.split('[/,]', narrative['CHARACTER TYPES'])
        if len(input_characters) != 0 and narrative_characters[0] != "NA":
            weight = 50 / len(input_characters)
            # note: type should be equally important for all character combos, regardless of their # of possible types
            total_weight -= 50
            match = False
            for character_types in input_character_types:
                for type in character_types:
                    if type in narrative_characters:
                        match = True
                if match:
                    character_score += weight
            update(narrative_scores, i, character_score)
        
        # all remaining pts for topic overlaps (compare input topics to RELEVANT TOPICS)
        topic_score = 0
        narrative_topics = narrative['RELEVANT TOPICS'].split('/')
        if len(input_topics) != 0 and len(narrative_topics) != 0:
            weight = total_weight / len(input_topics)
            for topic in input_topics:
                if topic in narrative_topics:
                    topic_score += weight
            update(narrative_scores, i, topic_score)
        
    print("narrative scores:", narrative_scores)

    # PICK BEST-FIT NARRATIVE
    # isolate top scorers
    max_score = 0
    for score in narrative_scores:
        if score != "DQ" and score > max_score:
            max_score = score
    best_indices = [index for index, score in enumerate(narrative_scores) if score == max_score]
    top_narrative = all_narratives[random.choice(best_indices)] # pick randomly to break ties
    
    # CREATE DECISION EXPLANATION
    explanation = f"We determined this trope to be a {max_score:.0f}% match based on your input."

    print("top narrative:", top_narrative)
    # shuffle characters before picking character_0
    narrative_characters = top_narrative['CHARACTER TYPES'].split(',')
    if narrative_characters != 'NA':
        for i in range(len(narrative_characters)):
            narrative_characters[i] = narrative_characters[i].split('/')
        print("narrative characters:", narrative_characters)

    # assign characters
    character_0_name = ""
    by_default = ""
    if "{CHARACTER_0}" in top_narrative['DESCRIPTION']:
        desired_types_0 = narrative_characters[0]
        print("desired types for character 0:", desired_types_0)
        weight = 1/len(desired_types_0)
        max_score = -1
        for i in range(len(input_character_types)):
            score = 0
            character_types = input_character_types[i]
            for type in character_types:
                if type in desired_types_0:
                    score += weight
            if score > max_score:
                character_0 = input_characters[i]
                character_0_name = character_0['NAME']
                index_0 = i
        if max_score == -1: # no good matches
            index_0 = random.randint(0, len(input_character_types) - 1)
            character_0 = input_characters[index_0]
            character_0_name = character_0['NAME']
            if len(input_character_types) == 1:
                by_default = ", by default,"
        input_characters.pop(index_0)
        input_character_types.pop(index_0)
        print("character 0:", character_0)
    
    character_1_name = ""
    if "{CHARACTER_1}" in top_narrative['DESCRIPTION']:
        if len(narrative_characters) > 1:
            desired_types_1 = narrative_characters[1]
        # else same types as before, don't need to be distinct
        weight = 1/len(desired_types_1)
        max_score = -1
        for i in range(len(input_character_types)):
            score = 0
            character_types = input_character_types[i]
            for type in character_types:
                if type in desired_types_1:
                    score += weight
            if score > max_score:
                character_1 = input_characters[i]
                character_1_name = character_1['NAME']
                index_1 = i
        if max_score == -1: # no good matches
            index_1 = random.randint(0, len(input_character_types) - 1)
            character_1 = input_characters[index_1]
            character_1_name = character_1['NAME']
        input_characters.pop(index_1)
        input_character_types.pop(index_1)

    remaining_characters_names = ""
    if "{REMAINING_CHARACTERS}" in top_narrative['DESCRIPTION']:
        if len(input_characters) == 1:
            remaining_characters_names = input_characters[0]['NAME']
        else:
            remaining_characters_names = "" # list, ex. "Ann, Bob, and Carl"
            for i in range(len(input_characters)):
                if i == len(input_characters) - 1:
                    remaining_characters_names += f"and the {input_characters[i]['NAME']}"
                elif i == len(input_characters) - 2:
                    remaining_characters_names += f"the {input_characters[i]['NAME']} "
                else:
                    remaining_characters_names += f"the {input_characters[i]['NAME']}, "

    suggestion = top_narrative['NAME']
    description = top_narrative['DESCRIPTION'].format(CHARACTER_0=character_0_name, CHARACTER_1=character_1_name, REMAINING_CHARACTERS=remaining_characters_names)
    
    # character explanation
    comparison = ""
    if top_narrative['MIN CHARACTERS'] == "NA" and top_narrative['MAX CHARACTERS'] == "NA":
        comparison = "any amount of"
    else:
        if top_narrative['MIN CHARACTERS'] == "NA":
            comparison += "at least "
        else:
            comparison += top_narrative['MIN CHARACTERS']
        if top_narrative['MAX CHARACTERS'] == "NA":
            comparison += " or more"
        else:
            if not comparison:
                comparison += top_narrative['MAX CHARACTERS']
            elif top_narrative['MAX CHARACTERS'] != top_narrative['MIN CHARACTERS']:
                comparison += f" to {top_narrative['MAX CHARACTERS']}"
    
    first_s = "" if max_characters == 1 else "s"
    second_s = "s" if num_input_characters > 1 else ""
    explanation += f" The '{top_narrative['NAME']}' trope involves {comparison} character{first_s}, and you gave us {num_input_characters} character{second_s}, which works out."

    if character_0_name:
        explanation += f" The {character_0_name} can be described as {character_0['DESCRIPTION']}. We decided{by_default} that they should be our {desired_types_0[0]}."
    if character_1_name:
        explanation += f" Meanwhile, the {character_1_name} is {character_1['DESCRIPTION']}. They'll make do as our {desired_types_1[0]}."

    # topic explanation
    narrative_topics = top_narrative['RELEVANT TOPICS'].split('/')
    overlap_topics = []
    for topic in narrative_topics:
        if topic in input_topics:
            overlap_topics.append(topic)
    print("overlap_topics:", overlap_topics)
    if len(overlap_topics) > 0:
        explanation += f" This trope suggestion is topically similar to your input: they both involve "
        if len(overlap_topics) == 1:
            explanation += f"{overlap_topics[0]}."
        else:
            for i in range(len(overlap_topics)):
                if i == len(overlap_topics) - 1:
                    explanation += f"and {overlap_topics[i]}."
                elif i == len(overlap_topics) - 2:
                    explanation += f"{overlap_topics[i]} "
                else:
                    explanation += f"{overlap_topics[i]}, "

    # genre explanation for tag
    narrative_tag = top_narrative['TAG']
    genres_with_tag_overlap = []
    input_genre_names = []
    for genre in input_genres:
        input_genre_names.append(genre['NAME']) # will use in next part of analysis
        input_tags = genre['IMPORTANT TAGS'].split('/')
        if narrative_tag in input_tags:
            genres_with_tag_overlap.append(genre)
    if len(genres_with_tag_overlap) > 0:
        first_s = "s" if len(genres_with_tag_overlap) > 1 else ""
        explanation += f" Tropes about {narrative_tag} are important in the genre{first_s} that you selected: "
        if len(genres_with_tag_overlap) == 1:
            explanation += f"{genres_with_tag_overlap[0]['NAME']}."
        else:
            for i in range(len(genres_with_tag_overlap)):
                if i == len(genres_with_tag_overlap) - 1:
                    explanation += f"and {genres_with_tag_overlap[i]['NAME']}."
                elif i == len(genres_with_tag_overlap) - 2:
                    explanation += f"{genres_with_tag_overlap[i]['NAME']} "
                else:
                    explanation += f"{genres_with_tag_overlap[i]['NAME']}, "

    # genre explanation for topics
    topics_with_genre_overlap = defaultdict(list)
    for topic in all_topics:
        print("narrative topics:", narrative_topics)
        if topic['NAME'] in narrative_topics:
            narrative_topic_genres = topic['RELEVANT GENRES'].split('/')
            print("narrative topic genres:", narrative_topic_genres)
            print("input genres:", input_genres)
            for narrative_genre in narrative_topic_genres:
                if narrative_genre in input_genre_names:
                    topics_with_genre_overlap[narrative_genre].append(topic['NAME'])

    print("topics with genre overlap:", topics_with_genre_overlap)
    
    for genre, topic_list in topics_with_genre_overlap.items():
        explanation += f" The genre of {genre} especially concerns topics such as "
        if len(topic_list) == 1:
            explanation += f"{topic_list[0]}."
        else:
            for i in range(len(topic_list)):
                if i == len(topic_list) - 1:
                    explanation += f"and {topic_list[i]}."
                elif i == len(topic_list) - 2:
                    explanation += f"{topic_list[i]} "
                else:
                    explanation += f"{topic_list[i]}, "
        print("explanation:", explanation)


    return suggestion, description, explanation