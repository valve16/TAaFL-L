import re
from collections import defaultdict
import csv
import sys

def preprocess_grammar(grammar_text):
    processed_text = re.sub(r'\|\s*\n\s*', '| ', grammar_text.strip())
    return processed_text

def parse_grammar(grammar_text):
    """Парсинг грамматики для определения её типа и генерации переходов."""
    lines = grammar_text.strip().split('\n')
    transitions = defaultdict(list)
    start_symbol = None
    first_line = lines[0].strip()
    leftGr = False
    left_regex = re.compile(r'^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$')
    right_regex = re.compile(r'^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$')
    left_rule = left_regex.match(first_line)
    right_rule = right_regex.match(first_line)

    for i, line in enumerate(lines):
        line = line.strip()
        right_match = right_regex.match(line)
        left_match = left_regex.match(line)

        if not line:
            continue
        if left_rule:
            leftGr = True
            process_left_rule(left_match, transitions)
        elif right_rule:

            process_right_rule(right_match, transitions)
        else:
            raise ValueError(f"Некорректная строка грамматики: {line}")

    return transitions, leftGr

def process_left_rule(match, transitions):
    """Обработка левого правила."""
    next_non_terminal = match.group(1)
    rules = match.group(2).split('|')

    for rule in rules:
        rule = rule.strip()
        parts = rule.split()
        if len(parts) == 1:
            terminal = parts[0]
            transitions["H"].append((terminal, next_non_terminal))
            #print("H", terminal, next_non_terminal)
        else:
            prev_non_terminal = parts[0].replace('<', '').replace('>', '')
            terminal = parts[1] if len(parts) > 1 else ''
            transitions[prev_non_terminal].append((terminal, next_non_terminal))
            #print(prev_non_terminal, terminal, next_non_terminal)

def process_right_rule(match, transitions):
    """Обработка правого правила."""
    non_terminal = match.group(1)
    rules = match.group(2).split('|')

    for rule in rules:
        rule = rule.strip()
        parts = rule.split()
        if len(parts) == 1:
            terminal = parts[0]
            transitions[non_terminal].append((terminal, "F"))
        else:
            terminal = parts[0]
            next_non_terminal = parts[1].replace('<', '').replace('>', '')
            transitions[non_terminal].append((terminal, next_non_terminal))


def generate_right_moore_automaton(transitions):
    """Генерация автомата Мура."""
    state_mapping = {}
    state_counter = 0

    # Генерация уникальных состояний для каждого нетерминала
    for non_terminal in transitions.keys():
        state_mapping[non_terminal] = {
            "state": f"q{state_counter}",
            "output": f""
        }
        #print(non_terminal, state_mapping[non_terminal]["state"])
        state_counter += 1

    state_mapping["F"] = {
        "state": f"q{state_counter}",
        "output": f"F"
    }

    all_input_symbols = set()
    for state, trans in transitions.items():
        for terminal, _ in trans:
            all_input_symbols.add(terminal)
    # for rules in transitions.values():
    #     for _, next_non_terminal in rules:
    #         if next_non_terminal and next_non_terminal not in state_mapping:
    #             state_mapping[next_non_terminal] = {
    #                 "state": f"q{state_counter}",
    #                 "output": f"y{state_counter}"
    #             }
    #             state_counter += 1

    # Генерация переходов автомата Мура
    moore_automaton = []

    for state, trans in transitions.items():
        current_state = state_mapping[state]["state"]
        current_output = state_mapping[state]["output"]

        transitions_list = []

        for symbol in all_input_symbols:
            next_state = None
            # Находим переход для данного символа
            for terminal, next_state_row in trans:
                if terminal == symbol:
                    next_state = state_mapping[next_state_row]["state"]
                    break

            # Если перехода нет, оставляем next_state пустым
            if not next_state:
                next_state = ""

            transitions_list.append({"inputSym": symbol, "nextPos": next_state})

        moore_automaton.append({
            "state": current_state,
            "output": current_output,
            "transitions": transitions_list
        })
        #print(current_state, current_output, transitions_list)

    moore_automaton.append({
        "state": state_mapping["F"]["state"],
        "output": state_mapping["F"]["output"],
        "transitions": [{"inputSym": _, "nextPos": ""} for _ in all_input_symbols]
    })


    # for state in moore_automaton:
    #     print(state)

    return moore_automaton

def generate_left_moore_automaton(transitions):
    state_mapping = {}
    state_counter = 0

    state_mapping["H"] = {
        "state": f"q{state_counter}",
        "output": f""
    }
    state_counter += 1
    #print(list(transitions.values())[0][0][1])
    # Генерация уникальных состояний для каждого нетерминала
    for non_terminal in transitions.keys():
        if non_terminal != "H":
            state_mapping[non_terminal] = {
                "state": f"q{state_counter}",
                "output": f""
            }
            state_counter += 1
        print(non_terminal, state_mapping[non_terminal]["state"])


    state_mapping[list(transitions.values())[0][0][1]] = {
        "state": f"q{state_counter}",
        "output": f"F"
    }

    all_input_symbols = set()
    for state, trans in transitions.items():
        for terminal, _ in trans:
            all_input_symbols.add(terminal)
    # for rules in transitions.values():
    #     for _, next_non_terminal in rules:
    #         if next_non_terminal and next_non_terminal not in state_mapping:
    #             state_mapping[next_non_terminal] = {
    #                 "state": f"q{state_counter}",
    #                 "output": f"y{state_counter}"
    #             }
    #             state_counter += 1

    # Генерация переходов автомата Мура
    moore_automaton = []




    for state, trans in transitions.items():
        current_state = state_mapping[state]["state"]
        current_output = state_mapping[state]["output"]

        transitions_list = []

        for symbol in all_input_symbols:
            next_state = None
            # Находим переход для данного символа
            for terminal, next_state_row in trans:
                if terminal == symbol:
                    next_state = state_mapping[next_state_row]["state"]
                    break

            # Если перехода нет, оставляем next_state пустым
            if not next_state:
                next_state = ""

            transitions_list.append({"inputSym": symbol, "nextPos": next_state})

        moore_automaton.append({
            "state": current_state,
            "output": current_output,
            "transitions": transitions_list
        })
        print(current_state, current_output, transitions_list)

    moore_automaton.append({
        "state": state_mapping[list(transitions.values())[0][0][1]]["state"],
        "output": "F",
        "transitions": [{"inputSym": _, "nextPos": ""} for _ in all_input_symbols]
    })

    # for state in moore_automaton:
    #     print(state)

    return moore_automaton

def export_moore_automaton_to_csv(moore_automaton, filename):
    # Получаем все уникальные inputSym
    all_input_symbols = set()
    for state in moore_automaton:
        for transition in state['transitions']:
            all_input_symbols.add(transition['inputSym'])

    all_input_symbols = sorted(all_input_symbols)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        headers = [''] + [state['state'] for state in moore_automaton]
        writer.writerow(headers)

        # Для каждого inputSym создаем строку в CSV
        for symbol in all_input_symbols:
            row = [symbol]
            for state in moore_automaton:
                # Ищем переход для данного символа
                next_pos = ""
                for transition in state['transitions']:
                    if transition['inputSym'] == symbol:
                        next_pos = transition['nextPos']
                        break
                row.append(next_pos)
            writer.writerow(row)

    print(f"Moore automaton exported to {filename}")



def main():
    if len(sys.argv) != 3:
        print("Usage: lab3 grammar.txt output.csv")
        sys.exit(1)

    grammar_file = sys.argv[1]
    output_file = sys.argv[2]

    # Чтение грамматики из файла
    with open(grammar_file, 'r', encoding='utf-8') as file:
        input_grammar = file.read()

    input_grammar = preprocess_grammar(input_grammar)
    transitions, leftGr = parse_grammar(input_grammar)

    if leftGr:
        moore_automaton = generate_left_moore_automaton(transitions)
    else:
        moore_automaton = generate_right_moore_automaton(transitions)
    export_moore_automaton_to_csv(moore_automaton, output_file)
if __name__ == "__main__":
    main()
