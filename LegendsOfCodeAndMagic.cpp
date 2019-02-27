#pragma GCC optimize("-O3", "inline", "omit-frame-pointer", "unroll-loops")

#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <algorithm>
#include <sstream>
#include <iterator>
#include <chrono>
#include <unordered_set>
#include <unordered_map>
#include <map>
#include <queue>
#include <set>

using namespace std;
using namespace std::chrono;

class Player;
class Card;
class State;
class StateManager;

#define CREATURE 0
#define GREEN_ITEM 1
#define RED_ITEM 2
#define BLUE_ITEM 3
#define SUMMON 0
#define ATTACK 1
#define USE 2
#define PASS 3
#define HAND 0
#define PLAYER_BOARD 1
#define OPPONENT_BOARD (-1)

int turn;
int simsNo;
high_resolution_clock::time_point start;
high_resolution_clock::time_point finish;

map<int, float> pickValues;
map<int, int> creaturesCurve;
map<int, int> itemsCurve;
map<int, int> habilitiesCurve;
map<int, int> minCreaturesCurve;
map<int, int> maxCreaturesCurve;
map<int, int> minItemsCurve;
map<int, int> maxItemsCurve;
map<char, int> minHabilitiesCurve;

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

class Action{
public:
    int actionType;
    int id1;
    int id2;

    Action() = default;

    Action(int actionType, int id1, int id2):
            actionType(actionType),
            id1(id1),
            id2(id2)
    {};

    bool operator < (const Action & other) const{
        return this->actionType + this->id1 * 31 + this->id2 * 127 < other.actionType + other.id1 * 31 + other.id2 * 127;
    };
};

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
    bool hasAttacked = false;


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
        this->hasAttacked = c.hasAttacked;
    }

    Card(int *cardNumber, int instanceId, int location, int *cardType, int *cost, int attack, int defense,
         string* abilities, int *myHealthChange, int *opponentHealthChange, int *cardDraw, bool canAttack, bool hasAttacked) :
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
            canAttack(canAttack),
            hasAttacked(hasAttacked){
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

    float getPickValue() const{
        float pickValue = pickValues[*this->cardNumber];

        if(*this->cardType == CREATURE){
            pickValue += *this->cost == 0 && creaturesCurve[0] < minCreaturesCurve[0] ? 2 : 0;
            pickValue += *this->cost == 1 && creaturesCurve[1] < minCreaturesCurve[1] ? 3 : 0;
            pickValue += *this->cost == 2 && creaturesCurve[2] < minCreaturesCurve[2] ? 1 : 0;
            pickValue += *this->cost == 3 && creaturesCurve[3] < minCreaturesCurve[3] ? 1 : 0;
            pickValue += *this->cost == 4 && creaturesCurve[4] < minCreaturesCurve[4] ? 1 : 0;


            pickValue -= *this->cost == 0 && creaturesCurve[0] >= maxCreaturesCurve[0] ? 1 : 0;
            pickValue -= *this->cost == 1 && creaturesCurve[1] >= maxCreaturesCurve[1] ? 1 : 0;
            pickValue -= *this->cost == 2 && creaturesCurve[2] >= maxCreaturesCurve[2] ? 1 : 0;
            pickValue -= *this->cost == 3 && creaturesCurve[3] >= maxCreaturesCurve[3] ? 1 : 0;
            pickValue -= *this->cost == 4 && creaturesCurve[4] >= maxCreaturesCurve[4] ? 1 : 0;
            pickValue -= *this->cost == 5 && creaturesCurve[5] >= maxCreaturesCurve[5] ? 1 : 0;

            pickValue += this->hasGuard && habilitiesCurve['G'] < minHabilitiesCurve['G'] ? 1 : 0;
            pickValue += this->hasLethal && habilitiesCurve['L'] < minHabilitiesCurve['L'] ? 1 : 0;


            if(turn >= 13){
                pickValue += *this->cost == 0 && creaturesCurve[0] < minCreaturesCurve[0] ? 1 : 0;
                pickValue += *this->cost == 1 && creaturesCurve[1] < minCreaturesCurve[1] ? 1 : 0;
                pickValue += *this->cost == 2 && creaturesCurve[2] < minCreaturesCurve[2] ? 1 : 0;
                pickValue += *this->cost == 3 && creaturesCurve[3] < minCreaturesCurve[3] ? 1 : 0;
                pickValue += *this->cost == 4 && creaturesCurve[4] < minCreaturesCurve[4] ? 1 : 0;
                pickValue += *this->cost == 5 && creaturesCurve[5] < minCreaturesCurve[5] ? 1 : 0;
                pickValue += *this->cost == 6 && creaturesCurve[6] < minCreaturesCurve[6] ? 1 : 0;
                pickValue += *this->cost >= 7 && creaturesCurve[7] < minCreaturesCurve[7] ? 1 : 0;

                pickValue -= *this->cost == 0 && creaturesCurve[0] >= maxCreaturesCurve[0] ? 1 : 0;
                pickValue -= *this->cost == 1 && creaturesCurve[1] >= maxCreaturesCurve[1] ? 2 : 0;
                pickValue -= *this->cost == 2 && creaturesCurve[2] >= maxCreaturesCurve[2] ? 1 : 0;
                pickValue -= *this->cost == 6 && creaturesCurve[6] >= maxCreaturesCurve[6] ? 1 : 0;
                pickValue -= *this->cost >= 7 && creaturesCurve[7] >= maxCreaturesCurve[7] ? 2 : 0;
            }
        }else{

            pickValue += itemsCurve[0] < minItemsCurve[0] ? 1 : 0;

            pickValue -= itemsCurve[0] >= maxItemsCurve[0] ? 1 : 0;
            pickValue -= *this->cardType == GREEN_ITEM && itemsCurve[1] >= maxItemsCurve[1] ? 1 : 0;
            pickValue -= *this->cardType == RED_ITEM && itemsCurve[2] >= maxItemsCurve[2] ? 1 : 0;
            pickValue -= *this->cardType == BLUE_ITEM && itemsCurve[3] >= maxItemsCurve[3] ? 1 : 0;
        }

        return pickValue;
    }

    int getBoardValue() const{
        int value = this->attack + this->defense;
        value += this->hasWard ? 1 : 0;
        value += this->hasLethal ? 1 : 0;
        value += this->hasDrain ? 1 : 0;
        value += this->hasGuard ? 1 : 0;
        return value;
    }

    void takeDamage(int amount){
        this->defense -= amount;
    }
};

class Player{
public:
    int health{};
    int maxMana{};
    int mana{};
    int deck{};
    int rune{};
    int handSize{};
    int turn{};
    int nextTurnDraw{};

    unordered_map<int, Card> cardsInHand;
    unordered_map<int, Card> creaturesInBoard;

    Player() = default;

    Player(int health, int mana, int deck, int rune, int turn){
        this->health = health;
        this->mana = mana;
        this->maxMana = mana;
        this->deck = deck;
        this->rune = rune;
        this->handSize = 0;
        this->turn = turn;
        this->nextTurnDraw = 0;
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

    int playCreature(int instanceId){
        Card & creature = this->cardsInHand[instanceId];

        this->mana -= *creature.cost;
        this->cardsInHand.erase(instanceId);
        creature.location = PLAYER_BOARD;
        creature.canAttack = creature.hasCharge;
        this->creaturesInBoard.insert({creature.instanceId, creature});
        this->health += *creature.myHealthChange;
        this->nextTurnDraw += *creature.cardDraw;

        return *creature.opponentHealthChange;
    }

    Player(const Player& other){
        this->health = other.health;
        this->mana = other.mana;
        this->deck = other.deck;
        this->rune = other.rune;
        this->handSize = other.handSize;
        this->turn = other.turn;
        this->nextTurnDraw = other.nextTurnDraw;
        this->maxMana = other.maxMana;
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

class BoardInfo{
public:
    int p1BoardValue = 0;
    int p2BoardValue = 0;
    int p1GuardValue = 0;
    int p2AttackPotential = 0;
    bool infoUpdated = false;

    BoardInfo() = default;
};

class State{
public:
    Player player1;
    Player player2;
    int turn{};
    int id{};


    State() = default;

    State(const Player *p1, const Player* p2){
        this->player1 = *p1;
        this->player2 = *p2;
    }

    bool operator < (const State & other) const;
};

class PSol{
public:

    int id;
    int parentId;
    Action * action;
    int score;

    PSol() = default;

    PSol(int id, int parentId, Action * action, int score):
            id(id),
            parentId(parentId),
            action(action),
            score(score)
    {};

    bool operator < (const PSol & other) const{
        return this->id < other.id;
    };

};

class StateManager{
public:

    static State* simulate(const State* initialState, const Action & action){
        auto * s = new State(&initialState->player1, &initialState->player2);
        simsNo++;

        // SUMMON id1
        if(action.actionType == SUMMON){
            int enemyDamage = s->player1.playCreature(action.id1);
            s->player2.health += enemyDamage;
        } else if (action.actionType == ATTACK){                                              // ATTACK id1 id2
            Card * attCreature = &s->player1.creaturesInBoard[action.id1];

            if(action.id2 == -1){
                s->player2.health -= attCreature->attack;
                if(attCreature->hasDrain){
                    s->player1.health += attCreature->attack;
                }
                attCreature->canAttack = false;
            } else{
                Card * defCreature = &s->player2.creaturesInBoard[action.id2];

                int damageGiven = false;
                int damageTaken = false;

                if(attCreature->attack > 0){
                    if(defCreature->hasWard){
                        defCreature->hasWard = false;
                    }else{
                        if(attCreature->hasBreakthrough){
                            s->player2.health -= max(attCreature->attack - defCreature->defense, 0);
                        }
                        if(attCreature->hasDrain){
                            s->player1.health += attCreature->attack;
                        }
                        defCreature->defense -= attCreature->attack;
                        damageGiven = true;
                    }
                }
                if(defCreature->attack > 0){
                    if(attCreature->hasWard){
                        attCreature->hasWard = false;
                    }else{
                        if(defCreature->hasDrain){
                            s->player2.health += defCreature->attack;
                        }

                        attCreature->defense -= defCreature->attack;
                        damageTaken = true;
                    }
                }
                if(attCreature->defense <= 0 || damageTaken && defCreature->hasLethal){
                    s->player1.creaturesInBoard.erase(action.id1);
                }
                if(defCreature->defense <= 0 || damageGiven && attCreature->hasLethal){
                    s->player2.creaturesInBoard.erase(action.id2);
                }
                attCreature->canAttack = false;
                attCreature->hasAttacked = true;
            }
        } else if(action.actionType == USE){                                // USE id1 id2
            Card * item = &s->player1.cardsInHand[action.id1];
            s->player1.mana -= *item->cost;
            if(*item->cardType == GREEN_ITEM){                              // USE id1 ownBoardCreatureId
                Card * target = &s->player1.creaturesInBoard[action.id2];
                target->hasCharge = target->hasCharge || item->hasCharge;
                if(target->hasCharge){
                    target->canAttack = !target->hasAttacked;
                }
                target->hasDrain = target->hasDrain || item->hasDrain;
                target->hasWard = target->hasWard || item->hasWard;
                target->hasGuard = target->hasGuard || item->hasGuard;
                target->hasLethal = target->hasLethal || item->hasLethal;
                target->hasBreakthrough = target->hasBreakthrough || item->hasBreakthrough;
                target->attack += item->attack;
                target->defense += item->defense;
            } else {
                if(action.id2 != -1){                                                   // USE id1 enemyBoardCreatureId
                    Card * target = &s->player2.creaturesInBoard[action.id2];
                    target->hasCharge = target->hasCharge && !item->hasCharge;
                    target->hasDrain = target->hasDrain && !item->hasDrain;
                    target->hasWard = target->hasWard && !item->hasWard;
                    target->hasGuard = target->hasGuard && !item->hasGuard;
                    target->hasLethal = target->hasLethal && !item->hasLethal;
                    target->hasBreakthrough = target->hasBreakthrough && !item->hasBreakthrough;
                    target->attack = max(0, target->attack + item->attack);
                    if(target->hasWard && item->defense < 0){
                        target->hasWard = false;
                    }else{
                        target->defense += item->defense;
                    }

                    if(target->defense <= 0){
                        s->player2.creaturesInBoard.erase(action.id2);
                    }
                }
                s->player1.health += *item->myHealthChange;
                s->player1.nextTurnDraw += *item->cardDraw;
                s->player2.health += *item->opponentHealthChange;
            }
            s->player1.cardsInHand.erase(action.id1);
        }

        if(s->player2.health <= s->player2.rune){
            int runesCrushed = (s->player2.rune - s->player2.health) / 5;
            s->player2.nextTurnDraw += runesCrushed;
            s->player2.rune -= 5 * runesCrushed;
        }
        return s;
    };

    static State* nextPlayer(const State* initialState){
        auto * s = new State(&initialState->player2, &initialState->player1);

        for(auto & pair: s->player1.creaturesInBoard){
            Card * c = &pair.second;
            s->player1.creaturesInBoard[c->instanceId].canAttack = true;
            s->player1.creaturesInBoard[c->instanceId].hasAttacked = false;
        }

        s->player1.handSize += 1 + s->player1.nextTurnDraw;
        s->player1.nextTurnDraw = 0;
        s->player1.mana = s->player1.maxMana + 1;

        return s;
    }

    static unordered_set<Action*> legalActions(const State* s){
        unordered_set<Action*> actions;

        // Legal summons and items
        for(auto & pair: s->player1.cardsInHand) {
            const Card *c = &pair.second;

            if (*c->cost <= s->player1.mana) {
                if (*c->cardType == CREATURE && s->player1.creaturesInBoard.size() < 6) {
                    auto * a = new Action(SUMMON, c->instanceId, 0);
                    actions.insert(a);
                } else if (*c->cardType == GREEN_ITEM) {
                    for (auto &targetPair: s->player1.creaturesInBoard) {
                        const Card *target = &targetPair.second;
                        auto * a = new Action(USE, c->instanceId, target->instanceId);
                        actions.insert(a);
                    }
                } else if (*c->cardType == RED_ITEM || *c->cardType == BLUE_ITEM && c->defense < 0) {
                    for (auto &targetPair: s->player2.creaturesInBoard) {
                        const Card *target = &targetPair.second;
                        auto * a = new Action(USE, c->instanceId, target->instanceId);
                        actions.insert(a);
                    }
                } else if (*c->cardType == BLUE_ITEM && c->defense >= 0) {
                    auto * a = new Action(USE, c->instanceId, -1);
                    actions.insert(a);
                }
            }
        }

        // Legal attacks
        unordered_set<Action*> guardAttacks;
        unordered_set<Action*> otherAttacks;
        for(auto & pair: s->player1.creaturesInBoard){
            const Card * c = &pair.second;


            if(!c->canAttack || c->attack <= 0 || c->hasAttacked){
                continue;
            }

            for(auto & targetPair: s->player2.creaturesInBoard){
                const Card * target = &targetPair.second;

                auto * a = new Action(ATTACK, c->instanceId, target->instanceId);
                if(target->hasGuard){
                    guardAttacks.insert(a);
                }else{
                    otherAttacks.insert(a);
                }
            }



            // Attack to opponent
            auto * a = new Action(ATTACK, c->instanceId, -1);
            otherAttacks.insert(a);
        }

        if(guardAttacks.empty()){
            actions.insert(otherAttacks.begin(), otherAttacks.end());
        }else{
            actions.insert(guardAttacks.begin(), otherAttacks.end());
        }

        return actions;
    }

    static int eval(const State* s){
        // Win condition
        if(s->player2.health <= 0){
            return 1000 - s->player1.turn;
        }
        // Lose condition
        if(s->player1.health <= 0){
            return -1000 + s->player1.turn;
        }
        int score = s->player1.health - 3*s->player2.health;

        int p1BoardValue = 0;
        int p2BoardValue = 0;
        int p1HealthAndGuard = s->player1.health;
        int p2TotalAttack = 0;


        for(auto & pair: s->player1.creaturesInBoard){
            const Card * creature = &pair.second;
            p1BoardValue += creature->getBoardValue();
            if(creature->hasGuard){
                p1HealthAndGuard += creature->defense;
            }
        }
        for(auto & pair: s->player2.creaturesInBoard){
            const Card * creature = &pair.second;
            p2BoardValue += creature->getBoardValue();
            p2TotalAttack += creature->attack;
        }
        score += 6*(s->player1.creaturesInBoard.size() - s->player2.creaturesInBoard.size());
        score += 2*(p1BoardValue - p2BoardValue);
        score += 2*(s->player1.handSize + s->player1.nextTurnDraw - s->player2.handSize - s->player2.nextTurnDraw);
        score += s->player2.creaturesInBoard.empty() ? 10 : 0;
        score -= s->player1.creaturesInBoard.empty() ? 10 : 0;
        score -= p2TotalAttack >= p1HealthAndGuard ? 100 : 0;

        return score;
    }

    static vector<Action *> dynamicSearch(State* initialState){
        int idCount = 0;
        unordered_map<int, PSol *> solTree;
        set<State *> statesToVisit;
        vector<Action *> solActions;

        solTree.insert({++idCount, new PSol(idCount, 0, new Action(3, 0, 0), StateManager::eval(initialState))});
        initialState->id = 1;
        statesToVisit.insert(initialState);

        State * stateVisiting;

        while(!statesToVisit.empty()){
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(high_resolution_clock::now() - start).count();
            if(elapsed >= 90){
                break;
            }
            stateVisiting = *std::next(statesToVisit.begin(), 0);
            int idParent = stateVisiting->id;

            for(Action * action: StateManager::legalActions(stateVisiting)){
                State * newState = StateManager::simulate(stateVisiting, *action);

                idCount++;
                int newScore = StateManager::eval(newState);
                int parentScore = solTree[idParent]->score;
                newState->id = idCount;

                solTree.insert({idCount, new PSol(idCount, idParent, action, newScore)});
                statesToVisit.insert(newState);
                if(statesToVisit.size() > 300){
                    statesToVisit.erase(std::next(statesToVisit.begin(), 300));
                }

            }
            statesToVisit.erase(stateVisiting);
        }

        if(solTree.size() <= 1){
            solActions.push_back(new Action(3, 0, 0));
            return solActions;
        }

        auto * bestSol = new PSol(0, 0, nullptr, -1000);
        PSol sol{};
        for(auto & pair: solTree){
            sol = *pair.second;
            if(bestSol->score < sol.score){
                *bestSol = sol;
            }
        }

        bool keepLooking = true;
        while(keepLooking){
            solActions.push_back(bestSol->action);
            bestSol = solTree[bestSol->parentId];
            if(!bestSol || bestSol->id == 1){
                keepLooking = false;
            }
        }

        std::reverse(solActions.begin(), solActions.end());

        return solActions;
    }
};

bool State::operator < (const State & other) const{
    return StateManager::eval(this) > StateManager::eval(&other);
};

// Given a creature, the best attack it can do ignoring allied creatures.
int bestAttack(Card* attackingCreature, Player* oppositePlayer){
    int target = -1;
    int valueGain = 0;
    for( auto& pair : oppositePlayer->creaturesInBoard){
        Card* opCreature = &pair.second;
        if(attackingCreature->attack >= opCreature->defense && valueGain < opCreature->getPickValue() -
                                                                           attackingCreature->getPickValue()){
            target = opCreature->instanceId;
            valueGain = opCreature->getPickValue() - attackingCreature->getPickValue();
        }
        if(opCreature->hasGuard){
            target = opCreature->instanceId;
            valueGain = opCreature->getPickValue() - attackingCreature->getPickValue();
            break;
        }
    }

    return target;
}

void executeActions(vector<Action *> actions){

    for(Action * a: actions){
        if(a->actionType == SUMMON){
            cout << "SUMMON " << a->id1 << ";";
        }else if(a->actionType == ATTACK){
            cout << "ATTACK " << a->id1 << " " << a->id2 << ";";
        }else if(a->actionType == USE){
            cout << "USE " << a->id1 << " " << a->id2 << ";";
        }else if(a->actionType == PASS){
            cout << "PASS";
        }
    }

    cout << endl;
}

// Pick between 3 cards based on the value of the cards.
int bestPick(){
    int maxValue = -100;
    Card * selectedCard = {};
    int selectedPick = 0;
    int cardNo = 0;
    for(Card* card: cardsToPick){
        if(card->getPickValue() > maxValue){
            selectedCard = card;
            selectedPick = cardNo;
            maxValue = card->getPickValue();
        }
        cardNo++;
    }

    int cardCost = *selectedCard->cost >= 7 ? 7 : *selectedCard->cost;

    if(*selectedCard->cardType == CREATURE){
        creaturesCurve[cardCost]++;
        if(selectedCard->hasLethal){
            habilitiesCurve['L']++;
        }else if(selectedCard->hasGuard){
            habilitiesCurve['G']++;
        }
    }else{
        itemsCurve[0]++;
        if(*selectedCard->cardType == GREEN_ITEM){
            itemsCurve[1]++;
        }else if(*selectedCard->cardType == RED_ITEM){
            itemsCurve[2]++;
        }else{
            itemsCurve[3]++;
        }
    }
    return selectedPick;
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

/*
 * For anyone trying to reuse contest code:
 * First two input lines have an extra int on the end (card draw)
 * Third line has an extra int on the end (number of opponent actions)
 * Then there are is a line for each opponentaction - these are slightly awkward to parse if you aren't reading entire
 *  lines in as they can have 3 or 4 fields.I'm just reading the entire line as a string and ignoring for now.
 * After that all inputs are the same as the contest (number of cards, then lines of card details).
 */
void initializeState(int turn){
    for (int i = 0; i < 2; i++) {
        int playerHealth;
        int playerMana;
        int playerDeck;
        int playerRune;
        int cardDraw;
        cin >> playerHealth >> playerMana >> playerDeck >> playerRune >> cardDraw; cin.ignore();
        players[i] = new Player(playerHealth, playerMana, playerDeck, playerRune, turn);
    }
    player1 = players[0];
    player2 = players[1];
    int opponentHand;
    int opponentActions;
    cin >> opponentHand >> opponentActions; cin.ignore();
    player2->handSize = opponentHand;
    string opponentAction;
    for (int i = 0; i< opponentActions; i++){
        cin >> opponentAction;
    }
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
        cards[i] = new Card(cardNumber, instanceId, location, cardType, cost, attack, defense, &abilities, myHealthChange, opponentHealthChange, cardDraw, true, false);
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
    pickValues.insert({{1, 4}, {2, 3}, {3, 6}, {4, 5}, {5, 4}, {6, 6}, {7, 6}, {8, 5}, {9, 6},
                       {10, 4}, {11, 4}, {12, 3}, {13, 5}, {14, 3}, {15, 5.1}, {16, 4}, {17, 6}, {18, 9}, {19, 5},
                       {20, 4}, {21, 6}, {22, 4}, {23, 6}, {24, 2}, {25, 3}, {26, 5}, {27, 5}, {28, 4}, {29, 4},
                       {30, 5}, {31, 3}, {32, 5}, {33, 6}, {34, 4}, {35, 3}, {36, 6}, {37, 6}, {38, 3}, {39, 4},
                       {40, 4}, {41, 5}, {42, 4}, {43, 5}, {44, 6}, {45, 4}, {46, 4}, {47, 3}, {48, 6}, {49, 6},
                       {50, 4}, {51, 6}, {52, 5}, {53, 6}, {54, 6}, {55, 2}, {56, 3}, {57, 2}, {58, 3}, {59, 5},
                       {60, 3}, {61, 5}, {62, 7}, {63, 3}, {64, 6}, {65, 7}, {66, 6}, {67, 7}, {68, 7}, {69, 7},
                       {70, 5}, {71, 6}, {72, 5}, {73, 6}, {74, 4}, {75, 5}, {76, 6}, {77, 6}, {78, 4}, {79, 6},
                       {80, 7}, {81, 6}, {82, 6}, {83, 5}, {84, 6}, {85, 3}, {86, 5}, {87, 4}, {88, 5}, {89, 3},
                       {90, 3}, {91, 7}, {92, 2}, {93, 4}, {94, 4}, {95, 7}, {96, 5}, {97, 4}, {98, 5}, {99, 5},
                       {100, 3}, {101, 5}, {102, 3}, {103, 6}, {104, 4}, {105, 4}, {106, 4}, {107, 3}, {108, 2}, {109, 5},
                       {110, 3}, {111, 5}, {112, 4}, {113, 2}, {114, 6}, {115, 5}, {116, 5}, {117, 2}, {118, 2}, {119, 4},
                       {120, 4}, {121, 3}, {122, 5}, {123, 5}, {124, 5}, {125, 4},{126, 4},{127, 3},{128, 6},{129, 4},
                       {130, 5},{131, 2},{132, 3},{133, 7},{134, 4},{135, 4},{136, 3},{137, 4},{138, 2},{139, 7.1},
                       {140, 3},{141, 5},{142, 2},{143, 2},{144, 8},{145, 3},{146, 4},{147, 5}, {148, 6},{149, 4},
                       {150, 7.1},{151, 7}, {152, 2}, {153, 2}, {154, 3}, {155, 5}, {156, 4}, {157, 3}, {158, 6}, {159, 4},
                       {160, 3}});

    creaturesCurve.insert({{0,0},{1,0},{2,0},{3,0},{4,0},{5,0},{6,0},{7,0}});
    itemsCurve.insert({{0,0},{1,0},{2,0},{3,0}});
    minCreaturesCurve.insert({{0, 1}, {1, 4}, {2, 6}, {3, 5}, {4, 4}, {5, 3}, {6, 0}, {7, 2}});
    maxCreaturesCurve.insert({{0, 2}, {1, 7}, {2, 8}, {3, 7}, {4, 6}, {5, 3}, {6, 2}, {7, 2}});
    minItemsCurve.insert({{0, 6}, {1, 2}, {2, 2}, {3, 2}});
    maxItemsCurve.insert({{0, 10}, {1, 4}, {2, 7}, {3, 4}});
    habilitiesCurve.insert({{'B', 0},{'C', 0}, {'D', 0},{'G', 0}, {'L', 0},{'W',0}});
    minHabilitiesCurve.insert({{'B', 0},{'C', 0}, {'D', 0},{'G', 4}, {'L', 2},{'W',0}});


    turn = 0;
    State * nextState;
    State * initialState;
    // game loop
    while (true) {
        simsNo = 0;
        initializeState(turn);
        start = high_resolution_clock::now();
        initialState = new State(player1, player2);

        // test

        if(turn < 30){
            for(Card* card: cardsToPick){
                cerr << " value: " << card->getPickValue() << " ";
            }
            cerr << endl;
            pick(bestPick());
            end();
        }else{
            executeActions(StateManager::dynamicSearch(initialState));
        }

        finish = high_resolution_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(finish - start).count();

        cerr << endl << "** Time: " << elapsed << " Sims: " << simsNo << endl;

        turn++;
    }
}