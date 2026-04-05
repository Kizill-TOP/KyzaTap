[app]
title = Kyza TapCat
package.name = kyzatapcat
package.domain = org.antisys
source.dir = .
source.include_exts = py,png,jpg,mp3
version = 1.0.0
requirements = python3,kivy,pygame,android
android.permissions = INTERNET, VIBRATE
android.api = 30
android.minapi = 21
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1