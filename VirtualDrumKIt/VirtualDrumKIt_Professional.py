"""
Professional Virtual Drum Kit with Advanced Visual Effects
Features:
- Glass morphism design
- Smooth animations and transitions  
- Real-time visualizer with frequency bands
- Professional color schemes
- Particle effects on drum hits
- Wave ripple effects
- Dynamic lighting
"""

import pygame
import numpy as np
import math
import time
import random
from typing import List, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

class Theme:
    # Professional dark theme
    BG_PRIMARY = (12, 12, 20)
    BG_SECONDARY = (18, 18, 28)
    BG_TERTIARY = (25, 25, 35)
    
    # Neon accent colors
    ELECTRIC_BLUE = (0, 191, 255)
    NEON_GREEN = (57, 255, 20)
    HOT_PINK = (255, 20, 147)
    CYBER_YELLOW = (255, 255, 0)
    PLASMA_PURPLE = (191, 64, 255)
    LASER_RED = (255, 64, 64)
    ARCTIC_CYAN = (64, 255, 255)
    TOXIC_ORANGE = (255, 165, 0)
    
    # UI colors
    TEXT_BRIGHT = (255, 255, 255)
    TEXT_NORMAL = (220, 220, 220)
    TEXT_DIM = (140, 140, 140)
    GLASS = (255, 255, 255, 30)
    BORDER_GLOW = (255, 255, 255, 100)

class Particle:
    def __init__(self, x, y, color, velocity=(0, 0), size=3, life=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = list(velocity)
        self.size = size
        self.life = life
        self.max_life = life
        
    def update(self, dt):
        # Move particle
        self.x += self.velocity[0] * dt * 60
        self.y += self.velocity[1] * dt * 60
        
        # Apply physics
        self.velocity[1] += 200 * dt  # gravity
        self.velocity[0] *= 0.98  # air resistance
        self.velocity[1] *= 0.98
        
        # Fade out
        self.life -= dt * 2
        self.size *= 0.995
        
    def draw(self, screen):
        if self.life <= 0:
            return
            
        alpha = int(255 * (self.life / self.max_life))
        size = max(1, int(self.size))
        
        # Create particle surface with alpha
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
        
        # Add glow effect
        if size > 2:
            glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            glow_color = (*self.color, alpha // 4)
            pygame.draw.circle(glow_surf, glow_color, (size * 2, size * 2), size * 2)
            screen.blit(glow_surf, (self.x - size * 2, self.y - size * 2))
        
        screen.blit(particle_surf, (self.x - size, self.y - size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def emit_burst(self, x, y, color, count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed - random.uniform(50, 150))
            size = random.uniform(2, 6)
            life = random.uniform(0.5, 1.5)
            
            self.particles.append(Particle(x, y, color, velocity, size, life))
    
    def update(self, dt):
        # Update all particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0 or particle.size < 0.5:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class WaveRipple:
    def __init__(self, x, y, color, max_radius=100):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 0
        self.max_radius = max_radius
        self.life = 1.0
        
    def update(self, dt):
        self.radius += dt * 300  # Expansion speed
        self.life = max(0, 1.0 - (self.radius / self.max_radius))
        
    def draw(self, screen):
        if self.life <= 0:
            return
            
        alpha = int(self.life * 100)
        if alpha > 0:
            # Draw multiple concentric circles for wave effect
            for i in range(3):
                r = self.radius - i * 10
                if r > 0:
                    wave_alpha = max(0, alpha - i * 30)
                    color_with_alpha = (*self.color, wave_alpha)
                    
                    # Create wave surface
                    wave_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
                    pygame.draw.circle(wave_surf, color_with_alpha, (r + 10, r + 10), int(r), 3)
                    screen.blit(wave_surf, (self.x - r - 10, self.y - r - 10))

class ProfessionalDrumPad:
    def __init__(self, x, y, width, height, label, sound_name, key, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.sound_name = sound_name
        self.key = key
        self.color = color
        self.base_color = color
        
        # Animation states
        self.is_pressed = False
        self.press_animation = 0.0
        self.glow_intensity = 0.0
        self.pulse_phase = 0.0
        self.hit_time = 0
        
        # Visual effects
        self.brightness_multiplier = 1.0
        self.scale_factor = 1.0
        
    def hit(self):
        self.is_pressed = True
        self.hit_time = time.time()
        self.glow_intensity = 1.0
        
    def release(self):
        self.is_pressed = False
        
    def update(self, dt):
        # Press animation
        target_press = 1.0 if self.is_pressed else 0.0
        self.press_animation += (target_press - self.press_animation) * dt * 12
        
        # Glow fade
        self.glow_intensity = max(0, self.glow_intensity - dt * 3)
        
        # Pulse effect
        self.pulse_phase += dt * 4
        
        # Scale animation
        target_scale = 0.95 if self.is_pressed else 1.0
        self.scale_factor += (target_scale - self.scale_factor) * dt * 10
        
        # Brightness
        self.brightness_multiplier = 0.8 + 0.2 * self.press_animation + 0.3 * self.glow_intensity
        
    def get_scaled_rect(self):
        # Calculate scaled rectangle for animation
        center = self.rect.center
        scaled_width = int(self.rect.width * self.scale_factor)
        scaled_height = int(self.rect.height * self.scale_factor)
        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_rect.center = center
        return scaled_rect
        
    def draw(self, screen, font):
        scaled_rect = self.get_scaled_rect()
        
        # Calculate current color
        brightness = self.brightness_multiplier
        current_color = tuple(min(255, int(c * brightness)) for c in self.base_color)
        
        # Draw outer glow
        if self.glow_intensity > 0:
            glow_size = int(30 * self.glow_intensity)
            glow_rect = scaled_rect.inflate(glow_size * 2, glow_size * 2)
            
            # Multiple glow layers
            for i in range(5):
                layer_size = glow_size - i * 3
                if layer_size > 0:
                    layer_alpha = int(self.glow_intensity * 40 * (5 - i) / 5)
                    layer_rect = scaled_rect.inflate(layer_size * 2, layer_size * 2)
                    
                    glow_surf = pygame.Surface((layer_rect.width, layer_rect.height), pygame.SRCALPHA)
                    glow_color = (*current_color, layer_alpha)
                    pygame.draw.rect(glow_surf, glow_color, (0, 0, layer_rect.width, layer_rect.height), 
                                   border_radius=20)
                    screen.blit(glow_surf, layer_rect)
        
        # Draw glass background
        glass_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        
        # Main background with transparency
        bg_alpha = 60 + int(self.press_animation * 40)
        pygame.draw.rect(glass_surf, (*Theme.BG_TERTIARY, bg_alpha), 
                        (0, 0, scaled_rect.width, scaled_rect.height), border_radius=20)
        
        # Gradient overlay for glass effect
        for i in range(scaled_rect.height // 3):
            alpha = int(30 * (1 - i / (scaled_rect.height // 3)))
            pygame.draw.rect(glass_surf, (*Theme.GLASS[:3], alpha), 
                           (0, i, scaled_rect.width, 1))
        
        screen.blit(glass_surf, scaled_rect)
        
        # Draw main pad with gradient
        pad_surf = pygame.Surface((scaled_rect.width - 6, scaled_rect.height - 6), pygame.SRCALPHA)
        
        # Vertical gradient
        for y in range(scaled_rect.height - 6):
            progress = y / (scaled_rect.height - 6)
            
            # Create gradient from light to dark
            top_color = tuple(min(255, int(c * 1.3)) for c in current_color)
            bottom_color = tuple(max(0, int(c * 0.7)) for c in current_color)
            
            gradient_color = tuple(
                int(top_color[i] * (1 - progress) + bottom_color[i] * progress)
                for i in range(3)
            )
            
            pygame.draw.rect(pad_surf, gradient_color, (0, y, scaled_rect.width - 6, 1))
        
        screen.blit(pad_surf, (scaled_rect.x + 3, scaled_rect.y + 3))
        
        # Draw border with glow
        border_alpha = 150 + int(self.glow_intensity * 105)
        border_color = (*current_color, border_alpha) if self.glow_intensity > 0 else (*Theme.BORDER_GLOW[:3], 80)
        
        border_surf = pygame.Surface((scaled_rect.width + 4, scaled_rect.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, border_color, (0, 0, scaled_rect.width + 4, scaled_rect.height + 4), 
                        2, border_radius=22)
        screen.blit(border_surf, (scaled_rect.x - 2, scaled_rect.y - 2))
        
        # Draw text with glow
        text_color = Theme.TEXT_BRIGHT
        
        # Text glow
        if self.glow_intensity > 0:
            glow_text = font.render(self.label, True, current_color)
            for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
                glow_rect = glow_text.get_rect(center=(scaled_rect.centerx + offset[0], 
                                                     scaled_rect.centery - 10 + offset[1]))
                glow_alpha_surf = glow_text.copy()
                glow_alpha_surf.set_alpha(int(self.glow_intensity * 100))
                screen.blit(glow_alpha_surf, glow_rect)
        
        # Main text
        text_surf = font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 10))
        screen.blit(text_surf, text_rect)
        
        # Key binding
        key_font = pygame.font.Font(None, 22)
        key_text = key_font.render(f"[{pygame.key.name(self.key).upper()}]", True, Theme.TEXT_DIM)
        key_rect = key_text.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + 25))
        screen.blit(key_text, key_rect)

class AdvancedVisualizer:
    def __init__(self, x, y, width, height, bands=24):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bands = bands
        self.values = [0.0] * bands
        self.peak_values = [0.0] * bands
        self.peak_decay = [0.0] * bands
        
    def trigger(self, intensity=1.0):
        # Simulate frequency response with some randomness
        for i in range(self.bands):
            # Create a frequency response curve
            freq_mult = 1.0 - abs(i - self.bands // 2) / (self.bands // 2)
            value = random.uniform(0.3, 1.0) * intensity * freq_mult
            self.values[i] = max(self.values[i], value)
            
            if value > self.peak_values[i]:
                self.peak_values[i] = value
                self.peak_decay[i] = 0.0
                
    def update(self, dt):
        for i in range(self.bands):
            # Smooth decay
            self.values[i] = max(0, self.values[i] - dt * 4)
            
            # Peak decay
            self.peak_decay[i] += dt
            if self.peak_decay[i] > 0.1:  # Hold peak for a moment
                self.peak_values[i] = max(0, self.peak_values[i] - dt * 2)
                
    def draw(self, screen):
        band_width = (self.width - (self.bands - 1) * 2) // self.bands
        
        for i, (value, peak) in enumerate(zip(self.values, self.peak_values)):
            band_x = self.x + i * (band_width + 2)
            band_height = int(self.height * value)
            peak_height = int(self.height * peak)
            
            band_y = self.y + self.height - band_height
            peak_y = self.y + self.height - peak_height
            
            # Color based on frequency position
            if i < self.bands // 4:
                color = Theme.LASER_RED
            elif i < self.bands // 2:
                color = Theme.TOXIC_ORANGE
            elif i < 3 * self.bands // 4:
                color = Theme.CYBER_YELLOW
            else:
                color = Theme.NEON_GREEN
            
            # Draw main bar with gradient
            if band_height > 0:
                for y in range(band_height):
                    alpha = int(255 * (1 - y / band_height) * 0.8 + 50)
                    bar_color = (*color, alpha)
                    bar_surf = pygame.Surface((band_width, 1), pygame.SRCALPHA)
                    bar_surf.fill(bar_color)
                    screen.blit(bar_surf, (band_x, band_y + y))
            
            # Draw peak indicator
            if peak_height > band_height + 2:
                peak_surf = pygame.Surface((band_width, 2), pygame.SRCALPHA)
                peak_surf.fill((*color, 200))
                screen.blit(peak_surf, (band_x, peak_y))

# Sound generation functions (same as before but with better quality)
def create_kick():
    duration = 0.6
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    t = np.linspace(0, duration, frames, False)
    # More realistic kick with pitch bend
    frequency = 80 * np.exp(-t * 8) + 40 * np.exp(-t * 4)
    wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 5)
    
    # Add some harmonics
    wave += 0.3 * np.sin(4 * np.pi * frequency * t) * np.exp(-t * 8)
    
    wave = np.clip(wave * 0.9, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

def create_snare():
    duration = 0.35
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    t = np.linspace(0, duration, frames, False)
    # Mix of tone and noise
    tone = np.sin(2 * np.pi * 250 * t) * 0.4 * np.exp(-t * 12)
    noise = np.random.normal(0, 0.5, frames) * np.exp(-t * 8)
    
    wave = tone + noise
    wave = np.clip(wave, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

def create_hihat():
    duration = 0.12
    sample_rate = 44100  
    frames = int(duration * sample_rate)
    
    t = np.linspace(0, duration, frames, False)
    # High frequency content for hi-hat
    noise = np.random.normal(0, 0.4, frames)
    high_freq = np.sin(2 * np.pi * 10000 * t) * 0.3
    
    wave = (noise + high_freq) * np.exp(-t * 40)
    wave = np.clip(wave, -1, 1)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

class ProfessionalDrumKit:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🥁 Professional Virtual Drum Kit")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.pad_font = pygame.font.Font(None, 36)
        self.ui_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Visual effects
        self.particles = ParticleSystem()
        self.ripples = []
        self.visualizer = AdvancedVisualizer(100, 80, 400, 120)
        
        # Create drum pads
        self.drum_pads = []
        self.create_pads()
        
        # Load sounds
        self.sounds = {
            'kick': create_kick(),
            'snare': create_snare(),
            'hihat': create_hihat(),
            'tom1': create_kick(),
            'tom2': create_kick(),
            'crash': create_hihat(),
            'ride': create_hihat(), 
            'clap': create_snare()
        }
        
        # Settings
        self.volume = 0.8
        
    def create_pads(self):
        pad_configs = [
            # Top row
            ("KICK", "kick", pygame.K_a, Theme.LASER_RED),
            ("SNARE", "snare", pygame.K_s, Theme.TOXIC_ORANGE),
            ("HI-HAT", "hihat", pygame.K_d, Theme.CYBER_YELLOW),
            ("CRASH", "crash", pygame.K_f, Theme.NEON_GREEN),
            
            # Bottom row
            ("TOM 1", "tom1", pygame.K_q, Theme.ELECTRIC_BLUE),
            ("TOM 2", "tom2", pygame.K_w, Theme.PLASMA_PURPLE),
            ("RIDE", "ride", pygame.K_e, Theme.ARCTIC_CYAN),
            ("CLAP", "clap", pygame.K_r, Theme.HOT_PINK),
        ]
        
        pad_width = 200
        pad_height = 120
        start_x = 150
        start_y = 300
        cols = 4
        
        for i, (label, sound_name, key, color) in enumerate(pad_configs):
            row = i // cols
            col = i % cols
            x = start_x + col * (pad_width + 50)
            y = start_y + row * (pad_height + 60)
            
            pad = ProfessionalDrumPad(x, y, pad_width, pad_height, label, sound_name, key, color)
            self.drum_pads.append(pad)
    
    def play_sound(self, sound_name, pad):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
            
            # Visual effects
            pad.hit()
            self.particles.emit_burst(pad.rect.centerx, pad.rect.centery, pad.color, 20)
            self.ripples.append(WaveRipple(pad.rect.centerx, pad.rect.centery, pad.color, 120))
            self.visualizer.trigger(0.9)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.volume = min(1.0, self.volume + 0.05)
                elif event.key == pygame.K_DOWN:
                    self.volume = max(0.0, self.volume - 0.05)
                else:
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
    
    def update(self, dt):
        # Update drum pads
        for pad in self.drum_pads:
            pad.update(dt)
            
        # Update visual effects
        self.particles.update(dt)
        self.visualizer.update(dt)
        
        # Update ripples
        for ripple in self.ripples[:]:
            ripple.update(dt)
            if ripple.life <= 0:
                self.ripples.remove(ripple)
    
    def draw_background(self):
        # Animated gradient background
        time_factor = time.time() * 0.5
        
        for y in range(WINDOW_HEIGHT):
            progress = y / WINDOW_HEIGHT
            
            # Create moving gradient
            wave = math.sin(progress * math.pi + time_factor) * 0.1
            
            r = int(Theme.BG_PRIMARY[0] * (1 + wave))
            g = int(Theme.BG_PRIMARY[1] * (1 + wave))
            b = int(Theme.BG_PRIMARY[2] * (1 + progress * 0.3 + wave))
            
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def draw_ui(self):
        # Title with glow effect
        title_text = "🥁 PROFESSIONAL DRUM KIT"
        
        # Title glow
        for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            glow_surf = self.title_font.render(title_text, True, Theme.ELECTRIC_BLUE)
            glow_surf.set_alpha(100)
            glow_rect = glow_surf.get_rect(centerx=WINDOW_WIDTH // 2 + offset[0], y=30 + offset[1])
            self.screen.blit(glow_surf, glow_rect)
            
        # Main title
        title_surf = self.title_font.render(title_text, True, Theme.TEXT_BRIGHT)
        title_rect = title_surf.get_rect(centerx=WINDOW_WIDTH // 2, y=30)
        self.screen.blit(title_surf, title_rect)
        
        # Volume control
        vol_text = f"VOLUME: {int(self.volume * 100)}%"
        vol_surf = self.ui_font.render(vol_text, True, Theme.TEXT_NORMAL)
        self.screen.blit(vol_surf, (100, 230))
        
        # Volume bar
        vol_bar_rect = pygame.Rect(280, 235, 300, 15)
        pygame.draw.rect(self.screen, Theme.BG_TERTIARY, vol_bar_rect, border_radius=8)
        
        vol_fill_width = int(300 * self.volume)
        vol_fill_rect = pygame.Rect(280, 235, vol_fill_width, 15)
        
        # Volume color based on level
        if self.volume > 0.8:
            vol_color = Theme.LASER_RED
        elif self.volume > 0.6:
            vol_color = Theme.TOXIC_ORANGE
        elif self.volume > 0.3:
            vol_color = Theme.CYBER_YELLOW
        else:
            vol_color = Theme.NEON_GREEN
            
        pygame.draw.rect(self.screen, vol_color, vol_fill_rect, border_radius=8)
        
        # Instructions
        instructions = [
            "🎵 CONTROLS:",
            "A S D F (Top Row) | Q W E R (Bottom Row)",
            "↑/↓ Volume | Mouse Click | ESC Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            color = Theme.TEXT_BRIGHT if i == 0 else Theme.TEXT_DIM
            font = self.ui_font if i == 0 else self.small_font
            
            inst_surf = font.render(instruction, True, color)
            inst_rect = inst_surf.get_rect(centerx=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT - 90 + i * 25)
            self.screen.blit(inst_surf, inst_rect)
    
    def draw(self):
        self.draw_background()
        
        # Draw ripple effects
        for ripple in self.ripples:
            ripple.draw(self.screen)
            
        # Draw visualizer
        self.visualizer.draw(self.screen)
        
        # Draw drum pads
        for pad in self.drum_pads:
            pad.draw(self.screen, self.pad_font)
            
        # Draw particle effects
        self.particles.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        print("🥁 Professional Virtual Drum Kit Started!")
        print("Features:")
        print("- Advanced visual effects")
        print("- Real-time visualizer")
        print("- Professional glass morphism design")
        print("")
        print("Controls:")
        print("- A S D F (top row)")
        print("- Q W E R (bottom row)")
        print("- ↑/↓ arrows (volume)")
        print("- Mouse clicks")
        print("- ESC to exit")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()

def main():
    app = ProfessionalDrumKit()
    app.run()

if __name__ == "__main__":
    main()
