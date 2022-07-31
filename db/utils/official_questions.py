import os

# https://stackoverflow.com/a/5137509
dir_path = os.path.dirname(os.path.realpath(__file__))

problems_path = os.path.join(dir_path, '../../problems/scripts')
explanation_path = os.path.join(dir_path, '../../problems/explanations')

official_questions = [["problem_1_multiplication.py", 'Feature', 'Multiplication', "problem_1.md", 0],
                      ["problem_2_square_of_a_number.py", 'Bug', 'Square of a number', "problem_2.md", 0],
                      ["problem_3_slot_machine.py", 'Bug', 'Slot machine', "problem_3.md", 1],
                      ["problem_4_double_base_palindrome.py", 'Bug', 'Double base palindrome',
                       "problem_4.md", 1],
                      ["problem_5_count_ways_to_make_number.py", 'Feature',
                       'Count Ways to make a number', "problem_5.md", 2],
                      ["problem_6_truncatable_number.py", 'Feature',
                       'Is it truncatable?', "problem_6.md", 2],
                      ["problem_7_lychrel_numbers.py", 'Feature',
                       'Is it Lychrel?', "problem_7.md", 2],
                      ["problem_8_count_letter.py", 'Bug',
                       'Count letter of a number?', "problem_8.md", 2],
                      ["problem_9_amicable_numbers.py", 'Bug',
                       'Are amicable numbers', "problem_9.md", 2],
                      ["problem_10_monopoly_simulation.py", 'Feature',
                       'Monopoly Probabilities', "problem_10.md", 3],
                      ["problem_11_are_equal.py", 'Bug',
                       'Are equal?', "problem_11.md", 0],
                      ["problem_12_equal_except_integers.py", 'Feature',
                       'integers do the opposite', "problem_12.md", 0]
                      ]

# Change to absolute paths
for row in official_questions:
    full_script_path = os.path.abspath(os.path.join(problems_path, row[0]))
    full_explanation_path = os.path.abspath(os.path.join(explanation_path, row[3]))

    row[0] = full_script_path
    row[3] = full_explanation_path
