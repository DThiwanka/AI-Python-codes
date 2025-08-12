import pygame
import os
import time
import tkinter as tk
from tkinter import filedialog
import json
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Virtual Drum Kit Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Drum kit configuration with 12 sounds
DRUM_SOUNDS = {
    'kick': {'key': pygame.K_a, 'file': 'kick.wav', 'rect': pygame.Rect(400, 500, 120, 60), 'label': 'Kick (A)'},
    'snare': {'key': pygame.K_s, 'file': 'snare.wav', 'rect': pygame.Rect(300, 400, 100, 50), 'label': 'Snare (S)'},
    'hi_hat_closed': {'key': pygame.K_d, 'file': 'hi_hat_closed.wav', 'rect': pygame.Rect(200, 300, 80, 40), 'label': 'Hi-Hat Closed (D)'},
    'hi_hat_open': {'key': pygame.K_f, 'file': 'hi_hat_open.wav', 'rect': pygame.Rect(250, 250, 80, 40), 'label': 'Hi-Hat Open (F)'},
    'crash': {'key': pygame.K_g, 'file': 'crash.wav', 'rect': pygame.Rect(600, 200, 100, 50), 'label': 'Crash (G)'},
    'tom_high': {'key': pygame.K_h, 'file': 'tom_high.wav', 'rect': pygame.Rect(350, 300, 90, 45), 'label': 'Tom High (H)'},
    'tom_mid': {'key': pygame.K_j, 'file': 'tom_mid.wav', 'rect': pygame.Rect(450, 300, 90, 45), 'label': 'Tom Mid (J)'},
    'tom_low': {'key': pygame.K_k, 'file': 'tom_low.wav', 'rect': pygame.Rect(550, 300, 90, 45), 'label': 'Tom Low (K)'},
    'ride': {'key': pygame.K_l, 'file': 'ride.wav', 'rect': pygame.Rect(650, 250, 100, 50), 'label': 'Ride (L)'},
    'splash': {'key': pygame.K_z, 'file': 'splash.wav', 'rect': pygame.Rect(700, 200, 80, 40), 'label': 'Splash (Z)'},
    'china': {'key': pygame.K_x, 'file': 'china.wav', 'rect': pygame.Rect(150, 200, 80, 40), 'label': 'China (X)'},
    'cowbell': {'key': pygame.K_c, 'file': 'cowbell.wav', 'rect': pygame.Rect(500, 400, 80, 40), 'label': 'Cowbell (C)'},
}

# Drum kit presets
PRESETS = {
    'Default': {
        'kick': 'kick.wav',
        'snare': 'snare.wav',
        'hi_hat_closed': 'hi_hat_closed.wav',
        'hi_hat_open': 'hi_hat_open.wav',
        'crash': 'crash.wav',
        'tom_high': 'tom_high.wav',
        'tom_mid': 'tom_mid.wav',
        'tom_low': 'tom_low.wav',
        'ride': 'ride.wav',
        'splash': 'splash.wav',
        'china': 'china.wav',
        'cowbell': 'cowbell.wav',
    },
    'Rock': {
        'kick': 'kick_rock.wav',
        'snare': 'snare_rock.wav',
        'hi_hat_closed': 'hi_hat_closed_rock.wav',
        'hi_hat_open': 'hi_hat_open_rock.wav',
        'crash': 'crash_rock.wav',
        'tom_high': 'tom_high_rock.wav',
        'tom_mid': 'tom_mid_rock.wav',
        'tom_low': 'tom_low_rock.wav',
        'ride': 'ride_rock.wav',
        'splash': 'splash_rock.wav',
        'china': 'china_rock.wav',
        'cowbell': 'cowbell_rock.wav',
    },
    'Jazz': {
        'kick': 'kick_jazz.wav',
        'snare': 'snare_jazz.wav',
        'hi_hat_closed': 'hi_hat_closed_jazz.wav',
        'hi_hat_open': 'hi_hat_open_jazz.wav',
        'crash': 'crash_jazz.wav',
        'tom_high': 'tom_high_jazz.wav',
        'tom_mid': 'tom_mid_jazz.wav',
        'tom_low': 'tom_low_jazz.wav',
        'ride': 'ride_jazz.wav',
        'splash': 'splash_jazz.wav',
        'china': 'china_jazz.wav',
        'cowbell': 'cowbell_jazz.wav',
    },
    'Electronic': {
        'kick': 'kick_electronic.wav',
        'snare': 'snare_electronic.wav',
        'hi_hat_closed': 'hi_hat_closed_electronic.wav',
        'hi_hat_open': 'hi_hat_open_electronic.wav',
        'crash': 'crash_electronic.wav',
        'tom_high': 'tom_high_electronic.wav',
        'tom_mid': 'tom_mid_electronic.wav',
        'tom_low': 'tom_low_electronic.wav',
        'ride': 'ride_electronic.wav',
        'splash': 'splash_electronic.wav',
        'china': 'china_electronic.wav',
        'cowbell': 'cowbell_electronic.wav',
    },
    'Custom': {}  # For user-saved presets
}

# Recording, playback, and metronome variables
recording = False
playing_back = False
recorded_notes = []
playback_start_time = 0
playback_index = 0
metronome_on = False
bpm = 120
metronome_sound = None
last_beat_time = 0
beat_interval = 60 / bpm

# Sound and UI variables
sounds = {}
highlight_timers = {name: 0 for name in DRUM_SOUNDS}
HIGHLIGHT_DURATION = 0.1
volume = 0.5
current_preset = 'Default'
volume_rect = pygame.Rect(50, 600, 200, 20)
volume_handle = pygame.Rect(50 + int(volume * 200), 595, 10, 30)
bpm_rect = pygame.Rect(300, 600, 200, 20)
bpm_handle = pygame.Rect(300 + int((bpm - 60) / 240 * 200), 595, 10, 30)  # BPM range: 60-300
dragging_volume = False
dragging_bpm = False

# Load sounds
def load_sounds(preset='Default'):
    global sounds, metronome_sound
    sounds.clear()
    
    print(f"Loading preset: {preset}")
    
    # Ensure all drums have sounds
    for drum, info in DRUM_SOUNDS.items():
        try:
            # Try to load from preset first
            if preset in PRESETS and drum in PRESETS[preset]:
                sound_file = PRESETS[preset][drum]
                sounds[drum] = pygame.mixer.Sound(sound_file)
                print(f"Loaded {drum} from preset: {sound_file}")
            else:
                # Fall back to default file
                sounds[drum] = pygame.mixer.Sound(info['file'])
                print(f"Loaded {drum} from default: {info['file']}")
            
            sounds[drum].set_volume(volume)
            
        except (FileNotFoundError, pygame.error) as e:
            # Generate synthetic sound if file not found
            print(f"File not found for {drum}, generating synthetic sound: {e}")
            freq = get_drum_frequency(drum)
            sounds[drum] = generate_drum_sound(drum, freq)
            sounds[drum].set_volume(volume)
    
    # Load metronome sound
    try:
        metronome_sound = pygame.mixer.Sound('metronome_click.wav')
        metronome_sound.set_volume(volume)
    except (FileNotFoundError, pygame.error):
        print("Metronome sound not found, generating synthetic click")
        metronome_sound = generate_drum_sound('click', 1000)
        metronome_sound.set_volume(volume)

def get_drum_frequency(drum_name):
    """Get appropriate frequency for each drum type"""
    frequencies = {
        'kick': 60,
        'snare': 200,
        'hi_hat_closed': 8000,
        'hi_hat_open': 6000,
        'crash': 4000,
        'tom_high': 400,
        'tom_mid': 300,
        'tom_low': 200,
        'ride': 3000,
        'splash': 5000,
        'china': 3500,
        'cowbell': 800,
        'click': 1000
    }
    return frequencies.get(drum_name, 440)

def generate_drum_sound(drum_name, frequency):
    """Generate more realistic drum sounds based on drum type"""
    sample_rate = 44100
    
    if drum_name == 'kick':
        # Kick drum: low frequency with quick decay
        duration = 0.3
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        freq_envelope = frequency * np.exp(-t * 8)  # Frequency drops
        tone = np.sin(2 * np.pi * freq_envelope * t) * np.exp(-t * 6)
        
    elif drum_name == 'snare':
        # Snare: mix of tone and noise
        duration = 0.2
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        tone = np.sin(2 * np.pi * frequency * t) * 0.3
        noise = np.random.normal(0, 0.5, samples)
        tone = (tone + noise) * np.exp(-t * 12)
        
    elif 'hi_hat' in drum_name or drum_name in ['crash', 'ride', 'splash', 'china']:
        # Cymbals: high frequency noise with metallic ring
        duration = 0.15 if 'hi_hat_closed' in drum_name else 0.8
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        noise = np.random.normal(0, 0.4, samples)
        metallic = np.sin(2 * np.pi * frequency * t) * 0.2
        tone = (noise + metallic) * np.exp(-t * (20 if 'closed' in drum_name else 3))
        
    elif 'tom' in drum_name:
        # Toms: pitched drums with resonance
        duration = 0.4
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        tone = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 4)
        # Add some harmonics
        tone += 0.3 * np.sin(4 * np.pi * frequency * t) * np.exp(-t * 6)
        
    elif drum_name == 'cowbell':
        # Cowbell: metallic with specific harmonics
        duration = 0.2
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        tone = (np.sin(2 * np.pi * frequency * t) + 
                0.5 * np.sin(2 * np.pi * frequency * 1.5 * t)) * np.exp(-t * 8)
        
    else:  # click or other
        duration = 0.05
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        tone = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 50)
    
    # Normalize and convert to stereo
    tone = np.clip(tone * 0.8, -1, 1)
    tone = (tone * 32767).astype(np.int16)
    stereo_tone = np.column_stack((tone, tone))
    return pygame.sndarray.make_sound(stereo_tone)

# Load custom sound files
def load_custom_sound(drum):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        try:
            DRUM_SOUNDS[drum]['file'] = file_path
            sounds[drum] = pygame.mixer.Sound(file_path)
            sounds[drum].set_volume(volume)
        except Exception as e:
            print(f"Error loading custom sound for {drum}: {e}")

# Save custom preset
def save_custom_preset():
    PRESETS['Custom'] = {drum: info['file'] for drum, info in DRUM_SOUNDS.items()}
    with open('custom_preset.json', 'w') as f:
        json.dump(PRESETS['Custom'], f)

# Load custom preset
def load_custom_preset():
    try:
        with open('custom_preset.json', 'r') as f:
            PRESETS['Custom'] = json.load(f)
        load_sounds('Custom')
    except FileNotFoundError:
        print("No custom preset found.")

# Draw GUI
def draw_gui():
    screen.fill(BLACK)
    # Draw drum kit
    for name, info in DRUM_SOUNDS.items():
        color = YELLOW if time.time() < highlight_timers[name] else GRAY
        pygame.draw.ellipse(screen, color, info['rect'])  # Circular pads for realism
        text = small_font.render(info['label'], True, WHITE)
        screen.blit(text, (info['rect'].x + 10, info['rect'].y + 10))
    
    # Draw controls
    record_text = "Recording: ON" if recording else "Recording: OFF"
    screen.blit(font.render(record_text, True, RED), (50, 50))
    playback_text = "Playback: ON" if playing_back else "Playback: OFF"
    screen.blit(font.render(playback_text, True, RED), (50, 80))
    screen.blit(font.render(f"Metronome: {'ON' if metronome_on else 'OFF'} ({bpm} BPM)", True, WHITE), (50, 110))
    screen.blit(font.render(f"Preset: {current_preset}", True, WHITE), (50, 140))
    screen.blit(font.render(f"Volume: {int(volume * 100)}%", True, WHITE), (50, 170))
    
    # Draw volume slider
    pygame.draw.rect(screen, GRAY, volume_rect)
    pygame.draw.rect(screen, BLUE, volume_handle)
    screen.blit(small_font.render("Volume", True, WHITE), (50, 570))
    
    # Draw BPM slider
    pygame.draw.rect(screen, GRAY, bpm_rect)
    pygame.draw.rect(screen, BLUE, bpm_handle)
    screen.blit(small_font.render("BPM (60-300)", True, WHITE), (300, 570))
    
    # Draw instructions
    instruction_text = "ESC: Quit, R: Record, P: Playback, M: Metronome, T: Switch Presets, C: Custom Sounds, S: Save Preset, L: Load Preset, +/-: BPM"
    screen.blit(small_font.render(instruction_text, True, WHITE), (50, 650))
    
    pygame.display.flip()

# Handle events
def handle_events():
    global recording, playing_back, metronome_on, bpm, volume, current_preset, beat_interval
    global dragging_volume, dragging_bpm, volume_handle, bpm_handle
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                recording = not recording
                if not recording and recorded_notes:
                    save_recording()
                playing_back = False
            elif event.key == pygame.K_p:
                if recorded_notes and not recording:
                    playing_back = not playing_back
                    if playing_back:
                        global playback_start_time, playback_index
                        playback_start_time = time.time()
                        playback_index = 0
            elif event.key == pygame.K_m:
                metronome_on = not metronome_on
            elif event.key == pygame.K_c:
                for drum in DRUM_SOUNDS:
                    load_custom_sound(drum)
            elif event.key == pygame.K_s:
                save_custom_preset()
                current_preset = 'Custom'
            elif event.key == pygame.K_l:
                load_custom_preset()
                current_preset = 'Custom'
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                bpm = min(300, bpm + 10)
                beat_interval = 60 / bpm
                bpm_handle.x = 300 + int((bpm - 60) / 240 * 200)
            elif event.key == pygame.K_MINUS:
                bpm = max(60, bpm - 10)
                beat_interval = 60 / bpm
                bpm_handle.x = 300 + int((bpm - 60) / 240 * 200)
            elif event.key == pygame.K_t:
                # Cycle through all available presets
                preset_list = ['Default', 'Rock', 'Jazz', 'Electronic', 'Custom']
                current_index = preset_list.index(current_preset) if current_preset in preset_list else 0
                next_index = (current_index + 1) % len(preset_list)
                current_preset = preset_list[next_index]
                load_sounds(current_preset)
                print(f"Switched to preset: {current_preset}")
            for name, info in DRUM_SOUNDS.items():
                if event.key == info['key']:
                    sounds[name].play()
                    highlight_timers[name] = time.time() + HIGHLIGHT_DURATION
                    if recording:
                        recorded_notes.append((name, time.time()))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if volume_rect.collidepoint(event.pos):
                dragging_volume = True
            elif bpm_rect.collidepoint(event.pos):
                dragging_bpm = True
            for name, info in DRUM_SOUNDS.items():
                if info['rect'].collidepoint(event.pos):
                    sounds[name].play()
                    highlight_timers[name] = time.time() + HIGHLIGHT_DURATION
                    if recording:
                        recorded_notes.append((name, time.time()))
        if event.type == pygame.MOUSEBUTTONUP:
            dragging_volume = False
            dragging_bpm = False
        if event.type == pygame.MOUSEMOTION and dragging_volume:
            volume_handle.x = max(volume_rect.x, min(event.pos[0], volume_rect.x + volume_rect.width))
            volume = (volume_handle.x - volume_rect.x) / volume_rect.width
            for sound in sounds.values():
                sound.set_volume(volume)
            if metronome_sound:
                metronome_sound.set_volume(volume)
        if event.type == pygame.MOUSEMOTION and dragging_bpm:
            bpm_handle.x = max(bpm_rect.x, min(event.pos[0], bpm_rect.x + bpm_rect.width))
            bpm = 60 + (bpm_handle.x - bpm_rect.x) / bpm_rect.width * 240
            bpm = round(bpm / 10) * 10  # Round to nearest 10
            beat_interval = 60 / bpm

    return True

# Save recording
def save_recording():
    with open(f"recording_{int(time.time())}.txt", 'w') as f:
        start_time = recorded_notes[0][1] if recorded_notes else time.time()
        for note, timestamp in recorded_notes:
            f.write(f"{note},{timestamp - start_time}\n")
    recorded_notes.clear()

# Playback recording
def play_recording():
    global playback_index, playing_back
    if playing_back and playback_index < len(recorded_notes):
        note, timestamp = recorded_notes[playback_index]
        if time.time() - playback_start_time >= timestamp:
            sounds[note].play()
            highlight_timers[note] = time.time() + HIGHLIGHT_DURATION
            playback_index += 1
        if playback_index >= len(recorded_notes):
            playing_back = False

# Metronome
def update_metronome():
    global last_beat_time
    if metronome_on and time.time() - last_beat_time >= beat_interval:
        metronome_sound.play()
        last_beat_time = time.time()

# Main loop
def main():
    load_sounds()
    running = True
    clock = pygame.time.Clock()
    while running:
        running = handle_events()
        update_metronome()
        play_recording()
        draw_gui()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()