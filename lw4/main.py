import re
from collections import defaultdict
import csv
import sys

def read_moore_to_list(positions, file, alphabet):
    alphabet_set = set()  # Множество для хранения символов алфавита
    lines = file.readlines()

    # Чтение первой строки
    temp_row = lines[0].strip().split(';')
    temp_row_st = lines[1].strip().split(';')

    # Добавление состояний
    for i in range(1, len(temp_row)):
        state = {
            "state": temp_row_st[i],
            "output": temp_row[i],
            "transitions": []  # Переходы для текущего состояния
        }
        positions.append(state)

    # Чтение оставшихся строк
    for line in lines[2:]:
        temp_row = line.strip().split(';')
        input_sym = temp_row[0]

        if input_sym != "Оµ":
            alphabet_set.add(input_sym)
        print(input_sym, end=" ")

        for i in range(1, len(temp_row)):
            # Для каждого перехода собираем список состояний
            transition = {
                "inputSym": input_sym,
                "nextPos": temp_row[i].split(',') if temp_row[i] else []  # Множество состояний для каждого символа
            }
            positions[i - 1]["transitions"].append(transition)

    # Преобразование множества в список
    alphabet = list(alphabet_set)

    return positions, alphabet

def export_moore_automaton_to_csv(moore_automaton, filename):
    # Получаем все уникальные inputSym
    all_input_symbols = set()
    for state in moore_automaton:
        for transition in state['transitions']:
            #if transition['nextPos']:  # используемые символы ввода
            all_input_symbols.add(transition['inputSym'])

    all_input_symbols = sorted(all_input_symbols)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        output_row = ['']
        for state in moore_automaton:
            output_row.append(state['output'])
        writer.writerow(output_row)

        headers = [''] + [state['state'] for state in moore_automaton]
        writer.writerow(headers)

        #создаем строку в CSV
        for symbol in all_input_symbols:
            row = [symbol]

            for state in moore_automaton:
                # Ищем переход для данного символа
                next_states = []
                for transition in state['transitions']:
                    if transition['inputSym'] == symbol:
                        next_states.append(transition['nextPos'])
                    #  несколько переходов
                #row.append(next_states)
                if not next_states:
                    row.append('')
                else:
                    output_str = ','.join(next_states)  #  все состояния
                    row.append(output_str)

            writer.writerow(row)

    print(f"Moore automaton exported to {filename}")

def epsilon_closure(states, moore_automaton):
    """
    Нахождение ε-замыкания для множества состояний.
    """
    closure = set(states)
    changes = True
    while changes:
        changes = False
        for state in closure.copy():
            for transition in moore_automaton[state]['transitions']:
                if transition['inputSym'] == "Оµ":  # ε-переход
                    next_states = transition['nextPos']
                    for next_state in next_states:
                        if next_state not in closure:
                            closure.add(next_state)
                            changes = True
    return closure

def move(states, symbol, moore_automaton):
    """
    Получение множества состояний, в которые можно попасть из текущих состояний по символу.
    """
    next_states = set()
    for state in states:
        for transition in moore_automaton[state]['transitions']:
            if transition['inputSym'] == symbol:
                next_states.update(transition['nextPos'])
    return next_states

def convert_nfa_to_dfa(moore_automaton, alphabet):
    """
    Преобразование НКА в ДКА.
    """
    dfa_automaton = []
    state_map = {}
    queue = []
    initial_state = epsilon_closure([list(moore_automaton.keys())[0]], moore_automaton)
    state_map[frozenset(initial_state)] = "q0"  # Назначаем имя начального состояния ДКА
    queue.append(frozenset(initial_state))

    while queue:
        current_states = queue.pop(0)
        current_state_name = state_map[current_states]
        dfa_state = {
            "state": current_state_name,
            "output": moore_automaton[next(iter(current_states))]['output'],  # Выход для состояния
            "transitions": []
        }

        for symbol in alphabet:
            # Получаем множества состояний, в которые можно попасть по символу
            next_states = move(current_states, symbol, moore_automaton)
            if next_states:
                # Находим ε-замыкание для нового множества состояний
                next_closure = epsilon_closure(next_states, moore_automaton)
                frozen_next_closure = frozenset(next_closure)

                if frozen_next_closure not in state_map:
                    # Назначаем новое имя состоянию ДКА
                    new_state_name = f"q{len(state_map)}"
                    state_map[frozen_next_closure] = new_state_name
                    queue.append(frozen_next_closure)

                # Добавляем переход
                dfa_state['transitions'].append({
                    'inputSym': symbol,
                    'nextPos': state_map[frozen_next_closure]
                })
        print(dfa_state)
        dfa_automaton.append(dfa_state)

    return dfa_automaton

def main():

    if len(sys.argv) != 3:
        print("Usage: lab3 grammar.txt output.csv")
        sys.exit(1)

    grammar_file = sys.argv[1]
    output_file = sys.argv[2]

    positions = []  # Список для состояний
    alphabet = []   # Алфавит
    # output_file = "out.csv"

    with open(grammar_file, 'r') as file:
        positions, alphabet = read_moore_to_list(positions, file, alphabet)
    # for state in positions:
    #         print(f"Состояние: {state['state']}, Выход: {state['output']}")
    #         for transition in state['transitions']:
    #             print(f"  Переход по символу '{transition['inputSym']}': {', '.join(transition['nextPos'])}")
    #
    # print("States:", [state["state"] for state in positions])
    # print("Alphabet:", alphabet)
    moore_automaton = {}

    for state in positions:
        moore_automaton[state["state"]] = {
            "output": state["output"],
            "transitions": state["transitions"]
        }

    dfa_automaton = convert_nfa_to_dfa(moore_automaton, alphabet)

    export_moore_automaton_to_csv(dfa_automaton, output_file)
if __name__ == "__main__":
    main()
