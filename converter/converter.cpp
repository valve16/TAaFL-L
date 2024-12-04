#include "converter.h"


std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}



struct Trans
{
    std::string inputSym;
    std::string nextPos;
    std::string outSym;
};

struct MealyState
{
    std::string curr;
    std::vector<Trans> transitions;
};

struct MooreState
{
    std::string state;
    std::string newState;
    std::string output;
    std::unordered_map<std::string, std::string> transitions; // input -> next state
};

std::vector<MealyState> findReachableStates(const std::vector<MealyState>& mealyStates)
{
    if (mealyStates.empty()) return {};

    std::unordered_set<std::string> visited;
    std::queue<std::string> toVisit;
    std::vector<MealyState> reachableStates;

    visited.insert(mealyStates[0].curr);
    toVisit.push(mealyStates[0].curr);
    reachableStates.push_back(mealyStates[0]);

    while (!toVisit.empty())
    {
        std::string currentState = toVisit.front();
        toVisit.pop();

        for (const auto& state : mealyStates)
        {
            if (state.curr == currentState)
            {
                for (const auto& transition : state.transitions)
                {
                    if (visited.find(transition.nextPos) == visited.end())
                    {
                        visited.insert(transition.nextPos);
                        toVisit.push(transition.nextPos);

                        for (const auto& nextState : mealyStates)
                        {
                            if (nextState.curr == transition.nextPos)
                            {
                                reachableStates.push_back(nextState);
                                std::cout << nextState.curr << "\n";
                                break;
                            }
                        }
                    }
                }
                break;
            }
        }
    }

    return reachableStates;
}




std::vector<MooreState> convertToMoore(const std::vector<MealyState>& mealyAutomaton)
{

    std::vector<MooreState> mooreAutomaton;
    std::set<std::string> stateOutputSet; // словарь
    std::unordered_map<std::string, std::string> eqNewStateOld; // first - old; second - new(q1, q2);

    std::string startState = mealyAutomaton.begin()->curr;
    std::string mooreStartState;

    bool foundStartState = false;
    std::string currOutSym = "";

    for (const auto& pos : mealyAutomaton)
    {
        for (const auto& trans : pos.transitions)
        {
            if (trans.nextPos == startState)
            {
                if (currOutSym.empty())
                {
                    currOutSym = trans.outSym;
                }
                else
                {
                    currOutSym = min(trans.outSym, currOutSym);
                }
            }
        }
    }

    if (currOutSym.empty())
    {
        currOutSym = "-";
    }


    for (const auto& pos : mealyAutomaton)
    {
        for (const auto& trans : pos.transitions)
        {
            if (trans.nextPos == startState && currOutSym == trans.outSym)
            {
                std::string mooreState = trans.nextPos + "_" + trans.outSym;
                std::string NewMooreStateName = "q0"; // начальное состояние для автомата мура
                MooreState newMooreState;

                stateOutputSet.insert(mooreState).second;
                newMooreState.state = mooreState;
                newMooreState.output = trans.outSym;
                newMooreState.newState = NewMooreStateName;

                mooreAutomaton.push_back(newMooreState);

                eqNewStateOld[mooreState] = NewMooreStateName;
                std::cout << mooreState << " " << NewMooreStateName;
                foundStartState = true;
                break;
            }
        }
        if (foundStartState)
        {
            break;
        }
    }

    if (currOutSym == "-")
    {
        std::string mooreState = startState + "_-";
        std::string NewMooreStateName = "q0"; // начальное состояние для автомата мура
        MooreState newMooreState;


        stateOutputSet.insert(mooreState).second;
        newMooreState.state = mooreState;
        newMooreState.output = "-";
        newMooreState.newState = NewMooreStateName;
        mooreAutomaton.push_back(newMooreState);

        eqNewStateOld[mooreState] = NewMooreStateName;

    }

    int i = 1;
    bool needNextState = false;
    bool needCheck = true;
    while (needCheck)
    {
        std::set<std::string> newNameStateSet;
        std::set<std::string> outSymSet;
        std::set<std::string> baseNameStateSet;

        for (const auto& pos : mealyAutomaton)
        {
            for (const auto& trans : pos.transitions)
            {
                std::string mooreState = trans.nextPos + "_" + trans.outSym;

                if (trans.nextPos == startState || needNextState) // Проверка на наличие этого состояния в автомате Мура
                {
                    if (stateOutputSet.insert(mooreState).second)
                    {
                        needNextState = false;
                        outSymSet.insert(trans.outSym);

                        startState = trans.nextPos; //след значение в переходах

                        std::string NewMooreStateName = "q" + std::to_string(i);
                        newNameStateSet.insert(NewMooreStateName);

                        baseNameStateSet.insert(mooreState);

                        i++;
                    }
                }
            }
        }
        if (needCheck && needNextState)
        {
            needCheck = false;
        }

        if (needCheck)
        {
            std::vector<MooreState> tempMooreStates;
            needNextState = true; // отсортировать по возростанию curr state

            auto stateIt = newNameStateSet.begin();
            auto outIt = outSymSet.begin();
            auto baseStIt = baseNameStateSet.begin();
            while (stateIt != newNameStateSet.end() && outIt != outSymSet.end() && baseStIt != baseNameStateSet.end())
            {
                MooreState mooreState;
                mooreState.newState = *stateIt; //q1...
                mooreState.output = *outIt; // y1....
                mooreState.state = *baseStIt; //S0_y0 ...


                tempMooreStates.push_back(mooreState);
                std::string tempString = *stateIt;
                eqNewStateOld[*baseStIt] = *stateIt;
                ++stateIt;
                ++outIt;
                ++baseStIt;
            }
            mooreAutomaton.insert(mooreAutomaton.end(), tempMooreStates.begin(), tempMooreStates.end());

        }
    }

    // переходы для состояний Мура
    for (auto& mooreState : mooreAutomaton)
    {
        std::string baseState = mooreState.state.substr(0, mooreState.state.find('_'));
        std::string partOut = mooreState.state.substr(mooreState.state.find('_') + 1);

        for (const auto& pos : mealyAutomaton)
        {
            if (pos.curr == baseState)
            {
                for (const auto& trans : pos.transitions)
                {
                    std::string nextState = trans.nextPos + "_" + trans.outSym;
                    std::string nextMooreState = eqNewStateOld[nextState];
                    mooreState.transitions[trans.inputSym] = nextMooreState;
                }
            }
        }
    }

    return mooreAutomaton;
}


std::vector<MealyState> ReadMealyToVec(std::vector<MealyState>& positions, std::ifstream& file)
{

    std::string line;
    std::getline(file, line);
    std::vector<std::string> tempRow = split(line, ';');


    for (size_t i = 1; i < tempRow.size(); ++i) // Пропускаем первый элемент (пустой)
    {
        MealyState currPos;
        currPos.curr = tempRow[i]; // Текущая позиция - имя состояния
        positions.push_back(currPos);
    }

    std::vector<std::string> tRow;
    while (std::getline(file, line))
    {
        tempRow = split(line, ';');
        std::string input_sym = tempRow[0];
        for (int i = 0; i < positions.size(); i++)
        {

            Trans trans;
            tRow = split(tempRow[i + 1], '/');
            trans.inputSym = input_sym;
            trans.nextPos = tRow[0];
            trans.outSym = tRow[1];
            positions[i].transitions.push_back(trans);
        }
    };
    file.close();

    return positions;
}

void ConvertMooreToMealy(std::ifstream& file, std::ofstream& outFile)
{
    std::string line;
    std::getline(file, line);
    std::vector<std::string> tempRowOut = split(line, ';');
    std::getline(file, line);
    std::vector<std::string> tempRowStates = split(line, ';');


    std::unordered_map<std::string, std::string> stateToOut;

    for (size_t i = 1; i < tempRowOut.size(); ++i)
    {
        stateToOut[tempRowStates[i]] = tempRowOut[i]; // выходной символ соответсвующий состоянию
        outFile << ";" << tempRowStates[i];
    }
    outFile << "\n";

    while (std::getline(file, line))
    {
        std::vector<std::string> rowNextSt = split(line, ';');
        outFile << rowNextSt[0] << ";";
        for (int i = 1; i < rowNextSt.size(); i++)
        {
            outFile << rowNextSt[i] << "/" << stateToOut[rowNextSt[i]] << ";";
        }
        outFile << "\n";
    }
    file.close();
    outFile.close();
}

void WriteMooreToFile(std::vector<MooreState>& mooreAutomaton, std::ofstream& outFile)
{
    if (outFile.is_open())
    {

        outFile << ";";
        for (const auto& state : mooreAutomaton)
        {
            outFile << state.output << ";";
        }
        outFile << "\n";

        outFile << ";";
        for (const auto& state : mooreAutomaton)
        {
            outFile << state.newState << ";";
        }
        outFile << "\n";

        for (const auto& trans : mooreAutomaton[0].transitions)
        {
            outFile << trans.first << ";"; // Символ входа (inputSym)
            for (const auto& state : mooreAutomaton)
            {
                outFile << state.transitions.at(trans.first) << ";";

            }
            outFile << "\n";
        }

        outFile.close();
        std::cout << "CSV file has been created successfully.\n";
    }
    else
    {
        std::cerr << "Failed to open file for writing.\n";
    }

}

int main(int argc, char* argv[])
{

    std::string nameOperation;

    nameOperation = argv[1];
    std::string inputFileName = argv[2];
    std::string outputFileName = argv[3];   
    


    std::ifstream file(inputFileName);
    std::ofstream outFile(outputFileName);

    if (!file.is_open())
    {
        std::cerr << "Ошибка при открытии файла!" << std::endl;
        return 1;
    }


    if (nameOperation == "mealy-to-moore")
    {
        std::vector<MealyState> mealyStates;
        mealyStates = ReadMealyToVec(mealyStates, file);

        std::vector<MealyState> reachableStates = findReachableStates(mealyStates);

        std::vector<MooreState> mooreAutomaton = convertToMoore(reachableStates);
        WriteMooreToFile(mooreAutomaton, outFile);
    }
    else if (nameOperation == "moore-to-mealy")
    {
        ConvertMooreToMealy(file, outFile);
    }
    return 0;
}


