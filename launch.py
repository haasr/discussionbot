from tkwindow import DiscussionWindow, ProcWindow
import config

if __name__ == '__main__':
    THEMES = {
        'light': 'plastik',
        'dark': 'black'
    }

    d = DiscussionWindow(
        theme=THEMES[config.THEME],
        email=config.EMAIL,
        courses_list=config.COURSES_LIST,
        discussions_list=config.DISCUSSIONS_LIST
    )