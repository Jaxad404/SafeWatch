from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Fbo, ClearColor, ClearBuffers, Rectangle
from utils import countStats
from utils.util import hashedPwd
from kivy.utils import get_color_from_hex, platform
from model.datastore import DTB
from model.conf import dbConfig, userConfig
from kivy.properties import StringProperty
from kivymd.theming import ThemeManager
from kivy_garden.mapview import MapMarkerPopup
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from matplotlib.figure import Figure
from kivymd.uix.snackbar import MDSnackbar
from kivymd.toast import toast
import webbrowser, random, time
import pandas as pd
from threading import Thread


Window.size = (1080 / 2.5, 2340 / 3)


class SplashScreen(MDScreen):
    pass


class SignUPScreen(MDScreen):
    pass


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dtb = DTB(dbConfig)
        self.app = MDApp.get_running_app()


    def validate_login(self, username, password):
        try:
            pwd = hashedPwd(password)
            if self.dtb.validateUser((username, pwd)):
                self.app.show_screen('landingPage')

                if self.app.user is None:
                    self.app.user = username
            else:
                MDSnackbar(MDLabel(text="Invalid username or password",
                                   text_color= "red",
                                   theme_text_color="Custom")
                           ).open()

        except Exception as e:
            self.app.show_screen('login')

    def on_leave(self, *args):
        self.dtb.close()


class ReportScreen(MDScreen):
    theme_cls = ThemeManager()
    theme_mode = StringProperty("Dark")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.case_data = {
            "total_cases": 0,
            "solved_cases": 0,
            "pending_cases": 0,
            "dismissed_cases": 0
        }
    reports_data = None

    def on_enter(self):
        app = MDApp.get_running_app()
        app.active_tab = 'Report'
        self.reports_data = app.cache_data
        self.load_data()

    def load_data(self):
        cases = self.reports_data
        self.case_data["total_cases"] = cases.shape[0]
        self.case_data["solved_cases"] = int(self.case_data['total_cases'] / 2)
        self.case_data["pending_cases"] = random.randint(0, self.case_data["total_cases"] - self.case_data["solved_cases"])
        self.case_data["dismissed_cases"] = self.case_data["total_cases"] - (self.case_data["solved_cases"] + self.case_data["pending_cases"])
        self.ids.total_cases_label.text = str(self.case_data["total_cases"])
        self.ids.solved_cases_label.text = str(self.case_data["solved_cases"])
        self.ids.pending_cases_label.text = str(self.case_data["pending_cases"])
        self.ids.dismissed_cases_label.text = str(self.case_data["dismissed_cases"])

    def refresh_data(self):
        MDSnackbar(MDLabel(text="Refreshing Case Status...",
                           theme_text_color='Custom',
                           text_color="teal")
                   ).open()
        self.load_data()

    def view_case_charts(self):
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        labels = ['Solved', 'Pending', 'Dismissed']
        sizes = [self.case_data["solved_cases"], self.case_data["pending_cases"], self.case_data["dismissed_cases"]]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#4caf50', '#ffeb3b', '#f44336'])
        ax.axis('equal')
        card = MDCard(
            orientation='vertical',
            size_hint=(0.8, None),
            height=dp(400),
            md_bg_color=get_color_from_hex('#4279a3'),
            radius=[15, ],
            shadow_color=get_color_from_hex('#88BDF2'),
            shadow_offset=(1, -2),
            shadow_softness=1,
            pos_hint={"center_x": .5, "center_y": .7},
            elevation=5,
        )
        chart_canvas = FigureCanvasKivyAgg(fig)
        card.add_widget(chart_canvas)
        close_button = MDFlatButton(
            text="Close",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            size_hint=(1,None),
            height=dp(40),
            padding=(0, dp(10)),
            on_release=lambda *args: self.ids.chart_layout.remove_widget(card)
        )
        card.add_widget(close_button)
        self.ids.chart_layout.add_widget(card)

    def handle_speed_dial(self, instance_fab, instance_label):
        if instance_label == "Send SMS":
            self.open_sms_app(self)
        elif instance_label == "Make Call":
            self.open_call_app(self)

    @staticmethod
    def open_sms_app(self):
        if platform == "android":
            webbrowser.open("sms:")
        else:
            MDSnackbar(MDLabel(text="SMS is only supported on Android.",
                               theme_text_color='Custom',
                               text_color="teal")
                       ).open()

    @staticmethod
    def open_call_app(self):
        if platform == "android":
            webbrowser.open("tel:")
        else:
            MDSnackbar(MDLabel(text="Phone calls are only supported on Android.",
                               theme_text_color='Custom',
                               text_color="teal")
                       ).open()


class LandingPageScreen(MDScreen):
    theme_cls = ThemeManager()
    theme_mode = StringProperty('Dark')
    division_to_sort_by = None
    card_data = None
    div_name = None
    active_tab = "Home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        self.card_data = app.cache_data
        self.load_card_data()

    def toggle_card_stats(self):
        results = self.card_data
        grid = self.ids.md_card_grid
        grid.clear_widgets()
        grid.cols = 1
        divisions =  [dict.get('id') for dict in countStats.divisions]
        groups = results.groupby("Division", as_index=False)

        for idx, division in enumerate(divisions):
            for div in countStats.divisions:
                if div.get('id') == division:
                    self.div_name = div.get('name')

            grp = groups.get_group(division)
            total_cases = len(grp)
            avg_year = grp['occurrenceyear'].mean()
            latest_year = grp['occurrenceyear'].max()
            most_common_crime = grp['MCI'].value_counts().idxmax()

            stats_text = (
                f"[b]Division Name:[/b] {self.div_name}\n"
                f"[b]Division: Code[/b] {division}\n"
                f"[b]Total Cases:[/b] {total_cases}\n"
                f"[b]Violent Crimes:[/b] Assault\n"
                f"[b]Latest Year:[/b] {latest_year}\n"
                f"[b]Common Crime:[/b] {most_common_crime}\n"
                f"[b]Non-Violent Crime:[/b] Auto Theft\n"
            )
            card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(290),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[20,],
                pos_hint={"center_y": 0.5},
                elevation=3,
            )
            stats_label = MDLabel(
                text=stats_text,
                halign="left",
                valign='top',
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                markup=True,  # rich text formatting
                size_hint=(1, None),
                height=dp(270),
                padding=(dp(10), dp(10)),
            )
            card.add_widget(stats_label)
            grid.add_widget(card)
        grid.height = len(divisions) * (dp(200) + dp(10))

    def load_card_data(self):
        if self.card_data is None:
            app = MDApp.get_running_app()
            app.get_card_data()
            self.card_data = app.cache_data

        grid = self.ids.md_card_grid
        divisions =  [dict.get('id') for dict in countStats.divisions]
        groups = self.card_data.groupby("Division", as_index=False)
        grid.cols = 2
        grid.clear_widgets()
        for idx, division in enumerate(divisions):
            grp = groups.get_group(division)
            total_cases = len(grp)
            avg_year = grp['occurrenceyear'].mean()
            latest_year = grp['occurrenceyear'].max()
            most_common_crime = grp['MCI'].value_counts().idxmax()
            crime_counts = grp['MCI'].value_counts()

            fig = Figure(figsize=(5, 3))
            ax = fig.add_subplot(111)
            fig.patch.set_facecolor('#2E2E2E')
            ax.set_facecolor('#2E2E2E')
            ax.bar(crime_counts.index, crime_counts.values, color='cyan', alpha=0.7)
            ax.set_title(f"Crime Types in {division}", color="white")
            ax.tick_params(colors="white")
            ax.set_xticks(range(len(crime_counts.index)))
            ax.set_xticklabels(crime_counts.index, rotation=22, ha="right", fontsize=7, color="white")
            ax.grid(color='#444444', linestyle='--', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.yaxis.set_visible(False)
            card = MDCard(
                orientation='vertical',
                size_hint=(0.5, None),
                height=dp(280),
                md_bg_color=[0.2, 0.2, 0.2, 1],
                radius=[20],
                pos_hint={"center_y": 0.5},
                elevation=2,
            )
            canvas = FigureCanvasKivyAgg(fig, size_hint=(1, 1))
            card.add_widget(canvas)
            grid.add_widget(card)

        grid.height = len(divisions) * (dp(200) + dp(10))

    def searchDialog(self, *args):
        self.dialog = MDDialog(
            title="Search by Division:",
            type="custom",
            md_bg_color= get_color_from_hex('#2E2E2E'),
            pos_hint={"center_y": .85},
            content_cls= MDBoxLayout(
                MDTextField(
                    id='search_by_division',
                    theme_text_color = "Custom",
                    text_color_normal = "white",
                    text_color_focus = "white",
                ),
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="30dp"),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= self.close_dialog
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= self.on_search
                )],
            )
        return self.dialog.open()

    def on_search(self, *args):
        content_cls = self.dialog.content_cls
        self.dialog.dismiss()
        self.division_to_sort_by = str.upper(content_cls.ids.search_by_division.text)
        results = self.card_data
        grid = self.ids.md_card_grid
        divisions =  [dict.get('id') for dict in countStats.divisions]
        groups = results.groupby("Division", as_index=False)
        grid.clear_widgets()
        grid.cols = 1
        grid.spacing = dp(20)

        grp = groups.get_group(self.division_to_sort_by)
        total_cases = len(grp)
        avg_year = grp['occurrenceyear'].mean()
        latest_year = grp['occurrenceyear'].max()
        most_common_crime = grp['MCI'].value_counts().idxmax()

        fig = Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor('#2E2E2E')
        ax.set_facecolor('#2E2E2E')
        crime_counts = grp['MCI'].value_counts()
        ax.bar(crime_counts.index, crime_counts.values, color='cyan', alpha=0.7)
        ax.set_title(f"Crime Types in {self.division_to_sort_by}", color="white")
        ax.tick_params(colors="white")
        ax.set_xticks(range(len(crime_counts.index)))
        ax.set_xticklabels(crime_counts.index, rotation=22, ha="right", fontsize=7, color="white")
        ax.grid(color='#444444', linestyle='--', linewidth=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.yaxis.set_visible(False)

        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(280),
            md_bg_color=[0.2, 0.2, 0.2, 1],
            radius=[20,],
            pos_hint={"center_x": 0.5},
            elevation=3,
        )
        card2 = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(280),
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[20],
            pos_hint={"center_x": 0.5},
            elevation=2,
        )
        stats_text = (
            f"[b]Division Name:[/b] {self.div_name}\n"
            f"[b]Division: Code[/b] {self.division_to_sort_by}\n"
            f"[b]Total Cases:[/b] {total_cases}\n"
            f"[b]Violent Crimes:[/b] Assault\n"
            f"[b]Latest Year:[/b] {latest_year}\n"
            f"[b]Common Crime:[/b] {most_common_crime}\n"
            f"[b]Non-Violent Crime:[/b] Auto Theft\n"

        )
        stats_label = MDLabel(
            text=stats_text,
            halign="left",
            valign='top',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            markup=True,
            size_hint=(1, None),
            height=dp(270),
            padding=(dp(10), dp(10)),
        )
        canvas = FigureCanvasKivyAgg(fig, size_hint=(1, 1))
        card.add_widget(canvas)
        card2.add_widget(stats_label)
        grid.add_widget(card)
        grid.add_widget(card2)

    def menuDialog(self, *args):
        self.dialog = MDDialog(
            title="Menu Options",
            type="custom",
            md_bg_color= get_color_from_hex('#4279a3'),
            pos_hint={"center_y": .85},
            content_cls= MDBoxLayout(
                MDIconButton(
                    text = "Change Theme",
                    theme_text_color="Custom",
                    text_color = "white",
                    icon = "theme-light-dark",
                    on_release=self.change_theme
                ),
                orientation="vertical",
                size_hint_y=None,
                height="60dp"),
        )
        return self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()

    def change_theme(self, *args):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"

    def logout(self, *args):
        self.dialog.dismiss()
        self.manager.current = 'login'


class MapScreen(MDScreen):
    active_tab = "Map"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.divisions = countStats.divisions

    @staticmethod
    def get_marker_color(crimes):
        if crimes > 15000:
            return get_color_from_hex("#FF0000")  # Red
        elif crimes > 10000:
            return get_color_from_hex("#f08a15")  # Orange
        else:
            return get_color_from_hex("#0a7c46")  # Green

    def on_enter(self):
        app = MDApp.get_running_app()
        map_view = self.ids.map_view
        map_view.lat = 43.651070
        map_view.lon = -79.347015
        map_view.zoom = 11


        for division in self.divisions:
            marker = MapMarkerPopup(lat=division["lat"], lon=division["lon"])
            color = self.get_marker_color(division["crimes"])

            label = MDLabel(
                text=f"{division['id']} - {division['name']} ({division['crimes']} crimes)",
                halign="center",
                theme_text_color="Custom",
                text_color=color,
                size_hint_y=None,
                height="40dp"
            )
            marker.add_widget(label)
            map_view.add_widget(marker)


class ProfileScreen(MDScreen):
    username = None
    user_data = None
    profile_image = StringProperty("assets/images/3.jpg")
    fullname = StringProperty('N/A')
    email = StringProperty('N/A')
    phone = StringProperty('N/A')
    street_address = StringProperty('N/A')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.dialog = None


    def on_enter(self, *args):
        app = MDApp.get_running_app()
        self.username = app.user
        self.user_data = app.dtb.getUserData(self.username)
        if self.user_data:
            self.fullname = self.user_data.get('fullname')
            self.email = self.user_data.get('email')
            self.phone = self.user_data.get('phone')
            self.street_address = self.user_data.get('address')
        else:
            return MDSnackbar(MDLabel(text="Failed To Load User Data.",
                               theme_text_color='Custom',
                               text_color="teal")).open()

    def edit_profile(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Edit Profile",
                type="custom",
                content_cls=MDBoxLayout(
                    MDTextField(
                        id="fullname_field",
                        hint_text="Full Name",
                        text=self.fullname,
                    ),
                    MDTextField(
                        id="email_field",
                        hint_text="Email",
                        text=self.email,
                    ),
                    MDTextField(
                        id="phone_field",
                        hint_text="Phone",
                        text=self.phone,
                    ),
                    MDTextField(
                        id="address_field",
                        hint_text="Street Address",
                        text=self.street_address,
                    ),
                    orientation="vertical",
                    spacing="12dp",
                    size_hint_y=None,
                    height="300dp",
                ),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda _: self.dialog.dismiss(),
                    ),
                    MDRaisedButton(
                        text="SAVE",
                        on_release=lambda _: self.save_profile_changes(),
                    ),
                ],
            )
        self.dialog.open()

    def save_profile_changes(self):
        app = MDApp.get_running_app()
        content = self.dialog.content_cls
        new_fullname = content.ids.fullname_field.text

        userConfig['fullname'] = new_fullname
        new_email = content.ids.email_field.text
        userConfig['email'] = new_email
        new_phone = content.ids.phone_field.text
        userConfig['phone'] = new_phone
        new_address = content.ids.address_field.text
        userConfig['address'] = new_address

        if not (new_fullname and new_email and new_phone and new_address):
            MDSnackbar(MDLabel(text="All fields are required.",
                               theme_text_color='Custom',
                               text_color="red")).open()

        try:
            app.dtb.updateUserData(userConfig)
            self.fullname = new_fullname
            self.email = new_email
            self.phone = new_phone
            self.street_address = new_address

            MDSnackbar(MDLabel(text="Profile Update Success.",
                               theme_text_color='Custom',
                               text_color="teal")).open()
        except Exception as _:
            MDSnackbar(MDLabel(text="Failed to update profile.",
                               theme_text_color='Custom',
                               text_color="teal")).open()
        finally:
            self.dialog.dismiss()


class SafeWatchApp(MDApp):
    active_tab = StringProperty('Home')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fbo = None
        self.title = "SAFE WATCH"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Teal"
        self.cache_data = None
        self.user = None
        

    def build(self):
        self.sm = ScreenManager()
        self.dtb = DTB(dbConfig)
        self.load_kv_views()
        self.sm.add_widget(SplashScreen(name='Splash'))
        self.sm.add_widget(LoginScreen())
        self.sm.add_widget(SignUPScreen(name='SignUp'))
        self.sm.add_widget(LandingPageScreen(name='landingPage'))
        self.sm.add_widget(MapScreen(name='Map'))
        self.sm.add_widget(ReportScreen(name='Report'))
        self.sm.add_widget(ProfileScreen(name='Profile'))
        return self.sm

    @staticmethod
    def load_kv_views():
        Builder.load_file('views/main.kv')

    def show_screen(self, screen_name):
        if not self.sm.has_screen(screen_name):
            screen = MDScreen(name=screen_name)
            self.sm.add_widget(screen)
        self.sm.current = screen_name

    def on_start(self):
        Clock.schedule_once(self.login, 3)
        start = time.perf_counter()
        self.get_card_data()
        thread = Thread(target=self.get_card_data)
        thread.start()
        thread.join(timeout=10)



    def on_stop(self):
        self.dtb.close()
        self.clear_fbo()

    def clear_fbo(self):
        self.fbo = None

    def on_pause(self):
        if not self.fbo:
            self.fbo = Fbo(size=self.root_window.size)
        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            self.root_window.canvas.ask_update()
            self.fbo.add(Rectangle(size=self.root_window.size, texture=self.root_window.texture))
        return True

    def on_resume(self):
        if self.fbo:
            with self.root_window.canvas:
                Rectangle(texture=self.fbo.texture, size=self.root_window.size)

    def get_card_data(self, *args):
        try:
            query_results = pd.read_sql_query("SELECT * FROM Crime", self.dtb.dtb)
            if type(query_results) == pd.core.frame.DataFrame:
                self.cache_data = query_results
            else:
                print("False pd.core.frame.DataFrame()")
                exit(1)
        except Exception as e:
            print(e)


    def registerUser(self, fullname, username, email, password, phone, address):
        try:
            if username == "" or password == "":
                MDSnackbar(MDLabel(text="Username or Password can\'t be empty.",
                                   text_color="red",
                                   theme_text_color="Custom")
                           ).open()
            else:
                pwd = hashedPwd(password)
                userConfig['fullname'] = fullname
                userConfig['username'] = username
                userConfig['email'] = email
                userConfig['password'] = password
                userConfig['phone'] = fullname
                userConfig['address'] = address
                self.dtb.insertUserData(userConfig)
                MDSnackbar(MDLabel(text="Registration Success.",
                                   text_color="teal",
                                   theme_text_color="Custom")
                           ).open()

        except Exception as e:
            MDSnackbar(MDLabel(text="Registration Failed.",
                               text_color="teal",
                               theme_text_color="Custom")
                       ).open()
            # Log The Exception to kivy.logger.Logger
        finally:
            self.sm.current = 'login'

    # CALLBACK METHODS
    def ReportPage_callback(self):
        self.active_tab = "Report"
        self.show_screen('Report')

    def MapPage_callback(self):
        self.active_tab = "Map"
        self.show_screen('Map')

    def login(self, *args):
        self.show_screen('login')

    def logout(self, *args):
        self.cache_data = None
        self.user = None
        self.dtb.dtb.close()
        self.show_screen('login')

    def LandingPage_callback(self):
        self.show_screen('landingPage')

    def profile_callback(self):
        self.show_screen('Profile')

    def signup_callback(self):
        self.show_screen('SignUp')


if __name__ == '__main__':
    SafeWatchApp().run()
