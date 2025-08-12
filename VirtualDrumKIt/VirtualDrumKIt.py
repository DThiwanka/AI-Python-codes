"""
Virtual Drum Kit Simulator
- GUI: pygame
- Sound: synthesized with numpy, playable via pygame.sndarray
- Recorder: records events (time, pad) and can playback / export
- Metronome: adjustable BPM and audible clicks
- Custom sound upload: desktop via file dialog (wav/mp3), browser (Pyodide) via HTML file input (wav)
- Presets: Rock, Jazz, Electronic
- Pyodide compatibility: uses asyncio loop when sys.platform == "emscripten"
"""

import sys
import time
import json
import io
import asyncio
import math
import traceback

import numpy as np

# Optional imports that may not exist in Pyodide or simple environments
try:
    import pygame
    from pygame import gfxdraw
except Exception as e:
    raise RuntimeError("pygame is required to run this program. In Pyodide, pygame must be available.") from e

# Desktop file dialogs
IS_EMSCRIPTEN = (sys.platform == "emscripten")
if not IS_EMSCRIPTEN:
    try:
        import tkinter as tk
        from tkinter import filedialog
        _TK_ROOT = tk.Tk()
        _TK_ROOT.withdraw()
    except Exception:
        _TK_ROOT = None


# ------------------------------
# Utilities: sound synthesis
# ------------------------------
SAMPLE_RATE = 44100
DEFAULT_VOLUME = 0.8  # master volume

def to_stereo(arr):
    """Ensure 2D stereo float array shape (2, N). Expects float32 in -1..1"""
    if arr.ndim == 1:
        return np.vstack([arr, arr])
    elif arr.shape[0] == 2:
        return arr
    elif arr.shape[1] == 2:
        # (N,2) convert to (2,N)
        return arr.T
    else:
        # duplicate channel
        return np.vstack([arr.mean(axis=0), arr.mean(axis=0)])

def float_to_int16(arr):
    clipped = np.clip(arr, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)

def make_sound_from_array(arr):
    """Convert float stereo shape (2,N) to a pygame Sound object."""
    stereo = to_stereo(arr)
    int16 = float_to_int16(stereo)
    # pygame expects (N,2) shaped array for stereo
    arr_2d = np.vstack([int16[0], int16[1]]).T.copy()
    try:
        sound = pygame.sndarray.make_sound(arr_2d)
        sound.set_volume(DEFAULT_VOLUME)
        return sound
    except Exception as e:
        print("Error creating pygame Sound:", e)
        raise

def envelope(signal, attack=0.001, decay=0.3, sustain=0.0, release=0.05, sr=SAMPLE_RATE):
    N = len(signal)
    env = np.ones(N, dtype=np.float32) * sustain
    a_samples = max(1, int(attack * sr))
    d_samples = max(1, int(decay * sr))
    r_samples = max(1, int(release * sr))
    # Attack
    env[:a_samples] = np.linspace(0.0, 1.0, a_samples)
    # Decay
    end_d = min(N, a_samples + d_samples)
    if end_d > a_samples:
        env[a_samples:end_d] = np.linspace(1.0, sustain, end_d - a_samples)
    # Release
    if r_samples > 0:
        env[-r_samples:] = np.linspace(sustain, 0.0, r_samples)
    # Middle remains sustain
    signal *= env
    return signal

def synth_kick(duration=0.6, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # pitch drop
    freqs = 100 * (2.0 ** (-5 * t / duration))  # drop
    signal = 0.9 * np.sin(2 * np.pi * freqs * t)
    signal = envelope(signal, attack=0.001, decay=0.45, sustain=0.0, release=0.05, sr=sr)
    return np.vstack([signal, signal])

def synth_snare(duration=0.4, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # noise body
    noise = np.random.normal(0, 1, len(t)).astype(np.float32)
    # tonal component
    tone = 0.4 * np.sin(2 * np.pi * 200 * t) * np.exp(-8 * t)
    signal = 0.7 * noise * np.exp(-10 * t) + tone
    signal = envelope(signal, attack=0.001, decay=0.3, sustain=0.0, release=0.02, sr=sr)
    return np.vstack([signal, signal])

def synth_closed_hihat(duration=0.08, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    noise = np.random.normal(0,1,len(t))
    # high-pass-ish: multiply by linearly increasing freq envelope
    signal = noise * np.sin(2*np.pi*(5000 + 8000*t)*t) * np.exp(-60*t)
    signal = envelope(signal, attack=0.0005, decay=0.05, sustain=0.0, release=0.001, sr=sr)
    return np.vstack([signal, signal])

def synth_open_hihat(duration=0.5, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    noise = np.random.normal(0,1,len(t))
    signal = noise * np.exp(-4 * t) * np.sin(2*np.pi*(3000 + 2000*t)*t)
    signal = envelope(signal, attack=0.001, decay=0.45, sustain=0.0, release=0.02, sr=sr)
    return np.vstack([signal, signal])

def synth_crash(duration=1.2, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    noise = np.random.normal(0,1,len(t))
    signal = noise * np.exp(-2 * t) * np.sin(2*np.pi*(2000 + 1000*t)*t)
    signal = envelope(signal, attack=0.001, decay=0.9, sustain=0.0, release=0.05, sr=sr)
    return np.vstack([signal, signal]) * 0.9

def synth_ride(duration=1.0, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    noise = np.random.normal(0,1,len(t))
    signal = 0.6*noise * np.exp(-1.8*t) * np.sin(2*np.pi*(2200 + 800*t)*t)
    signal = envelope(signal, attack=0.001, decay=0.6, sustain=0.0, release=0.02, sr=sr)
    return np.vstack([signal, signal]) * 0.8

def synth_tom(freq=300, duration=0.6, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    signal = 0.9 * np.sin(2 * np.pi * (freq * (1 + 0.02*t)) * t) * np.exp(-5*t)
    signal = envelope(signal, attack=0.001, decay=0.45, sustain=0.0, release=0.02, sr=sr)
    return np.vstack([signal, signal])

def synth_cowbell(duration=0.3, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    # metallic: sum of inharmonics with decay
    freqs = [800, 1000, 1400, 2000]
    signal = sum([0.3*np.sin(2*np.pi*f*t) for f in freqs])
    signal *= np.exp(-8*t)
    signal = envelope(signal, attack=0.001, decay=0.4, sustain=0.0, release=0.02, sr=sr)
    return np.vstack([signal, signal]) * 0.8

def synth_click(duration=0.05, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    noise = np.random.normal(0,1,len(t)) * np.exp(-60 * t)
    return np.vstack([noise, noise])

# Map instrument ids to synthesis functions (factory)
DEFAULT_SOUND_FACTORIES = {
    "kick": lambda: synth_kick(),
    "snare": lambda: synth_snare(),
    "closed_hh": lambda: synth_closed_hihat(),
    "open_hh": lambda: synth_open_hihat(),
    "crash": lambda: synth_crash(),
    "ride": lambda: synth_ride(),
    "tom1": lambda: synth_tom(440),
    "tom2": lambda: synth_tom(330),
    "floortom": lambda: synth_tom(220),
    "cowbell": lambda: synth_cowbell(),
    "click": lambda: synth_click(0.05),
}

# ------------------------------
# SoundManager: load / manage sounds
# ------------------------------
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_default_kit()
        self.master_volume = DEFAULT_VOLUME

    def load_default_kit(self, preset="Rock"):
        """Three simple presets alter relative volumes or variations."""
        try:
            self.sounds.clear()
            # generate core sounds
            for name, factory in DEFAULT_SOUND_FACTORIES.items():
                arr = factory()
                # Ensure stereo shape (2,N) float32
                arr = np.array(arr, dtype=np.float32)
                self.sounds[name] = make_sound_from_array(arr)
            # presets: modify volumes / slight variations
            if preset == "Rock":
                # boost kick/snare
                self.sounds["kick"].set_volume(1.0)
                self.sounds["snare"].set_volume(1.0)
                self.sounds["crash"].set_volume(0.9)
            elif preset == "Jazz":
                self.sounds["ride"].set_volume(1.0)
                self.sounds["closed_hh"].set_volume(0.6)
                self.sounds["snare"].set_volume(0.7)
            elif preset == "Electronic":
                # re-synthesize some with sharper envelopes
                self.sounds["kick"] = make_sound_from_array(synth_kick(duration=0.5))
                self.sounds["snare"] = make_sound_from_array(synth_snare(duration=0.25))
                self.sounds["closed_hh"] = make_sound_from_array(synth_closed_hihat(duration=0.04))
            # master vol
            self.set_master_volume(DEFAULT_VOLUME)
        except Exception as e:
            print("Error loading default kit:", e)
            traceback.print_exc()

    def set_master_volume(self, vol:float):
        self.master_volume = max(0.0, min(1.0, vol))
        for s in self.sounds.values():
            try:
                s.set_volume(self.master_volume)
            except Exception:
                pass

    def play(self, name):
        try:
            s = self.sounds.get(name)
            if s:
                s.play()
            else:
                print("Sound not found:", name)
        except Exception as e:
            print("Playback error:", e)

    def replace_sound_with_wave_bytes(self, name, wav_bytes):
        """
        Replace a sound 'name' with wav bytes (WAV RIFF format).
        wav_bytes: bytes containing WAV data. For desktop mp3 support use pygame.mixer.Sound(file)
        """
        try:
            import wave
            with wave.open(io.BytesIO(wav_bytes), "rb") as w:
                nchan = w.getnchannels()
                sampwidth = w.getsampwidth()
                fr = w.getframerate()
                nframes = w.getnframes()
                raw = w.readframes(nframes)
            # only handle PCM 16-bit or 8-bit
            if sampwidth == 2:
                arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
            elif sampwidth == 1:
                arr = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128.0
            else:
                raise ValueError("Unsupported sample width: %d" % sampwidth)
            if nchan == 1:
                stereo = np.vstack([arr, arr])
            else:
                stereo = arr.reshape(-1, nchan).T
                if stereo.shape[0] == 1:
                    stereo = np.vstack([stereo[0], stereo[0]])
            # resample if needed (naive)
            if fr != SAMPLE_RATE:
                # naive linear resample
                length = stereo.shape[1]
                new_len = int(length * SAMPLE_RATE / fr)
                stereo = np.vstack([
                    np.interp(np.linspace(0, length, new_len, endpoint=False),
                              np.arange(length), stereo[0]),
                    np.interp(np.linspace(0, length, new_len, endpoint=False),
                              np.arange(length), stereo[1])
                ])
            sound = make_sound_from_array(stereo.astype(np.float32))
            self.sounds[name] = sound
            self.set_master_volume(self.master_volume)
            return True
        except Exception as e:
            print("Failed to replace sound:", e)
            traceback.print_exc()
            return False


# ------------------------------
# Recorder: capture events and playback
# ------------------------------
class Recorder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.events = []  # list of (t_offset, pad_name)
        self.recording = False
        self.start_time = None

    def start(self):
        self.events = []
        self.recording = True
        self.start_time = time.time()
        print("Recording started")

    def stop(self):
        self.recording = False
        print(f"Recording stopped, {len(self.events)} events captured")

    def record_hit(self, pad_name):
        if self.recording:
            t = time.time() - self.start_time
            self.events.append((t, pad_name))

    async def playback(self, sound_manager:SoundManager, loop=False):
        if not self.events:
            print("No events to play")
            return
        start = time.time()
        for t_offset, pad in self.events:
            now = time.time() - start
            wait = t_offset - now
            if wait > 0:
                await asyncio.sleep(wait)
            sound_manager.play(pad)
        if loop:
            # naive loop
            await self.playback(sound_manager, loop=True)

    def export_json(self):
        return json.dumps({"events": self.events}, indent=2)

    def save_to_file_desktop(self, default_name="drum_session.json"):
        if _TK_ROOT:
            try:
                path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_name)
                if path:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(self.export_json())
                    print("Saved recording to", path)
            except Exception as e:
                print("Failed to save recording:", e)
        else:
            print("No desktop file dialog available.")

    def trigger_browser_download(self, filename="drum_session.json"):
        # In pyodide environment, use JS to create a download link
        try:
            from js import document, Blob, URL
            blob = Blob.new([self.export_json()], {"type":"application/json"})
            link = document.createElement("a")
            link.href = URL.createObjectURL(blob)
            link.download = filename
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(link.href)
            print("Triggered download in browser")
        except Exception as e:
            print("Browser download failed:", e)


# ------------------------------
# Metronome
# ------------------------------
class Metronome:
    def __init__(self, sound_manager:SoundManager, bpm=100):
        self.bpm = bpm
        self._running = False
        self._task = None
        self.sound_manager = sound_manager
        # ensure there's a click sound available
        if "click" not in self.sound_manager.sounds:
            self.sound_manager.sounds["click"] = make_sound_from_array(synth_click())
        self._accent_interval = 4  # accent first beat of bar
        self._beat_count = 0

    def set_bpm(self, bpm):
        self.bpm = max(20, min(300, int(bpm)))

    def start(self, loop=None):
        self._running = True

    def stop(self):
        self._running = False

    async def run_loop(self):
        # call this as a background task when using asyncio
        try:
            self._beat_count = 0
            while True:
                if self._running:
                    interval = 60.0 / self.bpm
                    # accent on first beat (play same click but could be louder)
                    self._beat_count = (self._beat_count % self._accent_interval) + 1
                    # play click (accent louder)
                    vol = 1.0 if self._beat_count == 1 else 0.7
                    try:
                        s = self.sound_manager.sounds.get("click")
                        if s:
                            s.set_volume(vol * self.sound_manager.master_volume)
                            s.play()
                    except Exception as e:
                        pass
                    await asyncio.sleep(interval)
                else:
                    await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            pass


# ------------------------------
# GUI and Application
# ------------------------------
PAD_LAYOUT = [
    # row wise: label, sound_name, key
    ("A", "kick", pygame.K_a),
    ("S", "snare", pygame.K_s),
    ("D", "closed_hh", pygame.K_d),
    ("F", "open_hh", pygame.K_f),
    ("G", "crash", pygame.K_g),
    ("H", "ride", pygame.K_h),
    ("J", "tom1", pygame.K_j),
    ("K", "tom2", pygame.K_k),
    ("L", "floortom", pygame.K_l),
    (";", "cowbell", pygame.K_SEMICOLON if hasattr(pygame, "K_SEMICOLON") else pygame.K_COLON),
]

class App:
    WIDTH = 1000
    HEIGHT = 600
    PAD_COLOR = (40, 40, 40)
    PAD_ACTIVE = (200, 120, 60)
    TEXT_COLOR = (240,240,240)
    BG = (30,30,30)

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE)
        except Exception:
            print("Warning: could not init mixer with requested sample rate.")
            pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Virtual Drum Kit")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.recorder = Recorder()
        self.metronome = Metronome(self.sound_manager, bpm=100)
        self.met_task = None
        self.font = pygame.font.SysFont(None, 22)
        self.bigfont = pygame.font.SysFont(None, 28)
        self.running = True
        # create pad rects
        self.pads = []
        self.build_pad_layout()
        self.pressed_pads = set()
        self.playback_task = None
        self.is_playing_back = False

        # preset buttons
        self.presets = ["Rock", "Jazz", "Electronic"]
        self.selected_preset = "Rock"

        # async handling for browser
        self.loop = asyncio.get_event_loop() if IS_EMSCRIPTEN else None

    def build_pad_layout(self):
        pad_w = 170
        pad_h = 120
        margin_x = 30
        margin_y = 30
        cols = 5
        for idx, (label, sound_name, key) in enumerate(PAD_LAYOUT):
            row = idx // cols
            col = idx % cols
            x = margin_x + col * (pad_w + margin_x)
            y = margin_y + row * (pad_h + margin_y)
            rect = pygame.Rect(x, y, pad_w, pad_h)
            self.pads.append({
                "rect": rect,
                "label": label,
                "sound": sound_name,
                "key": key,
            })

    def draw(self):
        self.screen.fill(self.BG)
        # title
        title_surf = self.bigfont.render("Virtual Drum Kit - Press keys or click pads. R=Record, M=Metronome, Space=Play Rec", True, self.TEXT_COLOR)
        self.screen.blit(title_surf, (20, 10))
        # draw pads
        for p in self.pads:
            r = p["rect"]
            name = p["sound"]
            active = name in self.pressed_pads
            color = self.PAD_ACTIVE if active else self.PAD_COLOR
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            # label
            lab = self.font.render(f"{p['label']}  {name}", True, self.TEXT_COLOR)
            self.screen.blit(lab, (r.x + 12, r.y + 12))
            # small note about key
            ktxt = self.font.render(f"Key: {pygame.key.name(p['key'])}", True, (200,200,200))
            self.screen.blit(ktxt, (r.x + 12, r.y + 40))

        # controls
        ctrlx = 30
        ctly = 300
        lineh = 28
        controls = [
            f"Metronome: {'ON' if self.metronome._running else 'OFF'}  BPM: {self.metronome.bpm} (+/- to change)",
            f"Recording: {'YES' if self.recorder.recording else 'NO'}  Events: {len(self.recorder.events)} (Press R to toggle)",
            f"Selected Preset: {self.selected_preset} (press 1-3 or use buttons)",
            "Upload custom sound: U (desktop/browser; browser accepts WAV)",
            "Save recording: Ctrl+S (desktop) or use button (browser)",
        ]
        for i, c in enumerate(controls):
            self.screen.blit(self.font.render(c, True, self.TEXT_COLOR), (ctrlx, ctly + i*lineh))

        # preset buttons
        bx = 30
        by = 450
        bw = 140
        bh = 36
        for i, p in enumerate(self.presets):
            rect = pygame.Rect(bx + i*(bw+10), by, bw, bh)
            pygame.draw.rect(self.screen, (70,70,70), rect, border_radius=6)
            txt = self.font.render(p, True, self.TEXT_COLOR)
            self.screen.blit(txt, (rect.x + 10, rect.y + 8))
            # save rect for click detection
            self.presets[i] = p if isinstance(self.presets[i], str) else self.presets[i]

        # small footer
        footer = self.font.render("Keys: A S D F G H J K L ;   |  Controls: R=Record  M=Metronome Toggle  Space=Play Recording", True, (180,180,180))
        self.screen.blit(footer, (20, self.HEIGHT - 30))

        pygame.display.flip()

    def handle_keydown(self, key):
        # pad triggers
        for p in self.pads:
            if key == p["key"]:
                self.sound_manager.play(p["sound"])
                self.recorder.record_hit(p["sound"])
                # mark active
                self.pressed_pads.add(p["sound"])
                return
        # controls
        if key == pygame.K_r:
            if self.recorder.recording:
                self.recorder.stop()
            else:
                self.recorder.start()
        elif key == pygame.K_m:
            if self.metronome._running:
                self.metronome.stop()
            else:
                self.metronome.start()
        elif key == pygame.K_SPACE:
            # play recorded sequence (async-safe)
            if IS_EMSCRIPTEN:
                # schedule async playback
                asyncio.ensure_future(self.recorder.playback(self.sound_manager))
            else:
                # run blocking playback in background thread via asyncio
                async def do_play():
                    await self.recorder.playback(self.sound_manager)
                try:
                    asyncio.run(do_play())
                except Exception:
                    # fallback to synchronous playback (simple)
                    start = time.time()
                    for t_offset, pad in self.recorder.events:
                        wait = t_offset - (time.time() - start)
                        if wait > 0:
                            time.sleep(wait)
                        self.sound_manager.play(pad)
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.metronome.set_bpm(self.metronome.bpm + 5)
        elif key == pygame.K_MINUS or key == pygame.K_UNDERSCORE:
            self.metronome.set_bpm(self.metronome.bpm - 5)
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            idx = {pygame.K_1:0, pygame.K_2:1, pygame.K_3:2}[key]
            preset = self.presets[idx]
            self.selected_preset = preset
            self.sound_manager.load_default_kit(preset=preset)
            print("Switched preset:", preset)
        elif key == pygame.K_u:
            # open custom upload flow
            if IS_EMSCRIPTEN:
                asyncio.ensure_future(self.browser_file_input_and_replace())
            else:
                self.desktop_file_dialog_and_replace()

    def handle_keyup(self, key):
        # release pads
        for p in self.pads:
            if key == p["key"]:
                try:
                    self.pressed_pads.discard(p["sound"])
                except Exception:
                    pass

    def desktop_file_dialog_and_replace(self):
        if not _TK_ROOT:
            print("File dialog not available.")
            return
        try:
            path = filedialog.askopenfilename(title="Choose WAV or MP3", filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")])
            if not path:
                return
            # try letting pygame load directly first (works for mp3/ogg/wav)
            try:
                snd = pygame.mixer.Sound(path)
                # ask which pad to replace: simple text input
                pad_name = self._ask_which_pad_desktop()
                if pad_name:
                    self.sound_manager.sounds[pad_name] = snd
                    print("Replaced pad", pad_name, "with", path)
            except Exception:
                # fallback: read bytes and let SoundManager parse WAV bytes
                with open(path, "rb") as f:
                    b = f.read()
                pad_name = self._ask_which_pad_desktop()
                if pad_name:
                    ok = self.sound_manager.replace_sound_with_wave_bytes(pad_name, b)
                    if ok:
                        print("Replaced pad with WAV bytes")
                    else:
                        print("Failed to replace pad.")
        except Exception as e:
            print("Upload failed:", e)
            traceback.print_exc()

    def _ask_which_pad_desktop(self):
        # simple choice dialog
        try:
            choice = None
            print("Enter pad name to replace from:", [p["sound"] for p in self.pads])
            choice = input("Pad name (e.g., snare): ").strip()
            if choice not in [p["sound"] for p in self.pads]:
                print("Invalid pad name")
                return None
            return choice
        except Exception:
            return None

    async def browser_file_input_and_replace(self):
        # Creates an invisible file input element in DOM and reads first selected file as ArrayBuffer
        try:
            from js import document
            input_el = document.createElement("input")
            input_el.type = "file"
            input_el.accept = ".wav"
            input_el.style.display = "none"
            document.body.appendChild(input_el)

            future = asyncio.get_event_loop().create_future()

            def onchange(evt):
                try:
                    files = input_el.files
                    if files.length > 0:
                        f = files.item(0)
                        # read as arrayBuffer
                        fr = __import__("js").FileReader.new()
                        def onload(e):
                            future.set_result(fr.result)
                        fr.onload = onload
                        fr.readAsArrayBuffer(f)
                    else:
                        future.set_result(None)
                except Exception as e:
                    future.set_exception(e)

            input_el.onchange = onchange
            # trigger click
            input_el.click()
            arraybuf = await future
            document.body.removeChild(input_el)
            if not arraybuf:
                print("No file selected")
                return
            # convert arraybuffer to Python bytes
            py_bytes = bytes(arraybuf.to_py().to_bytes())
            # ask user via simple JS prompt which pad to replace
            pad = document.prompt("Enter pad to replace (kick, snare, closed_hh, open_hh, crash, ride, tom1, tom2, floortom, cowbell):")
            if not pad:
                print("No pad chosen")
                return
            success = self.sound_manager.replace_sound_with_wave_bytes(pad, py_bytes)
            print("Replace success:", success)
        except Exception as e:
            print("Browser upload failed:", e)
            traceback.print_exc()

    def run_once(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
            elif event.type == pygame.KEYUP:
                self.handle_keyup(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # check pads
                for p in self.pads:
                    if p["rect"].collidepoint(pos):
                        self.sound_manager.play(p["sound"])
                        self.recorder.record_hit(p["sound"])
                        self.pressed_pads.add(p["sound"])
                # check preset buttons by positions (these are drawn at fixed positions)
                # quick check: presets are at y=450, boxes 140 width
                bx = 30
                by = 450
                bw = 140
                bh = 36
                for i, p in enumerate(self.presets):
                    rect = pygame.Rect(bx + i*(bw+10), by, bw, bh)
                    if rect.collidepoint(pos):
                        self.selected_preset = p
                        self.sound_manager.load_default_kit(preset=p)
                        print("Preset clicked:", p)
            elif event.type == pygame.MOUSEBUTTONUP:
                # release pads on mouse up
                for p in self.pads:
                    if p["sound"] in self.pressed_pads:
                        self.pressed_pads.discard(p["sound"])

    async def main_async(self):
        # start metronome background task
        try:
            self.met_task = asyncio.create_task(self.metronome.run_loop())
        except Exception:
            self.met_task = None
        try:
            while self.running:
                self.run_once()
                self.draw()
                await asyncio.sleep(0.016)  # ~60fps
        finally:
            if self.met_task:
                self.met_task.cancel()

    def main_loop(self):
        # desktop blocking loop
        try:
            # start metronome task manually in a background thread (non-async)
            import threading
            def met_thread():
                # simple loop
                while self.running:
                    if self.metronome._running:
                        interval = 60.0 / self.metronome.bpm
                        try:
                            s = self.sound_manager.sounds.get("click")
                            if s: s.play()
                        except Exception:
                            pass
                        time.sleep(interval)
                    else:
                        time.sleep(0.05)
            t = threading.Thread(target=met_thread, daemon=True)
            t.start()
        except Exception:
            pass

        while self.running:
            self.run_once()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


def main():
    app = App()
    if IS_EMSCRIPTEN:
        # run async loop - Pyodide / Emscripten expects async
        asyncio.ensure_future(app.main_async())
    else:
        app.main_loop()

if __name__ == "__main__":
    main()
