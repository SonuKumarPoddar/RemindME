from database.db import create_table, insert_reminder, get_reminder_by_id
from plyer import notification
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.core.window import Window

from datetime import datetime, timedelta

# Mobile-like window size
Window.size = (360, 640)

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="RemindMe",
        timeout=10
    )

def parse_datetime(date_str, time_str):
    # Example: date_str = "2026-01-03"
    # time_str = "11:00 AM"
    return datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %I:%M %p"
    )
def check_reminders(dt):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, date, primary_time FROM reminders")
    reminders = cursor.fetchall()
    conn.close()

    now = datetime.now()

    for r in reminders:
        reminder_id, title, date, time1 = r
        reminder_time = parse_datetime(date, time1)

        if 0 <= (reminder_time - now).total_seconds() <= 30:
            show_notification(
                "⏰ Reminder",
                f"{title}"
            )


def test_notification():
    notification.notify(
        title="RemindMe Test",
        message="Notification system is working 🔔",
        app_name="RemindMe",
        timeout=5
    )

# ---------------- HOME SCREEN ----------------


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        layout.add_widget(Label(text="RemindMe", font_size=32))

        create_btn = Button(text="Create Reminder")
        join_btn = Button(text="Join Reminder")

        create_btn.bind(on_press=lambda x: setattr(self.manager, "current", "create"))
        join_btn.bind(on_press=lambda x: setattr(self.manager, "current", "join"))

        layout.add_widget(create_btn)
        layout.add_widget(join_btn)

        self.add_widget(layout)


# ---------------- CREATE REMINDER SCREEN ----------------
class CreateReminderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # state variables
        self.selected_date = None
        self.selected_image = ""
        self.primary_time = "11:00"
        self.fallback_time = "16:00"

        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        self.main_layout.add_widget(Label(text="Create Reminder", font_size=26))

        # Title input
        self.title_input = TextInput(
            hint_text="Enter reminder title",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        self.main_layout.add_widget(self.title_input)

        # Image preview
        self.image_preview = Image(size_hint=(1, 0.25))
        self.main_layout.add_widget(self.image_preview)

        self.main_layout.add_widget(
            Button(text="Add Photo", on_press=self.open_gallery)
        )

        # Date label
        self.date_label = Label(text="No date selected")
        self.main_layout.add_widget(self.date_label)

        # Date buttons
        date_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        date_grid.bind(minimum_height=date_grid.setter("height"))

        btn_2_days = Button(text="2 Days", size_hint_y=None, height=60)
        btn_2_days.bind(on_press=self.set_2_days)

        btn_2_weeks = Button(text="2 Weeks", size_hint_y=None, height=60)
        btn_2_weeks.bind(on_press=self.set_2_weeks)

        date_grid.add_widget(btn_2_days)
        date_grid.add_widget(btn_2_weeks)

        self.main_layout.add_widget(date_grid)

        # Time pickers
        self.time_label = Label(
            text=f"Primary: {self.primary_time} | Fallback: {self.fallback_time}"
        )
        self.main_layout.add_widget(self.time_label)

        time_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, height=60)

        self.hour_spinner = Spinner(
            text="11",
            values=[str(i) for i in range(1, 13)]
        )

        self.minute_spinner = Spinner(
            text="00",
            values=[f"{i:02d}" for i in range(0, 60, 5)]
        )

        self.ampm_spinner = Spinner(
            text="AM",
            values=["AM", "PM"]
        )

        time_grid.add_widget(self.hour_spinner)
        time_grid.add_widget(self.minute_spinner)
        time_grid.add_widget(self.ampm_spinner)

        self.main_layout.add_widget(time_grid)

        self.main_layout.add_widget(
            Button(text="Save Time", on_press=self.save_time)
        )

        # Save reminder
        self.main_layout.add_widget(
            Button(text="Save Reminder", on_press=self.save_reminder)
        )

        # Back
        self.main_layout.add_widget(
            Button(text="Back", on_press=lambda x: setattr(self.manager, "current", "home"))
        )

        self.add_widget(self.main_layout)

    # -------- DATE LOGIC --------
    def set_2_days(self, instance):
        self.selected_date = (datetime.now() + timedelta(days=2)).date()
        self.date_label.text = f"Date: {self.selected_date}"

    def set_2_weeks(self, instance):
        self.selected_date = (datetime.now() + timedelta(weeks=2)).date()
        self.date_label.text = f"Date: {self.selected_date}"

    # -------- TIME LOGIC --------
    def save_time(self, instance):
        h = self.hour_spinner.text
        m = self.minute_spinner.text
        ap = self.ampm_spinner.text

        if ap == "PM" and h != "12":
            h = str(int(h) + 12)
        if ap == "AM" and h == "12":
            h = "00"

        self.primary_time = f"{h}:{m}"
        self.fallback_time = "16:00"  # default fallback

        self.time_label.text = (
            f"Primary: {self.primary_time} | Fallback: {self.fallback_time}"
        )

    # -------- IMAGE PICKER --------
    def open_gallery(self, instance):
        self.filechooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg"]
        )

        select_btn = Button(text="Select Image")
        select_btn.bind(on_press=self.confirm_selection)

        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.filechooser)
        self.main_layout.add_widget(select_btn)

    def confirm_selection(self, instance):
        if self.filechooser.selection:
            self.selected_image = self.filechooser.selection[0]
            self.image_preview.source = self.selected_image

        self.main_layout.clear_widgets()
        self.__init__()

    # -------- SAVE TO DB --------
    def save_reminder(self, instance):
        title = self.title_input.text

        if not title or not self.selected_date:
            print("❌ Title or Date missing")
            return

        reminder_id = insert_reminder(
            title,
            self.selected_image,
            str(self.selected_date),
            self.primary_time,
            self.fallback_time
        )

        print("✅ Reminder saved with ID:", reminder_id)
        self.manager.current = "home"


# ---------------- JOIN REMINDER SCREEN ----------------
class JoinReminderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )

        self.layout.add_widget(Label(text="Join Reminder", font_size=26))

        self.id_input = TextInput(
            hint_text="Enter Reminder ID",
            multiline=False
        )
        self.layout.add_widget(self.id_input)

        join_btn = Button(text="Join")
        join_btn.bind(on_press=self.join_reminder)
        self.layout.add_widget(join_btn)

        self.result_label = Label(text="")
        self.layout.add_widget(self.result_label)

        back_btn = Button(text="Back")
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "home"))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def join_reminder(self, instance):
     reminder_id = self.id_input.text.strip()

     if not reminder_id:
        self.result_label.text = "❌ Please enter Reminder ID"
        return

     data = get_reminder_by_id(reminder_id)

     if data:
        _, title, image, date, t1, t2 = data
        self.result_label.text = (
            f"🟢 Reminder Found\n"
            f"Title: {title}\n"
            f"Date: {date}\n"
            f"Time: {t1}, {t2}"
        )
     else:
        self.result_label.text = "❌ Reminder not found"


# ---------------- MAIN APP ----------------
class RemindMeApp(App):
    def build(self):
        create_table()
        print("DB connected")

        Clock.schedule_interval(check_reminders, 30)

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CreateReminderScreen(name="create"))
        sm.add_widget(JoinReminderScreen(name="join"))

        return sm


if __name__ == "__main__":
    RemindMeApp().run()