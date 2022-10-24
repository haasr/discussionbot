from lib.bot import DiscussionBot
import config
import numpy as np

THEMES = {
    'light': 'plastik',
    'dark': 'black'
}

def print_title(title):
    print(f"{title}", end="\n"+"-"*44+"\n")

def main():
    theme = THEMES[config.THEME]
    email = config.EMAIL

    discussions_keys = np.arange(0, len(config.DISCUSSIONS_LIST))
    discussions_map = dict(zip(discussions_keys, config.DISCUSSIONS_LIST))

    courses_keys = np.arange(0, len(config.COURSES_LIST))
    courses_map = dict(zip(courses_keys, config.COURSES_LIST))

    print_title("Config")
    password = input(f"Password for {email} >>")

    print_title("\nChoose Course by number:")
    [ print(f"{k}   {v}") for k, v in courses_map.items() ]

    course_key = int(input(f"Course #: >>"))
    course_name = courses_map[course_key]

    print_title("\nChoose Discussion by number:")
    [ print(f"{k}   {v}") for k, v in discussions_map.items() ]

    disc_key = int(input(f"Discussion #: >>"))
    disc_name = discussions_map[disc_key]

    print_title("\nEnter min word count (int):")
    min_word_count = int(input("Min word count >>"))

    print_title("\nDebug mode (d) or run auto (a)?")
    debug = input("d/a >>").lower()

    start_auto = True
    if debug == 'd':
        start_auto = False

    DiscussionBot(
        theme, email, password, course_name,
        disc_name, min_word_count, start_auto=start_auto
    )

if __name__ == '__main__':
    main()
    