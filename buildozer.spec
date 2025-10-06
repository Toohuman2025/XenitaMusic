[app]
title = Xenita Music Player
package.name = xenitamusic
package.domain = com.toohuman
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,mp3,ogg,wav,flac,m4a
version = 1.0.0
requirements = python3,kivy==2.2.1,android,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,WAKE_LOCK
android.minapi = 21
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.enable_proguard = True
android.enable_multidex = True
android.statusbar_color = #1a1a2e
log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2
build_dir = ./.buildozer
bin_dir = ./bin
