"""
evaluate.py

This file evaluates the Jeopardy question answering system.

It loads the Jeopardy questions, searches the Whoosh Wikipedia index for each
category/clue pair, returns the top-ranked Wikipedia page title, and compares
that prediction against the correct answer.

The program writes:
    results/predictions.csv  - one row per question
    results/metrics.txt      - overall Precision@1 score
"""

import os
import csv
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser


QUESTIONS_FILE = "data/questions.txt"
INDEX_DIR = "index"
RESULTS_DIR = "results"


def normalize_answer(text):
    """
    Normalizes answers before comparison.

    This helps avoid marking answers wrong because of small formatting
    differences such as capitalization, underscores, and leading 'the'.
    """
    text = text.lower().strip().replace("_", " ")

    if text.startswith("the "):
        text = text[4:]

    return text


def is_correct_answer(predicted_answer, gold_answer):
    """
    Checks whether the predicted answer matches the gold answer.

    Some gold answers contain multiple acceptable forms separated by '|',
    for example:
        The Salvation Army|Salvation Army

    The prediction is counted as correct if it matches any acceptable answer.
    """
    predicted = normalize_answer(predicted_answer)

    acceptable_answers = gold_answer.split("|")

    for answer in acceptable_answers:
        if predicted == normalize_answer(answer):
            return True

    return False


def load_questions(filepath):
    """
    Loads the Jeopardy questions.

    Expected format:
        CATEGORY
        CLUE
        ANSWER
        blank line

    Returns:
        A list of dictionaries, where each dictionary has:
            category
            clue
            answer
    """
    questions = []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        lines = [line.strip() for line in file.readlines()]

    i = 0

    while i < len(lines):
        # Skip blank lines between questions
        if lines[i] == "":
            i += 1
            continue

        category = lines[i]
        clue = lines[i + 1]
        answer = lines[i + 2]

        questions.append({
            "category": category,
            "clue": clue,
            "answer": answer
        })

        # Move to the next question block
        i += 4

    return questions


def search_index(searcher, parser, category, clue):
    """
    Searches the Whoosh index using the Jeopardy category and clue.

    The top-ranked Wikipedia page title is returned as the predicted answer.
    """
    query_text = category + " " + clue
    query = parser.parse(query_text)

    results = searcher.search(query, limit=10)

    if len(results) == 0:
        return ""

    return results[0]["title"]


def save_predictions(rows):
    """
    Saves one prediction row per question to results/predictions.csv.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output_path = os.path.join(RESULTS_DIR, "predictions.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "number",
            "category",
            "clue",
            "gold_answer",
            "predicted_answer",
            "correct"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_metrics(total, correct_count):
    """
    Saves the overall Precision@1 score to results/metrics.txt.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    incorrect_count = total - correct_count
    precision_at_1 = correct_count / total if total > 0 else 0

    output_path = os.path.join(RESULTS_DIR, "metrics.txt")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(f"Total questions: {total}\n")
        file.write(f"Correct: {correct_count}\n")
        file.write(f"Incorrect: {incorrect_count}\n")
        file.write(f"Precision@1: {precision_at_1:.4f}\n")


def evaluate():
    """
    Runs retrieval for all Jeopardy questions and evaluates performance.
    """
    questions = load_questions(QUESTIONS_FILE)
    print(f"Loaded {len(questions)} questions.")

    index = open_dir(INDEX_DIR)

    rows = []
    correct_count = 0

    with index.searcher() as searcher:
        parser = MultifieldParser(["title", "content"], schema=index.schema)

        for number, question in enumerate(questions, start=1):
            predicted_answer = search_index(
                searcher,
                parser,
                question["category"],
                question["clue"]
            )

            correct = is_correct_answer(
                predicted_answer,
                question["answer"]
            )

            if correct:
                correct_count += 1

            rows.append({
                "number": number,
                "category": question["category"],
                "clue": question["clue"],
                "gold_answer": question["answer"],
                "predicted_answer": predicted_answer,
                "correct": correct
            })

            print(
                f"{number}. Gold: {question['answer']} | "
                f"Predicted: {predicted_answer} | Correct: {correct}"
            )

    total = len(questions)

    save_predictions(rows)
    save_metrics(total, correct_count)

    precision_at_1 = correct_count / total if total > 0 else 0

    print()
    print("Evaluation complete.")
    print(f"Total questions: {total}")
    print(f"Correct: {correct_count}")
    print(f"Incorrect: {total - correct_count}")
    print(f"Precision@1: {precision_at_1:.4f}")


if __name__ == "__main__":
    evaluate()