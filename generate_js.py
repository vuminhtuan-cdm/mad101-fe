import json
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_JS = os.path.join(BASE_DIR, "exams.js")

exam_configs = [
    {
        "id": "exam_1",
        "code": "MAD101_SU26_FE_815892",
        "title": "Đề 1: MAD101 - SU26 - FE (815892)",
        "shortTitle": "Đề 1 (SU26 FE)",
        "type": "text",
        "filename": "MAD101_SU26_FE_815892.json"
    },
    {
        "id": "exam_2",
        "code": "MAD101_SP26_B5_FE_RE",
        "title": "Đề 2: Đề Thi FE - MAD101 - SP26 - B5 - FE/RE (Đề Ảnh)",
        "shortTitle": "Đề 2 (SP26 B5 Ảnh)",
        "type": "image",
        "filename": "MAD101_SP26_B5_FE_RE.json"
    },
    {
        "id": "exam_3",
        "code": "MAD101_SP26_RE",
        "title": "Đề 3: Đề Thi FE - MAD101 - SP26 - RE (Đề Ảnh)",
        "shortTitle": "Đề 3 (SP26 RE Ảnh)",
        "type": "image",
        "filename": "MAD101_SP26_RE.json"
    },
    {
        "id": "exam_4",
        "code": "MAD101_SP26_FE",
        "title": "Đề 4: Đề Thi FE - MAD101 - SP26 - FE (Đề Ảnh)",
        "shortTitle": "Đề 4 (SP26 FE Ảnh)",
        "type": "image",
        "filename": "MAD101_SP26_FE.json"
    },
    {
        "id": "exam_5",
        "code": "MAD101_FA25_RE",
        "title": "Đề 5: Đề Thi FE - MAD101 - FA25 - RE (Đề Ảnh)",
        "shortTitle": "Đề 5 (FA25 RE Ảnh)",
        "type": "image",
        "filename": "MAD101_FA25_RE.json"
    },
    {
        "id": "exam_6",
        "code": "MAD101_FA25_FE",
        "title": "Đề 6: Đề Thi FE - MAD101 - FA25 - FE (Đề Ảnh)",
        "shortTitle": "Đề 6 (FA25 FE Ảnh)",
        "type": "image",
        "filename": "MAD101_FA25_FE.json"
    }
]


def clean_non_math_escapes(text):
    """Replace literal \\n, \\t, \\quad outside KaTeX math blocks ($...$, $$...$$)."""
    if not text:
        return text
    parts = re.split(r'(\$\$[\s\S]*?\$\$|\$[^$\n]*?\$)', text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
        else:
            cleaned = (
                part.replace('\\n', '\n')
                    .replace('\\t', '    ')
                    .replace('\\quad ', '    ')
                    .replace('\\quad', '    ')
            )
            out.append(cleaned)
    return ''.join(out)


exams = []
all_combined_questions = []
all_counts = {}

for config in exam_configs:
    file_path = os.path.join(DATA_DIR, config["filename"])
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found.")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    counts = {}
    clean_questions = []

    for q in questions:
        raw_options = q.get("question_options", [])
        correct_labels = [opt["label"] for opt in raw_options if opt.get("is_correct")]
        correct_labels.sort()
        correct_str = ", ".join(correct_labels)

        counts[correct_str] = counts.get(correct_str, 0) + 1
        all_counts[correct_str] = all_counts.get(correct_str, 0) + 1

        img = q.get("local_image_url") or q.get("image_url")
        content = clean_non_math_escapes(q.get("content"))

        q_obj = {
            "id": f"{config['code']}_{q.get('id', q.get('order_num'))}",
            "raw_id": q.get("id"),
            "order_num": q.get("order_num", len(clean_questions) + 1),
            "exam_source": config["shortTitle"],
            "exam_code": config["code"],
            "content": content,
            "image_url": img,
            "type": q.get("type", "image" if img else "text"),
            "chapter_name": q.get("chapter_name", "MAD101"),
            "correct_answer": correct_str,
            "is_multi": len(correct_labels) > 1,
            "correct_count": len(correct_labels),
            "options": [
                {
                    "id": opt.get("id", f"{q.get('order_num')}_{opt.get('label')}"),
                    "label": opt.get("label"),
                    "content": clean_non_math_escapes(opt.get("content", "")),
                    "is_correct": opt.get("is_correct", False)
                }
                for opt in raw_options
            ]
        }
        clean_questions.append(q_obj)
        all_combined_questions.append(q_obj)

    config["questions"] = clean_questions
    config["counts"] = counts
    config["total"] = len(clean_questions)
    exams.append(config)

# Tạo đề tổng hợp toàn bộ 6 đề (300 câu)
all_exam_config = {
    "id": "exam_all",
    "code": f"ALL_{len(all_combined_questions)}",
    "title": f"TỔNG HỢP CẢ {len(exams)} ĐỀ ({len(all_combined_questions)} CÂU TOÀN DIỆN)",
    "shortTitle": f"🔥 Tổng Hợp {len(exams)} Đề ({len(all_combined_questions)} Câu)",
    "type": "mixed",
    "isAll": True,
    "questions": all_combined_questions,
    "counts": all_counts,
    "total": len(all_combined_questions)
}
exams.append(all_exam_config)

with open(OUTPUT_JS, "w", encoding="utf-8") as f:
    f.write("// Dữ liệu các bộ đề thi MAD101 - Toán Rời Rạc (Discrete Mathematics)\n")
    f.write("var EXAMS_DATA = " + json.dumps(exams, ensure_ascii=False, indent=2) + ";\n")
    f.write("if (typeof window !== 'undefined') { window.EXAMS_DATA = EXAMS_DATA; }\n")

print(f"Generated exams.js with {len(exams)} items ({len(exam_configs)} đề đơn + 1 đề tổng hợp {len(all_combined_questions)} câu)!")
