from flask import Flask, render_template, request, redirect, url_for
import csv

from suggest import make_suggestion

app = Flask(__name__)

all_data = {}

def load_data():
    '''read in data from csv files'''
    csv_files = ['genres.csv', 'characters.csv', 'topics.csv', 'narratives.csv']
    for file_name in csv_files:
        with open(file_name, 'r', newline='') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')
            data = list(reader)
            name = file_name.split('.')[0]
            all_data[name] = data
    # print("all data:", all_data)

load_data()

@app.route('/data')
def data():
    '''display data tables'''
    display_data = {} # will remove 'None'/default items from dict
    display_data['genres'] = all_data['genres'][1:]
    display_data['characters'] = all_data['characters'][1:]
    display_data['topics'] = all_data['topics'][1:]
    display_data['narratives'] = all_data['narratives'][1:]
            
    return render_template('data.html', data=display_data)

@app.route('/', methods=['GET','POST'])
def home():
    '''allow user to input current info for their story'''
    if request.method == 'POST':
        return redirect(url_for('result'))
    dropdown_data = {}
    for group, data in all_data.items():
        dropdown_items = [entry['NAME'] + ": " + entry['DESCRIPTION'] if 'DESCRIPTION' in entry else entry['NAME'] for entry in data]
        dropdown_data[group] = dropdown_items
    return render_template('home.html', data=dropdown_data)


@app.route('/result', methods=['POST'])
def result():
    '''offer story suggestions'''
    if request.method == 'POST':
        genres = request.form.getlist('genre')
        characters = request.form.getlist('character')
        topics = request.form.getlist('topic')
        suggestion = make_suggestion(genres, characters, topics, all_data)
    return render_template('result.html', suggestion=suggestion)
    

if __name__ == '__main__':
    app.run(debug=True)
