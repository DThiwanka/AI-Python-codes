import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Initialize Pygame mixer
pygame.mixer.init()

# Default sounds (replace with your local paths or placeholders)
sounds = {
    'Kick': "kick.wav",
    'Snare': "snare.wav",
    'Hi-Hat': "hihat.wav",
    'Tom': "tom.wav",
    'Crash': "crash.wav"
}

# Load initial sounds
for key in sounds:
    if os.path.exists(sounds[key]):
        sounds[key] = pygame.mixer.Sound(sounds[key])
    else:
        sounds[key] = None

# Play sound function
def play_sound(name):
    sound = sounds.get(name)
    if sound:
        sound.set_volume(volume_scale.get() / 100)
        sound.play()
        status_var.set(f"Played: {name}")
    else:
        status_var.set(f"No sound loaded for: {name}")

# Load custom sound
def load_custom_sound(name):
    file_path = filedialog.askopenfilename(
        title=f"Select sound for {name}",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if file_path:
        try:
            sounds[name] = pygame.mixer.Sound(file_path)
            status_var.set(f"Loaded custom sound for: {name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sound: {e}")

# GUI setup
root = tk.Tk()
root.title("🎵 Drum Simulator (Tkinter Edition)")
root.geometry("500x400")
root.resizable(False, False)

status_var = tk.StringVar(value="Welcome! Select a pad or press a key.")

# Drum buttons
drum_frame = tk.Frame(root)
drum_frame.pack(pady=20)

for idx, drum_name in enumerate(sounds.keys()):
    frame = tk.Frame(drum_frame)
    frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10)
    
    tk.Button(frame, text=drum_name, font=("Arial", 14, "bold"), width=12, height=2,
              command=lambda n=drum_name: play_sound(n)).pack()
    
    tk.Button(frame, text="Load Sound", font=("Arial", 10),
              command=lambda n=drum_name: load_custom_sound(n)).pack(pady=5)

# Volume control
volume_frame = tk.Frame(root)
volume_frame.pack(pady=10)

tk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL)
volume_scale.set(80)
volume_scale.pack(side=tk.LEFT)

# Status bar
status_label = tk.Label(root, textvariable=status_var, relief="sunken", anchor="w", font=("Arial", 10))
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Keyboard bindings
key_mapping = {
    'a': 'Kick',
    's': 'Snare',
    'd': 'Hi-Hat',
    'f': 'Tom',
    'g': 'Crash'
}

def on_key(event):
    drum = key_mapping.get(event.char.lower())
    if drum:
        play_sound(drum)

root.bind("<Key>", on_key)

root.mainloop()
