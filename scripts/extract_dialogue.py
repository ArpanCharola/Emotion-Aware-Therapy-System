import os
import json
from PyPDF2 import PdfReader

def extract_dialogues(pdf_path, assistant_tags, user_tags):
    reader = PdfReader(pdf_path)
    dialogues = []
    current_dialogue = []

    def match_tag(line, tag_list):
        """Returns matching tag or None if not found"""
        for tag in tag_list:
            if line.lower().startswith(tag.lower()):
                return tag
        return None

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        # Show first 500 chars for debugging
        print(f"\n--- Page {page_num + 1} Preview ---\n{text[:500]}\n------------")

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            assistant_tag = match_tag(line, assistant_tags)
            user_tag = match_tag(line, user_tags)
            if assistant_tag:
                if current_dialogue:
                    dialogues.append(current_dialogue)
                    current_dialogue = []
                # Try "Speaker:", "Speaker -", or tag only
                if ":" in line:
                    content = line.split(":", 1)[-1]
                elif "-" in line:
                    content = line.split("-", 1)[-1]
                else:
                    content = line[len(assistant_tag):]
                current_dialogue.append({"role": "assistant", "content": content.strip()})
            elif user_tag:
                if ":" in line:
                    content = line.split(":", 1)[-1]
                elif "-" in line:
                    content = line.split("-", 1)[-1]
                else:
                    content = line[len(user_tag):]
                current_dialogue.append({"role": "user", "content": content.strip()})
            else:
                if current_dialogue:
                    current_dialogue[-1]["content"] += " " + line.strip()

    if current_dialogue:
        dialogues.append(current_dialogue)
    return dialogues

def save_dialogues_jsonl(dialogues, out_path):
    with open(out_path, 'w', encoding='utf-8') as f_out:
        for dialogue in dialogues:
            json.dump(dialogue, f_out, ensure_ascii=False)
            f_out.write('\n')
    print(f"Dialogues saved to {out_path}")

if __name__ == "__main__":
    # === CHANGE BELOW FOR EACH SCRIPT ===
    filename = "cbt_script.pdf"
    assistant_tags = ["Dr. Beck"]           # Put all possible therapist tags for the current file
    user_tags = ["Alex"]                    # Put all possible client tags for the current file

    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', filename))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', filename.replace('.pdf', '.jsonl')))

    dialogues = extract_dialogues(input_path, assistant_tags, user_tags)
    print(f"Extracted {len(dialogues)} dialogues from {filename}")

    save_dialogues_jsonl(dialogues, output_path)
