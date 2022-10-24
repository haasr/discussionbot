from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyshadow.main import Shadow

from datetime import datetime as dt
from pprint import pprint

from lib.tkwindow import DFReviewWindow

import pandas as pd
import time
import re

pd.set_option('display.max_rows', 150)

def print_title(title):
    print(f"{title}", end="\n"+"-"*44+"\n")
            
class DiscussionBot:
    def __init__(self, theme, email, password, course_name, discussion_name, min_word_count=14, start_auto=True):
        self.min_word_count_students_dict = {}
        pd.set_option('display.max_rows', 150) # Set pandas to display full dataframe notebook

        self.theme = theme
        self.email = email
        self.course_name = course_name
        self.discussion_name = discussion_name
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.get('https://elearn.etsu.edu/d2l/lp/auth/saml/initiate-login?entityId=https%3A%2F%2Fsts.windows.net%2F962441d5-5055-4349-bad3-baec43c3d741%2F&target=%2fd2l%2fhome')
        self.min_word_count=min_word_count

        self.start_automagically(password) if start_auto else self.step_thru(password)
    
    def start_automagically(self, password):
        self.login(self.email, password)
        self.navigate_to_discussion()
        self.grade_discussion()
        self.dispose_browser_gracefully()

        review_df = self.get_min_word_discussions_report()
        pprint(review_df)
        self.min_word_count_students_dict.clear()

        disc_name, fname = self.construct_dfreview_window_names()

        d = DFReviewWindow(self.theme, df=review_df, discussion_name=disc_name, filename=fname)
        d.mainloop()

    def step_thru(self, password):
        print_title('\nLogin')
        time.sleep(1)
        self.login(self.email, password)
        
        print_title('\n2FA completed?')
        input("Enter to continue >>")

        print_title('\n(m) Manually navigate to Discussion or\n(a) automatically?')
        text = input("m/a >>")
        self.navigate_to_discussion() if text.lower() == 'a' else print_title("Navigate to Discussion \"Assess\" screen")
        input("Enter to continue >>")

        print_title('\nBegin grading')
        input("Enter to continue >>")
        self.grade_discussion(step_thru=True)
        self.dispose_browser_gracefully()

        review_df = self.get_min_word_discussions_report()
        pprint(review_df)

    def login(self, email, password):
        time.sleep(4)
        element = self.browser.find_element(By.NAME, 'loginfmt')
        element.clear()
        element.send_keys(email)
        time.sleep(1)
        # Find and click next
        self.browser.find_element(By.ID, 'idSIButton9').click()
        time.sleep(2)
        # Find and enter password
        element = self.browser.find_element(By.NAME, 'passwd')
        element.clear()
        element.send_keys(password)
        time.sleep(1)
        # Find and click sign in
        self.browser.find_element(By.ID, 'idSIButton9').click()
        time.sleep(1)

        while not len(self.browser.find_elements(By.CLASS_NAME, 'd2l-body')) == 1: # 2FA not completed yet
            time.sleep(2)
        time.sleep(4)

    def dispose_browser_gracefully(self):
        self.browser.close()
        self.browser.quit()

    def navigate_to_discussion(self):
        time.sleep(1)
        self.browser.find_element(By.CLASS_NAME, 'd2l-navigation-s-course-menu').click()
        time.sleep(1)
        self.browser.find_element(By.PARTIAL_LINK_TEXT, self.course_name).click()
        time.sleep(1)
        self.browser.find_element(By.XPATH, '/html/body/header/nav/d2l-navigation/d2l-navigation-main-footer/div/div[1]/div[4]/d2l-dropdown/button/span/span').click()
        time.sleep(1)
        self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Discussions').click()
        time.sleep(1)
        self.browser.find_element(By.PARTIAL_LINK_TEXT, self.discussion_name).click()
        time.sleep(1)
        self.browser.find_element(By.XPATH, '//*[@id="topicContextMenu"]').click()
        time.sleep(1)
        self.browser.find_element(By.ID, 'd2l_pageTitleActions_assess').click()
        time.sleep(1)

    def grade_first_student(self, step_thru=False):
        print_title("\nGrade First Student:")

        shadow = Shadow(self.browser)
        shadow.set_explicit_wait(4, 3)
        elements = shadow.find_elements("span")
        inputs = shadow.find_elements('input')
        # I have no fucking clue why but if the buttons line is not included,
        # final_student = int(user_info[3]) doesn't parse...It's just magic. Just accept it.
        buttons = shadow.find_elements('button')
        d2l_buttons = shadow.find_elements('d2l-button')
            
        try:
            save_draft = d2l_buttons[20]
        except:
            save_draft = d2l_buttons[19]
        next_student = elements[3]

        try:
            overall_grade = inputs[7]
        except:
            overall_grade = inputs[5]
        user_info = elements[4].text.split()
        
        final_student = int(user_info[3])

        # prevents students who didn't submit from breaking the bot
        if 'Post:' in elements[24].text:
            post_info = elements[24].text
        else:
            post_info = 'Post: 0 threads, 0 replies'

        post_info = post_info.split()

        threads = int(post_info[1])
        replies = int(post_info[3])
        total, feedback = self.grade_disc(threads, replies)

        self.check_min_word_count(shadow, num_threads=threads, num_replies=replies, word_count=self.min_word_count)
        self.enter_feedback(shadow, feedback)

        # Send data to D2L
        overall_grade.clear()
        overall_grade.send_keys(total)
        time.sleep(1.5)

        try:
            save_draft.click()
        except:
            d2l_buttons[18].click()
        time.sleep(3)

        if step_thru:
            input("Enter to continue >>\n")

        next_student.click()
        return final_student

    def grade_last_student(self, step_thru=False):
        print_title("\nGrade Last Student:")
        time.sleep(4)
        shadow = Shadow(self.browser)
        shadow.set_explicit_wait(4, 3)
        elements = shadow.find_elements("span")
        inputs = shadow.find_elements('input')
        d2l_buttons = shadow.find_elements('d2l-button')
            
        try:
            save_draft = d2l_buttons[20]
        except:
            save_draft = d2l_buttons[19]

        try:
            overall_grade = inputs[7]
        except:
            overall_grade = inputs[5]

        # prevents students who didn't submit from breaking the bot
        if 'Post:' in elements[24].text:
            post_info = elements[24].text
        else:
            post_info = 'Post: 0 threads, 0 replies'

        post_info = post_info.split()

        threads = int(post_info[1])
        replies = int(post_info[3])
        total, feedback = self.grade_disc(threads, replies)

        self.check_min_word_count(shadow, num_threads=threads, num_replies=replies, word_count=self.min_word_count)
        self.enter_feedback(shadow, feedback)

        overall_grade.clear()
        overall_grade.send_keys(total)
        time.sleep(1.5)

        try:
            save_draft.click()
        except:
            d2l_buttons[18].click()
        time.sleep(3)

        if step_thru:
            input("Enter to continue >>")

    def grade_discussion(self, step_thru=False):
        links = self.browser.find_elements(By.CLASS_NAME, 'd2l-link') #all d2l links on page
        links[11].click() #idk what first 10 are, but index 10 is search options and 11 is first student
        self.currently_grading = True
        time.sleep(3)

        final_student = self.grade_first_student(step_thru=step_thru)

        print_title("\nEntering grading loop:")
        for i in range(1, final_student-1):
            time.sleep(4)
            shadow = Shadow(self.browser)
            shadow.set_explicit_wait(4, 3)
            elements = shadow.find_elements("span")
            inputs = shadow.find_elements('input')
            d2l_buttons = shadow.find_elements('d2l-button')
            
            save_draft = d2l_buttons[20]
            next_student = elements[4]

            try:
                overall_grade = inputs[7]
            except:
                overall_grade = inputs[5]

            # prevents students who didn't submit from breaking the bot
            if 'Post:' in elements[25].text:
                post_info = elements[25].text
            else:
                post_info = 'Post: 0 threads, 0 replies'

            post_info = post_info.split()

            threads = int(post_info[1])
            replies = int(post_info[3])
            total, feedback = self.grade_disc(threads, replies)

            self.check_min_word_count(shadow, num_threads=threads, num_replies=replies, word_count=self.min_word_count)
            self.enter_feedback(shadow, feedback)
            
            # Send data to D2L
            overall_grade.clear()
            overall_grade.send_keys(total)
            time.sleep(1.5)
            try:
                save_draft.click()
            except:
                d2l_buttons[18].click()
            time.sleep(3)
            next_student.click()

            if step_thru:
                input("Enter to continue >>")

        self.grade_last_student(step_thru=step_thru)
        self.currently_grading = False

    def get_min_word_discussions_report(self):
        return self.construct_discussions_to_check_df()

    def construct_discussions_to_check_df(self):
        discussions_to_check_df = pd.DataFrame(columns=['Name', 'Original Post', 'Reply 1', 'Reply 2'])
        op_list = []
        r1_list = []
        r2_list = []
        for student, discussion_list in self.min_word_count_students_dict.items():
            op_list.append(discussion_list[0])
            r1_list.append(discussion_list[1])
            r2_list.append(discussion_list[2])
        
        discussions_to_check_df['Name'] = list(self.min_word_count_students_dict.keys())
        discussions_to_check_df['Original Post'] = op_list
        discussions_to_check_df['Reply 1'] = r1_list
        discussions_to_check_df['Reply 2'] = r2_list
        
        return discussions_to_check_df

    def construct_dfreview_window_names(self):
        disc_name = self.course_name[-3:] + '-' + self.discussion_name[:25]
        fname = re.sub(r'[^A-Za-z0-9 ]+', '', disc_name)
        fname = re.sub(r'\s+', '-', fname)
        fname = f"{dt.now().strftime('%m-%dT%H-%M-%S')}_{fname}_review.csv"
        
        return disc_name, fname

    def get_student_name(self, shadow):
        # Get student's name (complicated AF as usual...)
        learner_context_bar_sr_outer = shadow.find_elements('d2l-consistent-evaluation-learner-context-bar')[0].shadow_root
        learner_context_bar_inner_div = learner_context_bar_sr_outer.find_elements(By.CLASS_NAME, 'd2l-consistent-evaluation-learner-context-bar')[0]
        learner_context_bar_sr_inner = learner_context_bar_inner_div.find_elements(By.TAG_NAME, 'd2l-consistent-evaluation-lcb-user-context')[0].shadow_root
        return learner_context_bar_sr_inner.find_elements(By.CLASS_NAME, 'd2l-consistent-evaluation-lcb-user-name')[0].text

    def check_min_word_count(self, shadow, num_threads, num_replies, word_count=10): # Type should be original, post1, post2
        if not num_threads == 0:
            discussion_threads_sr_outer = shadow.find_elements('d2l-consistent-evaluation-evidence-discussion')[0].shadow_root
            discussion_threads_sr_inner = discussion_threads_sr_outer.find_elements(By.CSS_SELECTOR, 'd2l-consistent-evaluation-discussion-post-page')[0].shadow_root
            posts_table = discussion_threads_sr_inner.find_elements(By.CLASS_NAME, 'd2l-table')[0].find_elements(By.TAG_NAME, 'tbody')[0]
            table_rows = posts_table.find_elements(By.CSS_SELECTOR, 'td')

            posts_threads_to_check = ['OK', 'OK', 'OK']
            store_student_in_dict = False

            # Basically parsing the entire post together with all
            # newlines removed so it can be tokenized for accurate
            # word count
            post = " ".join(table_rows[0].text.split('\n', 3)[2:])
            if len(re.split('\s+', post)) < word_count: 
                posts_threads_to_check[0] = post
                store_student_in_dict = True

            if num_replies > 0:
                # Basically parsing the entire reply together with all
                # newlines removed so it can be tokenized for accurate
                # word count
                r1 = " ".join(table_rows[1].text.split('\n', 4)[3:])
                r1 = r1.split("<<< Replied")[0]
                if len(re.split('\s+', r1)) < word_count:
                    posts_threads_to_check[1] = r1
                    store_student_in_dict = True

                if num_replies == 2:
                    r2 = " ".join(table_rows[2].text.split('\n', 4)[3:])
                    r2 = r2.split("<<< Replied")[0]
                    if len(re.split('\s+', r2)) < word_count:
                        posts_threads_to_check[2] = r2
                        store_student_in_dict = True
                        
            if store_student_in_dict:
                student_name = self.get_student_name(shadow)
                self.min_word_count_students_dict[student_name] = posts_threads_to_check

    def grade_disc(self, threads, replies):
        total = 6
        feedback = ''
        if threads == 0:
            total -= 2
            feedback += 'Missing Original Post\n'
        if replies < 1:
            total -= 4
            feedback += 'Missing responses to 2+ classmates\n'
        elif replies < 2:
            total -= 2
            feedback += 'Missing response to 1 classmate\n'
        return total,feedback

    def enter_feedback(self, shadow, feedback):
        feedback_panel = shadow.find_elements('d2l-consistent-evaluation-right-panel-block')[2]
        sr = feedback_panel.find_elements(By.TAG_NAME, 'd2l-htmleditor')[0].shadow_root
        iframe = sr.find_elements(By.CLASS_NAME, 'd2l-htmleditor-label-flex-container')[0].find_elements(By.TAG_NAME, 'iframe')[0]
        self.browser.switch_to.frame(iframe)
        b = self.browser.find_element(By.XPATH, '//*[@id="tinymce"]')
        b.send_keys(Keys.CONTROL + "a")
        b.send_keys(Keys.DELETE) # If pre-existing feedback, deletes it
        b.send_keys(feedback)
        self.browser.switch_to.default_content()
        time.sleep(1)