CANONICAL_COLUMNS = [
    "reg_no",
    "student_name",
    "class",
    "term",
    "marks",
    "attendance"
]


COLUMN_ALIASES = {
    "reg_no": [
        "reg no", "reg_no", "registration number",
        "registration no", "roll no", "roll number"
    ],
    "student_name": [
        "student name", "name", "student"
    ],
    "class": [
        "class", "grade", "std", "standard"
    ],
    "term": [
        "term", "exam", "semester", "assessment"
    ],
    "marks": [
        "marks", "score", "marks obtained"
    ],
    "attendance": [
        "attendance", "attendance %", "attendance percentage"
    ]
}

MARKS_MIN = 0
MARKS_MAX = 100
PASS_MARK = 35

ATTENDANCE_MIN = 0
ATTENDANCE_MAX = 100