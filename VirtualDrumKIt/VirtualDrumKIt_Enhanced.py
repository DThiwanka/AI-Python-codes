"""
Enhanced Virtual Drum Kit with Modern Visual Styling
Features:
- Modern gradient backgrounds and glowing effects
- Animated drum pad responses with visual feedback
- Particle effects on drum hits
- Professional UI with glass morphism design
- Smooth animations and transitions
- Visual equalizer bars
- Custom color themes
"""

import sys
import time
import json
import math
import random
import asyncio
import traceback
from typing import List, Tuple, Dict

import numpy as np
import pygame
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
SAMPLE_RATE = 44100
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

# Color Schemes
class ColorTheme:
    # Dark Modern Theme
    DARK_BG = (15, 15, 25)
    DARK_SURFACE = (25, 25, 40)
    ACCENT_BLUE = (64, 156, 255)
    ACCENT_PURPLE = (138, 43, 226)
    ACCENT_CYAN = (0, 255, 255)
    ACCENT_ORANGE = (255, 140, 0)
    ACCENT_GREEN = (50, 205, 50)
    ACCENT_RED = (255, 69, 58)
    ACCENT_YELLOW = (255, 214, 10)
    
    TEXT_PRIMARY = (240, 240, 245)
    TEXT_SECONDARY = (160, 160, 175)
    TEXT_MUTED = (100, 100, 115)
    
    GLASS_WHITE = (255, 255, 255, 30)
    GLASS_BORDER = (255, 255, 255, 50)
    
    GLOW_INNER = (255, 255, 255, 100)
    GLOW_OUTER = (255, 255, 255, 20)

# Particle system for visual effects
class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], velocity: Tuple[float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 1.0
        self.size = random.uniform(2, 6)
        self.decay = random.uniform(0.02, 0.04)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] * 0.98 + 0.1)  # gravity
        self.life -= self.decay
        self.size *= 0.99
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life * 255)
            color = (*self.color, alpha)
            try:
                # Create a surface for the particle with per-pixel alpha
                particle_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (int(self.size), int(self.size)), int(self.size))
                surface.blit(particle_surf, (self.x - self.size, self.y - self.size))
            except:
                pass

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit(self, x: float, y: float, color: Tuple[int, int, int], count: int = 20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed - random.uniform(2, 5))
            self.particles.append(Particle(x, y, color, velocity))
    
    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Enhanced drum pad class
class DrumPad:
    def __init__(self, x: int, y: int, width: int, height: int, label: str, 
                 sound_name: str, key: int, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.sound_name = sound_name
        self.key = key
        self.color = color
        self.base_color = color
        self.is_pressed = False
        self.press_animation = 0.0
        self.glow_intensity = 0.0
        self.last_hit_time = 0
        self.hit_effect_duration = 0.3
        
    def update(self, dt: float):
        # Update animations
        if self.is_pressed:
            self.press_animation = min(1.0, self.press_animation + dt * 8)
        else:
            self.press_animation = max(0.0, self.press_animation - dt * 6)
            
        # Update glow effect
        time_since_hit = time.time() - self.last_hit_time
        if time_since_hit < self.hit_effect_duration:
            self.glow_intensity = 1.0 - (time_since_hit / self.hit_effect_duration)
        else:
            self.glow_intensity = 0.0
    
    def on_hit(self):
        self.last_hit_time = time.time()
        self.is_pressed = True
    
    def on_release(self):
        self.is_pressed = False
    
    def draw(self, surface, font):
        # Calculate dynamic colors and effects
        press_factor = self.press_animation * 0.3
        glow_factor = self.glow_intensity
        
        # Base pad color with press effect
        current_color = tuple(min(255, max(0, int(c * (1 + press_factor)))) for c in self.base_color)
        
        # Draw outer glow
        if glow_factor > 0:
            glow_size = int(20 * glow_factor)
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            
            # Create radial gradient for glow
            center = (glow_rect.width // 2, glow_rect.height // 2)
            for r in range(glow_size, 0, -2):
                alpha = int((1 - r / glow_size) * glow_factor * 100)
                color = (*current_color, alpha)
                pygame.draw.circle(glow_surf, color, center, 
                                 self.rect.width // 2 + r, 2)
            
            surface.blit(glow_surf, glow_rect.topleft)
        
        # Draw glass morphism background
        glass_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Background with transparency
        bg_alpha = 40 + int(press_factor * 30)
        pygame.draw.rect(glass_surf, (*ColorTheme.DARK_SURFACE, bg_alpha), 
                        (0, 0, self.rect.width, self.rect.height), border_radius=20)
        
        # Gradient overlay
        for i in range(self.rect.height // 2):
            alpha = int((1 - i / (self.rect.height // 2)) * 20)
            color = (*ColorTheme.GLASS_WHITE[:3], alpha)
            pygame.draw.rect(glass_surf, color, 
                           (0, i, self.rect.width, 2))
        
        surface.blit(glass_surf, self.rect.topleft)
        
        # Draw main pad with gradient
        pad_surf = pygame.Surface((self.rect.width - 8, self.rect.height - 8), pygame.SRCALPHA)
        
        # Create gradient effect
        for i in range(self.rect.height - 8):
            ratio = i / (self.rect.height - 8)
            color_top = tuple(min(255, max(0, int(c * 1.2))) for c in current_color)
            color_bottom = tuple(min(255, max(0, int(c * 0.8))) for c in current_color)
            
            blended_color = tuple(
                min(255, max(0, int(color_top[j] * (1 - ratio) + color_bottom[j] * ratio)))
                for j in range(3)
            )
            
            pygame.draw.rect(pad_surf, blended_color, (0, i, self.rect.width - 8, 1))
        
        # Apply border radius effect
        mask_surf = pygame.Surface((self.rect.width - 8, self.rect.height - 8), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), 
                        (0, 0, self.rect.width - 8, self.rect.height - 8), border_radius=15)
        
        pad_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        surface.blit(pad_surf, (self.rect.x + 4, self.rect.y + 4))
        
        # Draw border
        border_color = ColorTheme.GLASS_BORDER if not self.is_pressed else current_color
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=20)
        
        # Draw text with shadow
        text_color = ColorTheme.TEXT_PRIMARY
        shadow_color = (0, 0, 0, 100)
        
        # Main label
        text_surf = font.render(self.label, True, text_color)
        shadow_surf = font.render(self.label, True, shadow_color[:3])
        
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 15))
        shadow_rect = text_rect.move(2, 2)
        
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
        
        # Sound name
        small_font = pygame.font.Font(None, 24)
        sound_surf = small_font.render(self.sound_name, True, ColorTheme.TEXT_SECONDARY)
        sound_rect = sound_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
        surface.blit(sound_surf, sound_rect)
        
        # Key binding
        key_surf = small_font.render(f"Key: {pygame.key.name(self.key)}", True, ColorTheme.TEXT_MUTED)
        key_rect = key_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 35))
        surface.blit(key_surf, key_rect)

# Visual equalizer for audio visualization
class Equalizer:
    def __init__(self, x: int, y: int, width: int, height: int, num_bars: int = 20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.num_bars = num_bars
        self.bars = [0.0] * num_bars
        self.target_bars = [0.0] * num_bars
        
    def trigger(self, intensity: float = 1.0):
        # Simulate frequency response
        for i in range(self.num_bars):
            freq_response = random.uniform(0.3, 1.0) * intensity
            self.target_bars[i] = freq_response
    
    def update(self, dt: float):
        for i in range(self.num_bars):
            # Smooth interpolation
            diff = self.target_bars[i] - self.bars[i]
            self.bars[i] += diff * dt * 8
            
            # Decay
            self.target_bars[i] *= 0.95
            self.bars[i] = max(0, self.bars[i] - dt * 2)
    
    def draw(self, surface):
        bar_width = self.width // self.num_bars - 2
        
        for i, height_ratio in enumerate(self.bars):
            bar_height = int(self.height * height_ratio)
            bar_x = self.x + i * (bar_width + 2)
            bar_y = self.y + self.height - bar_height
            
            # Color gradient based on height
            if height_ratio > 0.8:
                color = ColorTheme.ACCENT_RED
            elif height_ratio > 0.6:
                color = ColorTheme.ACCENT_ORANGE
            elif height_ratio > 0.4:
                color = ColorTheme.ACCENT_YELLOW
            elif height_ratio > 0.2:
                color = ColorTheme.ACCENT_GREEN
            else:
                color = ColorTheme.ACCENT_BLUE
            
            # Draw bar with gradient
            for y in range(bar_height):
                alpha = int(255 * (1 - y / max(1, bar_height)) * 0.8 + 50)
                bar_color = (*color, min(255, alpha))
                try:
                    pygame.draw.rect(surface, bar_color, 
                                   (bar_x, bar_y + y, bar_width, 1))
                except:
                    pass

# Sound synthesis (simplified from original)
def create_kick_sound():
    duration = 0.6
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    freqs = 100 * (2.0 ** (-5 * t / duration))
    signal = 0.9 * np.sin(2 * np.pi * freqs * t)
    envelope = np.exp(-8 * t)
    signal *= envelope
    
    # Convert to stereo int16 - ensure C-contiguous
    stereo = np.vstack([signal, signal])
    int16_signal = (np.clip(stereo, -1, 1) * 32767).astype(np.int16).T
    int16_signal = np.ascontiguousarray(int16_signal)
    return pygame.sndarray.make_sound(int16_signal)

def create_snare_sound():
    duration = 0.4
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    noise = np.random.normal(0, 1, len(t)).astype(np.float32)
    tone = 0.4 * np.sin(2 * np.pi * 200 * t) * np.exp(-8 * t)
    signal = 0.7 * noise * np.exp(-10 * t) + tone
    
    stereo = np.vstack([signal, signal])
    int16_signal = (np.clip(stereo, -1, 1) * 32767).astype(np.int16).T
    int16_signal = np.ascontiguousarray(int16_signal)
    return pygame.sndarray.make_sound(int16_signal)

def create_hihat_sound():
    duration = 0.08
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    noise = np.random.normal(0, 1, len(t))
    signal = noise * np.sin(2 * np.pi * (5000 + 8000 * t) * t) * np.exp(-60 * t)
    
    stereo = np.vstack([signal, signal])
    int16_signal = (np.clip(stereo, -1, 1) * 32767).astype(np.int16).T
    int16_signal = np.ascontiguousarray(int16_signal)
    return pygame.sndarray.make_sound(int16_signal)

# Main application class
class EnhancedDrumKit:
    def __init__(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🥁 Enhanced Virtual Drum Kit")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 48)
        self.pad_font = pygame.font.Font(None, 32)
        self.ui_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        # Create particle system
        self.particles = ParticleSystem()
        
        # Create equalizer
        self.equalizer = Equalizer(50, 50, 300, 100)
        
        # Create drum pads
        self.create_drum_pads()
        
        # Load sounds
        self.load_sounds()
        
        # UI state
        self.master_volume = 0.8
        self.bpm = 120
        self.recording = False
        self.metronome_active = False
        
    def create_drum_pads(self):
        self.drum_pads = []
        
        # Pad layout configuration
        pad_configs = [
            # Row 1
            ("KICK", "kick", pygame.K_a, ColorTheme.ACCENT_RED),
            ("SNARE", "snare", pygame.K_s, ColorTheme.ACCENT_ORANGE),
            ("HI-HAT", "hihat", pygame.K_d, ColorTheme.ACCENT_YELLOW),
            ("CRASH", "crash", pygame.K_f, ColorTheme.ACCENT_GREEN),
            
            # Row 2
            ("TOM 1", "tom1", pygame.K_q, ColorTheme.ACCENT_BLUE),
            ("TOM 2", "tom2", pygame.K_w, ColorTheme.ACCENT_PURPLE),
            ("RIDE", "ride", pygame.K_e, ColorTheme.ACCENT_CYAN),
            ("CLAP", "clap", pygame.K_r, ColorTheme.ACCENT_GREEN),
        ]
        
        pad_width = 200
        pad_height = 120
        margin_x = 50
        margin_y = 200
        cols = 4
        
        for i, (label, sound_name, key, color) in enumerate(pad_configs):
            row = i // cols
            col = i % cols
            x = margin_x + col * (pad_width + margin_x)
            y = margin_y + row * (pad_height + margin_y)
            
            pad = DrumPad(x, y, pad_width, pad_height, label, sound_name, key, color)
            self.drum_pads.append(pad)
    
    def load_sounds(self):
        self.sounds = {
            "kick": create_kick_sound(),
            "snare": create_snare_sound(),
            "hihat": create_hihat_sound(),
            "crash": create_hihat_sound(),  # Placeholder
            "tom1": create_kick_sound(),    # Placeholder
            "tom2": create_kick_sound(),    # Placeholder
            "ride": create_hihat_sound(),   # Placeholder
            "clap": create_snare_sound(),   # Placeholder
        }
    
    def play_sound(self, sound_name: str, pad: DrumPad):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.master_volume)
            sound.play()
            
            # Visual effects
            pad.on_hit()
            self.particles.emit(pad.rect.centerx, pad.rect.centery, pad.color, 15)
            self.equalizer.trigger(0.8)
    
    def draw_background(self):
        # Gradient background
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color = tuple(
                int(ColorTheme.DARK_BG[i] * (1 - ratio) + ColorTheme.DARK_SURFACE[i] * ratio)
                for i in range(3)
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def draw_title(self):
        title_text = "🥁 ENHANCED DRUM KIT"
        title_surf = self.title_font.render(title_text, True, ColorTheme.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 50))
        
        # Title glow effect
        glow_surf = self.title_font.render(title_text, True, ColorTheme.ACCENT_BLUE)
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_rect = title_rect.move(*offset)
            self.screen.blit(glow_surf, glow_rect)
        
        self.screen.blit(title_surf, title_rect)
    
    def draw_controls(self):
        # Control panel background
        panel_rect = pygame.Rect(50, WINDOW_HEIGHT - 200, WINDOW_WIDTH - 100, 150)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*ColorTheme.DARK_SURFACE, 100), 
                        (0, 0, panel_rect.width, panel_rect.height), border_radius=15)
        self.screen.blit(panel_surf, panel_rect.topleft)
        
        # Volume control visualization
        vol_x = 70
        vol_y = WINDOW_HEIGHT - 160
        vol_width = 200
        vol_height = 20
        
        # Volume bar background
        pygame.draw.rect(self.screen, ColorTheme.DARK_BG, 
                        (vol_x, vol_y, vol_width, vol_height), border_radius=10)
        
        # Volume bar fill
        fill_width = int(vol_width * self.master_volume)
        color = ColorTheme.ACCENT_GREEN if self.master_volume > 0.7 else ColorTheme.ACCENT_ORANGE
        pygame.draw.rect(self.screen, color, 
                        (vol_x, vol_y, fill_width, vol_height), border_radius=10)
        
        # Volume label
        vol_text = f"Volume: {int(self.master_volume * 100)}%"
        vol_surf = self.ui_font.render(vol_text, True, ColorTheme.TEXT_PRIMARY)
        self.screen.blit(vol_surf, (vol_x, vol_y - 30))
        
        # Instructions
        instructions = [
            "Controls: A S D F Q W E R - Play drums",
            "Mouse: Click drum pads",
            "Volume: Up/Down arrows",
            "ESC: Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surf = self.small_font.render(instruction, True, ColorTheme.TEXT_SECONDARY)
            self.screen.blit(inst_surf, (400, WINDOW_HEIGHT - 180 + i * 25))
    
    def handle_events(self):
        dt = self.clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Volume controls
                if event.key == pygame.K_UP:
                    self.master_volume = min(1.0, self.master_volume + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.master_volume = max(0.0, self.master_volume - 0.1)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    # Check drum pad keys
                    for pad in self.drum_pads:
                        if event.key == pad.key:
                            self.play_sound(pad.sound_name, pad)
            
            elif event.type == pygame.KEYUP:
                # Release drum pads
                for pad in self.drum_pads:
                    if event.key == pad.key:
                        pad.on_release()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check pad clicks
                mouse_pos = pygame.mouse.get_pos()
                for pad in self.drum_pads:
                    if pad.rect.collidepoint(mouse_pos):
                        self.play_sound(pad.sound_name, pad)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # Release all pads
                for pad in self.drum_pads:
                    pad.on_release()
        
        return dt
    
    def update(self, dt: float):
        # Update drum pads
        for pad in self.drum_pads:
            pad.update(dt)
        
        # Update particle system
        self.particles.update()
        
        # Update equalizer
        self.equalizer.update(dt)
    
    def draw(self):
        # Draw background
        self.draw_background()
        
        # Draw title
        self.draw_title()
        
        # Draw equalizer
        self.equalizer.draw(self.screen)
        
        # Draw drum pads
        for pad in self.drum_pads:
            pad.draw(self.screen, self.pad_font)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Draw controls
        self.draw_controls()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        print("🥁 Enhanced Virtual Drum Kit Started!")
        print("Controls:")
        print("- Keys: A S D F Q W E R")
        print("- Mouse: Click drum pads")
        print("- Volume: Up/Down arrows")
        print("- ESC: Exit")
        
        while self.running:
            dt = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()

def main():
    app = EnhancedDrumKit()
    app.run()

if __name__ == "__main__":
    main()
