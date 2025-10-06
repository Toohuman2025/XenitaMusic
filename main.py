from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
import os
import glob

Window.clearcolor = (0.1, 0.1, 0.15, 1)

class XenitaMusicPlayer(App):
    def build(self):
        self.current_sound = None
        self.is_playing = False
        self.playlist = []
        self.current_index = 0
        self.is_shuffle = False
        self.is_repeat = False
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint=(1, 0.08), padding=5)
        with header.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.header_rect = RoundedRectangle(radius=[15])
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)
        
        title = Label(
            text='[b]🎵 XENITA MUSIC[/b]',
            markup=True,
            font_size=28,
            color=(0.66, 0.33, 0.93, 1)
        )
        self.track_count = Label(
            text='0 canciones',
            font_size=14,
            color=(0.66, 0.33, 0.93, 1),
            size_hint=(0.3, 1)
        )
        header.add_widget(title)
        header.add_widget(self.track_count)
        
        # Player Card
        player_card = BoxLayout(orientation='vertical', size_hint=(1, 0.5), padding=20, spacing=15)
        with player_card.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.player_rect = RoundedRectangle(radius=[25])
        player_card.bind(size=self._update_player_rect, pos=self._update_player_rect)
        
        # Album Art
        album_art = FloatLayout(size_hint=(1, 0.5))
        with album_art.canvas:
            Color(0.42, 0.16, 0.58, 1)
            self.album_rect = RoundedRectangle(radius=[20])
        album_art.bind(size=self._update_album_rect, pos=self._update_album_rect)
        
        album_icon = Label(
            text='🎵',
            font_size=120,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        album_art.add_widget(album_icon)
        
        # Track info
        self.track_label = Label(
            text='Sin música',
            font_size=22,
            bold=True,
            size_hint=(1, 0.08)
        )
        
        self.artist_label = Label(
            text='Selecciona una canción',
            font_size=16,
            color=(0.66, 0.33, 0.93, 1),
            size_hint=(1, 0.05)
        )
        
        # Progress slider
        progress_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.12), spacing=5)
        self.progress_slider = Slider(
            min=0,
            max=100,
            value=0,
            size_hint=(1, 0.5),
            cursor_size=(15, 15)
        )
        self.progress_slider.bind(on_touch_up=self.seek_position)
        
        time_layout = BoxLayout(size_hint=(1, 0.5))
        self.current_time = Label(text='0:00', font_size=12, color=(0.66, 0.33, 0.93, 1))
        self.total_time = Label(text='0:00', font_size=12, color=(0.66, 0.33, 0.93, 1))
        time_layout.add_widget(self.current_time)
        time_layout.add_widget(Label())
        time_layout.add_widget(self.total_time)
        
        progress_layout.add_widget(self.progress_slider)
        progress_layout.add_widget(time_layout)
        
        # Controls
        controls = BoxLayout(size_hint=(1, 0.15), spacing=15, padding=[20, 10])
        
        self.shuffle_btn = Button(
            text='🔀',
            font_size=24,
            size_hint=(0.15, 1),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        self.shuffle_btn.bind(on_press=self.toggle_shuffle)
        
        prev_btn = Button(
            text='⏮️',
            font_size=28,
            size_hint=(0.15, 1),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        prev_btn.bind(on_press=self.previous_track)
        
        self.play_btn = Button(
            text='▶️',
            font_size=40,
            size_hint=(0.25, 1),
            background_color=(0.66, 0.33, 0.93, 1),
            background_normal=''
        )
        self.play_btn.bind(on_press=self.toggle_play)
        
        next_btn = Button(
            text='⏭️',
            font_size=28,
            size_hint=(0.15, 1),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        next_btn.bind(on_press=self.next_track)
        
        self.repeat_btn = Button(
            text='🔁',
            font_size=24,
            size_hint=(0.15, 1),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        self.repeat_btn.bind(on_press=self.toggle_repeat)
        
        controls.add_widget(self.shuffle_btn)
        controls.add_widget(prev_btn)
        controls.add_widget(self.play_btn)
        controls.add_widget(next_btn)
        controls.add_widget(self.repeat_btn)
        
        # Volume control
        volume_layout = BoxLayout(size_hint=(1, 0.08), spacing=10, padding=[50, 0])
        volume_layout.add_widget(Label(text='🔊', font_size=20, size_hint=(0.1, 1)))
        self.volume_slider = Slider(min=0, max=1, value=1, size_hint=(0.9, 1))
        self.volume_slider.bind(value=self.change_volume)
        volume_layout.add_widget(self.volume_slider)
        
        player_card.add_widget(album_art)
        player_card.add_widget(self.track_label)
        player_card.add_widget(self.artist_label)
        player_card.add_widget(progress_layout)
        player_card.add_widget(controls)
        player_card.add_widget(volume_layout)
        
        # Load button
        load_btn = Button(
            text='📁 CARGAR MÚSICA',
            font_size=18,
            bold=True,
            size_hint=(1, 0.08),
            background_color=(0.66, 0.33, 0.93, 1),
            background_normal=''
        )
        load_btn.bind(on_press=self.load_music)
        
        # Playlist
        scroll = ScrollView(size_hint=(1, 0.34))
        self.playlist_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=10)
        self.playlist_layout.bind(minimum_height=self.playlist_layout.setter('height'))
        scroll.add_widget(self.playlist_layout)
        
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(player_card)
        self.main_layout.add_widget(load_btn)
        self.main_layout.add_widget(scroll)
        
        Clock.schedule_interval(self.update_progress, 0.5)
        self.auto_load_music()
        
        return self.main_layout
    
    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def _update_player_rect(self, instance, value):
        self.player_rect.pos = instance.pos
        self.player_rect.size = instance.size
    
    def _update_album_rect(self, instance, value):
        padding = 40
        size = min(instance.width, instance.height) - padding
        self.album_rect.pos = (
            instance.x + (instance.width - size) / 2,
            instance.y + (instance.height - size) / 2
        )
        self.album_rect.size = (size, size)
    
    def auto_load_music(self):
        music_paths = [
            '/storage/emulated/0/Music',
            '/sdcard/Music',
            './assets/musica'
        ]
        
        for path in music_paths:
            if os.path.exists(path):
                files = []
                for ext in ['*.mp3', '*.ogg', '*.wav', '*.flac', '*.m4a']:
                    files.extend(glob.glob(os.path.join(path, ext)))
                
                if files:
                    self.playlist = sorted(files)
                    self.update_playlist_ui()
                    break
    
    def load_music(self, instance):
        self.auto_load_music()
    
    def update_playlist_ui(self):
        self.playlist_layout.clear_widgets()
        self.track_count.text = f'{len(self.playlist)} canciones'
        
        for idx, track in enumerate(self.playlist):
            track_btn = Button(
                text=f'{"▶️" if idx == self.current_index else "🎵"} {os.path.basename(track)}',
                size_hint=(1, None),
                height=60,
                background_color=(0.42, 0.16, 0.58, 0.5) if idx == self.current_index else (0.2, 0.2, 0.25, 1),
                background_normal='',
                halign='left',
                padding=[10, 0]
            )
            track_btn.bind(on_press=lambda x, i=idx: self.play_track(i))
            self.playlist_layout.add_widget(track_btn)
    
    def play_track(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            track_path = self.playlist[index]
            
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound.unload()
            
            self.current_sound = SoundLoader.load(track_path)
            
            if self.current_sound:
                self.current_sound.volume = self.volume_slider.value
                self.current_sound.play()
                self.is_playing = True
                self.play_btn.text = '⏸️'
                self.track_label.text = os.path.basename(track_path).replace('.mp3', '').replace('.ogg', '')
                self.artist_label.text = 'Reproduciendo...'
                self.update_playlist_ui()
                self.current_sound.bind(on_stop=self.on_track_end)
    
    def on_track_end(self, instance):
        if self.is_repeat:
            self.play_track(self.current_index)
        else:
            self.next_track(None)
    
    def toggle_play(self, instance):
        if not self.playlist:
            return
        
        if not self.current_sound:
            self.play_track(self.current_index)
            return
        
        if self.is_playing:
            self.current_sound.stop()
            self.play_btn.text = '▶️'
            self.is_playing = False
        else:
            self.current_sound.play()
            self.play_btn.text = '⏸️'
            self.is_playing = True
    
    def next_track(self, instance):
        if not self.playlist:
            return
        
        if self.is_shuffle:
            import random
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        
        self.play_track(self.current_index)
    
    def previous_track(self, instance):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_track(self.current_index)
    
    def toggle_shuffle(self, instance):
        self.is_shuffle = not self.is_shuffle
        self.shuffle_btn.background_color = (0.66, 0.33, 0.93, 1) if self.is_shuffle else (0.3, 0.3, 0.35, 1)
    
    def toggle_repeat(self, instance):
        self.is_repeat = not self.is_repeat
        self.repeat_btn.background_color = (0.66, 0.33, 0.93, 1) if self.is_repeat else (0.3, 0.3, 0.35, 1)
    
    def change_volume(self, instance, value):
        if self.current_sound:
            self.current_sound.volume = value
    
    def seek_position(self, instance, touch):
        if self.current_sound and instance.collide_point(*touch.pos):
            seek_pos = (instance.value / 100) * self.current_sound.length
            self.current_sound.seek(seek_pos)
    
    def update_progress(self, dt):
        if self.current_sound and self.is_playing:
            if self.current_sound.length > 0:
                progress = (self.current_sound.get_pos() / self.current_sound.length) * 100
                self.progress_slider.value = progress
                
                current = int(self.current_sound.get_pos())
                total = int(self.current_sound.length)
                
                self.current_time.text = f'{current//60}:{current%60:02d}'
                self.total_time.text = f'{total//60}:{total%60:02d}'

if __name__ == '__main__':
    XenitaMusicPlayer().run()
