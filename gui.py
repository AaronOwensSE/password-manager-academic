# GUI MODULE #

import tkinter
from tkinter import ttk
from tkinter import messagebox

from api import *

# A class representing the GUI for a password manager.
class gui:
    # STATIC DATA

    ## LITERAL SUBSTITUTIONS

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FRAME_WIDTH = 780
    FRAME_HEIGHT = 580
    TITLE_FONT_SIZE = 20

    # USER METHODS

    # Constructor
    # Initializes an API module and a main window.
    def __init__(self):
        self.api = api()
        self.root = self.create_window()

    # Runs the GUI.
    def run(self):
        self.profiles_page()
        self.root.mainloop()
    
    # GENERAL METHODS

    ## GENERAL STATIC METHODS

    # Creates a window using predetermined specifications.
    @staticmethod
    def create_window():
        window = tkinter.Tk()

        window.title("Password Manager")

        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)

        x = int((window.winfo_screenwidth() - gui.WINDOW_WIDTH) / 2)
        y = int((window.winfo_screenheight() - gui.WINDOW_HEIGHT) / 2)
        window.geometry(f"{gui.WINDOW_WIDTH}x{gui.WINDOW_HEIGHT}+{x}+{y}")

        return window

    # Clears a container of all widgets.
    @staticmethod
    def clear_container(container):
        for widget in container.winfo_children():
            widget.destroy()

    # Clears an entry box of text.
    @staticmethod
    def clear_entry(entry):
        entry.delete(0, len(entry.get()))

    # Displays error_message and terminates the program.
    #@staticmethod
    def terminal_error(self, error_message):
        messagebox.showerror("Terminal Error", error_message)
        self.api.log_out()
        exit()

    ## GENERAL INSTANCE METHODS
    
    # Creates a frame with rows rows and cols columns and places it within the root window.
    def create_and_place_frame(self, rows, cols):
        frame = ttk.Frame(self.root, width=gui.FRAME_WIDTH, height=gui.FRAME_HEIGHT, relief="groove", borderwidth=3)

        for i in range(rows):
            frame.rowconfigure(i, weight=1)

        for i in range(cols):
            frame.columnconfigure(i, weight=1)

        frame.grid_propagate(False) # Prevents resizing of frame to size of its contents.
        frame.grid(row=0, column=0)

        return frame

    # PAGE METHODS

    # Displays the profiles page.
    def profiles_page(self):
        self.clear_container(self.root)

        frame = self.create_and_place_frame(6, 3)

        title_label = ttk.Label(frame, text="Profiles")
        title_label.grid(row=0, column=0, columnspan=3)

        profile_tree = ttk.Treeview(frame, columns=("profile_name", "num_platforms", "datetime_added"), selectmode="browse", show="headings")
        profile_tree.heading("profile_name", text="Profile")
        profile_tree.heading("num_platforms", text="Platforms")
        profile_tree.heading("datetime_added", text="Added")

        try:
            profiles = self.api.get_profiles(get_name=True, get_datetime_added=True)
        except fields_not_selected_error as e:
            self.terminal_error(e.error_message())

        for profile in profiles:
            try:
                num_platforms = self.api.get_num_platforms(profile[0])
            except profile_does_not_exist_error as e:
                self.terminal_error(e.error_message())

            profile_tree.insert("", "end", values=(profile[0], num_platforms, profile[1]))

        profile_tree.grid(row=1, column=0, columnspan=3)

        password_label = ttk.Label(frame, text="Password")
        password_label.grid(row=2, column=0, columnspan=3)

        password_entry = ttk.Entry(frame, show="*")
        password_entry.bind("<Return>",
                            lambda event:self.log_in(event,
                                                     profile_tree.set(profile_tree.focus(), 0),
                                                     password_entry.get()))
        password_entry.grid(row=3, column=0, columnspan=3)

        log_in_button = ttk.Button(frame, text="Log In")
        log_in_button.bind("<Button-1>", lambda event:self.log_in(event,
                                                                  profile_tree.set(profile_tree.focus(), 0),
                                                                  password_entry.get()))
        log_in_button.bind("<Return>", lambda event:self.log_in(event,
                                                                profile_tree.set(profile_tree.focus(), 0),
                                                                password_entry.get()), add=True)
        log_in_button.bind("<space>", lambda event:self.log_in(event,
                                                               profile_tree.set(profile_tree.focus(), 0),
                                                               password_entry.get()), add=True)
        log_in_button.grid(row=4, column=0, columnspan=3)

        add_profile_button = ttk.Button(frame, text="Add Profile")
        add_profile_button.bind("<Button-1>", self.go_to_add_profile_page)
        add_profile_button.bind("<Return>", self.go_to_add_profile_page, add=True)
        add_profile_button.bind("<space>", self.go_to_add_profile_page, add=True)
        add_profile_button.grid(row=5, column=0)

        change_password_button = ttk.Button(frame, text="Change Password")
        change_password_button.bind("<Button-1>", lambda event:self.go_to_change_password_page(event,
                                                                                               profile_tree.set(profile_tree.focus(), 0)))
        change_password_button.bind("<Return>", lambda event:self.go_to_change_password_page(event,
                                                                                             profile_tree.set(profile_tree.focus(), 0)), add=True)
        change_password_button.bind("<space>", lambda event:self.go_to_change_password_page(event,
                                                                                            profile_tree.set(profile_tree.focus(), 0)), add=True)
        change_password_button.grid(row=5, column=1)

        delete_profile_button = ttk.Button(frame, text="Delete Profile")
        delete_profile_button.bind("<Button-1>", lambda event:self.delete_profile(event,
                                                                                  profile_tree.set(profile_tree.focus(), 0),
                                                                                  password_entry.get()))
        delete_profile_button.bind("<Return>", lambda event:self.delete_profile(event,
                                                                                profile_tree.set(profile_tree.focus(), 0),
                                                                                password_entry.get()), add=True)
        delete_profile_button.bind("<space>", lambda event:self.delete_profile(event,
                                                                               profile_tree.set(profile_tree.focus(), 0),
                                                                               password_entry.get()), add=True)
        delete_profile_button.grid(row=5, column=2)

    # Displays the add profile page.
    def add_profile_page(self):
        self.clear_container(self.root)

        frame = self.create_and_place_frame(9, 3)

        title_label = ttk.Label(frame, text="Add Profile")
        title_label.grid(row=0, column=0, columnspan=3)

        profile_name_label = ttk.Label(frame, text="Profile Name")
        profile_name_label.grid(row=1, column=0, columnspan=3)

        profile_name_entry = ttk.Entry(frame)
        profile_name_entry.bind("<Return>", lambda event:self.add_profile(event,
                                                                          profile_name_entry.get(),
                                                                          password_1_entry.get(),
                                                                          password_2_entry.get()))
        profile_name_entry.grid(row=2, column=0, columnspan=3)

        password1_label = ttk.Label(frame, text="Password")
        password1_label.grid(row=3, column=0, columnspan=3)

        password_1_entry = ttk.Entry(frame, show="*")
        password_1_entry.bind("<Return>", lambda event:self.add_profile(event,
                                                                        profile_name_entry.get(),
                                                                        password_1_entry.get(),
                                                                        password_2_entry.get()))
        password_1_entry.grid(row=4, column=0, columnspan=3)

        password_2_label = ttk.Label(frame, text="Confirm Password")
        password_2_label.grid(row=5, column=0, columnspan=3)

        password_2_entry = ttk.Entry(frame, show="*")
        password_2_entry.bind("<Return>", lambda event:self.add_profile(event,
                                                                        profile_name_entry.get(),
                                                                        password_1_entry.get(),
                                                                        password_2_entry.get()))
        password_2_entry.grid(row=6, column=0, columnspan=3)

        add_profile_button = ttk.Button(frame, text="Add Profile")
        add_profile_button.bind("<Button-1>", lambda event:self.add_profile(event,
                                                                            profile_name_entry.get(),
                                                                            password_1_entry.get(),
                                                                            password_2_entry.get()))
        add_profile_button.bind("<Return>", lambda event:self.add_profile(event,
                                                                          profile_name_entry.get(),
                                                                          password_1_entry.get(),
                                                                          password_2_entry.get()), add=True)
        add_profile_button.bind("<space>", lambda event:self.add_profile(event,
                                                                         profile_name_entry.get(),
                                                                         password_1_entry.get(),
                                                                         password_2_entry.get()), add=True)
        add_profile_button.grid(row=7, column=0, columnspan=3)

        back_button = ttk.Button(frame, text="Back")
        back_button.bind("<Button-1>", self.go_to_profiles_page)
        back_button.bind("<Return>", self.go_to_profiles_page, add=True)
        back_button.bind("<space>", self.go_to_profiles_page, add=True)
        back_button.grid(row=8, column=0)
    
    # Displays the change (profile) password page.
    def change_password_page(self, profile_name):
        self.clear_container(self.root)

        frame = self.create_and_place_frame(9, 3)

        title_label = ttk.Label(frame, text="Change Password for Profile " + profile_name)
        title_label.grid(row=0, column=0, columnspan=3)

        current_password_label = ttk.Label(frame, text="Current Password")
        current_password_label.grid(row=1, column=0, columnspan=3)

        current_password_entry = ttk.Entry(frame, show="*")
        current_password_entry.bind("<Return>", lambda event:self.change_profile_password(event,
                                                                                          profile_name,
                                                                                          current_password_entry.get(),
                                                                                          new_password_1_entry.get(),
                                                                                          new_password_2_entry.get()))
        current_password_entry.grid(row=2, column=0, columnspan=3)

        new_password_1_label = ttk.Label(frame, text="New Password")
        new_password_1_label.grid(row=3, column=0, columnspan=3)

        new_password_1_entry = ttk.Entry(frame, show="*")
        new_password_1_entry.bind("<Return>", lambda event:self.change_profile_password(event,
                                                                                        profile_name,
                                                                                        current_password_entry.get(),
                                                                                        new_password_1_entry.get(),
                                                                                        new_password_2_entry.get()))
        new_password_1_entry.grid(row=4, column=0, columnspan=3)

        new_password_2_label = ttk.Label(frame, text="Confirm New Password")
        new_password_2_label.grid(row=5, column=0, columnspan=3)

        new_password_2_entry = ttk.Entry(frame, show="*")
        new_password_2_entry.bind("<Return>", lambda event:self.change_profile_password(event,
                                                                                        profile_name,
                                                                                        current_password_entry.get(),
                                                                                        new_password_1_entry.get(),
                                                                                        new_password_2_entry.get()))
        new_password_2_entry.grid(row=6, column=0, columnspan=3)

        change_password_button = ttk.Button(frame, text="Change Password")
        change_password_button.bind("<Button-1>", lambda event:self.change_profile_password(event,
                                                                                            profile_name,
                                                                                            current_password_entry.get(),
                                                                                            new_password_1_entry.get(),
                                                                                            new_password_2_entry.get()), add=True)
        change_password_button.bind("<Return>", lambda event:self.change_profile_password(event,
                                                                                          profile_name,
                                                                                          current_password_entry.get(),
                                                                                          new_password_1_entry.get(),
                                                                                          new_password_2_entry.get()), add=True)
        change_password_button.bind("<space>", lambda event:self.change_profile_password(event,
                                                                                         profile_name,
                                                                                         current_password_entry.get(),
                                                                                         new_password_1_entry.get(),
                                                                                         new_password_2_entry.get()), add=True)
        change_password_button.grid(row=7, column=0, columnspan=3)

        back_button = ttk.Button(frame, text="Back")
        back_button.bind("<Button-1>", self.go_to_profiles_page)
        back_button.bind("<Return>", self.go_to_profiles_page, add=True)
        back_button.bind("<space>", self.go_to_profiles_page, add=True)
        back_button.grid(row=8, column=0)
    
    # Displays the dashboard page for the currently logged in profile.
    def dashboard_page(self):
        self.clear_container(self.root)

        frame = self.create_and_place_frame(8, 3)

        title_label = ttk.Label(frame, text="Dashboard")
        title_label.grid(row=0, column=0, columnspan=3)

        welcome_label = ttk.Label(frame, text="Welcome, " + self.api.profile_name + "! Profile created on " + self.api.profile_datetime_added + ".")
        welcome_label.grid(row=1, column=0, columnspan=3)

        platform_tree = ttk.Treeview(frame,
                                     columns=("platform_name", "platform_location", "platform_datetime_added"),
                                     selectmode="browse",
                                     show="headings")
        platform_tree.heading("platform_name", text="Platform")
        platform_tree.heading("platform_location", text="Location")
        platform_tree.heading("platform_datetime_added", text="Added")

        try:
            platforms = self.api.get_platforms(get_name=True, get_username=True, get_password=True, get_location=True, get_datetime_added=True)
        except (profile_not_logged_in_error, fields_not_selected_error) as e:
            self.terminal_error(e.error_message())

        for platform in platforms:
            platform_tree.insert("", "end", values=(platform[0], platform[3], platform[4]))

        platform_tree.grid(row=2, column=0, columnspan=3)

        location_label = ttk.Label(frame, text="Location")
        location_label.grid(row=3, column=0)

        username_label = ttk.Label(frame, text="Username")
        username_label.grid(row=3, column=1)

        password_label = ttk.Label(frame, text="Password")
        password_label.grid(row=3, column=2)

        location_entry = ttk.Entry(frame)
        location_entry.grid(row=4, column=0)

        username_entry = ttk.Entry(frame)
        username_entry.grid(row=4, column=1)

        password_entry = ttk.Entry(frame)
        password_entry.grid(row=4, column=2)

        show_data_button = ttk.Button(frame, text="Show Data")
        show_data_button.bind("<Button-1>", lambda event:self.show_platform_data(event,
                                                                                 platform_tree.set(platform_tree.focus(), 0),
                                                                                 location_entry,
                                                                                 username_entry,
                                                                                 password_entry))
        show_data_button.bind("<Return>", lambda event:self.show_platform_data(event,
                                                                               platform_tree.set(platform_tree.focus(), 0),
                                                                               location_entry,
                                                                               username_entry,
                                                                               password_entry), add=True)
        show_data_button.bind("<space>", lambda event:self.show_platform_data(event,
                                                                              platform_tree.set(platform_tree.focus(), 0),
                                                                              location_entry,
                                                                              username_entry,
                                                                              password_entry), add=True)
        show_data_button.grid(row=5, column=0)

        clear_data_button = ttk.Button(frame, text="Clear Data")
        clear_data_button.bind("<Button-1>", lambda event:self.clear_platform_data(event,
                                                                                   location_entry,
                                                                                   username_entry,
                                                                                   password_entry))
        clear_data_button.bind("<Return>", lambda event:self.clear_platform_data(event,
                                                                                 location_entry,
                                                                                 username_entry,
                                                                                 password_entry), add=True)
        clear_data_button.bind("<space>", lambda event:self.clear_platform_data(event,
                                                                                location_entry,
                                                                                username_entry,
                                                                                password_entry), add=True)
        clear_data_button.grid(row=5, column=2)

        add_platform_button = ttk.Button(frame, text="Add Platform")
        add_platform_button.bind("<Button-1>", self.go_to_add_platform_page)
        add_platform_button.bind("<Return>", self.go_to_add_platform_page, add=True)
        add_platform_button.bind("<space>", self.go_to_add_platform_page, add=True)
        add_platform_button.grid(row=6, column=0)

        modify_platform_button = ttk.Button(frame, text="Modify Platform")
        modify_platform_button.bind("<Button-1>", lambda event: self.go_to_platform_page(event,
                                                                                         platform_tree.set(platform_tree.focus(), 0)))
        modify_platform_button.bind("<Return>", lambda event: self.go_to_platform_page(event,
                                                                                       platform_tree.set(platform_tree.focus(), 0)), add=True)
        modify_platform_button.bind("<space>", lambda event: self.go_to_platform_page(event,
                                                                                      platform_tree.set(platform_tree.focus(), 0)), add=True)
        modify_platform_button.grid(row=6, column=1)

        delete_platform_button = ttk.Button(frame, text="Delete Platform")
        delete_platform_button.bind("<Button-1>", lambda event: self.delete_platform(event,
                                                                                     platform_tree.set(platform_tree.focus(), 0)))
        delete_platform_button.bind("<Return>", lambda event: self.delete_platform(event,
                                                                                   platform_tree.set(platform_tree.focus(), 0)), add=True)
        delete_platform_button.bind("<space>", lambda event: self.delete_platform(event,
                                                                                  platform_tree.set(platform_tree.focus(), 0)), add=True)
        delete_platform_button.grid(row=6, column=2)

        log_out_button = ttk.Button(frame, text="Log Out")
        log_out_button.bind("<Button-1>", self.log_out)
        log_out_button.bind("<Return>", self.log_out, add=True)
        log_out_button.bind("<space>", self.log_out, add=True)
        log_out_button.grid(row=7, column=2)
    
    # Displays the add platform page for the currently logged in profile.
    def add_platform_page(self):
        self.clear_container(self.root)

        frame = self.create_and_place_frame(7, 3)

        title_label = ttk.Label(frame, text="Add Platform")
        title_label.grid(row=0, column=0, columnspan=3)

        platform_name_label = ttk.Label(frame, text="Name")
        platform_name_label.grid(row=1, column=0, columnspan=3)
        platform_name_entry = ttk.Entry(frame)
        platform_name_entry.bind("<Return>", lambda event: self.add_platform(event,
                                                                             platform_name_entry.get(),
                                                                             platform_location_entry.get()))
        platform_name_entry.grid(row=2, column=0, columnspan=3)

        platform_location_label = ttk.Label(frame, text="Location")
        platform_location_label.grid(row=3, column=0, columnspan=3)
        platform_location_entry = ttk.Entry(frame)
        platform_location_entry.bind("<Return>", lambda event: self.add_platform(event,
                                                                                 platform_name_entry.get(),
                                                                                 platform_location_entry.get()))
        platform_location_entry.grid(row=4, column=0, columnspan=3)

        add_platform_button = ttk.Button(frame, text="Add Platform")
        add_platform_button.bind("<Button-1>", lambda event: self.add_platform(event,
                                                                               platform_name_entry.get(),
                                                                               platform_location_entry.get()))
        add_platform_button.bind("<Return>", lambda event: self.add_platform(event,
                                                                             platform_name_entry.get(),
                                                                             platform_location_entry.get()), add=True)
        add_platform_button.bind("<space>", lambda event: self.add_platform(event,
                                                                            platform_name_entry.get(),
                                                                            platform_location_entry.get()), add=True)
        add_platform_button.grid(row=5, column=0, columnspan=3)

        back_button = ttk.Button(frame, text="Back")
        back_button.bind("<Button-1>", self.go_to_dashboard_page)
        back_button.bind("<Return>", self.go_to_dashboard_page, add=True)
        back_button.bind("<space>", self.go_to_dashboard_page, add=True)
        back_button.grid(row=6, column=0)

        log_out_button = ttk.Button(frame, text="Log Out")
        log_out_button.bind("<Button-1>", self.log_out)
        log_out_button.bind("<Return>", self.log_out, add=True)
        log_out_button.bind("<space>", self.log_out, add=True)
        log_out_button.grid(row=6, column=2)
    
    # Displays the platform page for platform_name for the currently logged in profile.
    def platform_page(self, platform_name):
        try:
            platform = self.api.get_platform(platform_name, get_username=True, get_password=True, get_salt=True, get_location=True)    # Do we want to return encrypted or unencrypted? 2nd func for both?
        except (profile_not_logged_in_error, platform_does_not_exist_error, fields_not_selected_error) as e:
            self.terminal_error(e.error_message())

        self.clear_container(self.root)

        frame = self.create_and_place_frame(5, 3)

        platform_name_label = ttk.Label(frame, text="Platform: " + platform_name)
        platform_name_label.grid(row=0, column=0, columnspan=3)
        
        two_column_subframe = ttk.Frame(frame)
        two_column_subframe.rowconfigure(0, weight=1)
        two_column_subframe.columnconfigure(0, weight=1)
        two_column_subframe.columnconfigure(1, weight=1)
        two_column_subframe.rowconfigure(1, weight=1)
        two_column_subframe.rowconfigure(2, weight=1)
        two_column_subframe.rowconfigure(3, weight=1)
        two_column_subframe.grid(row=1, column=0, columnspan=3)

        location_label = ttk.Label(two_column_subframe, text="Location")
        location_label.grid(row=0, column=0)

        password_label = ttk.Label(two_column_subframe, text="Password")
        password_label.grid(row=0, column=1)

        location_entry = ttk.Entry(two_column_subframe)

        # Location is the only field that can be empty in the database. Passing None to insert causes error.
        if (platform[3]):
            location_entry.insert(0, platform[3])
        else:
            location_entry.insert(0, "")

        location_entry.bind("<Return>", lambda event: self.update_platform(event,
                                                                           platform_name,
                                                                           location_entry.get(),
                                                                           username_entry.get(),
                                                                           password_entry.get()))
        location_entry.grid(row=1, column=0)

        password_entry = ttk.Entry(two_column_subframe)
        password_entry.insert(0, decrypt(platform[1], derived_key(self.api.profile_password, platform[2])))
        password_entry.bind("<Return>", lambda event: self.update_platform(event,
                                                                           platform_name,
                                                                           location_entry.get(),
                                                                           username_entry.get(),
                                                                           password_entry.get()))
        password_entry.grid(row=1, column=1)

        username_label = ttk.Label(two_column_subframe, text="Username")
        username_label.grid(row=2, column=0)

        three_column_subframe = ttk.Frame(two_column_subframe)
        three_column_subframe.rowconfigure(0, weight=1)
        three_column_subframe.columnconfigure(0, weight=1)
        three_column_subframe.columnconfigure(1, weight=1)
        three_column_subframe.columnconfigure(2, weight=1)
        three_column_subframe.grid(row=2, column=1)

        letters = tkinter.IntVar()
        letters_checkbutton = ttk.Checkbutton(three_column_subframe, variable=letters, text="Letters")
        letters_checkbutton.grid(row=0, column=0)

        digits = tkinter.IntVar()
        digits_checkbutton = ttk.Checkbutton(three_column_subframe, variable=digits, text="Digits")
        digits_checkbutton.grid(row=0, column=1)

        punctuation = tkinter.IntVar()
        punctuation_checkbutton = ttk.Checkbutton(three_column_subframe, variable=punctuation, text="Punctuation")
        punctuation_checkbutton.grid(row=0, column=2)

        username_entry = ttk.Entry(two_column_subframe)
        username_entry.insert(0, decrypt(platform[0], derived_key(self.api.profile_password, platform[2])))
        username_entry.bind("<Return>", lambda event: self.update_platform(event,
                                                                           platform_name,
                                                                           location_entry.get(),
                                                                           username_entry.get(),
                                                                           password_entry.get()))
        username_entry.grid(row=3, column=0)

        randomize_button = ttk.Button(two_column_subframe, text="Randomize")
        randomize_button.bind("<Button-1>", lambda event: self.randomize_password(event,
                                                                                  password_entry,
                                                                                  letters.get(),
                                                                                  digits.get(),
                                                                                  punctuation.get()))
        randomize_button.bind("<Return>", lambda event: self.randomize_password(event,
                                                                                password_entry,
                                                                                letters.get(),
                                                                                digits.get(),
                                                                                punctuation.get()), add=True)
        randomize_button.bind("<space>", lambda event: self.randomize_password(event,
                                                                               password_entry,
                                                                               letters.get(),
                                                                               digits.get(),
                                                                               punctuation.get()), add=True)
        randomize_button.grid(row=3, column=1)

        update_button = ttk.Button(frame, text="Update")
        update_button.bind("<Button-1>", lambda event: self.update_platform(event,
                                                                            platform_name,
                                                                            location_entry.get(),
                                                                            username_entry.get(),
                                                                            password_entry.get()))
        update_button.bind("<Return>", lambda event: self.update_platform(event,
                                                                          platform_name,
                                                                          location_entry.get(),
                                                                          username_entry.get(),
                                                                          password_entry.get()), add=True)
        update_button.bind("<space>", lambda event: self.update_platform(event,
                                                                         platform_name,
                                                                         location_entry.get(),
                                                                         username_entry.get(),
                                                                         password_entry.get()), add=True)
        update_button.grid(row=4, column=0, columnspan=3)

        back_button = ttk.Button(frame, text="Back")
        back_button.bind("<Button-1>", self.go_to_dashboard_page)
        back_button.bind("<Return>", self.go_to_dashboard_page)
        back_button.bind("<space>", self.go_to_dashboard_page)
        back_button.grid(row=5, column=0)

        logout_button = ttk.Button(frame, text="Log Out")
        logout_button.bind("<Button-1>", self.log_out)
        logout_button.bind("<Return>", self.log_out)
        logout_button.bind("<space>", self.log_out)
        logout_button.grid(row=5, column=2)
    
    # EVENT HANDLERS

    ## STATIC EVENT HANDLERS

    # Clears text from location_entry, username_entry, and password_entry entry boxes.
    @staticmethod
    def clear_platform_data(event, location_entry, username_entry, password_entry):
        gui.clear_entry(location_entry)
        gui.clear_entry(username_entry)
        gui.clear_entry(password_entry)
    
    # Creates a random platform password string in entry box password_entry, according to provided options.
    @staticmethod
    def randomize_password(event, password_entry, letters, digits, punctuation):
        if (letters or digits or punctuation):
            gui.clear_entry(password_entry)
            password_entry.insert(0, secure_random_string(api.PLATFORM_PASSWORD_LENGTH, letters, digits, punctuation))
        else:
            messagebox.showerror("Error", "Select at least one password option.")

    ## INSTANCE EVENT HANDLERS

    # Proceeds to profiles page (avoids passing event directly to the page).
    def go_to_profiles_page(self, event):
        self.profiles_page()
    
    # Proceeds to change password page for profile profile_name (avoids passing event directly to the page).
    def go_to_change_password_page(self, event, profile_name):
        if (not self.api.profile_name_available(profile_name)):
            self.change_password_page(profile_name)
        else:
            messagebox.showerror("Error", "No profile is selected.")
    
    # Proceeds to add profile page (avoids passing event directly to the page).
    def go_to_add_profile_page(self, event):
        self.add_profile_page()
    
    # Proceeds to dashboard page (avoids passing event directly to the page).
    def go_to_dashboard_page(self, event):
        self.dashboard_page()
    
    # Proceeds to add platform page (avoids passing event directly to the page).
    def go_to_add_platform_page(self, event):
        self.add_platform_page()
    
    # Proceeds to platform page for platform_name (avoids passing event directly to the page).
    def go_to_platform_page(self, event, platform_name):
        try:
            if (not self.api.platform_name_available(platform_name)):
                self.platform_page(platform_name)
            else:
                messagebox.showerror("Error", "No platform is selected.")
        except profile_not_logged_in_error as e:
            self.terminal_error(e.error_message())

    # Logs into profile_name using password and proceeds to dashboard page.
    def log_in(self, event, profile_name, password):
        try:
            self.api.log_in(profile_name, password)
            self.dashboard_page()
        except (profile_does_not_exist_error) as e:
            messagebox.showerror("Error", "No profile is selected.")
        except (invalid_credentials_error) as e:
            messagebox.showerror("Error", e.error_message())    # Should this be handled via Boolean return instead?

    # Logs out and proceeds to profiles page.
    def log_out(self, event):
        self.api.log_out()
        self.profiles_page()
    
    # Attempts to add profile_name after matching password_1 to password_2 and proceed to profiles page.
    def add_profile(self, event, profile_name, password_1, password_2):
        if (passwords_match(password_1, password_2)):
            try:
                self.api.add_profile(profile_name, password_1)
                self.profiles_page()
            except (profile_name_invalid_error, profile_password_invalid_error, profile_name_unavailable_error) as e:
                messagebox.showerror("Error", e.error_message())
        else:
            messagebox.showerror("Error", "Passwords do not match.")

    # Attempts to change password for profile_name and proceed to profiles page after matching password_1 to password_2 and checking current_password.
    def change_profile_password(self, event, profile_name, current_password, password_1, password_2):
        if (passwords_match(password_1, password_2)):
            try:
                self.api.update_profile(profile_name, current_password, new_password=password_1)
                self.profiles_page()
            except (profile_does_not_exist_error, fields_not_selected_error) as e:
                self.terminal_error(e.error_message())
            except (invalid_credentials_error, profile_password_invalid_error) as e:
                messagebox.showerror("Error", e.error_message())
        else:
            messagebox.showerror("Error", "Passwords do not match.")

    # Attempts to delete profile_name using password and proceed to profiles page.
    def delete_profile(self, event, profile_name, password):
        response = messagebox.askyesno("Delete Profile", "Are you sure you want to delete " + profile_name + "?")

        if (response):
            try:
                self.api.delete_profile(profile_name, password)
                self.profiles_page()
            except profile_does_not_exist_error as e:
                messagebox.showerror("Error", "No profile is selected.")
            except deleting_current_profile_error as e:
                self.terminal_error(e.error_message())   # Will this terminate when no profile is selected? Logged out, so current profile = "".
            except invalid_credentials_error as e:
                messagebox.showerror("Error", e.error_message())

    # Inserts location, username, and password data for platform_name into their respective entry boxes for the currently logged in profile.
    def show_platform_data(self, event, platform_name, location_entry, username_entry, password_entry):
        try:
            if (not self.api.platform_name_available(platform_name)):
                gui.clear_entry(location_entry)
                gui.clear_entry(username_entry)
                gui.clear_entry(password_entry)

                try:
                    platform = self.api.get_platform(platform_name, get_username=True, get_password=True, get_salt=True, get_location=True)
                except (profile_not_logged_in_error, platform_does_not_exist_error, fields_not_selected_error) as e:
                    self.terminal_error(e.error_message())

                location_entry.insert(0, platform[3])
                username_entry.insert(0, decrypt(platform[0], derived_key(self.api.profile_password, platform[2])))
                password_entry.insert(0, decrypt(platform[1], derived_key(self.api.profile_password, platform[2])))
            else:
                messagebox.showerror("Error", "No platform is selected.")
        except (profile_not_logged_in_error) as e:
            self.terminal_error(e.error_message())

    # Attempts to add platform platform_name with location data platform_location for the currently logged in profile.
    def add_platform(self, event, platform_name, platform_location):
        try:
            self.api.add_platform(platform_name, location=platform_location)
            self.platform_page(platform_name)
        except (profile_not_logged_in_error) as e:
            self.terminal_error(e.error_message())
        except (platform_name_invalid_error, platform_name_unavailable_error) as e:
            messagebox.showerror("Error", e.error_message())

    # Attempts to update platform_name with location, username, and password data for the currently logged in profile.
    def update_platform(self, event, platform_name, location, username, password):  # reorder args
        try:
            self.api.update_platform(platform_name, new_username=username, new_password=password, new_location=location)
            self.dashboard_page()
        except (profile_not_logged_in_error, fields_not_selected_error) as e:
            self.terminal_error(e.error_message())
        except platform_does_not_exist_error as e:
            messagebox.showerror("Error", "No platform is selected.")

    # Attempts to delete platform_name from the currently logged in profile.
    def delete_platform(self, event, platform_name):
        response = messagebox.askyesno("Delete Platform", "Are you sure you want to delete " + platform_name + "?") # Possible to get message when no platform selected. If this is fixed, error message below needs to change too.

        if (response):
            try:
                self.api.delete_platform(platform_name)
                self.dashboard_page()
            except profile_not_logged_in_error as e:
                self.terminal_error(e.error_message())
            except platform_does_not_exist_error as e:
                messagebox.showerror("Error", "No platform is selected.")
