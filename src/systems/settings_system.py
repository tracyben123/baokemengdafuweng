import json
import os
import pygame

class SettingsSystem:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "sound": {
                "sfx_volume": 1.0,
                "bgm_volume": 0.5,
                "enable_sfx": True,
                "enable_bgm": True
            },
            "display": {
                "fullscreen": False,
                "resolution": (1280, 720),
                "fps_limit": 60
            },
            "gameplay": {
                "battle_animation": True,
                "auto_save": True,
                "auto_save_interval": 10,  # 回合数
                "difficulty": "normal",    # easy, normal, hard
                "starting_coins": 1000,
                "starting_pokemon_level": 5
            },
            "controls": {
                "roll_dice": "SPACE",
                "menu": "ESCAPE",
                "confirm": "RETURN",
                "cancel": "BACKSPACE"
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        """加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return {**self.default_settings, **json.load(f)}
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()
        
    def save_settings(self):
        """保存设置"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
    def get_setting(self, category, key):
        """获取设置值"""
        return self.settings.get(category, {}).get(key, 
               self.default_settings[category][key])
               
    def set_setting(self, category, key, value):
        """设置值"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
        
    def apply_settings(self, game_loop):
        """应用设置到游戏"""
        # 应用音频设置
        game_loop.sound_system.set_volume(
            self.get_setting("sound", "sfx_volume"))
        game_loop.sound_system.set_bgm_volume(
            self.get_setting("sound", "bgm_volume"))
            
        # 应用显示设置
        resolution = self.get_setting("display", "resolution")
        flags = pygame.FULLSCREEN if self.get_setting("display", "fullscreen") else 0
        game_loop.screen = pygame.display.set_mode(resolution, flags)
            
        # 应用游戏性设置
        game_loop.auto_save = self.get_setting("gameplay", "auto_save")
        game_loop.auto_save_interval = self.get_setting("gameplay", "auto_save_interval")
        
    def reset_to_default(self):
        """重置为默认设置"""
        self.settings = self.default_settings.copy()
        self.save_settings() 