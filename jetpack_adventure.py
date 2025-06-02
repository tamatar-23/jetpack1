#!/usr/bin/env python3
import pygame
import sys
import random
import os
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()  

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 0.3  # Reduced gravity for smoother falling
JUMP_STRENGTH = -7  # Less intense jump for more control
MAX_VELOCITY = 12  # Cap on maximum velocity
JETPACK_ACCELERATION = 0.8  # Gradual acceleration for jetpack
JETPACK_DECELERATION = 0.4  # Gradual deceleration when releasing jetpack
SCROLL_SPEED = 5
OBSTACLE_FREQUENCY = 1500  # milliseconds
COIN_FREQUENCY = 2000  # milliseconds
BACKGROUND_SPEED = 2
MISSILE_SPEED = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (135, 206, 250)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jetpack Adventure")
clock = pygame.time.Clock()

# Load fonts
# Use a more pixelated font style - try to use a more retro font if available
try:
    # Try to load a more pixelated retro font if available
    font_large = pygame.font.Font(None, 48)  # Use default font as fallback
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    
    # Try to find retro fonts on the system
    available_fonts = pygame.font.get_fonts()
    retro_fonts = ['pressstart2p', 'pixelmix', 'fixedsys', 'courier', 'consolas']
    
    for font in retro_fonts:
        if font in available_fonts:
            font_large = pygame.font.SysFont(font, 36, bold=True)
            font_medium = pygame.font.SysFont(font, 28, bold=True)
            font_small = pygame.font.SysFont(font, 20, bold=True)
            break
    
    # If no retro fonts found, make the default font bold for better visibility
    if font_large == pygame.font.Font(None, 48):
        font_large = pygame.font.SysFont(None, 36, bold=True)
        font_medium = pygame.font.SysFont(None, 28, bold=True)
        font_small = pygame.font.SysFont(None, 20, bold=True)
        
except:
    # Fallback to default fonts if custom ones aren't available
    font_large = pygame.font.SysFont(None, 36, bold=True)
    font_medium = pygame.font.SysFont(None, 28, bold=True)
    font_small = pygame.font.SysFont(None, 20, bold=True)

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
sounds_dir = os.path.join(assets_dir, 'sounds')
os.makedirs(assets_dir, exist_ok=True)
os.makedirs(sounds_dir, exist_ok=True)

# Sound effects
sounds = {}

# Function to create and save sound effects programmatically
def create_sound_effects():
    # Create jetpack sound (white noise with filtering)
    jetpack_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(
        np.random.randint(-32768, 32767, size=44100).astype(np.int16)))
    jetpack_sound.set_volume(0.4)
    
    # Create explosion sound (burst of noise with decay)
    explosion_samples = np.random.randint(-32768, 32767, size=22050).astype(np.int16)
    for i in range(len(explosion_samples)):
        explosion_samples[i] = int(explosion_samples[i] * (1 - i/len(explosion_samples)))
    explosion_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(explosion_samples))
    explosion_sound.set_volume(0.7)
    
    # Create coin collection sound (ascending beeps)
    coin_samples = np.zeros(11025, dtype=np.int16)
    for i in range(5):
        freq = 800 + i * 200
        for j in range(2205):
            t = j / 44100
            coin_samples[i*2205 + j] = int(32767 * 0.6 * math.sin(2 * math.pi * freq * t))
    coin_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(coin_samples))
    coin_sound.set_volume(0.5)
    
    # Create laser sound (sci-fi zap)
    laser_samples = np.zeros(11025, dtype=np.int16)
    for i in range(len(laser_samples)):
        t = i / 44100
        freq = 2000 - 1500 * (i / len(laser_samples))
        laser_samples[i] = int(32767 * 0.6 * math.sin(2 * math.pi * freq * t))
    laser_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(laser_samples))
    laser_sound.set_volume(0.5)
    
    # Create menu select sound (short beep)
    menu_samples = np.zeros(5512, dtype=np.int16)
    for i in range(len(menu_samples)):
        t = i / 44100
        freq = 1200
        menu_samples[i] = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
    menu_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(menu_samples))
    menu_sound.set_volume(0.6)
    
    # Create game over sound (descending notes)
    gameover_samples = np.zeros(22050, dtype=np.int16)
    for i in range(4):
        freq = 800 - i * 200
        for j in range(5512):
            t = j / 44100
            gameover_samples[i*5512 + j] = int(32767 * 0.7 * math.sin(2 * math.pi * freq * t))
    gameover_sound = pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(gameover_samples))
    gameover_sound.set_volume(0.7)
    
    # Store sounds in dictionary
    sounds["jetpack"] = jetpack_sound
    sounds["explosion"] = explosion_sound
    sounds["coin"] = coin_sound
    sounds["laser"] = laser_sound
    sounds["menu"] = menu_sound
    sounds["gameover"] = gameover_sound

# Create background music programmatically
def create_background_music():
    # Create a simple chiptune-style background music
    duration = 10  # seconds
    sample_rate = 44100
    total_samples = duration * sample_rate
    
    # Create a numpy array for the samples
    music_samples = np.zeros(total_samples, dtype=np.int16)
    
    # Define a simple melody (frequencies in Hz)
    melody = [262, 294, 330, 349, 392, 440, 494, 523]  # C4 to C5
    note_duration = 0.25  # seconds
    note_samples = int(note_duration * sample_rate)
    
    # Create a bassline
    bassline = [65, 73, 82, 98]  # C2, D2, E2, G2
    bass_duration = 0.5  # seconds
    bass_samples = int(bass_duration * sample_rate)
    
    # Fill the array with the melody and bassline
    for i in range(0, total_samples, note_samples * 8):
        # Melody
        for j, freq in enumerate(melody):
            if i + j * note_samples >= total_samples:
                break
                
            for k in range(note_samples):
                if i + j * note_samples + k >= total_samples:
                    break
                    
                t = k / sample_rate
                # Add some simple envelope
                if k < note_samples * 0.1:
                    amp = k / (note_samples * 0.1)  # Attack
                elif k > note_samples * 0.7:
                    amp = (note_samples - k) / (note_samples * 0.3)  # Release
                else:
                    amp = 1.0  # Sustain
                    
                # Add the melody note
                music_samples[i + j * note_samples + k] += int(16000 * amp * 0.5 * math.sin(2 * math.pi * freq * t))
        
        # Bassline
        for j in range(4):
            bass_freq = bassline[j % len(bassline)]
            if i + j * bass_samples >= total_samples:
                break
                
            for k in range(bass_samples):
                if i + j * bass_samples + k >= total_samples:
                    break
                    
                t = k / sample_rate
                # Add the bass note
                music_samples[i + j * bass_samples + k] += int(16000 * 0.3 * math.sin(2 * math.pi * bass_freq * t))
    
    # Save the music to a temporary WAV file
    music_path = os.path.join(sounds_dir, "background_music.wav")
    with wave.open(music_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(music_samples.tobytes())
    
    return music_path

# Try to import numpy for sound generation
try:
    import numpy as np
    import wave
    
    # Create sound effects
    create_sound_effects()
    
    # Create background music
    music_path = create_background_music()
    
    # Load the background music
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    
except ImportError:
    print("Numpy not found. Using silent mode.")
    # Create empty sounds dictionary
    sounds = {
        "jetpack": None,
        "explosion": None,
        "coin": None,
        "laser": None,
        "menu": None,
        "gameover": None
    }

# Global flag for sound effects
sounds_enabled = True

# Function to play sound safely
def play_sound(sound_name):
    if sounds_enabled and sound_name in sounds and sounds[sound_name] is not None:
        sounds[sound_name].play()

# Global game instance for particle effects
game_instance = None

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, is_dust=False):
        self.x = x
        self.y = y
        self.size = random.randint(3, 8)
        self.life = random.uniform(0.5, 1.5)
        self.is_dust = is_dust
        
        if is_dust:
            # Dust particles (when hitting ground)
            self.color = (100, 100, 100)  # Hardcoded GRAY value
            self.velocity_x = random.uniform(-2, 2)
            self.velocity_y = random.uniform(-3, -1)
        else:
            # Jetpack smoke particles
            color_choice = random.randint(0, 2)
            if color_choice == 0:
                self.color = (255, 165, 0)  # ORANGE
            elif color_choice == 1:
                self.color = (255, 255, 0)  # YELLOW
            else:
                self.color = (100, 100, 100)  # GRAY
            self.velocity_x = random.uniform(-1, -3)
            self.velocity_y = random.uniform(-0.5, 0.5)
    
    def update(self):
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Dust particles are affected by gravity
        if self.is_dust:
            self.velocity_y += 0.1
        
        # Decrease life and size
        self.life -= 0.05
        self.size = max(1, self.size * 0.95)
        
        # Return True if particle is still alive
        return self.life > 0
    
    def draw(self):
        # Calculate alpha based on remaining life
        alpha = int(255 * self.life)
        
        # Create a valid color with alpha
        try:
            # For pygame.draw.circle, we need to ensure the color is in the correct format
            if isinstance(self.color, tuple):
                if len(self.color) == 3:
                    # RGB tuple - use as is
                    color = self.color
                elif len(self.color) == 4:
                    # RGBA tuple - use RGB part only
                    color = self.color[:3]
                else:
                    # Invalid tuple length - use default
                    color = (255, 255, 255)
            else:
                # Not a tuple - use default
                color = (255, 255, 255)
        except:
            # Any error - fall back to white
            color = (255, 255, 255)
        
        # Draw particle
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (self.size // 2, self.size // 2), self.size // 2)
        
        # Apply alpha by setting the surface alpha
        particle_surface.set_alpha(alpha)
        
        # Draw to screen
        screen.blit(particle_surface, (int(self.x), int(self.y)))
# Game classes
class Player:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = 200
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.jetpack_on = False
        self.alive = True
        self.frame = 0
        self.animation_speed = 0.2
        self.jetpack_frames = []
        self.normal_frames = []
        
        # Create player animations
        self.create_player_frames()
        
        # Collision rectangle
        self.rect = pygame.Rect(self.x, self.y, self.width - 20, self.height - 20)
    
    def create_player_frames(self):
        # Create pixelated player frames
        base_player = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Body (more blocky/pixelated)
        pygame.draw.rect(base_player, BLUE, (10, 10, self.width - 20, self.height - 35))
        
        # Head (square for pixelated look)
        pygame.draw.rect(base_player, BLUE, (15, 5, self.width - 30, 25))
        
        # Eyes (simple pixels)
        pygame.draw.rect(base_player, WHITE, (self.width - 25, 10, 10, 10))
        pygame.draw.rect(base_player, BLACK, (self.width - 22, 13, 4, 4))
        
        # Helmet (pixelated)
        pygame.draw.rect(base_player, ORANGE, (10, 5, self.width - 20, 10))
        pygame.draw.rect(base_player, ORANGE, (5, 10, 10, 15))
        
        # Create normal frames with different leg positions
        for i in range(4):
            frame = base_player.copy()
            # Draw legs in different positions (pixelated)
            if i % 2 == 0:
                pygame.draw.rect(frame, BLUE, (15, self.height - 30, 15, 25))  # Left leg
                pygame.draw.rect(frame, BLUE, (self.width - 30, self.height - 20, 15, 15))  # Right leg bent
            else:
                pygame.draw.rect(frame, BLUE, (15, self.height - 20, 15, 15))  # Left leg bent
                pygame.draw.rect(frame, BLUE, (self.width - 30, self.height - 30, 15, 25))  # Right leg
            self.normal_frames.append(frame)
        
        # Create jetpack frames
        for i in range(4):
            frame = base_player.copy()
            # Draw jetpack (pixelated)
            pygame.draw.rect(frame, GRAY, (0, self.height - 60, 15, 40))
            
            # Draw flame with different lengths (pixelated)
            flame_height = 15 + i * 8
            flame = pygame.Surface((15, flame_height), pygame.SRCALPHA)
            
            # Main flame (pixelated triangle)
            for y in range(flame_height):
                width = max(3, 15 * (1 - y/flame_height))
                x_start = int((15 - width) / 2)
                pygame.draw.rect(flame, ORANGE, (x_start, y, int(width), 1))
            
            # Inner flame (pixelated)
            for y in range(flame_height - 5):
                if y < flame_height * 0.7:  # Only draw inner flame for part of the height
                    width = max(2, 7 * (1 - y/(flame_height-5)))
                    x_start = int((15 - width) / 2)
                    pygame.draw.rect(flame, YELLOW, (x_start, y, int(width), 1))
            
            frame.blit(flame, (0, self.height - 20))
            
            self.jetpack_frames.append(frame)
    
    def update(self):
        if not self.alive:
            return
            
        # Apply gravity with a smoother effect
        if not self.jetpack_on:
            self.velocity += GRAVITY
        
        # Apply jetpack thrust with gradual acceleration
        if self.jetpack_on:
            # Gradually decrease velocity (accelerate upward) with a smoother transition
            self.velocity -= JETPACK_ACCELERATION
            
            # Play jetpack sound
            if "jetpack" in sounds and sounds["jetpack"] is not None:
                if not pygame.mixer.get_busy():
                    play_sound("jetpack")
            
            # Add some smoke particles for visual effect when jetpack is active
            if random.random() > 0.7 and game_instance:
                game_instance.add_particle(self.x + 5, self.y + self.height - 20)
        else:
            # Stop jetpack sound when not using jetpack
            if "jetpack" in sounds and sounds["jetpack"] is not None:
                pygame.mixer.stop()
                
            # Add some deceleration when jetpack is turned off (feels more realistic)
            if self.velocity < 0:
                self.velocity += JETPACK_DECELERATION
        
        # Cap maximum velocity in both directions for better control
        if self.velocity > MAX_VELOCITY:
            self.velocity = MAX_VELOCITY
        elif self.velocity < -MAX_VELOCITY:
            self.velocity = -MAX_VELOCITY
        
        # Update position
        self.y += self.velocity
        
        # Keep player on screen with a small bounce effect
        if self.y < 0:
            self.y = 0
            self.velocity = self.velocity * -0.2  # Small bounce
        elif self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity = self.velocity * -0.2  # Small bounce when hitting ground
            
            # Add some dust particles when hitting the ground
            if self.velocity > 3 and game_instance:  # Only if coming down with some speed
                for _ in range(5):
                    game_instance.add_particle(self.x + random.randint(10, self.width - 10), 
                                              self.y + self.height, is_dust=True)
        
        # Update collision rectangle
        self.rect.x = self.x + 10
        self.rect.y = self.y + 10
        
        # Update animation frame
        self.frame = (self.frame + self.animation_speed) % len(self.normal_frames)
    
    def draw(self):
        # Choose appropriate frame based on jetpack state
        if self.jetpack_on:
            frame = self.jetpack_frames[int(self.frame)]
        else:
            frame = self.normal_frames[int(self.frame)]
        
        # Draw player
        screen.blit(frame, (self.x, self.y))
        
        # Debug: draw collision rectangle
        # pygame.draw.rect(screen, RED, self.rect, 2)
class Obstacle:
    def __init__(self, x, y, obstacle_type="missile"):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.passed = False
        
        if self.type == "missile":
            self.width = 80
            self.height = 30
            self.speed = MISSILE_SPEED
            self.create_missile_image()
        elif self.type == "laser":
            self.width = 30
            self.height = 150
            self.speed = SCROLL_SPEED
            self.create_laser_image()
        
        # Collision rectangle
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def create_missile_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Missile body (pixelated rectangle)
        pygame.draw.rect(self.image, GRAY, (20, 5, self.width - 30, self.height - 10))
        
        # Missile nose (pixelated triangle) - now pointing left for correct direction
        for i in range(10):
            height = min(i+1, self.height - 2*i)
            pygame.draw.rect(self.image, RED, (10-i, self.height//2 - height//2, i+1, height))
        
        # Missile tail fins (pixelated)
        pygame.draw.rect(self.image, GRAY, (self.width-15, 0, 15, 5))  # Top fin
        pygame.draw.rect(self.image, GRAY, (self.width-15, self.height-5, 15, 5))  # Bottom fin
        
        # Missile window (pixelated circle)
        pygame.draw.rect(self.image, LIGHT_BLUE, (25, self.height//2 - 4, 8, 8))
        
        # Missile exhaust (pixelated)
        for i in range(3):
            flame_length = random.randint(15, 25)
            flame_height = random.randint(4, 8)
            flame_y = self.height//2 - flame_height//2 + random.randint(-2, 2)
            
            # Draw pixelated flame
            for x in range(flame_length):
                flame_width = flame_height * (1 - x/flame_length)
                y_offset = (flame_height - flame_width) / 2
                pygame.draw.rect(self.image, ORANGE, 
                                (self.width - 5 + x, flame_y + y_offset, 1, max(1, int(flame_width))))
        
        # Add some pixel noise for texture
        for _ in range(10):
            x = random.randint(20, self.width - 20)
            y = random.randint(5, self.height - 5)
            size = random.randint(1, 3)
            color = (80, 80, 80)
            pygame.draw.rect(self.image, color, (x, y, size, size))
    
    def create_laser_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Laser beam (pixelated)
        for y in range(0, self.height, 4):  # Create scanlines for pixelated effect
            beam_height = min(3, self.height - y)
            pygame.draw.rect(self.image, RED, (0, y, self.width, beam_height))
        
        # Laser emitter at the right side (pixelated)
        emitter_width = 15
        emitter_height = 50
        pygame.draw.rect(self.image, GRAY, (self.width - emitter_width, self.height//2 - emitter_height//2, 
                                           emitter_width, emitter_height))
        
        # Emitter light (pixelated)
        pygame.draw.rect(self.image, RED, (self.width - emitter_width + 3, self.height//2 - 8, 8, 16))
        
        # Add some pixel noise for texture
        for _ in range(20):
            x = random.randint(0, self.width - emitter_width - 5)
            y = random.randint(0, self.height)
            if random.random() > 0.5:  # Only some pixels for sparse effect
                pygame.draw.rect(self.image, (255, 150, 150), (x, y, 2, 2))
    
    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        
        # Debug: draw collision rectangle
        # pygame.draw.rect(screen, RED, self.rect, 2)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.collected = False
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.frames = []
        
        # Create coin animation frames
        self.create_coin_frames()
        
        # Collision rectangle
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def create_coin_frames(self):
        # Create different frames for coin rotation (pixelated style)
        for i in range(8):
            frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Calculate width based on rotation (narrower in the middle of animation)
            width_factor = abs(math.sin(i / 8 * math.pi))
            width = max(4, int(self.width * width_factor))
            
            # Draw pixelated coin
            if width > self.width * 0.6:  # Front-facing coin
                # Outer circle (pixelated)
                pygame.draw.rect(frame, YELLOW, ((self.width - width) // 2, 0, width, self.height))
                
                # Inner details (pixelated dollar sign or star)
                inner_width = max(2, width // 2)
                pygame.draw.rect(frame, (200, 200, 0), 
                                ((self.width - inner_width) // 2, (self.height - inner_width) // 2, 
                                 inner_width, inner_width))
                
                # Shine effect (pixelated)
                shine_width = max(2, width // 4)
                pygame.draw.rect(frame, WHITE, 
                                ((self.width - width) // 2 + width // 4, self.height // 4, 
                                 shine_width, shine_width))
            else:  # Side view of coin
                # Draw a thin rectangle for side view
                pygame.draw.rect(frame, YELLOW, ((self.width - width) // 2, 0, width, self.height))
                
                # Add some shading
                if width > 2:
                    pygame.draw.rect(frame, (200, 200, 0), 
                                    ((self.width - width) // 2 + 1, 1, width - 2, self.height - 2))
            
            self.frames.append(frame)
    
    def update(self):
        self.x -= SCROLL_SPEED
        self.rect.x = self.x
        
        # Update animation
        self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.frames)
    
    def draw(self):
        if not self.collected:
            screen.blit(self.frames[int(self.animation_frame)], (self.x, self.y))
            
            # Debug: draw collision rectangle
            # pygame.draw.rect(screen, RED, self.rect, 2)
class Background:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
        # Create layers for parallax effect
        self.layers = []
        
        # Sky layer (static)
        sky = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        sky.fill(LIGHT_BLUE)
        self.layers.append({"image": sky, "speed": 0, "x": 0})
        
        # Distant buildings layer
        buildings_far = self.create_buildings_layer(0.7, 200, 300, GRAY)
        self.layers.append({"image": buildings_far, "speed": 1, "x": 0})
        
        # Mid-distance buildings layer
        buildings_mid = self.create_buildings_layer(0.8, 150, 350, (80, 80, 100))
        self.layers.append({"image": buildings_mid, "speed": 2, "x": 0})
        
        # Close buildings layer
        buildings_close = self.create_buildings_layer(1.0, 100, 400, (50, 50, 70))
        self.layers.append({"image": buildings_close, "speed": 3, "x": 0})
        
        # Ground layer
        ground = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        ground.fill((100, 100, 100))
        # Add some texture to the ground
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, 100)
            size = random.randint(2, 5)
            color = (80, 80, 80)
            pygame.draw.rect(ground, color, (x, y, size, size))
        self.layers.append({"image": ground, "speed": BACKGROUND_SPEED, "x": 0, "y": self.height - 100})
    
    def create_buildings_layer(self, opacity, min_height, max_height, base_color):
        layer = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        
        # Generate random buildings (pixelated style)
        x = 0
        while x < self.width * 2:
            # Use multiples of 8 for pixel-art feel
            building_width = random.randint(8, 20) * 8
            building_height = random.randint(min_height // 8, max_height // 8) * 8
            
            # Vary the color slightly
            color_variation = random.randint(-20, 20)
            color = (
                max(0, min(255, base_color[0] + color_variation)),
                max(0, min(255, base_color[1] + color_variation)),
                max(0, min(255, base_color[2] + color_variation))
            )
            
            # Draw building (pixelated rectangle)
            pygame.draw.rect(layer, color, (x, self.height - building_height, building_width, building_height))
            
            # Add windows (pixelated grid)
            for wy in range(self.height - building_height + 16, self.height - 16, 24):
                for wx in range(x + 16, x + building_width - 16, 24):
                    # Randomly decide if window is lit
                    if random.random() > 0.3:
                        window_color = YELLOW
                    else:
                        window_color = (50, 50, 50)
                    
                    # Draw pixelated window (square)
                    pygame.draw.rect(layer, window_color, (wx, wy, 8, 8))
            
            # Add pixelated roof details
            roof_detail_color = (
                max(0, min(255, color[0] - 30)),
                max(0, min(255, color[1] - 30)),
                max(0, min(255, color[2] - 30))
            )
            pygame.draw.rect(layer, roof_detail_color, 
                           (x, self.height - building_height, building_width, 8))
            
            # Random chance to add antenna or water tower on roof
            if random.random() > 0.7:
                if random.random() > 0.5:
                    # Antenna
                    pygame.draw.rect(layer, GRAY, 
                                   (x + building_width // 2 - 2, 
                                    self.height - building_height - 24, 
                                    4, 24))
                else:
                    # Water tower
                    tower_width = 16
                    tower_height = 24
                    tower_x = x + random.randint(tower_width, building_width - tower_width * 2)
                    pygame.draw.rect(layer, GRAY, 
                                   (tower_x, 
                                    self.height - building_height - tower_height, 
                                    tower_width, tower_height))
                    pygame.draw.rect(layer, (100, 50, 50), 
                                   (tower_x - 4, 
                                    self.height - building_height - tower_height // 2, 
                                    tower_width + 8, tower_height // 2))
            
            x += building_width + random.randint(0, 16)
        
        return layer
    
    def update(self):
        # Update layer positions for parallax scrolling
        for layer in self.layers:
            layer["x"] -= layer["speed"]
            
            # Reset position when image has scrolled off screen
            if "speed" in layer and layer["speed"] > 0:
                if layer["x"] <= -self.width:
                    layer["x"] = 0
    
    def draw(self):
        # Draw sky (static)
        screen.blit(self.layers[0]["image"], (0, 0))
        
        # Draw scrolling layers
        for i in range(1, len(self.layers)):
            layer = self.layers[i]
            if "y" in layer:
                screen.blit(layer["image"], (layer["x"], layer["y"]))
                # Draw a second copy for seamless scrolling
                screen.blit(layer["image"], (layer["x"] + self.width, layer["y"]))
            else:
                screen.blit(layer["image"], (layer["x"], 0))
                # Draw a second copy for seamless scrolling
                screen.blit(layer["image"], (layer["x"] + self.width, 0))

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 8
        self.frame_speed = 0.5
        self.size = 100
        self.frames = []
        
        # Create explosion frames
        self.create_explosion_frames()
    
    def create_explosion_frames(self):
        for i in range(self.max_frames):
            # Size increases then decreases (pixelated style)
            size_factor = 1.0
            if i < self.max_frames // 2:
                size_factor = 0.5 + i / (self.max_frames / 2) * 0.5
            else:
                size_factor = 1.0 - (i - self.max_frames // 2) / (self.max_frames / 2) * 0.5
                
            frame_size = int(self.size * size_factor)
            frame_size = frame_size - (frame_size % 4)  # Make size a multiple of 4 for pixelated look
            
            frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
            
            # Draw pixelated explosion
            # Outer circle (orange)
            radius = frame_size // 2
            for y in range(frame_size):
                for x in range(frame_size):
                    # Calculate distance from center
                    dx = x - frame_size // 2
                    dy = y - frame_size // 2
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Create pixelated circles
                    if distance < radius:
                        # Determine color based on distance from center
                        if distance < radius * 0.3:
                            color = WHITE
                        elif distance < radius * 0.6:
                            color = YELLOW
                        else:
                            color = ORANGE
                            
                        # Add some randomness for pixelated effect
                        if random.random() > 0.8:
                            if color == WHITE:
                                color = YELLOW
                            elif color == YELLOW:
                                color = ORANGE
                            elif color == ORANGE:
                                color = RED
                                
                        # Draw pixel
                        size = 2 if frame_size > 40 else 1
                        pygame.draw.rect(frame, color, (x, y, size, size))
            
            # Add some flying debris particles (pixelated)
            for _ in range(10):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, frame_size // 2)
                px = frame_size // 2 + math.cos(angle) * distance
                py = frame_size // 2 + math.sin(angle) * distance
                particle_size = random.randint(2, 4)
                pygame.draw.rect(frame, YELLOW, (int(px), int(py), particle_size, particle_size))
            
            self.frames.append(frame)
    
    def update(self):
        self.frame += self.frame_speed
        return self.frame < self.max_frames
    
    def draw(self):
        if int(self.frame) < len(self.frames):
            frame = self.frames[int(self.frame)]
            screen.blit(frame, (self.x - frame.get_width() // 2, self.y - frame.get_height() // 2))
class Game:
    def __init__(self):
        self.player = Player()
        self.background = Background()
        self.obstacles = []
        self.coins = []
        self.explosions = []
        self.particles = []  # Add particles list for visual effects
        self.score = 0
        self.high_score = 0
        self.coins_collected = 0  # Track collected coins separately
        self.game_state = "menu"  # menu, playing, game_over
        self.last_obstacle_time = 0
        self.last_coin_time = 0
        self.obstacle_types = ["missile", "laser"]
        
        # Make this instance globally accessible for particles
        global game_instance
        game_instance = self
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        play_sound("menu")
                        self.start_game()
                    elif self.game_state == "game_over":
                        play_sound("menu")
                        self.start_game()
                    elif self.game_state == "playing":
                        self.player.jetpack_on = True
                
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                # Toggle music with M key
                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                
                # Toggle sound effects with S key
                if event.key == pygame.K_s:
                    global sounds_enabled
                    sounds_enabled = not sounds_enabled
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.game_state == "playing":
                    self.player.jetpack_on = False
            
            # Mouse controls
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "menu":
                    play_sound("menu")
                    self.start_game()
                elif self.game_state == "game_over":
                    play_sound("menu")
                    self.start_game()
                elif self.game_state == "playing":
                    self.player.jetpack_on = True
            
            if event.type == pygame.MOUSEBUTTONUP and self.game_state == "playing":
                self.player.jetpack_on = False
    
    def start_game(self):
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.explosions = []
        self.particles = []
        self.score = 0
        self.coins_collected = 0  # Reset coins collected
        self.game_state = "playing"
        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_coin_time = pygame.time.get_ticks()
        
        # Resume background music
        pygame.mixer.music.unpause()
    
    def add_particle(self, x, y, is_dust=False):
        """Add a new particle effect at the specified position"""
        self.particles.append(Particle(x, y, is_dust))
    
    def update(self):
        # Update background
        self.background.update()
        
        if self.game_state == "playing":
            # Update player
            self.player.update()
            
            # Spawn obstacles
            current_time = pygame.time.get_ticks()
            if current_time - self.last_obstacle_time > OBSTACLE_FREQUENCY:
                self.spawn_obstacle()
                self.last_obstacle_time = current_time
            
            # Spawn coins
            if current_time - self.last_coin_time > COIN_FREQUENCY:
                self.spawn_coins()
                self.last_coin_time = current_time
            
            # Update obstacles
            for obstacle in self.obstacles[:]:
                obstacle.update()
                
                # Check collision with player
                if self.player.rect.colliderect(obstacle.rect) and self.player.alive:
                    self.player.alive = False
                    self.explosions.append(Explosion(self.player.x + self.player.width // 2, 
                                                    self.player.y + self.player.height // 2))
                    play_sound("explosion")  # Play explosion sound
                    self.game_over()
                
                # Remove obstacles that are off screen
                if obstacle.x + obstacle.width < 0:
                    self.obstacles.remove(obstacle)
                    if not obstacle.passed:
                        self.score += 5
                        obstacle.passed = True
            
            # Update coins
            for coin in self.coins[:]:
                coin.update()
                
                # Check collision with player
                if not coin.collected and self.player.rect.colliderect(coin.rect):
                    coin.collected = True
                    self.score += 10
                    self.coins_collected += 1  # Increment coin counter
                    play_sound("coin")  # Play coin collection sound
                
                # Remove coins that are off screen or collected
                if coin.x + coin.width < 0 or coin.collected:
                    self.coins.remove(coin)
            
            # Update score
            self.score += 0.1
        
        # Update explosions
        for explosion in self.explosions[:]:
            if not explosion.update():
                self.explosions.remove(explosion)
        
        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
    
    def spawn_obstacle(self):
        obstacle_type = random.choice(self.obstacle_types)
        
        if obstacle_type == "missile":
            y = random.randint(100, SCREEN_HEIGHT - 150)
            obstacle = Obstacle(SCREEN_WIDTH, y, "missile")
            # Play missile sound
            play_sound("laser")
        elif obstacle_type == "laser":
            y = random.randint(0, SCREEN_HEIGHT - 200)
            obstacle = Obstacle(SCREEN_WIDTH, y, "laser")
            # Play laser sound
            play_sound("laser")
        
        self.obstacles.append(obstacle)
    
    def spawn_coins(self):
        # Create a small cluster of coins
        num_coins = random.randint(3, 8)
        start_x = SCREEN_WIDTH
        start_y = random.randint(100, SCREEN_HEIGHT - 150)
        
        # Choose a pattern: line, arc, or zigzag
        pattern = random.choice(["line", "arc", "zigzag"])
        
        for i in range(num_coins):
            if pattern == "line":
                x = start_x + i * 40
                y = start_y
            elif pattern == "arc":
                x = start_x + i * 40
                y = start_y + int(math.sin(i * 0.5) * 80)
            elif pattern == "zigzag":
                x = start_x + i * 40
                y = start_y + (50 if i % 2 == 0 else -50)
            
            self.coins.append(Coin(x, y))
    
    def game_over(self):
        self.game_state = "game_over"
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Stop jetpack sound if playing
        pygame.mixer.stop()
        
        # Play game over sound
        play_sound("gameover")
        
        # Pause background music
        pygame.mixer.music.pause()
    
    def draw(self):
        # Draw background
        self.background.draw()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # Draw coins
        for coin in self.coins:
            coin.draw()
        
        # Draw particles (behind player)
        for particle in self.particles:
            particle.draw()
        
        # Draw player
        self.player.draw()
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw()
        
        # Draw UI with pixelated style
        # Create a black background for the score display (pixelated UI panel)
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, 280, 70))
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 280, 70), 2)  # Border
        
        # Draw score with pixelated font
        score_text = font_small.render(f"SCORE:{int(self.score)}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Draw high score (positioned to avoid overlap)
        high_score_text = font_small.render(f"HI-SCORE:{int(self.high_score)}", True, WHITE)
        screen.blit(high_score_text, (150, 20))
        
        # Draw coin counter with coin icon
        coin_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(coin_icon, YELLOW, (0, 0, 16, 16))
        pygame.draw.rect(coin_icon, (200, 200, 0), (2, 2, 12, 12))
        screen.blit(coin_icon, (20, 45))
        
        coin_text = font_small.render(f"x{self.coins_collected}", True, YELLOW)
        screen.blit(coin_text, (45, 45))
        
        # Draw sound controls info in a separate UI panel
        if self.game_state == "playing":
            # Sound controls panel
            pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 150, 10, 140, 50))
            pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH - 150, 10, 140, 50), 2)  # Border
            
            # Draw sound control text
            music_text = font_small.render("M:MUSIC", True, WHITE)
            screen.blit(music_text, (SCREEN_WIDTH - 140, 15))
            
            sfx_text = font_small.render("S:SFX", True, WHITE)
            screen.blit(sfx_text, (SCREEN_WIDTH - 140, 35))
            
            # Show music status
            if pygame.mixer.music.get_busy():
                music_status = font_small.render("ON", True, GREEN)
            else:
                music_status = font_small.render("OFF", True, RED)
            screen.blit(music_status, (SCREEN_WIDTH - 60, 15))
            
            # Show SFX status
            if sounds_enabled:
                sfx_status = font_small.render("ON", True, GREEN)
            else:
                sfx_status = font_small.render("OFF", True, RED)
            screen.blit(sfx_status, (SCREEN_WIDTH - 60, 35))
        
        # Draw menu or game over screen
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "game_over":
            self.draw_game_over()
    
    def draw_menu(self):
        # Semi-transparent overlay (pixelated)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pixelated border for menu
        border_width = 600
        border_height = 400
        border_x = (SCREEN_WIDTH - border_width) // 2
        border_y = 150
        
        # Draw pixelated border
        pygame.draw.rect(screen, (50, 50, 50), 
                       (border_x, border_y, border_width, border_height))
        pygame.draw.rect(screen, (100, 100, 100), 
                       (border_x + 4, border_y + 4, border_width - 8, border_height - 8))
        pygame.draw.rect(screen, (0, 0, 0), 
                       (border_x + 8, border_y + 8, border_width - 16, border_height - 16))
        
        # Title with pixelated effect - render with line breaks if needed
        title_text = "JETPACK ADVENTURE"
        title_surface = font_large.render(title_text, True, WHITE)
        
        # Check if title fits, if not use medium font
        if title_surface.get_width() > border_width - 40:
            title_surface = font_medium.render(title_text, True, WHITE)
        
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 200))
        
        # Pixelated underline
        pygame.draw.rect(screen, YELLOW, 
                       (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 240, 
                        title_surface.get_width(), 4))
        
        # Instructions with pixelated font - break into multiple lines if needed
        instructions_text = "PRESS SPACE OR CLICK"
        instructions_surface = font_medium.render(instructions_text, True, WHITE)
        screen.blit(instructions_surface, (SCREEN_WIDTH // 2 - instructions_surface.get_width() // 2, 300))
        
        instructions_text2 = "TO START"
        instructions_surface2 = font_medium.render(instructions_text2, True, WHITE)
        screen.blit(instructions_surface2, (SCREEN_WIDTH // 2 - instructions_surface2.get_width() // 2, 330))
        
        # Controls with pixelated font - break into multiple lines
        controls_text1 = "HOLD SPACE OR MOUSE"
        controls_surface1 = font_small.render(controls_text1, True, WHITE)
        screen.blit(controls_surface1, (SCREEN_WIDTH // 2 - controls_surface1.get_width() // 2, 380))
        
        controls_text2 = "BUTTON TO FLY"
        controls_surface2 = font_small.render(controls_text2, True, WHITE)
        screen.blit(controls_surface2, (SCREEN_WIDTH // 2 - controls_surface2.get_width() // 2, 405))
        
        # Sound controls
        sound_text = "M:MUSIC  S:SFX"
        sound_surface = font_small.render(sound_text, True, WHITE)
        screen.blit(sound_surface, (SCREEN_WIDTH // 2 - sound_surface.get_width() // 2, 440))
        
        # Draw pixelated jetpack icon
        jetpack_icon = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.rect(jetpack_icon, BLUE, (10, 0, 20, 40))  # Body
        pygame.draw.rect(jetpack_icon, GRAY, (0, 20, 10, 30))  # Jetpack
        pygame.draw.rect(jetpack_icon, ORANGE, (0, 50, 10, 10))  # Flame
        screen.blit(jetpack_icon, (SCREEN_WIDTH // 2 - 20, 470))
    
    def draw_game_over(self):
        # Semi-transparent overlay (pixelated)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pixelated border for game over screen
        border_width = 600
        border_height = 400
        border_x = (SCREEN_WIDTH - border_width) // 2
        border_y = 150
        
        # Draw pixelated border with red theme for game over
        pygame.draw.rect(screen, (100, 0, 0), 
                       (border_x, border_y, border_width, border_height))
        pygame.draw.rect(screen, (150, 0, 0), 
                       (border_x + 4, border_y + 4, border_width - 8, border_height - 8))
        pygame.draw.rect(screen, (0, 0, 0), 
                       (border_x + 8, border_y + 8, border_width - 16, border_height - 16))
        
        # Game over text with pixelated effect
        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        
        # Pixelated underline
        pygame.draw.rect(screen, RED, 
                       (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 240, 
                        game_over_text.get_width(), 4))
        
        # Final score with pixelated font - break into multiple lines if needed
        score_text = f"FINAL SCORE:{int(self.score)}"
        score_surface = font_medium.render(score_text, True, WHITE)
        screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, 280))
        
        # Coins collected with icon
        coin_icon = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(coin_icon, YELLOW, (0, 0, 24, 24))
        pygame.draw.rect(coin_icon, (200, 200, 0), (4, 4, 16, 16))
        
        # Position coin icon and text centered
        coins_text = font_medium.render(f"COINS:{self.coins_collected}", True, YELLOW)
        coin_display_width = coin_icon.get_width() + 10 + coins_text.get_width()
        coin_x = SCREEN_WIDTH // 2 - coin_display_width // 2
        
        screen.blit(coin_icon, (coin_x, 330))
        screen.blit(coins_text, (coin_x + coin_icon.get_width() + 10, 330))
        
        # Restart instructions with pixelated font - break into multiple lines
        restart_text1 = "PRESS SPACE OR CLICK"
        restart_surface1 = font_medium.render(restart_text1, True, WHITE)
        screen.blit(restart_surface1, (SCREEN_WIDTH // 2 - restart_surface1.get_width() // 2, 380))
        
        restart_text2 = "TO RESTART"
        restart_surface2 = font_medium.render(restart_text2, True, WHITE)
        screen.blit(restart_surface2, (SCREEN_WIDTH // 2 - restart_surface2.get_width() // 2, 410))
        
        # Draw pixelated skull icon
        skull_size = 60
        skull = pygame.Surface((skull_size, skull_size), pygame.SRCALPHA)
        
        # Skull base
        pygame.draw.rect(skull, WHITE, (10, 10, skull_size - 20, skull_size - 20))
        
        # Eyes
        pygame.draw.rect(skull, BLACK, (15, 25, 10, 10))
        pygame.draw.rect(skull, BLACK, (skull_size - 25, 25, 10, 10))
        
        # Nose
        pygame.draw.rect(skull, BLACK, (skull_size // 2 - 2, 35, 4, 4))
        
        # Teeth
        for i in range(3):
            pygame.draw.rect(skull, BLACK, (20 + i*10, 45, 2, 10))
        
        screen.blit(skull, (SCREEN_WIDTH // 2 - skull_size // 2, 460))

# Main game loop
def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
