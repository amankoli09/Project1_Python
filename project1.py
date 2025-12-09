"""
advanced_student_system.py
Advanced Student Management System (single-file)
Features:
 - Student class with per-subject marks
 - Gradebook manager with Add/Edit/Delete/Search
 - Compute averages, top students, grade distribution
 - Save/Load JSON persistence
 - Export CSV
 - Input validation and helpful prompts
"""

import json
import csv
from typing import Dict, List, Optional, Tuple


class Student:
    """Represents a student with name, roll and a dict of subject->marks."""
    def __init__(self, name: str, roll: int, marks: Optional[Dict[str, float]] = None):
        self.name = name.strip()
        self.roll = int(roll)
        self.marks = marks or {}  # e.g. {"Math": 85.0, "Physics": 78.5}

    def set_mark(self, subject: str, mark: float):
        assert 0 <= mark <= 100, "Mark must be between 0 and 100."
        self.marks[subject.strip()] = float(mark)

    def get_average(self) -> Optional[float]:
        if not self.marks:
            return None
        total = sum(self.marks.values())
        return total / len(self.marks)

    def to_dict(self) -> Dict:
        return {"name": self.name, "roll": self.roll, "marks": self.marks}

    @staticmethod
    def from_dict(d: Dict):
        return Student(name=d["name"], roll=d["roll"], marks=d.get("marks", {}))

    def __repr__(self):
        avg = self.get_average()
        avg_str = f"{avg:.2f}" if avg is not None else "N/A"
        return f"Student(name={self.name!r}, roll={self.roll}, avg={avg_str})"


class Gradebook:
    """Manages many Student objects and provides utility operations."""
    def __init__(self):
        self.students: Dict[int, Student] = {}  # key = roll number

    # ---------------- Basic CRUD ----------------
    def add_student(self, student: Student) -> None:
        if student.roll in self.students:
            raise ValueError(f"Roll {student.roll} already exists.")
        self.students[student.roll] = student

    def get_student(self, roll: int) -> Optional[Student]:
        return self.students.get(int(roll))

    def delete_student(self, roll: int) -> bool:
        return self.students.pop(int(roll), None) is not None

    def edit_student_name(self, roll: int, new_name: str) -> bool:
        s = self.get_student(roll)
        if not s:
            return False
        s.name = new_name.strip()
        return True

    # --------------- Searching / Listing ---------------
    def search_by_name(self, name_substring: str) -> List[Student]:
        q = name_substring.strip().lower()
        return [s for s in self.students.values() if q in s.name.lower()]

    def list_all(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.roll)

    # ---------------- Statistics ----------------
    def class_average(self) -> Optional[float]:
        avgs = [s.get_average() for s in self.students.values() if s.get_average() is not None]
        if not avgs:
            return None
        return sum(avgs) / len(avgs)

    def top_n_students(self, n: int = 3) -> List[Tuple[Student, float]]:
        scored = [(s, (s.get_average() or 0.0)) for s in self.students.values()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]

    def grade_distribution(self) -> Dict[str, int]:
        """
        Returns a grade bucket distribution:
         - 'A' : avg >= 80
         - 'B' : 60 <= avg < 80
         - 'C' : 50 <= avg < 60
         - 'D' : 40 <= avg < 50
         - 'F' : avg < 40 or no marks
        """
        buckets = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in self.students.values():
            avg = s.get_average()
            if avg is None:
                buckets["F"] += 1
            elif avg >= 80:
                buckets["A"] += 1
            elif avg >= 60:
                buckets["B"] += 1
            elif avg >= 50:
                buckets["C"] += 1
            elif avg >= 40:
                buckets["D"] += 1
            else:
                buckets["F"] += 1
        return buckets

    # ---------------- Persistence ----------------
    def save_to_json(self, filepath: str) -> None:
        payload = [s.to_dict() for s in self.list_all()]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved {len(payload)} students to {filepath}.")

    def load_from_json(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        loaded = 0
        for item in data:
            s = Student.from_dict(item)
            self.students[s.roll] = s
            loaded += 1
        print(f"Loaded {loaded} students from {filepath}.")

    def export_to_csv(self, filepath: str) -> None:
        # Collect all subjects to make columns consistent
        subjects = set()
        for s in self.students.values():
            subjects.update(s.marks.keys())
        subjects = sorted(subjects)

        headers = ["roll", "name"] + subjects + ["average"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for s in self.list_all():
                row = [s.roll, s.name]
                for sub in subjects:
                    row.append(s.marks.get(sub, ""))
                avg = s.get_average()
                row.append(f"{avg:.2f}" if avg is not None else "")
                writer.writerow(row)
        print(f"Exported {len(self.students)} students to {filepath}.")


# ----------------- Helper functions for CLI -----------------
def input_int(prompt: str) -> int:
    while True:
        try:
            val = int(input(prompt))
            return val
        except ValueError:
            print("Please enter a valid integer.")


def input_float(prompt: str) -> float:
    while True:
        try:
            val = float(input(prompt))
            return val
        except ValueError:
            print("Please enter a valid number.")


def create_student_interactive() -> Student:
    name = input("Name: ").strip()
    roll = input_int("Roll (integer): ")
    s = Student(name=name, roll=roll)
    print("Enter marks for subjects. Type 'done' when finished.")
    while True:
        subj = input(" Subject name (or 'done'): ").strip()
        if subj.lower() == "done":
            break
        mark_in = input(f"  Mark for {subj}: ").strip()
        try:
            mark = float(mark_in)
            s.set_mark(subj, mark)
        except (ValueError, AssertionError) as e:
            print("  Invalid mark:", e)
    return s


def show_student_details(s: Student):
    print("--------")
    print(f"Name: {s.name}")
    print(f"Roll: {s.roll}")
    if not s.marks:
        print("Marks: No marks recorded.")
    else:
        for sub, m in s.marks.items():
            print(f"  {sub}: {m}")
        avg = s.get_average()
        print(f"Average: {avg:.2f}")


def sample_data() -> Gradebook:
    gb = Gradebook()
    s1 = Student("Aman Koli", 101, {"Math": 85, "Physics": 78, "Chemistry": 90})
    s2 = Student("Bala Rao", 102, {"Math": 65, "Physics": 70})
    s3 = Student("Chitra Sen", 103, {"Math": 92, "English": 88, "Biology": 85})
    for s in (s1, s2, s3):
        gb.add_student(s)
    return gb


# ----------------- Command-line menu -----------------
def main_menu():
    gb = Gradebook()
    print("Would you like to load sample data? (y/n)")
    if input().strip().lower() == "y":
        gb = sample_data()
        print("Sample data loaded.")

    while True:
        print("\n--- Advanced Student Management ---")
        print("1) Add student")
        print("2) View all students")
        print("3) Search by name")
        print("4) View student by roll")
        print("5) Edit student name or marks")
        print("6) Delete student")
        print("7) Class statistics")
        print("8) Save to JSON")
        print("9) Load from JSON (replace current)")
        print("10) Export CSV")
        print("11) Exit")

        choice = input("Choose (1-11): ").strip()
        if choice == "1":
            try:
                s = create_student_interactive()
                gb.add_student(s)
                print("Student added.")
            except Exception as e:
                print("Failed to add student:", e)

        elif choice == "2":
            all_students = gb.list_all()
            if not all_students:
                print("No students.")
            for s in all_students:
                show_student_details(s)

        elif choice == "3":
            q = input("Enter name substring to search: ").strip()
            results = gb.search_by_name(q)
            if not results:
                print("No matches.")
            for s in results:
                show_student_details(s)

        elif choice == "4":
            r = input_int("Enter roll: ")
            s = gb.get_student(r)
            if not s:
                print("Not found.")
            else:
                show_student_details(s)

        elif choice == "5":
            r = input_int("Enter roll to edit: ")
            s = gb.get_student(r)
            if not s:
                print("No student with that roll.")
                continue
            print("1) Edit name")
            print("2) Add/Edit marks")
            print("3) Remove a subject mark")
            subchoice = input("Choose (1-3): ").strip()
            if subchoice == "1":
                newname = input("New name: ").strip()
                gb.edit_student_name(r, newname)
                print("Name updated.")
            elif subchoice == "2":
                subj = input("Subject name: ").strip()
                try:
                    mark = input_float("Mark (0-100): ")
                    s.set_mark(subj, mark)
                    print("Mark set.")
                except AssertionError as e:
                    print("Error:", e)
            elif subchoice == "3":
                subj = input("Subject name to remove: ").strip()
                if subj in s.marks:
                    s.marks.pop(subj)
                    print("Removed.")
                else:
                    print("Subject not found.")
            else:
                print("Invalid option.")

        elif choice == "6":
            r = input_int("Enter roll to delete: ")
            if gb.delete_student(r):
                print("Deleted.")
            else:
                print("Not found.")

        elif choice == "7":
            avg = gb.class_average()
            if avg is None:
                print("No averages available yet.")
            else:
                print(f"Class average: {avg:.2f}")
            print("Top 3 students:")
            for s, sc in gb.top_n_students(3):
                print(f"  Roll {s.roll} - {s.name} => {sc:.2f}")
            print("Grade distribution:")
            for k, v in gb.grade_distribution().items():
                print(f"  {k}: {v}")

        elif choice == "8":
            path = input("JSON filepath to save (e.g. students.json): ").strip()
            try:
                gb.save_to_json(path)
            except Exception as e:
                print("Error saving:", e)

        elif choice == "9":
            path = input("JSON filepath to load (e.g. students.json): ").strip()
            try:
                gb = Gradebook()  # replace current
                gb.load_from_json(path)
            except Exception as e:
                print("Error loading:", e)

        elif choice == "10":
            path = input("CSV filepath to export (e.g. students.csv): ").strip()
            try:
                gb.export_to_csv(path)
            except Exception as e:
                print("Error exporting:", e)

        elif choice == "11":
            print("Bye!")
            break

        else:
            print("Invalid choice. Please pick 1-11.")


if __name__ == "__main__":
    main_menu()
