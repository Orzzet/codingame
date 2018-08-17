#include <iostream>
#include <string>
#include <utility> #include <vector>
#include <algorithm>
#include <sstream>
#include <iterator>
#include <unordered_set>
#include <unordered_map>

using namespace std;

class Player;
class Card;

Player* player1;
Player* player2;
Player* players[2];

Card* cardsToPick[3];

void debug(const int& msg){
    cerr << msg << endl;
}

void debug(const string& msg){
    cerr << msg << endl;
}

void pick(int nb){
    cout << "PICK " << nb;
}

void summon(int id){
    cout << "SUMMON " << id;
}

void attack(int idAttacker, int idTarget){
    cout << "ATTACK " << idAttacker << " " << idTarget;
}

void pass(){
    cout << "PASS";
}

void end(){
    cout << endl;
}

class Card{
public:
    int cardNumber;
    int instanceId;
    int location;
    int cardType;
    int cost;
    int attack;
    int defense;
    string abilities;
    int myHealthChange = 0;
    int opponentHealthChange = 0;
    int cardDraw = 0;
    bool hasGuard = false;
    bool hasBreakthrough = false;
    bool hasCharge = false;

    Card(int cardNumber, int instanceId, int location, int cardType, int cost, int attack, int defense,
         string* abilities, int myHealthChange, int opponentHealthChange, int cardDraw) :
            cardNumber(cardNumber),
            instanceId(instanceId),
            location(location),
            cardType(cardType),
            cost(cost),
            attack(attack),
            defense(defense),
            abilities(*abilities),
            myHealthChange(
                    myHealthChange),
            opponentHealthChange(
                    opponentHealthChange),
            cardDraw(cardDraw) {
        for(char& c: *abilities){
            if(c == 'B'){
                this->hasBreakthrough = true;
            }else if (c == 'G'){
                this->hasGuard = true;
            }else if (c == 'C'){
                this->hasCharge = true;
            } 
        }
    }

    bool operator < (const Card & other) const{
        return this->instanceId < other.instanceId;
    }

    int getValue() const{
        return attack + defense - 2 * cost;
    }

    void takeDamage(int amount){
        this->defense -= amount;
    }
};

class Player{
public:
    int health{};
    int mana{};
    int deck{};
    int rune{};
    int handSize{};

    unordered_map<int, Card*> cardsInHand;
    unordered_map<int, Card*> cardsInBoard;

    Player() = default;

    Player(int health, int mana, int deck, int rune){
        this->health = health;
        this->mana = mana;
        this->deck = deck;
        this->rune = rune;
        this->handSize = 0;
    };

    void addCardToHand(Card* card){
        this->cardsInHand.insert({card->instanceId, card});
        this->handSize++;
    }

    void removeCardFromHand(Card* card){
        this->cardsInHand.erase(card->instanceId);
        this->handSize--;
    }

    void addCardToBoard(Card* card){
        this->cardsInBoard.insert({card->instanceId, card});

    }

    void removeCardFromBoard(Card* card){
        this->cardsInBoard.erase(card->instanceId);
    }

    void destroyCardInBoard(int instanceId){
        cardsInBoard.erase(instanceId);
    }
};

// Given a creature, the best attack it can do ignoring allied creatures.
int bestAttack(Card* attackingCreature, Player* oppositePlayer){
    int target = -1;
    int valueGain = 0;
    for( const auto& pair : oppositePlayer->cardsInBoard){
        Card* opCreature = pair.second;
        if(attackingCreature->attack >= opCreature->defense && valueGain < opCreature->getValue() - attackingCreature->getValue()){
            target = opCreature->instanceId;
            valueGain = opCreature->getValue() - attackingCreature->getValue();
        }
        if(opCreature->hasGuard){
            target = opCreature->instanceId;
            valueGain = opCreature->getValue() - attackingCreature->getValue();
            break;
        }
    }

    return target;
}

// Pick betweet 3 cards based on the value of the cards.
int bestPick(){
    int maxValue = -100;
    int id = 0;
    int cardNo = 0;
    for(Card* card: cardsToPick){
        if(card->getValue() > maxValue){
            id = cardNo;
            maxValue = card->getValue();
        }
        cardNo++;
    }
    return id;
}

unordered_set<Card*> selectCardsToPlay(Player* activePlayer){
    unordered_set<Card*> cards;
    int currentMana = activePlayer->mana;
    int manaCostCheck = currentMana;

    while(currentMana > 0 && manaCostCheck > 0){

        for(const auto& pair: activePlayer->cardsInHand){
            Card* card = pair.second;
            if(card->cost == manaCostCheck && currentMana >= card->cost){
                cards.insert(card);
                currentMana -= card->cost;
            }
        }

        manaCostCheck--;
    }

    return cards;

}

void playCards(){
    for(Card* card: selectCardsToPlay(player1)){
        summon(card->instanceId);
        cout << ";";
    }
}

void attackWIthCreatures(Player* attackingPlayer){

    for(const auto& pair: attackingPlayer->cardsInBoard){
        Card* card = pair.second;
        int target = bestAttack(card, player2);
        attack(card->instanceId, target);

        if(target != -1){
            Card* attackedCreature = player2->cardsInBoard[target];
            attackedCreature->takeDamage(card->attack);
            if(attackedCreature->defense <= 0){
                player2->destroyCardInBoard(attackedCreature->instanceId);
            }
        }

        cout << ";";
    }

}

void initializeState(int& time){
    for (int i = 0; i < 2; i++) {
        int playerHealth;
        int playerMana;
        int playerDeck;
        int playerRune;
        cin >> playerHealth >> playerMana >> playerDeck >> playerRune; cin.ignore();
        players[i] = new Player(playerHealth, playerMana, playerDeck, playerRune);
    }
    player1 = players[0];
    player2 = players[1];
    int opponentHand;
    cin >> opponentHand; cin.ignore();
    player2->handSize = opponentHand;
    int cardCount;
    cin >> cardCount; cin.ignore();
    Card* cards[cardCount];
    for (int i = 0; i < cardCount; i++) {
        int cardNumber;
        int instanceId;
        int location;
        int cardType;
        int cost;
        int attack;
        int defense;
        string abilities;
        int myHealthChange;
        int opponentHealthChange;
        int cardDraw;
        cin >> cardNumber >> instanceId >> location >> cardType >> cost >> attack >> defense >> abilities >> myHealthChange >> opponentHealthChange >> cardDraw; cin.ignore();
        cards[i] = new Card(cardNumber, instanceId, location, cardType, cost, attack, defense, &abilities, myHealthChange, opponentHealthChange, cardDraw);
        if(time<30){
            cardsToPick[i] = cards[i];
        }else if(location == 0){
            player1->addCardToHand(cards[i]);
        }else if(location == 1){
            player1->addCardToBoard(cards[i]);
        }else{
            player2->addCardToBoard(cards[i]);
        }
    }
}


int main()
{
    int time = 0;
    // game loop
    while (true) {
        initializeState(time);
        if(time < 30){
            pick(bestPick());
        }else{
            playCards();
            attackWIthCreatures(player1);
        }
        end();
        time++;
    }
}