from flask import Flask, render_template
import random
import json

app = Flask(__name__)

cards = []

with open('cards.json', 'r') as f:
    cards_dict = json.load(f)
for card in cards_dict:
    cards.append(card['location'])

players_current_cards = []

def random_number():
    return int(random.randint(0, len(cards)-1))

def get_new_card():
    card = cards.pop(random_number())
    players_current_cards.append(card)
    return card
@app.route('/', methods=["POST", "GET"])
def play():
    if(len(cards)==0):
        return "\n You have found all cards " + str(players_current_cards) + " \n the number of cards is" + str(len(players_current_cards))
    else:
        current_card = get_new_card()
        for card in cards_dict:
            if((card['location']) == current_card):
                return render_template('currentCardPage.html', location=card['location'], question=card['question'], answers=card['answers'], correctAnswer=card['correctAnswer'])

if __name__ == '__main__':
    app.run()

