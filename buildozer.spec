[app]
title = RemindME
package.name = remindme
package.domain = org.seenu

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
orientation = portrait

requirements = kivy,plyer

fullscreen = 0

android.api = 30
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True


[buildozer]
log_level = 2
warn_on_root = 1
