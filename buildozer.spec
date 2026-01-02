[app]
title = RemindME
package.name = remindme
package.domain = org.seenu

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
orientation = portrait

requirements = python3,kivy,plyer

fullscreen = 0

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True


[buildozer]
log_level = 2
warn_on_root = 1
