"""
Profile management system for ColorVisionAid
Handles user profiles with different settings combinations
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QSettings


@dataclass
class UserProfile:
    """Data class representing a user profile with all settings"""
    name: str
    color_blindness_type: str = "none"
    language: str = "en"
    theme: str = "dark"
    window_width: int = 1000
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    is_maximized: bool = False
    camera_permission: str = "ask"
    # Camera settings
    selected_camera_index: int = 0
    # Advanced settings
    detect_red: bool = True
    detect_green: bool = True
    detect_blue: bool = False
    detect_yellow: bool = False
    skin_tone_filtering_active: bool = True
    stability_enhancement_active: bool = True
    debug_mode_active: bool = False
    detection_sensitivity: float = 0.5
    color_enhancement: bool = True
    voice_feedback: bool = False
    auto_detection: bool = True
    filter_strength: float = 1.0
    created_date: str = ""
    last_used_date: str = ""
    # Gallery window placement (per-profile)
    gallery_x: int = -1
    gallery_y: int = -1
    gallery_width: int = -1
    gallery_height: int = -1

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from dictionary"""
        return cls(**data)


class ProfileManager:
    """Manages user profiles for ColorVisionAid"""
    
    def __init__(self):
        self.profiles_dir = self._get_profiles_directory()
        self.current_profile: Optional[UserProfile] = None
        self.settings = QSettings("ColorVisionAid", "CVA")
        
        # Ensure profiles directory exists
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Initialize with default profile if none exists
        self._initialize_default_profile()
    
    def _get_profiles_directory(self) -> str:
        """Get the directory where profiles are stored"""
        # Use user's documents directory for profile storage
        import platform
        if platform.system() == "Windows":
            base_dir = os.path.expanduser("~/Documents")
        else:
            base_dir = os.path.expanduser("~")
        
        profiles_dir = os.path.join(base_dir, "ColorVisionAid", "Profiles")
        return profiles_dir
    
    def _get_profile_file_path(self, profile_name: str) -> str:
        """Get the file path for a profile"""
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return os.path.join(self.profiles_dir, f"{safe_name}.json")
    
    def _initialize_default_profile(self):
        """Initialize default profile if no profiles exist"""
        if not self.get_all_profiles():
            from datetime import datetime
            from .translations import translator as tr
            default_profile = UserProfile(
                name=tr.get_text("default_profile"),
                created_date=datetime.now().isoformat(),
                last_used_date=datetime.now().isoformat()
            )
            self.save_profile(default_profile)
            self.current_profile = default_profile
    
    def create_profile(self, name: str, base_profile: Optional[UserProfile] = None) -> UserProfile:
        """Create a new profile"""
        from datetime import datetime
        
        if base_profile:
            # Copy settings from base profile
            new_profile = UserProfile(
                name=name,
                color_blindness_type=base_profile.color_blindness_type,
                language=base_profile.language,
                theme=base_profile.theme,
                window_width=base_profile.window_width,
                window_height=base_profile.window_height,
                window_x=base_profile.window_x,
                window_y=base_profile.window_y,
                is_maximized=base_profile.is_maximized,
                camera_permission=base_profile.camera_permission,
                detect_red=base_profile.detect_red,
                detect_green=base_profile.detect_green,
                detect_blue=base_profile.detect_blue,
                detect_yellow=base_profile.detect_yellow,
                skin_tone_filtering_active=base_profile.skin_tone_filtering_active,
                stability_enhancement_active=base_profile.stability_enhancement_active,
                debug_mode_active=base_profile.debug_mode_active,
                detection_sensitivity=base_profile.detection_sensitivity,
                color_enhancement=base_profile.color_enhancement,
                voice_feedback=base_profile.voice_feedback,
                auto_detection=base_profile.auto_detection,
                filter_strength=base_profile.filter_strength,
                created_date=datetime.now().isoformat(),
                last_used_date=datetime.now().isoformat()
            )
        else:
            # Create new profile with default settings
            new_profile = UserProfile(
                name=name,
                created_date=datetime.now().isoformat(),
                last_used_date=datetime.now().isoformat()
            )
        
        return new_profile
    
    def save_profile(self, profile: UserProfile) -> bool:
        """Save a profile to file"""
        try:
            file_path = self._get_profile_file_path(profile.name)
            
            # Update last used date
            from datetime import datetime
            profile.last_used_date = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving profile {profile.name}: {e}")
            return False
    
    def load_profile(self, profile_name: str) -> Optional[UserProfile]:
        """Load a profile from file with migration support"""
        try:
            file_path = self._get_profile_file_path(profile_name)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Migration: Add missing fields if they don't exist
            if 'selected_camera_index' not in data:
                data['selected_camera_index'] = 0
            
            # Ensure all required fields exist with defaults
            required_fields = {
                'name': profile_name,
                'color_blindness_type': 'none',
                'language': 'en',
                'theme': 'dark',
                'window_width': 1000,
                'window_height': 600,
                'window_x': 100,
                'window_y': 100,
                'is_maximized': False,
                'camera_permission': 'ask',
                'selected_camera_index': 0,
                'detect_red': True,
                'detect_green': True,
                'detect_blue': False,
                'detect_yellow': False,
                'skin_tone_filtering_active': True,
                'stability_enhancement_active': True,
                'debug_mode_active': False,
                'detection_sensitivity': 0.5,
                'color_enhancement': True,
                'voice_feedback': False,
                'auto_detection': True,
                'filter_strength': 1.0,
                'created_date': '',
                'last_used_date': '',
                'gallery_x': -1,
                'gallery_y': -1,
                'gallery_width': -1,
                'gallery_height': -1
            }
            
            for field, default_value in required_fields.items():
                if field not in data:
                    data[field] = default_value
            
            profile = UserProfile.from_dict(data)
            
            # Update last used date
            from datetime import datetime
            profile.last_used_date = datetime.now().isoformat()
            self.save_profile(profile)  # Save the updated last used date
            
            return profile
        except Exception as e:
            print(f"Error loading profile {profile_name}: {e}")
            return None
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        try:
            file_path = self._get_profile_file_path(profile_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting profile {profile_name}: {e}")
            return False
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile"""
        try:
            old_file_path = self._get_profile_file_path(old_name)
            new_file_path = self._get_profile_file_path(new_name)
            
            if not os.path.exists(old_file_path):
                return False
            
            if os.path.exists(new_file_path):
                return False  # New name already exists
            
            # Load profile data and update name
            profile = self.load_profile(old_name)
            if profile:
                profile.name = new_name
                # Save with new name
                if self.save_profile(profile):
                    # Delete old file
                    os.remove(old_file_path)
                    return True
            
            return False
        except Exception as e:
            print(f"Error renaming profile {old_name} to {new_name}: {e}")
            return False
    
    def get_all_profiles(self) -> List[str]:
        """Get list of all available profile names"""
        try:
            if not os.path.exists(self.profiles_dir):
                return []
            
            profiles = []
            for file_name in os.listdir(self.profiles_dir):
                if file_name.endswith('.json'):
                    profile_name = file_name[:-5]  # Remove .json extension
                    profiles.append(profile_name)
            
            return sorted(profiles)
        except Exception as e:
            print(f"Error getting profiles list: {e}")
            return []
    
    def get_profile_info(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get basic profile information without loading the full profile"""
        try:
            file_path = self._get_profile_file_path(profile_name)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'name': data.get('name', profile_name),
                'color_blindness_type': data.get('color_blindness_type', 'none'),
                'language': data.get('language', 'en'),
                'theme': data.get('theme', 'dark'),
                'created_date': data.get('created_date', ''),
                'last_used_date': data.get('last_used_date', '')
            }
        except Exception as e:
            print(f"Error getting profile info for {profile_name}: {e}")
            return None
    
    def apply_profile_to_settings(self, profile: UserProfile):
        """Apply profile settings to QSettings"""
        # Core window and general settings
        self.settings.setValue("language", profile.language)
        self.settings.setValue("theme", profile.theme)
        self.settings.setValue("camera_permission", profile.camera_permission)
        self.settings.setValue("color_blindness_type", profile.color_blindness_type)
        self.settings.setValue("window_width", profile.window_width)
        self.settings.setValue("window_height", profile.window_height)
        self.settings.setValue("window_x", profile.window_x)
        self.settings.setValue("window_y", profile.window_y)
        self.settings.setValue("is_maximized", profile.is_maximized)

        # Advanced: color selections and flags
        self.settings.setValue("detect_red", profile.detect_red)
        self.settings.setValue("detect_green", profile.detect_green)
        self.settings.setValue("detect_blue", profile.detect_blue)
        self.settings.setValue("detect_yellow", profile.detect_yellow)
        self.settings.setValue("skin_tone_filtering_active", profile.skin_tone_filtering_active)
        self.settings.setValue("stability_enhancement_active", profile.stability_enhancement_active)
        self.settings.setValue("debug_mode_active", profile.debug_mode_active)
        self.settings.setValue("detection_sensitivity", profile.detection_sensitivity)
        self.settings.setValue("color_enhancement", profile.color_enhancement)
        self.settings.setValue("voice_feedback", profile.voice_feedback)
        self.settings.setValue("auto_detection", profile.auto_detection)
        self.settings.setValue("filter_strength", profile.filter_strength)

        # Gallery window placement
        self.settings.setValue("gallery_x", profile.gallery_x)
        self.settings.setValue("gallery_y", profile.gallery_y)
        self.settings.setValue("gallery_width", profile.gallery_width)
        self.settings.setValue("gallery_height", profile.gallery_height)

        # Book-keeping
        self.settings.setValue("current_profile", profile.name)
        self.settings.sync()
    
    def load_profile_from_settings(self) -> UserProfile:
        """Load profile data from current QSettings"""
        from datetime import datetime
        
        return UserProfile(
            name=self.settings.value("current_profile", "Default Profile"),
            color_blindness_type=self.settings.value("color_blindness_type", "none"),
            language=self.settings.value("language", "en"),
            theme=self.settings.value("theme", "dark"),
            window_width=int(self.settings.value("window_width", 1000)),
            window_height=int(self.settings.value("window_height", 600)),
            window_x=int(self.settings.value("window_x", 100)),
            window_y=int(self.settings.value("window_y", 100)),
            is_maximized=self.settings.value("is_maximized", False, type=bool),
            camera_permission=self.settings.value("camera_permission", "ask"),
            detect_red=self.settings.value("detect_red", True, type=bool),
            detect_green=self.settings.value("detect_green", True, type=bool),
            detect_blue=self.settings.value("detect_blue", False, type=bool),
            detect_yellow=self.settings.value("detect_yellow", False, type=bool),
            skin_tone_filtering_active=self.settings.value("skin_tone_filtering_active", True, type=bool),
            stability_enhancement_active=self.settings.value("stability_enhancement_active", True, type=bool),
            debug_mode_active=self.settings.value("debug_mode_active", False, type=bool),
            detection_sensitivity=float(self.settings.value("detection_sensitivity", 0.5)),
            color_enhancement=self.settings.value("color_enhancement", True, type=bool),
            voice_feedback=self.settings.value("voice_feedback", False, type=bool),
            auto_detection=self.settings.value("auto_detection", True, type=bool),
            filter_strength=float(self.settings.value("filter_strength", 1.0)),
            created_date=self.settings.value("profile_created_date", datetime.now().isoformat()),
            last_used_date=datetime.now().isoformat(),
            gallery_x=int(self.settings.value("gallery_x", -1)),
            gallery_y=int(self.settings.value("gallery_y", -1)),
            gallery_width=int(self.settings.value("gallery_width", -1)),
            gallery_height=int(self.settings.value("gallery_height", -1))
        )
    
    def export_profile(self, profile_name: str, export_path: str) -> bool:
        """Export a profile to specified path"""
        try:
            profile = self.load_profile(profile_name)
            if not profile:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting profile {profile_name}: {e}")
            return False
    
    def import_profile(self, import_path: str) -> Optional[UserProfile]:
        """Import a profile from specified path"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profile = UserProfile.from_dict(data)
            
            # Ensure unique name if profile already exists
            original_name = profile.name
            counter = 1
            while original_name in self.get_all_profiles():
                original_name = f"{profile.name} ({counter})"
                counter += 1
            profile.name = original_name
            
            # Save the imported profile
            if self.save_profile(profile):
                return profile
            return None
        except Exception as e:
            print(f"Error importing profile from {import_path}: {e}")
            return None
