#include <iostream>
#include <string>
#include <utility> #include <vector>
#include <algorithm>
#include <unordered_map>

using namespace std;

class Player;
class Card;

Player* player1;
Player* player2;
Player* players[2];

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
    int myHealthChange;
    int opponentHealthChange;
    int cardDraw;

    Card(int cardNumber, int instanceId, int location, int cardType, int cost, int attack, int defense,
         string abilities, int myHealthChange, int opponentHealthChange, int cardDraw) :
            cardNumber(cardNumber),
            instanceId(instanceId),
            location(location),
            cardType(cardType),
            cost(cost),
            attack(attack),
            defense(defense),
            abilities(move(
                    abilities)),
            myHealthChange(
                    myHealthChange),
            opponentHealthChange(
                    opponentHealthChange),
            cardDraw(cardDraw) {}

    bool operator < (const Card & other) const{
        return this->instanceId < other.instanceId;
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
};



void initializeState(){
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
        cards[i] = new Card(cardNumber, instanceId, location, cardType, cost, attack, defense, abilities, myHealthChange, opponentHealthChange, cardDraw);
        if(location == 0){
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

    // game loop
    while (true) {

        initializeState();
        pass();
        end();

    }
}