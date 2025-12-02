#!/usr/bin/env python3
"""
Quiz Generator App - quiz_app.py
Simple local quiz application (no external libraries required).
"""

import json
import random
import csv
from datetime import datetime
import os
import threading

# ---------------- TIMER SYSTEM ---------------- #

def timed_input(prompt, timeout=10):
    answer = [None]

    def get_input():
        answer[0] = input(prompt)

    t = threading.Thread(target=get_input)
    t.daemon = True
    t.start()
    t.join(timeout)

    if t.is_alive():
        print("\n⏳ Time's up!")
        return None
    return answer[0]

# ---------------- FILES ---------------- #

QUESTIONS_FILE = "questions.json"
RESULTS_FILE = "quiz_results.csv"

# ---------------- QUESTION LOADING ---------------- #

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_questions(questions):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

# ---------------- QUIZ ENGINE ---------------- #

def take_quiz(questions, num_questions=None):
    if not questions:
        print("No questions available. Add questions first.\n")
        return

    if num_questions is None or num_questions > len(questions):
        num_questions = len(questions)

    quiz_qs = random.sample(questions, num_questions)
    score = 0
    answers = []

    for i, q in enumerate(quiz_qs, start=1):
        print(f"\nQ{i}. {q['question']}")
        for idx, opt in enumerate(q["options"], start=1):
            print(f"  {idx}. {opt}")

        # ------ TIMER ANSWER INPUT ------
        while True:
            user_input = timed_input("Your answer (number): ", timeout=10)

            if user_input is None:
                print("You ran out of time!")
                is_correct = False
                correct_index = q["answer_index"] + 1
                answers.append({
                    "question": q["question"],
                    "selected": None,
                    "correct": correct_index,
                    "is_correct": False
                })
                break

            try:
                choice = int(user_input)
                if 1 <= choice <= len(q["options"]):
                    break
                else:
                    print("Choice out of range. Try again.")
            except ValueError:
                print("Please enter a valid number.")

        correct_index = q["answer_index"] + 1
        is_correct = (choice == correct_index)

        if user_input is not None:
            if is_correct:
                print("Correct!")
                score += 1
            else:
                print(f"Wrong! Correct answer: {correct_index}. {q['options'][q['answer_index']]}")

        answers.append({
            "question": q["question"],
            "selected": choice if user_input is not None else None,
            "correct": correct_index,
            "is_correct": is_correct
        })

    print(f"\nQuiz completed. Score: {score} / {num_questions}\n")
    save_result(score, num_questions, answers)
    return score, num_questions

# ---------------- SAVE RESULTS ---------------- #

def save_result(score, total, answers):
    exists = os.path.exists(RESULTS_FILE)
    now = datetime.now().isoformat(timespec='seconds')

    with open(RESULTS_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "score", "total", "percentage"])
        writer.writerow([now, score, total, f"{(score/total*100):.2f}"])

    detail_file = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(detail_file, "w", encoding="utf-8") as f:
        json.dump(
            {"timestamp": now, "score": score, "total": total, "answers": answers},
            f, indent=2, ensure_ascii=False
        )

    print(f"Results saved to {RESULTS_FILE} and {detail_file}\n")

# ---------------- ADD QUESTION ---------------- #

def add_question(questions):
    print("\nAdd a new question (leave blank to cancel)")
    qtext = input("Question text: ").strip()
    if qtext == "":
        print("Cancelled.\n")
        return

    opts = []
    for i in range(4):
        opt = input(f"Option {i+1}: ").strip()
        opts.append(opt)

    while True:
        try:
            ai = int(input("Correct option number (1-4): ").strip())
            if 1 <= ai <= 4:
                break
            print("Enter between 1 and 4.")
        except ValueError:
            print("Please enter a number.")

    tags_input = input("Tags (comma-separated, e.g., easy,math): ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else []

    question = {
        "question": qtext,
        "options": opts,
        "answer_index": ai - 1,
        "tags": tags
    }

    questions.append(question)
    save_questions(questions)
    print("Question added.\n")

# ---------------- LIST QUESTIONS ---------------- #

def list_questions(questions):
    if not questions:
        print("No questions in database.\n")
        return

    print("\nQuestions in DB:")
    for i, q in enumerate(questions, start=1):
        print(f"{i}. {q['question']} (Answer: {q['answer_index']+1})")
    print("")

# ---------------- EXPORT CSV ---------------- #

def export_questions_csv(questions, filename="questions_export.csv"):
    if not questions:
        print("No questions to export.\n")
        return

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question","opt1","opt2","opt3","opt4","answer_index","tags"])
        for q in questions:
            row = [
                q["question"], *q["options"],
                q["answer_index"]+1,
                ",".join(q.get("tags", []))
            ]
            writer.writerow(row)

    print(f"Exported questions to {filename}\n")

# ---------------- MAIN MENU ---------------- #

def main_menu():
    questions = load_questions()

    while True:
        print("=== Quiz Generator App ===")
        print("1. Take Quiz (all questions)")
        print("2. Take Quiz (choose number of questions)")
        print("3. Add Question (admin)")
        print("4. List Questions")
        print("5. Export Questions to CSV")
        print("6. Exit")
        print("7. Levels (Easy / Medium / Hard)")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            take_quiz(questions)

        elif choice == "2":
            try:
                n = int(input("Number of questions: ").strip())
                if n > 0:
                    take_quiz(questions, n)
                else:
                    print("Enter a positive number.\n")
            except ValueError:
                print("Enter a valid number.\n")

        elif choice == "3":
            add_question(questions)

        elif choice == "4":
            list_questions(questions)

        elif choice == "5":
            fname = input("Export filename (default: questions_export.csv): ").strip()
            if fname == "":
                fname = "questions_export.csv"
            export_questions_csv(questions, fname)

        elif choice == "6":
            print("Exiting. Goodbye!")
            break

        elif choice == "7":
            print("\n=== LEVELS ===")
            print("1. Easy")
            print("2. Medium")
            print("3. Hard")
            level = input("Choose level: ").strip()

            diff_map = {"1": "easy", "2": "medium", "3": "hard"}
            diff = diff_map.get(level)

            if diff:
                filtered = [q for q in questions if diff in q.get("tags", [])]
                if filtered:
                    take_quiz(filtered)
                else:
                    print(f"No {diff} questions available.\n")
            else:
                print("Invalid level.\n")

        else:
            print("Invalid choice. Try again.\n")


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    main_menu()
