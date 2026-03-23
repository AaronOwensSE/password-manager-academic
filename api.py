# API MODULE #

from database_tools import *
from security_tools import *

# A class representing the API for a password manager.
class api:
    # STATIC DATA

    ## LITERAL SUBSTITUTIONS

    PROFILE_NAME_MIN_LENGTH = 4
    PROFILE_PASSWORD_MIN_LENGTH = 4
    PLATFORM_NAME_MIN_LENGTH = 4
    PLATFORM_PASSWORD_LENGTH = 32

    # STATIC METHODS

    # Determines if name is in a valid format for a profile name.
    @staticmethod
    def profile_name_valid(name):
        return len(name) >= api.PROFILE_NAME_MIN_LENGTH

    # Determines if password is in a valid format for a profile password.
    @staticmethod
    def profile_password_valid(password):
        return len(password) >= api.PROFILE_PASSWORD_MIN_LENGTH

    # Determines if name is in a valid format for a platform name.
    @staticmethod
    def platform_name_valid(name):
        return len(name) >= api.PLATFORM_NAME_MIN_LENGTH
    
    # Builds a comma-separated string from list of strings string_list.
    @staticmethod
    def build_comma_string(string_list):
        length = len(string_list)
        comma_string = ""

        for i in range(length):
            comma_string += string_list[i]

            if (i < length - 1):
                comma_string += ", "
        
        return comma_string
    
    # INSTANCE METHODS

    ## CREATION/DELETION METHODS

    # Constructor
    # Initializes data members, establishes database interaction tools, and creates database if none is found.
    def __init__(self):
        self.log_out()

        self.db_connection = connect_to_db(DB_RELATIVE_PATH)    # Database connection
        self.db_cursor = self.db_connection.cursor()            # Database cursor

        self.create_db()       # Creates DB if none is found.
        #self.populate_db()     # Uncomment on first use to populate test DB.

    # Destructor
    # Logs out and closes database connection.
    def __del__(self):
        self.log_out()
        self.db_connection.close()

    ## DATABASE SETUP METHODS

    # Creates a clean database if it does not already exist.
    def create_db(self):
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS profile ("
                        + "name TEXT PRIMARY KEY, "
                        + "password TEXT, "
                        + "salt TEXT, "
                        + "datetime_added INTEGER"
                        + ");")
        self.db_connection.commit()

        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS platform ("
                        + "name TEXT, "
                        + "for_profile TEXT REFERENCES profile(name) ON UPDATE CASCADE ON DELETE CASCADE, "
                        + "username TEXT, "
                        + "password TEXT, "
                        + "salt TEXT, "
                        + "location TEXT, "
                        + "datetime_added INTEGER, "
                        + "PRIMARY KEY(name, for_profile)"
                        + ");")
        self.db_connection.commit()

    # Populates the database with test values.
    def populate_db(self):
        self.add_profile("root", "doot")
        self.log_in("root", "doot")
        self.add_platform("Tax Program",
                          username="mytaxes1234",
                          password=secure_random_string(api.PLATFORM_PASSWORD_LENGTH),
                          location="C:\\stuff\\TaxProgram.exe")
        self.add_platform("My Bank Account",
                          username="mybanking555",
                          password=secure_random_string(api.PLATFORM_PASSWORD_LENGTH),
                          location="bankybank.com")
        self.add_platform("Video Games",
                          username="funandgames789",
                          password=secure_random_string(api.PLATFORM_PASSWORD_LENGTH),
                          location="vidyagames.com")
        self.log_out()

    ## ERROR METHODS

    def terminal_error(self, error_message):
        print("Error: " + error_message)
        self.log_out()
        exit()

    ## PROFILE METHODS

    # Logs into profile name, requiring password.
    # Raises profile_does_not_exist_error and invalid_credentials_error.
    def log_in(self, name, password):
        self.log_out()

        if (not self.profile_name_available(name)):
            if (self.validate_credentials(name, password)):
                self.logged_in = True
                self.profile_name = name

                profile = self.db_cursor.execute("SELECT datetime_added FROM profile WHERE name=?", [name]).fetchall()

                self.profile_datetime_added = profile[0][0]
                self.profile_password = password
            else:
                raise invalid_credentials_error
        else:
            raise profile_does_not_exist_error

    # Logs out any currently logged in profile out and clears profile-specific data members.
    def log_out(self):
        self.logged_in = False
        self.profile_name = ""
        self.profile_datetime_added = ""
        self.profile_password = ""
    
    # Determines if name and password are valid credentials for an existing profile.
    def validate_credentials(self, name, password):
        profile = self.db_cursor.execute("SELECT salt, password FROM profile WHERE name=?",
                                         [name]).fetchall()

        if (len(profile) > 0):
            hash = salted_hash(password, profile[0][0])

            return hash == profile[0][1]
        else:
            return False
    
    # Retrieves all profiles in the database with selected fields included.
    # As a design choice, this information is available to the user without login so that it may be displayed on a login page.
    # Raises fields_not_selected_error.
    def get_profiles(self, *, get_name=False, get_datetime_added=False):
        fields = []

        if get_name:
            fields.append("name")
        
        if get_datetime_added:
            fields.append("datetime_added")
        
        if (len(fields) > 0):
            sql = "SELECT " + api.build_comma_string(fields) + " FROM profile"
            profiles = self.db_cursor.execute(sql).fetchall()

            return profiles
        else:
            raise fields_not_selected_error
    
    # Returns the number of platforms associated with profile_name.
    # As a design choice, this information is available to the user without login so that it may be displayed on a login page.
    # Raises profile_does_not_exist_error.
    def get_num_platforms(self, profile_name):
        if (not self.profile_name_available(profile_name)):
            platforms = self.db_cursor.execute("SELECT name FROM platform WHERE for_profile=?", [profile_name]).fetchall()  # Is there a better query for this? Needlessly returning names.

            return len(platforms)
        else:
            raise profile_does_not_exist_error
        
    # Adds a profile consisting of name and password to the database.
    # Raises profile_name_invalid_error, profile_password_invalid_error, and profile_name_unavailable_error.
    def add_profile(self, name, password):
        if (api.profile_name_valid(name)):
            if (api.profile_password_valid(password)):
                if (self.profile_name_available(name)):
                    salt = secure_random_string(SALT_LENGTH)
                    hash = salted_hash(password, salt)

                    self.db_cursor.execute("INSERT INTO profile (name, password, salt, datetime_added) "
                                            + "VALUES (?, ?, ?, datetime(datetime(), 'localtime'));",
                                            [name, hash, salt])
                    self.db_connection.commit()
                else:
                    raise profile_name_unavailable_error
            else:
                raise profile_password_invalid_error
        else:
             raise profile_name_invalid_error
    
    # Updates selected fields in the database for profile name, requiring profile password.
    # Raises fields_not_selected_error, profile_password_invalid_error, profile_does_not_exist_error, invalid_credentials_error.
    def update_profile(self, name, password, *, new_password=False):
        if (new_password or new_password == ""):    # Very important to catch empty strings here so that correct error can be thrown.
            if (api.profile_password_valid(new_password)):
                self.log_in(name, password) # Pass profile_does_not_exist_error and invalid_credentials_error to update_profile caller.

                # Can't use update_platform here.
                # It will use the current key to encrypt platform passwords.
                new_profile_salt = secure_random_string(SALT_LENGTH)
                new_hash = salted_hash(new_password, new_profile_salt)
                #new_key = derived_key(new_password, new_profile_salt)

                try:
                    platforms = self.get_platforms(get_name=True, get_username=True, get_password=True, get_salt=True)    # Do not pass get_platforms exceptions to update_profile caller.
                except (profile_not_logged_in_error, fields_not_selected_error) as e:
                    self.terminal_error(e.error_message())

                for platform in platforms:
                    new_platform_salt = secure_random_string(SALT_LENGTH)
                    new_platform_key = derived_key(new_password, new_platform_salt)

                    platform_username = decrypt(platform[1], derived_key(self.profile_password, platform[3]))
                    new_encrypted_platform_username = encrypt(platform_username, new_platform_key)

                    platform_password = decrypt(platform[2], derived_key(self.profile_password, platform[3]))
                    new_encrypted_platform_password = encrypt(platform_password, new_platform_key)

                    self.db_cursor.execute("UPDATE platform SET username=?, password=?, salt=? WHERE name=? AND for_profile=?",
                                            [new_encrypted_platform_username, new_encrypted_platform_password, new_platform_salt, platform[0], self.profile_name])

                self.db_cursor.execute("UPDATE profile SET password=?, salt=? WHERE name=?",
                                        [new_hash, new_profile_salt, self.profile_name])
                self.db_connection.commit()

                self.profile_password = new_password

                self.log_out()
            else:
                raise profile_password_invalid_error
        else:
            raise fields_not_selected_error

    # Deletes profile name from database, requiring password.
    # Raises profile_does_not_exist_error, deleting_current_profile_error, and invalid_credentials_error.
    def delete_profile(self, name, password):
        if (not self.profile_name_available(name)):
            if (name != self.profile_name):
                if (self.validate_credentials(name, password)):
                    self.db_cursor.execute("DELETE FROM platform WHERE for_profile=?", [name])
                    self.db_cursor.execute("DELETE FROM profile WHERE name=?", [name])
                    self.db_connection.commit()
                else:
                    raise invalid_credentials_error
            else:
                raise deleting_current_profile_error
        else:
            raise profile_does_not_exist_error
    
    # Determines if profile name is available.
    def profile_name_available(self, name):
        profile = self.db_cursor.execute("SELECT name FROM profile WHERE name=?",
                                         [name]).fetchall()
        
        return len(profile) == 0

    ## PLATFORM METHODS

    # Retrieves selected fields from the database for platform name for the currently logged in profile.
    # Raises profile_not_logged_in_error, platform_does_not_exist_error, and fields_not_selected_error.
    def get_platform(self, name, *, get_name=False, get_username=False, get_password=False, get_salt=False, get_location=False, get_datetime_added=False):
        if (self.logged_in):
            if (not self.platform_name_available(name)):
                fields = []

                if (get_name):
                    fields.append("name")

                if (get_username):
                    fields.append("username")
                
                if (get_password):
                    fields.append("password")

                if (get_salt):
                    fields.append("salt")

                if (get_location):
                    fields.append("location")

                if (get_datetime_added):
                    fields.append("datetime_added")
                
                if (len(fields) > 0):
                    sql = "SELECT " + api.build_comma_string(fields) + " FROM platform WHERE name=? AND for_profile=?"
                    platform = self.db_cursor.execute(sql, [name, self.profile_name]).fetchone()

                    return platform
                else:
                    raise fields_not_selected_error
            else:
                raise platform_does_not_exist_error
        else:
            raise profile_not_logged_in_error
        
    # Retrieves selected fields from the database for all platforms for the currently logged in profile.
    # Raises profile_not_logged_in_error and fields_not_selected_error.
    def get_platforms(self, *, get_name=False, get_username=False, get_password=False, get_salt=False, get_location=False, get_datetime_added=False):
        if (self.logged_in):
            fields = []

            if (get_name):
                fields.append("name")

            if (get_username):
                fields.append("username")

            if (get_password):
                fields.append("password")
            
            if (get_salt):
                fields.append("salt")
            
            if (get_location):
                fields.append("location")
            
            if (get_datetime_added):
                fields.append("datetime_added")
            
            if (len(fields) > 0):
                sql = "SELECT " + api.build_comma_string(fields) + " FROM platform WHERE for_profile=?"
                platforms = self.db_cursor.execute(sql, [self.profile_name]).fetchall()
        
                return platforms
            else:
                raise fields_not_selected_error
        else:
            raise profile_not_logged_in_error

    # Adds platform name to the database with the provided fields for the currently logged in profile.
    # Raises profile_not_logged_in_error, platform_name_invalid_error, and platform_name_unavailable_error.
    def add_platform(self, name, *, location=False, username=False, password=False):
        if (self.logged_in):
            if (api.platform_name_valid(name)):
                if (self.platform_name_available(name)):
                    salt = secure_random_string(SALT_LENGTH)
                    key = derived_key(self.profile_password, salt)

                    fields = ["name", "salt", "for_profile"]
                    values = ["?", "?", "?"]
                    argument = [name, salt, self.profile_name]

                    # None (null) is regarded as a missing argument when passed to, for example, the insert method of Tkinter's entry boxes.
                    # We want to insert an emtpy string, not null, to avoid this problem when data is pulled back out of the database.
                    # Location is the only field with no minimum length that can cause this issue.

                    # *** We should also add NOT NULL to database schema and add this check to all variables so that length limitations can be tweaked freely.
                    if (not location):
                        location = ""

                    fields.append("location")
                    values.append("?")
                    argument.append(location)

                    if (username):
                        encrypted_username = encrypt(username, key)
                    else:
                        encrypted_username = encrypt("", key)

                    fields.append("username")
                    values.append("?")
                    argument.append(encrypted_username)

                    if (password):
                        encrypted_password = encrypt(password, key)
                    else:
                        encrypted_password = encrypt("", key)

                    fields.append("password")
                    values.append("?")
                    argument.append(encrypted_password)
                    
                    fields.append("datetime_added")
                    values.append("datetime(datetime(), 'localtime')")
                    
                    sql = "INSERT INTO platform (" + api.build_comma_string(fields) + ") VALUES (" + api.build_comma_string(values) + ")"

                    self.db_cursor.execute(sql, argument)
                    self.db_connection.commit()
                else:
                    raise platform_name_unavailable_error
            else:
                raise platform_name_invalid_error
        else:
            raise profile_not_logged_in_error

    # Updates platform name in the database with the provided fields for the currently logged in profile.
    # Raises profile_not_logged_in_error, platform_does_not_exist_error, and fields_not_selected_error.
    def update_platform(self, name, *, new_username=False, new_password=False, new_location=False):
        if (self.logged_in):
            if (not self.platform_name_available(name)):
                fields = []
                argument = []

                update_salt = False
                new_salt = secure_random_string(SALT_LENGTH)
                new_key = derived_key(self.profile_password, new_salt)

                if (new_username or new_username == ""):    # Very important to catch empty strings here so that erasure is possible.
                    update_salt = True

                    encrypted_new_username = encrypt(new_username, new_key)

                    fields.append("username=?")
                    argument.append(encrypted_new_username)
                
                if (new_password or new_password == ""):    # Very important to catch empty strings here so that erasure is possible.
                    update_salt = True

                    encrypted_new_password = encrypt(new_password, new_key)

                    fields.append("password=?")
                    argument.append(encrypted_new_password)

                if (update_salt):
                    fields.append("salt=?")
                    argument.append(new_salt)

                if (new_location or new_location == ""):    # Very important to catch empty strings here so that erasure is possible.
                    fields.append("location=?")
                    argument.append(new_location)
                    
                if (len(fields) > 0):
                    argument.append(name)
                    argument.append(self.profile_name)

                    sql = "UPDATE platform SET " + api.build_comma_string(fields) + " WHERE name=? AND for_profile=?"

                    self.db_cursor.execute(sql, argument)
                    self.db_connection.commit()
                else:
                    raise fields_not_selected_error
            else:
                raise platform_does_not_exist_error
        else:
            raise profile_not_logged_in_error

    # Deletes platform name from the database for the currently logged in profile.
    # Raises profile_not_logged_in_error and platform_does_not_exist_error.
    def delete_platform(self, name):
        if (self.logged_in):
            if (not self.platform_name_available(name)):
                self.db_cursor.execute("DELETE FROM platform WHERE name=? AND for_profile=?", [name, self.profile_name])
                self.db_connection.commit()
            else:
                raise platform_does_not_exist_error
        else:
            raise profile_not_logged_in_error
    
    # Determines if platform name is available for the currently logged in profile.
    # Raises profile_not_logged_in_error.
    def platform_name_available(self, name):
        if (self.logged_in):
            platform = self.db_cursor.execute("SELECT name FROM platform WHERE name=? AND for_profile=?",
                                              [name, self.profile_name]).fetchall()

            return len(platform) == 0
        else:
            raise profile_not_logged_in_error

# EXCEPTION CLASSES

## DATABASE EXCEPTIONS

# Raised when a database interaction method requiring fields is called with no fields specified.
class fields_not_selected_error(Exception):
    @staticmethod
    def error_message():
        return "Fields not selected."

## PROFILE EXCEPTIONS

# Raised when a proposed profile name does not fit the established profile name format rules.
class profile_name_invalid_error(Exception):
    @staticmethod
    def error_message():
        return "Profile name invalid."

# Raised when a proposed profile password does not fit the established profile password format rules.
class profile_password_invalid_error(Exception):
    @staticmethod
    def error_message():
        return "Profile password invalid."

# Raised when a proposed profile name already exists in the database.
class profile_name_unavailable_error(Exception):
    @staticmethod
    def error_message():
        return "Profile name unavailable."

# Raised when a method requiring login is called while no profile is logged in.
class profile_not_logged_in_error(Exception):
    @staticmethod
    def error_message():
        return "Profile not logged in."

# Raised when profile name and password credentials cannot be matched to a profile in the database.
class invalid_credentials_error(Exception):
    @staticmethod
    def error_message():
        return "Credentials invalid."

# Raised when a method requiring profile name is passed a name that does not exist in the database.
class profile_does_not_exist_error(Exception):
    @staticmethod
    def error_message():
        return "Profile does not exist."

# Raised when an attempt is made to delete the currently logged in profile.
class deleting_current_profile_error(Exception):
    @staticmethod
    def error_message():
        return "Cannot delete current profile while logged in."
    
## PLATFORM EXCEPTIONS

# Raised when a proposed platform name does not fit the established platform name format rules.
class platform_name_invalid_error(Exception):
    @staticmethod
    def error_message():
        return "Platform name invalid."

# Raised when a proposed platform name already exists in the database for the logged in profile.
class platform_name_unavailable_error(Exception):
    @staticmethod
    def error_message():
        return "Platform name unavailable."

# Raised when a method requiring platform name is passed a name that does not exist in the database.
class platform_does_not_exist_error(Exception):
    @staticmethod
    def error_message():
        return "Platform does not exist."
