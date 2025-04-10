import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk
import keyboard
import time
import re
import os

# Load images after root is initialized
def load_key_images():
    images = {}
    for key in ["LP", "MP", "HP", "LK", "MK", "HK"]:
        try:
            img_path = os.path.join("images", f"{key.lower()}.png")
            img = Image.open(img_path).resize((30, 30))
            images[key] = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading {key}.png:", e)
            images[key] = None
    return images

def convert_notes_to_notation(notes: str) -> str:
    # IO: Increase Octave, DO: Decrease Octave
    notation_map = {
        "C": "HP", "C#": "LP+MP+HP", "Db": "LP+MP+HP",
        "D": "LP+HP", "D#": "MP+HP", "Eb": "MP+HP",
        "E": "LP+MP", "F": "LP", "F#": "MP", "Gb": "MP",
        "G": "HK", "G#": "MK+HK", "Ab": "MK+HK",
        "A": "LK+MK", "A#": "LK", "Bb": "LK",
        "B": "MK", "8": "IO", "2": "DO"
    }

    notes_list = notes.split()
    converted_notes = []

    for note in notes_list:
        if re.match(r'^wait\d+(\.\d+)?$', note):
            converted_notes.append(note)
        else:
            combo = []
            i = 0
            while i < len(note):
                if i+1 < len(note) and note[i+1] in ['#', 'b']:
                    full_note = note[i:i+2]
                    i += 2
                else:
                    full_note = note[i]
                    i += 1
                combo.append(notation_map.get(full_note, "Invalid note"))
            converted_notes.append("|".join(combo))

    return " ".join(converted_notes)

def convert_notation_to_notes(notation: str) -> str:
    base_reverse_map = {
        "HP": "C", "LP+MP+HP": "C#",
        "LP+HP": "D", "MP+HP": "D#",
        "LP+MP": "E", "LP": "F", "MP": "F#",
        "HK": "G", "MK+HK": "G#",
        "LK+MK": "A", "LK": "A#", "MK": "B",
        "IO": "8", "DO": "2"
    }

    reverse_map = {"+".join(sorted(k.split("+"))): v for k, v in base_reverse_map.items()}

    parts = notation.split()
    notes = []
    for part in parts:
        if re.match(r'^wait\d+(\.\d+)?$', part):
            notes.append(part)
        else:
            simultaneous = part.split('|')
            reconstructed = ""
            for combo in simultaneous:
                sorted_combo = "+".join(sorted(combo.split('+')))
                note = reverse_map.get(sorted_combo, "Unknown")
                if note == "Unknown":
                    reconstructed += "?"
                else:
                    reconstructed += note
            notes.append(reconstructed)
    return " ".join(notes)

def simulate_typing(notation: str, default_delay=0.3):
    key_map = {
        "LP": "u",
        "MP": "i",
        "HP": "o",
        "LK": "j",
        "MK": "k",
        "HK": "l",
        "IO": "space",
        "DO": "s"
    }
    combos = notation.split()
    for combo in combos:
        if combo.startswith("wait"):
            try:
                delay_time = float(combo[4:])
                time.sleep(delay_time)
            except ValueError:
                continue
        else:
            simultaneous_notes = combo.split("|")
            keys_to_press = set()
            for note_combo in simultaneous_notes:
                keys = note_combo.split("+")
                for key in keys:
                    key = key.strip()
                    if key in key_map:
                        keys_to_press.add(key_map[key])
            for key in keys_to_press:
                keyboard.press(key)
            time.sleep(0.1)
            for key in keys_to_press:
                keyboard.release(key)
            time.sleep(default_delay)

def convert():
    input_notes = note_entry.get()
    converted_text = convert_notes_to_notation(input_notes)
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, converted_text)
    output_text.config(state=tk.DISABLED)

def reverse_convert():
    input_notation = notation_entry.get()
    converted_notes = convert_notation_to_notes(input_notation)
    reverse_output.config(state=tk.NORMAL)
    reverse_output.delete("1.0", tk.END)
    reverse_output.insert(tk.END, converted_notes)
    reverse_output.config(state=tk.DISABLED)

def auto_type():
    converted_text = output_text.get("1.0", tk.END).strip()
    if not converted_text:
        return

    try:
        delay = float(delay_entry.get())
    except ValueError:
        delay = 0.3

    countdown_time = 3
    countdown_label = tk.Label(frame1, text="", font=("Helvetica", 20), fg="red", bg="#f4f4f4")
    countdown_label.pack(pady=5, before=note_entry)

    def countdown(i):
        if i > 0:
            countdown_label.config(text=f"Tooting starts in {i}...")
            root.after(1000, countdown, i - 1)
        else:
            countdown_label.config(text="Tooting...")
            root.update()
            time.sleep(0.5)
            countdown_label.destroy()
            simulate_typing(converted_text, default_delay=delay)

    countdown(countdown_time)

root = tk.Tk()
root.title("Band Auto Tooter 3000")
root.geometry("800x600")
root.configure(bg="#f4f4f4")

key_images = load_key_images()

main_frame = tk.Frame(root, bg="#f4f4f4")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_frame, bg="#f4f4f4")
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(main_frame, bg="#f9f9f9", relief=tk.GROOVE, borderwidth=2)
right_frame.pack(side="right", fill="both", expand=False, padx=10)

notebook = ttk.Notebook(left_frame)
notebook.pack(pady=10, expand=True)

# Tab 1 - Note to Notation
frame1 = tk.Frame(notebook, bg="#f4f4f4")
frame1.pack(fill="both", expand=True)
notebook.add(frame1, text="Notes ➜ Notation")

tk.Label(frame1, text="Enter Notes (e.g. C D wait1 CD FG wait0.5 G):", bg="#f4f4f4").pack(pady=5)
note_entry = tk.Entry(frame1, width=50)
note_entry.pack(pady=5)

tk.Label(frame1, text="Delay between notes (seconds):", bg="#f4f4f4").pack(pady=5)
delay_entry = tk.Entry(frame1, width=10)
delay_entry.insert(0, "0.3")
delay_entry.pack(pady=5)

convert_button = tk.Button(frame1, text="Convert", command=convert, bg="#4CAF50", fg="white", width=15)
convert_button.pack(pady=5)

auto_type_button = tk.Button(frame1, text="Auto Tooting", command=auto_type, bg="#2196F3", fg="white", width=15)
auto_type_button.pack(pady=5)

tk.Label(frame1, text="Converted Notation:", bg="#f4f4f4").pack(pady=5)
output_text = scrolledtext.ScrolledText(frame1, width=60, height=5, state=tk.DISABLED, font=("Courier", 10))
output_text.pack(pady=5)

# Tab 2 - Notation to Note
frame2 = tk.Frame(notebook, bg="#f4f4f4")
frame2.pack(fill="both", expand=True)
notebook.add(frame2, text="Notation ➜ Notes")

tk.Label(frame2, text="Enter Notation (e.g. HP LP+MP+HP LP|HP):", bg="#f4f4f4").pack(pady=5)
notation_entry = tk.Entry(frame2, width=50)
notation_entry.pack(pady=5)

reverse_button = tk.Button(frame2, text="Convert Back", command=reverse_convert, bg="#FF5722", fg="white", width=15)
reverse_button.pack(pady=5)

tk.Label(frame2, text="Converted Notes:", bg="#f4f4f4").pack(pady=5)
reverse_output = scrolledtext.ScrolledText(frame2, width=60, height=5, state=tk.DISABLED, font=("Courier", 10))
reverse_output.pack(pady=5)

# Reference on the right panel
tk.Label(right_frame, text="Move List", font=("Helvetica", 20, "bold"), bg="#f9f9f9").pack(pady=10)

ref_canvas = tk.Canvas(right_frame, bg="#f9f9f9", width=280)
ref_canvas.pack(padx=10, pady=5, fill="both", expand=True)

notation_to_note = {
    "HP": "C", "LP+MP+HP": "C#/Db",
    "LP+HP": "D", "MP+HP": "D#/Eb",
    "LP+MP": "E", "LP": "F", "MP": "F#/Gb",
    "HK": "G", "MK+HK": "G#/Ab",
    "LK+MK": "A", "LK": "A#/Bb", "MK": "B"
}

def add_key_image_row(canvas, notation, keys, note):
    frame = tk.Frame(canvas, bg="#f9f9f9")
    frame.pack(pady=4, anchor="w")
    for key in keys:
        if key_images.get(key):
            tk.Label(frame, image=key_images[key], bg="#f9f9f9").pack(side="left", padx=1)
        else:
            tk.Label(frame, text=key, bg="#f9f9f9").pack(side="left", padx=1)
    tk.Label(frame, text=f"  ➜ {note}", bg="#f9f9f9", anchor="w", font=(20)).pack(side="left")

for notation, note in notation_to_note.items():
    keys = notation.split("+")
    add_key_image_row(ref_canvas, notation, keys, note)

root.mainloop()