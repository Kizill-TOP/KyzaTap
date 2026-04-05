import pygame
import sys
import random
import json
import os
import webbrowser
import time

pygame.init()
pygame.mixer.init()

# ========== АВТООПРЕДЕЛЕНИЕ РАЗРЕШЕНИЯ ==========
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 200, 200)
ORANGE = (255, 100, 0)
PURPLE = (150, 50, 200)

# Пути к файлам
CAT_IMG = "КотТап.jpg"
PURR_SOUND = "Мур.mp3"
BACKGROUND_MUSIC = "КотикТап.mp3"
TG_IMG = "Тг.jpg"
SAVE_FILE = "save.json"

class KyzaTapCat:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Kyza: TapCat | Glitch_TIME")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.load_resources()
        self.load_game()
        
        # Звуки и настройки
        self.sound_enabled = True
        self.purr_enabled = True
        self.music_volume = 0.2
        self.vibration_enabled = True
        self.purr_channel = None
        
        if self.background_music:
            self.background_music.set_volume(self.music_volume)
            self.background_music.play(-1)
        
        self.xp_to_next = 100
        self.cat_scale = 1.0
        self.cat_anim_time = 0
        self.floating_numbers = []
        self.max_floating = 15
        
        self.energy = self.max_energy
        self.last_tap_time = time.time()
        self.last_energy_regen = time.time()
        self.energy_regen_delay = 4.5
        self.energy_regen_speed = 15
        
        self.total_taps = 0
        self.total_coins_earned = 0
        
        self.shop_open = False
        self.settings_open = False
        
        btn_width = 160
        btn_height = 55
        btn_y = 15
        self.shop_btn_rect = pygame.Rect(20, btn_y, btn_width, btn_height)
        self.settings_btn_rect = pygame.Rect(SCREEN_WIDTH - btn_width - 20, btn_y, btn_width, btn_height)
        
        self.update_shop_items()
        self.show_intro()
        
        self.last_save = time.time()
        self.last_auto = time.time()
        self.last_passive = time.time()
    
    def update_shop_items(self):
        self.shop_items = [
            {"name": "СИЛА КЛИКА", "desc": f"+1 к силе (сейчас {self.click_power})", "cost": self.click_power * 20, "type": "click", "icon": "💪"},
            {"name": "АВТОКЛИКЕР", "desc": f"+1 клик/сек (сейчас {self.auto_power})", "cost": (self.auto_power + 1) * 80, "type": "auto", "icon": "🤖"},
            {"name": "ЗАПАС ЭНЕРГИИ", "desc": f"+50 к макс. энергии (сейчас {self.max_energy})", "cost": 100 + (self.max_energy // 10), "type": "max_energy", "icon": "🔋"},
            {"name": "ВОССТАНОВИТЬ", "desc": "+200 энергии сейчас", "cost": 60, "type": "energy", "icon": "⚡"},
            {"name": "ПАССИВНЫЙ", "desc": f"+1 монет/сек (сейчас {self.passive_income})", "cost": (self.passive_income + 1) * 150, "type": "passive", "icon": "💨"},
        ]
    
    def load_resources(self):
        # Кот чуть меньше
        cat_size = min(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) - 40
        try:
            self.cat_img = pygame.image.load(CAT_IMG)
            self.cat_img = pygame.transform.scale(self.cat_img, (cat_size, int(cat_size * 1.2)))
        except:
            self.cat_img = pygame.Surface((cat_size, int(cat_size * 1.2)))
            self.cat_img.fill(GRAY)
        
        # Кот выше
        self.cat_rect = self.cat_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        
        # Круг под котом
        self.circle_center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10)
        self.circle_radius = cat_size // 2 + 20
        
        try:
            self.purr_sound = pygame.mixer.Sound(PURR_SOUND)
        except:
            self.purr_sound = None
        
        try:
            self.background_music = pygame.mixer.Sound(BACKGROUND_MUSIC)
        except:
            self.background_music = None
        
        try:
            self.tg_icon = pygame.image.load(TG_IMG)
            self.tg_icon = pygame.transform.scale(self.tg_icon, (45, 45))
        except:
            self.tg_icon = None
    
    def show_intro(self):
        start_time = time.time()
        font = pygame.font.Font(None, int(SCREEN_HEIGHT / 12))
        font_small = pygame.font.Font(None, int(SCREEN_HEIGHT / 20))
        font_tiny = pygame.font.Font(None, int(SCREEN_HEIGHT / 28))
        
        while time.time() - start_time < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.screen.fill(BLACK)
            text1 = font.render("Kyza: TapCat", True, YELLOW)
            text2 = font_small.render("Glitch_TIME presents", True, CYAN)
            text3 = font_tiny.render("created by Kizill_TOP", True, WHITE)
            
            self.screen.blit(text1, (SCREEN_WIDTH//2 - text1.get_width()//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(text3, (SCREEN_WIDTH//2 - text3.get_width()//2, SCREEN_HEIGHT//2 + 20))
            pygame.display.flip()
            self.clock.tick(FPS)
    
    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                self.coins = data.get('coins', 0)
                self.energy = data.get('energy', 1000)
                self.max_energy = data.get('max_energy', 1000)
                self.click_power = data.get('click_power', 1)
                self.auto_power = data.get('auto_power', 0)
                self.passive_income = data.get('passive_income', 0)
                self.xp = data.get('xp', 0)
                self.level = data.get('level', 1)
                self.total_taps = data.get('total_taps', 0)
                self.total_coins_earned = data.get('total_coins_earned', 0)
            except:
                self.reset_game()
        else:
            self.reset_game()
        self.update_level()
    
    def reset_game(self):
        self.coins = 0
        self.energy = 1000
        self.max_energy = 1000
        self.click_power = 1
        self.auto_power = 0
        self.passive_income = 0
        self.xp = 0
        self.level = 1
        self.total_taps = 0
        self.total_coins_earned = 0
        self.update_level()
    
    def update_level(self):
        self.xp_to_next = 100 * self.level
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_energy += 50
            self.xp_to_next = 100 * self.level
    
    def save_game(self):
        data = {
            'coins': self.coins,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'click_power': self.click_power,
            'auto_power': self.auto_power,
            'passive_income': self.passive_income,
            'xp': self.xp,
            'level': self.level,
            'total_taps': self.total_taps,
            'total_coins_earned': self.total_coins_earned,
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
    
    def add_xp(self, amount):
        self.xp += amount
        self.update_level()
    
    def tap(self, pos):
        dx = pos[0] - self.circle_center[0]
        dy = pos[1] - self.circle_center[1]
        in_circle = (dx*dx + dy*dy) <= (self.circle_radius * self.circle_radius)
        in_cat = self.cat_rect.collidepoint(pos)
        
        if not (in_circle or in_cat):
            return
        
        now = time.time()
        self.last_tap_time = now
        
        if self.energy >= 1:
            gain = self.click_power
            self.coins += gain
            self.energy -= 1
            self.total_taps += 1
            self.total_coins_earned += gain
            self.add_xp(1)
            
            if len(self.floating_numbers) >= self.max_floating:
                for _ in range(min(2, len(self.floating_numbers))):
                    if self.floating_numbers:
                        self.floating_numbers.pop(0)
            
            self.floating_numbers.append({
                'x': pos[0],
                'y': pos[1],
                'value': f"+{gain}",
                'life': 60,
                'color': YELLOW
            })
            
            if self.vibration_enabled:
                self.vibrate(30)
            
            self.cat_scale = 1.08
            self.cat_anim_time = 6
            
            if self.sound_enabled and self.purr_enabled and self.purr_sound:
                if self.purr_channel is None or not self.purr_channel.get_busy():
                    self.purr_channel = self.purr_sound.play()
        else:
            if len(self.floating_numbers) >= self.max_floating:
                for _ in range(min(2, len(self.floating_numbers))):
                    if self.floating_numbers:
                        self.floating_numbers.pop(0)
            
            self.floating_numbers.append({
                'x': pos[0],
                'y': pos[1],
                'value': "НЕТ ЭНЕРГИИ!",
                'life': 60,
                'color': RED
            })
    
    def vibrate(self, duration):
        try:
            import subprocess
            subprocess.run(['termux-vibrate', '-d', str(duration)], capture_output=True)
        except:
            pass
    
    def update_energy(self, now):
        if now - self.last_tap_time >= self.energy_regen_delay:
            regen_amount = self.energy_regen_speed * (now - self.last_energy_regen)
            self.energy = min(self.max_energy, self.energy + regen_amount)
        self.last_energy_regen = now
    
    def update_auto_click(self, now):
        if self.auto_power > 0:
            gain = self.auto_power * self.click_power
            self.coins += gain
            self.total_coins_earned += gain
            self.add_xp(self.auto_power)
    
    def update_passive(self, now):
        if self.passive_income > 0:
            self.coins += self.passive_income
            self.total_coins_earned += self.passive_income
            self.add_xp(1)
    
    def buy_upgrade(self, item):
        if self.coins >= item["cost"]:
            self.coins -= item["cost"]
            if item["type"] == "click":
                self.click_power += 1
            elif item["type"] == "auto":
                self.auto_power += 1
            elif item["type"] == "max_energy":
                self.max_energy += 50
                self.energy += 50
            elif item["type"] == "energy":
                self.energy = min(self.max_energy, self.energy + 200)
            elif item["type"] == "passive":
                self.passive_income += 1
            self.update_shop_items()
            return True
        return False
    
    def draw_circle_background(self):
        for r in range(self.circle_radius, self.circle_radius - 60, -2):
            color = (20, 20, 40)
            pygame.draw.circle(self.screen, color, self.circle_center, r)
        pygame.draw.circle(self.screen, BLACK, (self.circle_center[0] + 5, self.circle_center[1] + 5), self.circle_radius)
        pygame.draw.circle(self.screen, (40, 40, 60), self.circle_center, self.circle_radius)
        pygame.draw.circle(self.screen, WHITE, self.circle_center, self.circle_radius, 2)
    
    def draw_xp_panel(self):
        # Полоска и счётчик XP вместе, над котом
        panel_x = SCREEN_WIDTH // 2
        panel_y = self.circle_center[1] - self.circle_radius - 35
        
        # Полоска XP
        bar_width = 400
        bar_height = 25
        bar_x = panel_x - bar_width // 2
        bar_y = panel_y - 15
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        progress = (self.xp / self.xp_to_next) if self.xp_to_next > 0 else 0
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Счётчик XP
        font = pygame.font.Font(None, int(SCREEN_HEIGHT / 22))
        xp_text = font.render(f"✨ XP: {int(self.xp)}/{int(self.xp_to_next)}", True, YELLOW)
        xp_rect = xp_text.get_rect(center=(panel_x, panel_y - 25))
        self.screen.blit(xp_text, xp_rect)
    
    def draw_top_stats(self):
        font = pygame.font.Font(None, int(SCREEN_HEIGHT / 20))
        
        coin_icon = pygame.font.Font(None, int(SCREEN_HEIGHT / 16)).render("💰", True, YELLOW)
        coin_text = font.render(f"{int(self.coins)}", True, YELLOW)
        self.screen.blit(coin_icon, (20, 80))
        self.screen.blit(coin_text, (60, 82))
        
        level_text = font.render(f"LVL {self.level}", True, CYAN)
        self.screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 20, 82))
    
    def draw_energy_text(self):
        font = pygame.font.Font(None, int(SCREEN_HEIGHT / 22))
        energy_color = GREEN if self.energy > self.max_energy * 0.3 else ORANGE if self.energy > self.max_energy * 0.1 else RED
        energy_text = font.render(f"🔋 {int(self.energy)}/{int(self.max_energy)}", True, energy_color)
        self.screen.blit(energy_text, (SCREEN_WIDTH//2 - energy_text.get_width()//2, 165))
    
    def draw_buttons(self):
        font = pygame.font.Font(None, 24)
        
        pygame.draw.rect(self.screen, BLUE, self.shop_btn_rect)
        pygame.draw.rect(self.screen, WHITE, self.shop_btn_rect, 3)
        shop_text = font.render("🛒 МАГАЗИН", True, WHITE)
        self.screen.blit(shop_text, (self.shop_btn_rect.x + 25, self.shop_btn_rect.y + 15))
        
        pygame.draw.rect(self.screen, ORANGE, self.settings_btn_rect)
        pygame.draw.rect(self.screen, WHITE, self.settings_btn_rect, 3)
        settings_text = font.render("⚙️ НАСТРОЙКИ", True, WHITE)
        self.screen.blit(settings_text, (self.settings_btn_rect.x + 20, self.settings_btn_rect.y + 15))
    
    def draw_shop_window(self):
        if not self.shop_open:
            return
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))
        
        win_w = SCREEN_WIDTH - 40
        win_h = SCREEN_HEIGHT - 80
        win_x = 20
        win_y = 40
        pygame.draw.rect(self.screen, DARK_GRAY, (win_x, win_y, win_w, win_h))
        pygame.draw.rect(self.screen, WHITE, (win_x, win_y, win_w, win_h), 4)
        
        title_font = pygame.font.Font(None, 40)
        title_text = title_font.render("МАГАЗИН", True, YELLOW)
        self.screen.blit(title_text, (win_x + win_w//2 - title_text.get_width()//2, win_y + 15))
        
        # Крестик побольше
        close_rect = pygame.Rect(win_x + win_w - 60, win_y + 15, 45, 45)
        pygame.draw.rect(self.screen, RED, close_rect)
        close_text = pygame.font.Font(None, 32).render("X", True, WHITE)
        self.screen.blit(close_text, (close_rect.x + 15, close_rect.y + 8))
        
        font = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 22)
        y_offset = win_y + 80
        item_height = 100
        self.shop_rects = []
        
        for i, item in enumerate(self.shop_items):
            rect = pygame.Rect(win_x + 15, y_offset + i * (item_height + 10), win_w - 30, item_height)
            can_buy = self.coins >= item["cost"]
            bg_color = (0, 80, 0) if can_buy else (60, 60, 60)
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 3)
            
            icon_text = pygame.font.Font(None, 50).render(item["icon"], True, WHITE)
            self.screen.blit(icon_text, (rect.x + 15, rect.y + 25))
            
            name_text = font.render(item["name"], True, YELLOW)
            self.screen.blit(name_text, (rect.x + 80, rect.y + 15))
            
            desc_text = small_font.render(item["desc"], True, WHITE)
            self.screen.blit(desc_text, (rect.x + 80, rect.y + 45))
            
            cost_text = small_font.render(f"Цена: {item['cost']}", True, CYAN)
            self.screen.blit(cost_text, (rect.x + 80, rect.y + 70))
            
            # Кнопка покупки большая
            buy_rect = pygame.Rect(rect.right - 120, rect.y + 25, 100, 50)
            pygame.draw.rect(self.screen, GREEN if can_buy else RED, buy_rect)
            pygame.draw.rect(self.screen, WHITE, buy_rect, 3)
            buy_text = small_font.render("КУПИТЬ", True, WHITE)
            self.screen.blit(buy_text, (buy_rect.x + 15, buy_rect.y + 13))
            
            self.shop_rects.append((rect, buy_rect, item, close_rect))
    
    def draw_settings_window(self):
        if not self.settings_open:
            return
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))
        
        win_w = SCREEN_WIDTH - 40
        win_h = SCREEN_HEIGHT - 80
        win_x = 20
        win_y = 40
        pygame.draw.rect(self.screen, DARK_GRAY, (win_x, win_y, win_w, win_h))
        pygame.draw.rect(self.screen, WHITE, (win_x, win_y, win_w, win_h), 4)
        
        title_font = pygame.font.Font(None, 40)
        title_text = title_font.render("НАСТРОЙКИ", True, YELLOW)
        self.screen.blit(title_text, (win_x + win_w//2 - title_text.get_width()//2, win_y + 15))
        
        # Крестик побольше
        close_rect = pygame.Rect(win_x + win_w - 60, win_y + 15, 45, 45)
        pygame.draw.rect(self.screen, RED, close_rect)
        close_text = pygame.font.Font(None, 32).render("X", True, WHITE)
        self.screen.blit(close_text, (close_rect.x + 15, close_rect.y + 8))
        
        font = pygame.font.Font(None, 28)
        y_offset = win_y + 100
        
        # Звук
        sound_text = font.render(f"🔊 ЗВУК: {'ВКЛ' if self.sound_enabled else 'ВЫКЛ'}", True, WHITE)
        self.screen.blit(sound_text, (win_x + 40, y_offset))
        sound_rect = pygame.Rect(win_x + 350, y_offset - 5, 160, 45)
        pygame.draw.rect(self.screen, GREEN if self.sound_enabled else DARK_GRAY, sound_rect)
        pygame.draw.rect(self.screen, WHITE, sound_rect, 3)
        
        # Мурлыкание
        purr_text = font.render(f"🐱 МУРЛЫКАНИЕ: {'ВКЛ' if self.purr_enabled else 'ВЫКЛ'}", True, WHITE)
        self.screen.blit(purr_text, (win_x + 40, y_offset + 70))
        purr_rect = pygame.Rect(win_x + 350, y_offset + 65, 160, 45)
        pygame.draw.rect(self.screen, GREEN if self.purr_enabled else DARK_GRAY, purr_rect)
        pygame.draw.rect(self.screen, WHITE, purr_rect, 3)
        
        # Вибрация
        vibro_text = font.render(f"📳 ВИБРАЦИЯ: {'ВКЛ' if self.vibration_enabled else 'ВЫКЛ'}", True, WHITE)
        self.screen.blit(vibro_text, (win_x + 40, y_offset + 140))
        vibro_rect = pygame.Rect(win_x + 350, y_offset + 135, 160, 45)
        pygame.draw.rect(self.screen, GREEN if self.vibration_enabled else DARK_GRAY, vibro_rect)
        pygame.draw.rect(self.screen, WHITE, vibro_rect, 3)
        
        # Telegram
        tg_rect = pygame.Rect(win_x + 150, y_offset + 220, win_w - 300, 70)
        pygame.draw.rect(self.screen, BLUE, tg_rect)
        pygame.draw.rect(self.screen, WHITE, tg_rect, 3)
        
        if self.tg_icon:
            self.screen.blit(self.tg_icon, (tg_rect.x + 20, tg_rect.y + 12))
            tg_text = font.render("@teoriesKizills", True, WHITE)
            self.screen.blit(tg_text, (tg_rect.x + 80, tg_rect.y + 22))
        else:
            tg_text = font.render("📱 НАШ TELEGRAM", True, WHITE)
            self.screen.blit(tg_text, (tg_rect.x + 50, tg_rect.y + 22))
        
        self.settings_rects = {
            "close": close_rect,
            "sound": sound_rect,
            "purr": purr_rect,
            "vibration": vibro_rect,
            "tg": tg_rect
        }
    
    def draw_cat(self):
        if self.cat_anim_time > 0:
            scale = 1.05
            self.cat_anim_time -= 1
        else:
            scale = 1.0
        
        w = int(self.cat_img.get_width() * scale)
        h = int(self.cat_img.get_height() * scale)
        scaled_img = pygame.transform.scale(self.cat_img, (w, h))
        rect = scaled_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(scaled_img, rect)
        self.cat_rect = rect
    
    def draw_floating_numbers(self):
        font = pygame.font.Font(None, int(SCREEN_HEIGHT / 15))
        for fn in self.floating_numbers[:]:
            text = font.render(fn['value'], True, fn['color'])
            self.screen.blit(text, (fn['x'] - text.get_width()//2, fn['y'] - fn['life']))
            fn['life'] -= 1
            if fn['life'] <= 0:
                self.floating_numbers.remove(fn)
    
    def handle_click(self, pos):
        if self.shop_open:
            for rect, buy_rect, item, close_rect in self.shop_rects:
                if close_rect.collidepoint(pos):
                    self.shop_open = False
                    return
                if buy_rect.collidepoint(pos):
                    self.buy_upgrade(item)
                    self.update_shop_items()
                    return
            return
        
        if self.settings_open:
            if self.settings_rects["close"].collidepoint(pos):
                self.settings_open = False
                return
            if self.settings_rects["sound"].collidepoint(pos):
                self.sound_enabled = not self.sound_enabled
                if self.background_music:
                    self.background_music.set_volume(self.music_volume if self.sound_enabled else 0)
                return
            if self.settings_rects["purr"].collidepoint(pos):
                self.purr_enabled = not self.purr_enabled
                return
            if self.settings_rects["vibration"].collidepoint(pos):
                self.vibration_enabled = not self.vibration_enabled
                return
            if self.settings_rects["tg"].collidepoint(pos):
                webbrowser.open("https://t.me/teoriesKizills")
            return
        
        if self.shop_btn_rect.collidepoint(pos):
            self.shop_open = True
            self.update_shop_items()
            return
        
        if self.settings_btn_rect.collidepoint(pos):
            self.settings_open = True
            return
        
        self.tap(pos)
    
    def run(self):
        while self.running:
            now = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.update_energy(now)
            self.update_auto_click(now)
            self.update_passive(now)
            
            if now - self.last_save > 30:
                self.save_game()
                self.last_save = now
            
            self.screen.fill((15, 15, 30))
            self.draw_circle_background()
            self.draw_top_stats()
            self.draw_energy_text()
            self.draw_buttons()
            self.draw_xp_panel()
            self.draw_cat()
            self.draw_floating_numbers()
            
            if self.shop_open:
                self.draw_shop_window()
            if self.settings_open:
                self.draw_settings_window()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        self.save_game()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = KyzaTapCat()
    game.run()