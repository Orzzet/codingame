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

const int CREATURE = 0;
const int GREEN_ITEM = 1;
const int RED_ITEM = 2;
const int BLUE_ITEM = 3;

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
    // All cards with the same cardNumber share the same
    int* cardNumber{};
    int instanceId{};
    int location{};
    int* cardType{};
    int* cost{};
    int attack{};
    int defense{};
    int* myHealthChange = nullptr;
    int* opponentHealthChange = nullptr;
    int* cardDraw = nullptr;
    bool hasGuard = false;
    bool hasBreakthrough = false;
    bool hasCharge = false;
    bool hasDrain = false;
    bool hasLethal = false;
    bool hasWard = false;
    bool canAttack = false;


    Card() = default;

    Card(const Card& c){
        this->cardNumber = c.cardNumber;
        this->instanceId = c.instanceId;
        this->cardType = c.cardType;
        this->cost = c.cost;
        this->myHealthChange = c.myHealthChange;
        this->opponentHealthChange = c.opponentHealthChange;
        this->cardDraw = c.cardDraw;
        this->location = c.location;
        this->attack = c.attack;
        this->defense = c.defense;
        this->hasGuard = c.hasGuard;
        this->hasBreakthrough = c.hasBreakthrough;
        this->hasCharge = c.hasCharge;
        this->hasDrain = c.hasDrain;
        this->hasLethal = c.hasLethal;
        this->hasWard = c.hasWard;
        this->canAttack = c.canAttack;
    }

    Card(int *cardNumber, int instanceId, int location, int *cardType, int *cost, int attack, int defense,
         string* abilities, int *myHealthChange, int *opponentHealthChange, int *cardDraw, bool canAttack) :
            cardNumber(cardNumber),
            instanceId(instanceId),
            location(location),
            cardType(cardType),
            cost(cost),
            attack(attack),
            defense(defense),
            myHealthChange(
                    myHealthChange),
            opponentHealthChange(
                    opponentHealthChange),
            cardDraw(cardDraw),
            canAttack(canAttack){
        for(char& c: *abilities){
            if(c == 'B'){
                this->hasBreakthrough = true;
            }else if (c == 'G'){
                this->hasGuard = true;
            }else if (c == 'C'){
                this->hasCharge = true;
            }else if (c == 'D'){
                this->hasDrain = true;
            }else if (c == 'L'){
                this->hasLethal = true;
            }else if (c == 'W'){
                this->hasWard = true;
            }
        }
    }

    bool operator < (const Card & other) const{
        return this->instanceId < other.instanceId;
    }

    int getValue() const{
        return attack + defense - 2 * *cost; // oh s**t
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
    int turn{};

    unordered_map<int, Card> cardsInHand;
    unordered_map<int, Card> creaturesInBoard;

    Player() = default;

    Player(int health, int mana, int deck, int rune, int turn){
        this->health = health;
        this->mana = mana;
        this->deck = deck;
        this->rune = rune;
        this->handSize = 0;
        this->turn = turn;
    };

    void addCardToHand(Card* card){
        this->cardsInHand.insert({card->instanceId, *card});
        this->handSize++;
    }

    void removeCardFromHand(Card* card){
        this->cardsInHand.erase(card->instanceId);
        this->handSize--;
    }

    void addCardToBoard(Card* card){
        this->creaturesInBoard.insert({card->instanceId, *card});

    }

    void removeCardFromBoard(Card* card){
        this->creaturesInBoard.erase(card->instanceId);
    }

    void destroyCardInBoard(int instanceId){
        creaturesInBoard.erase(instanceId);
    }

    Player(const Player& other){
        this->health = other.health;
        this->mana = other.mana;
        this->deck = other.deck;
        this->rune = other.rune;
        this->handSize = other.handSize;
        this->turn = other.turn;
        for(const auto & pair: other.creaturesInBoard){
            Card creature = pair.second;
            this->creaturesInBoard.insert({creature.instanceId, creature});
        }
        for(const auto & pair: other.cardsInHand){
            Card card = pair.second;
            this->cardsInHand.insert({card.instanceId, card});
        }
    }
};

class State{
public:
    Player player1;
    Player player2;
    int turn{};

    State() = default;

    State(const Player *p1, const Player* p2){
        this->player1 = *p1;
        this->player2 = *p2;
    }
};

class StateManager{
public:

    static State* simulate(State* initialState){
        auto * s = new State(&initialState->player1, &initialState->player2);

        return s;
    };

    static unordered_set<string> legalActions(State* s){
        unordered_set<string> actions;

        // Legal summons and items
        for(auto & pair: s->player1.cardsInHand) {
            Card *c = &pair.second;

            if (*c->cost <= s->player1.mana) {
                if (*c->cardType == CREATURE && s->player1.creaturesInBoard.size() < 6) {
                    string a = "SUMMON ";
                    actions.insert(a + to_string(c->instanceId));
                } else if (*c->cardType == GREEN_ITEM) {
                    for (auto &targetPair: s->player1.creaturesInBoard) {
                        Card *target = &targetPair.second;
                        string a = "USE ";
                        a += to_string(c->instanceId) + " " + to_string(target->instanceId);
                        actions.insert(a);
                    }
                } else if (*c->cardType == RED_ITEM || *c->cardType == BLUE_ITEM && c->defense < 0) {
                    for (auto &targetPair: s->player2.creaturesInBoard) {
                        Card *target = &targetPair.second;
                        string a = "USE ";
                        a += to_string(c->instanceId) + " " + to_string(target->instanceId);
                        actions.insert(a);
                    }
                } else {
                    string a = "USE ";
                    a += to_string(c->instanceId) + " -1";
                    actions.insert(a);
                }
            }
        }

        // Legal attacks
        unordered_set<string> guardAttacks;
        unordered_set<string> otherAttacks;
        for(auto & pair: s->player1.creaturesInBoard){
            Card * c = &pair.second;

            if(!c->canAttack){
                continue;
            }

            for(auto & targetPair: s->player2.creaturesInBoard){
                Card * target = &targetPair.second;
                string a = "ATTACK ";
                a += to_string(c->instanceId) + " " + to_string(target->instanceId);
                if(target->hasGuard){
                    guardAttacks.insert(a);
                }else{
                    otherAttacks.insert(a);
                }
            }

            // Attack to opponent
            string a = "ATTACK ";
            a += to_string(c->instanceId) + " -1";
            otherAttacks.insert(a);
        }

        if(guardAttacks.empty()){
            actions.insert(otherAttacks.begin(), otherAttacks.end());
        }else{
            actions.insert(guardAttacks.begin(), otherAttacks.end());
        }

        return actions;
    }
};

// Given a creature, the best attack it can do ignoring allied creatures.
int bestAttack(Card* attackingCreature, Player* oppositePlayer){
    int target = -1;
    int valueGain = 0;
    for( auto& pair : oppositePlayer->creaturesInBoard){
        Card* opCreature = &pair.second;
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

// Pick between 3 cards based on the value of the cards.
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

        for(auto& pair: activePlayer->cardsInHand){
            Card* card = &pair.second;
            if(*card->cost == manaCostCheck && currentMana >= *card->cost){
                cards.insert(card);
                currentMana -= *card->cost;
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

void attackWithCreatures(Player *attackingPlayer){

    for(auto& pair: attackingPlayer->creaturesInBoard){
        Card* card = &pair.second;
        int target = bestAttack(card, player2);
        attack(card->instanceId, target);

        if(target != -1){
            Card* attackedCreature = &player2->creaturesInBoard[target];
            attackedCreature->takeDamage(card->attack);
            if(attackedCreature->defense <= 0){
                player2->destroyCardInBoard(attackedCreature->instanceId);
            }
        }

        cout << ";";
    }

}

void initializeState(int turn){
    for (int i = 0; i < 2; i++) {
        int playerHealth;
        int playerMana;
        int playerDeck;
        int playerRune;
        cin >> playerHealth >> playerMana >> playerDeck >> playerRune; cin.ignore();
        players[i] = new Player(playerHealth, playerMana, playerDeck, playerRune, turn);
    }
    player1 = players[0];
    player2 = players[1];
    int opponentHand;
    cin >> opponentHand; cin.ignore();
    player2->handSize = opponentHand;
    int cardCount;
    cin >> cardCount; cin.ignore();
    Card * cards[cardCount];
    for (int i = 0; i < cardCount; i++) {
        int * cardNumber = new int();
        int instanceId;
        int location;
        int * cardType = new int();
        int * cost = new int();
        int attack;
        int defense;
        string abilities;
        int * myHealthChange = new int();
        int * opponentHealthChange = new int();
        int * cardDraw = new int();
        cin >> *cardNumber >> instanceId >> location >> *cardType >> *cost >> attack >> defense >> abilities >> *myHealthChange >> *opponentHealthChange >> *cardDraw; cin.ignore();
        cards[i] = new Card(cardNumber, instanceId, location, cardType, cost, attack, defense, &abilities, myHealthChange, opponentHealthChange, cardDraw, true);
        if(turn<30){
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
    int turn = 0;
    State * nextState;
    State * initialState;
    // game loop
    while (true) {
        initializeState(turn);
        initialState = new State(player1, player2);

        // test
        unordered_set<string> actions = StateManager::legalActions(initialState);
        for(const string &s: actions){
            cerr << s << endl;
        }


        if(turn < 30){
            pick(bestPick());
        }else{
            playCards();
            attackWithCreatures(player1);
        }
        end();
        turn++;
    }
}