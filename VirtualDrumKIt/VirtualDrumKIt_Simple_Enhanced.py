"""
Simplified Enhanced Virtual Drum Kit
A more stable version with beautiful visual styling but simpler effects
"""

import pygame
import numpy as np
import math
import time
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Color palette
class Colors:
    # Dark theme
    BACKGROUND = (20, 20, 30)
    SURFACE = (30, 30, 45)
    
    # Accent colors for pads
    RED = (220, 50, 50)
    ORANGE = (255, 140, 0)
    YELLOW = (255, 200, 0)
    GREEN = (50, 200, 50)
    BLUE = (50, 150, 255)
    PURPLE = (150, 50, 255)
    CYAN = (0, 200, 255)
    PINK = (255, 100, 150)
    
    # UI colors
    TEXT = (240, 240, 240)
    TEXT_DIM = (150, 150, 150)
    BORDER = (100, 100, 120)
    GLOW = (255, 255, 255)

# Simple sound generation
def create_kick():
    duration = 0.5
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    # Generate kick drum sound
    t = np.linspace(0, duration, frames, False)
    frequency = 60 * np.exp(-t * 8)  # Frequency drops quickly
    wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 6)
    
    # Convert to stereo int16
    wave = np.clip(wave * 0.8, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

def create_snare():
    duration = 0.3
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    # Mix tone and noise for snare
    t = np.linspace(0, duration, frames, False)
    tone = np.sin(2 * np.pi * 200 * t) * 0.3
    noise = np.random.normal(0, 0.4, frames)
    wave = (tone + noise) * np.exp(-t * 8)
    
    wave = np.clip(wave, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

def create_hihat():
    duration = 0.1
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    # High frequency noise for hi-hat
    t = np.linspace(0, duration, frames, False)
    noise = np.random.normal(0, 0.3, frames)
    high_freq = np.sin(2 * np.pi * 8000 * t) * 0.2
    wave = (noise + high_freq) * np.exp(-t * 50)
    
    wave = np.clip(wave, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

class DrumPad:
    def __init__(self, x, y, width, height, label, sound_name, key, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.sound_name = sound_name
        self.key = key
        self.color = color
        self.is_pressed = False
        self.hit_time = 0
        self.glow_alpha = 0
        
    def hit(self):
        self.is_pressed = True
        self.hit_time = time.time()
        self.glow_alpha = 255
        
    def release(self):
        self.is_pressed = False
        
    def update(self):
        # Fade glow effect
        if self.glow_alpha > 0:
            self.glow_alpha = max(0, self.glow_alpha - 8)
            
    def draw(self, screen, font):
        # Calculate colors
        base_brightness = 0.7 if self.is_pressed else 0.5
        pad_color = tuple(int(c * base_brightness) for c in self.color)
        
        # Draw glow effect
        if self.glow_alpha > 0:
            glow_size = 10
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            
            glow_color = (*self.color, self.glow_alpha // 4)
            pygame.draw.rect(glow_surface, glow_color, 
                           (0, 0, glow_rect.width, glow_rect.height), 
                           border_radius=20)
            screen.blit(glow_surface, glow_rect)
        
        # Draw main pad
        pygame.draw.rect(screen, pad_color, self.rect, border_radius=15)
        
        # Draw border
        border_color = Colors.GLOW if self.is_pressed else Colors.BORDER
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=15)
        
        # Draw text
        text_surface = font.render(self.label, True, Colors.TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw key binding
        key_font = pygame.font.Font(None, 24)
        key_text = key_font.render(f"[{pygame.key.name(self.key).upper()}]", True, Colors.TEXT_DIM)
        key_rect = key_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
        screen.blit(key_text, key_rect)

class VisualizerBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bars = [0] * 16
        self.target_bars = [0] * 16
        
    def trigger(self):
        # Simulate audio response
        for i in range(len(self.bars)):
            self.target_bars[i] = random.uniform(0.3, 1.0)
            
    def update(self):
        for i in range(len(self.bars)):
            # Smooth animation
            diff = self.target_bars[i] - self.bars[i]
            self.bars[i] += diff * 0.2
            
            # Natural decay
            self.target_bars[i] *= 0.95
            
    def draw(self, screen):
        bar_width = self.width // len(self.bars) - 2
        
        for i, height_ratio in enumerate(self.bars):
            bar_height = int(self.height * height_ratio)
            bar_x = self.x + i * (bar_width + 2)
            bar_y = self.y + self.height - bar_height
            
            # Color based on height
            if height_ratio > 0.7:
                color = Colors.RED
            elif height_ratio > 0.5:
                color = Colors.ORANGE
            elif height_ratio > 0.3:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
                
            pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width, bar_height), border_radius=2)

class EnhancedDrumKit:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🥁 Enhanced Drum Kit")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.pad_font = pygame.font.Font(None, 36)
        self.ui_font = pygame.font.Font(None, 28)
        
        # Create drum pads
        self.drum_pads = []
        self.create_pads()
        
        # Load sounds
        self.sounds = {
            'kick': create_kick(),
            'snare': create_snare(),
            'hihat': create_hihat(),
            'tom1': create_kick(),  # Reuse for now
            'tom2': create_kick(),
            'crash': create_hihat(),
            'ride': create_hihat(),
            'clap': create_snare()
        }
        
        # Visualizer
        self.visualizer = VisualizerBar(50, 100, 300, 80)
        
        # Settings
        self.volume = 0.8
        
    def create_pads(self):
        pad_configs = [
            # Row 1
            ("KICK", "kick", pygame.K_a, Colors.RED),
            ("SNARE", "snare", pygame.K_s, Colors.ORANGE),
            ("HI-HAT", "hihat", pygame.K_d, Colors.YELLOW),
            ("CRASH", "crash", pygame.K_f, Colors.GREEN),
            
            # Row 2  
            ("TOM 1", "tom1", pygame.K_q, Colors.BLUE),
            ("TOM 2", "tom2", pygame.K_w, Colors.PURPLE),
            ("RIDE", "ride", pygame.K_e, Colors.CYAN),
            ("CLAP", "clap", pygame.K_r, Colors.PINK),
        ]
        
        pad_width = 180
        pad_height = 100
        start_x = 100
        start_y = 250
        cols = 4
        
        for i, (label, sound_name, key, color) in enumerate(pad_configs):
            row = i // cols
            col = i % cols
            x = start_x + col * (pad_width + 30)
            y = start_y + row * (pad_height + 40)
            
            pad = DrumPad(x, y, pad_width, pad_height, label, sound_name, key, color)
            self.drum_pads.append(pad)
    
    def play_sound(self, sound_name, pad):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
            pad.hit()
            self.visualizer.trigger()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.volume = min(1.0, self.volume + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.volume = max(0.0, self.volume - 0.1)
                else:
                    # Check drum pad keys
                    for pad in self.drum_pads:
                        if event.key == pad.key:
                            self.play_sound(pad.sound_name, pad)
                            
            elif event.type == pygame.KEYUP:
                for pad in self.drum_pads:
                    if event.key == pad.key:
                        pad.release()
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for pad in self.drum_pads:
                    if pad.rect.collidepoint(mouse_pos):
                        self.play_sound(pad.sound_name, pad)
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                for pad in self.drum_pads:
                    pad.release()
    
    def update(self):
        for pad in self.drum_pads:
            pad.update()
        self.visualizer.update()
        
    def draw_background(self):
        # Simple gradient background
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(Colors.BACKGROUND[0] * (1 - ratio * 0.3))
            g = int(Colors.BACKGROUND[1] * (1 - ratio * 0.3))  
            b = int(Colors.BACKGROUND[2] * (1 + ratio * 0.5))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def draw_ui(self):
        # Title
        title_text = "🥁 ENHANCED DRUM KIT"
        title_surface = self.title_font.render(title_text, True, Colors.TEXT)
        title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=30)
        self.screen.blit(title_surface, title_rect)
        
        # Volume indicator
        vol_text = f"Volume: {int(self.volume * 100)}%"
        vol_surface = self.ui_font.render(vol_text, True, Colors.TEXT)
        self.screen.blit(vol_surface, (50, 200))
        
        # Volume bar
        vol_bar_width = 200
        vol_bar_height = 10
        vol_bar_rect = pygame.Rect(200, 205, vol_bar_width, vol_bar_height)
        pygame.draw.rect(self.screen, Colors.SURFACE, vol_bar_rect)
        
        vol_fill_width = int(vol_bar_width * self.volume)
        vol_fill_rect = pygame.Rect(200, 205, vol_fill_width, vol_bar_height)
        vol_color = Colors.GREEN if self.volume > 0.7 else Colors.ORANGE if self.volume > 0.3 else Colors.RED
        pygame.draw.rect(self.screen, vol_color, vol_fill_rect)
        
        # Instructions
        instructions = [
            "KEYS: A S D F (top row) | Q W E R (bottom row)",
            "VOLUME: ↑/↓ arrows | MOUSE: Click pads | ESC: Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.ui_font.render(instruction, True, Colors.TEXT_DIM)
            inst_rect = inst_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT - 80 + i * 30)
            self.screen.blit(inst_surface, inst_rect)
    
    def draw(self):
        self.draw_background()
        
        # Draw visualizer
        self.visualizer.draw(self.screen)
        
        # Draw drum pads
        for pad in self.drum_pads:
            pad.draw(self.screen, self.pad_font)
            
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        print("🥁 Enhanced Drum Kit Started!")
        print("Controls:")
        print("- A S D F (top row drums)")
        print("- Q W E R (bottom row drums)")  
        print("- ↑/↓ arrows (volume)")
        print("- Mouse click pads")
        print("- ESC to exit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

def main():
    app = EnhancedDrumKit()
    app.run()

if __name__ == "__main__":
    main()
