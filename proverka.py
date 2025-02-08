from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.animation import Animation
import string
import requests
import hashlib


KV = """
Screen:
    canvas.before:
        Color:
            rgba: (0.05, 0.05, 0.15, 1)  # Темний градієнтний фон
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        text: "🔐 Перевірка пароля"
        font_style: "H4"
        halign: "center"
        pos_hint: {"center_y": 0.92}
        bold: True
        theme_text_color: "Custom"
        text_color: (1, 1, 1, 0.8)

    MDCard:
        size_hint: 0.92, 0.6
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 20
        radius: [25, 25, 25, 25]
        md_bg_color: 0.1, 0.1, 0.2, 0.8  # Скляний ефект

        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)

            MDTextField:
                id: password_entry
                hint_text: "Введіть пароль"
                password: False  # Пароль тепер завжди видимий
                mode: "fill"
                fill_color: (0.2, 0.2, 0.3, 0.8)
                icon_right: "eye"  # Іконка залишена, але не функціонує
                # on_icon_right: app.toggle_password_visibility()  # Видалено виклик функції

            MDRaisedButton:
                text: "🔍 Перевірити пароль"
                md_bg_color: (0.1, 0.7, 1, 1)
                pos_hint: {"center_x": 0.5}
                on_release: app.check_password()

            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_x: 1
                height: dp(10)  # Менша висота для прогресбару

            MDLabel:
                id: feedback_label
                text: ""
                font_style: "Body1"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                bold: True
                theme_text_color: "Custom"
                text_color: (1, 1, 1, 1)
                opacity: 0  # Початковий стан непрозорості
                pos_hint: {"center_y": 0.1}  # Розташування під підказками
"""

class PasswordCheckerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def check_password_strength(self, password):
        """Перевірка надійності пароля."""
        strength = 0
        comments = []

        if len(password) >= 12:
            strength += 2
        elif len(password) >= 8:
            strength += 1
        else:
            comments.append("⚠️ Пароль занадто короткий!")

        if any(char.isdigit() for char in password):
            strength += 1
        else:
            comments.append("➕ Додай хоча б одну цифру.")

        if any(char.islower() for char in password) and any(char.isupper() for char in password):
            strength += 2
        else:
            comments.append("🔠 Використовуй великі та малі літери.")

        if any(char in string.punctuation for char in password):
            strength += 2
        else:
            comments.append("🔣 Додай хоча б один спецсимвол (!, @, #, etc.).")

        return min(strength, 5), comments

    def check_password_leak(self, password):
        """Перевірка пароля у витоках даних."""
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url)

        if response.status_code == 200:
            hashes = (line.split(":") for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
        return 0

    def animate_progress_bar(self, progress_value):
        """Анімація шкали надійності пароля."""
        animation = Animation(value=progress_value, duration=0.7)
        animation.start(self.root.ids.progress_bar)

    def animate_feedback_label(self):
        """Анімація для підказок."""
        feedback_label = self.root.ids.feedback_label
        animation = Animation(opacity=1, duration=1)
        animation.start(feedback_label)

    def check_password(self):
        """Основна функція перевірки пароля."""
        password = self.root.ids.password_entry.text
        feedback_label = self.root.ids.feedback_label
        progress_bar = self.root.ids.progress_bar

        if not password:
            feedback_label.text = "⚠️ Введи пароль!"
            progress_bar.value = 0
            progress_bar.color = (0.5, 0.5, 0.5, 1)
            return

        strength, tips = self.check_password_strength(password)
        self.animate_progress_bar((strength / 5) * 100)

        if strength <= 1:
            progress_bar.color = (1, 0, 0, 1)  
        elif strength <= 3:
            progress_bar.color = (1, 0.5, 0, 1) 
        else:
            progress_bar.color = (0, 1, 0, 1) 

        leak_count = self.check_password_leak(password)
        if leak_count > 0:
            tips.append(f"⚠️ Цей пароль зламаний {leak_count} разів! НЕ ВИКОРИСТОВУЙ ЙОГО!")

        feedback_label.text = "\n".join(tips) if tips else "✅ Пароль сильний!"
        self.animate_feedback_label()

if __name__ == "__main__":
    PasswordCheckerApp().run()
