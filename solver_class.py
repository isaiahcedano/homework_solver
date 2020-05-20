#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8  
import requests
import PyPDF2
import os 
import re 
import time
import types 
import sys 
import smtplib
import platform
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.common.exceptions import TimeoutException
from googletrans import Translator
from PyDictionary import PyDictionary
from bs4 import BeautifulSoup
from itertools import cycle
from threading import Thread

class HomeworkSolver:

    def translate_en_es(self, text): 
        return self.translator.translate(text, "es", "en").text.encode("utf-8")

    def translate_es_en(self, text):
        return self.translator.translate(text, "en", "es").text.encode("utf-8")

    def get_synonym_spanish(self, text):
        self.dictionary

    def play_sound(self, wav_sound):
        subprocess.check_call(["paplay", wav_sound])

    def send_mail(self, email, password, message):
        server = smtplib.SMTP_SSL("smtp.gmail.com")
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def notify(self):
        self.play_sound("time-is-now.wav")

    def set_browser(self):
        self.user_operating_system = platform.system()
        if self.user_operating_system == "Windows":
            program_files_x86_path = os.environ['programfiles(x86)']
            files_in_program_files_x86 = os.listdir(program_files_x86_path)  
            main_path = os.environ["homepath"]
            if "Google" in files_in_program_files_x86:
                if "chrome" in os.listdir("{}\\{}\\{}\\{}".format(main_path, program_files_x86_path, "Google", "Chrome")):
                    self.browser = webdriver.Chrome()
        elif self.user_operating_system == "Linux":
            if "firefox" in os.listdir("/usr/bin"):
                self.browser = webdriver.Firefox()
        else:
            print("[-] This program is not for mac")
            sys.exit()
            
    def __init__(self, email, password):
        self.start_time = time.time()
        self.set_browser()
        print("[!] If this program is interrupted in any given moment, it will crash\n")
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.homework_files_names = []
        self.total_pdf_text_extraction = ""
        self.file_extraction_dict = {} # For each file there is corresponding text. File is key, text is value
        self.homework_questions = []
        self.websites_of_first_page_search_result = {}
        self.data_set_questions_and_links = {} # For each brainly link there is a corresponding question. Link is key, question is value
        self.lookuped_questions = []
        self.brainly_links = []
        self.total_amount_of_urls_found = 0
        self.email = email
        self.downloaded_files = []
        self.password = password
        self.questions_answers = {}
        self.space_between_lines = "\n"
        self.docs_questions_answers = {}
        self.doc_subject = {} # For each document, there is a subject
        self.translator = Translator()
        self.dictionary = PyDictionary()
        self.content_of_valid_brainly_links = {} # For each brainly link, there is a corresponding answer. Link is key, answer is value
        
        # self.proxies = []
        # self.proxy_Thread = Thread(target=self.get_proxies)
        # self.proxy_Thread.start()
        
        self.delete_file_thread = Thread(target=self.delete_downloaded_homework_files)
        self.delete_file_thread.start()

        self.open_brainly_links_thread = Thread(target=self.open_brainly_links_and_capture_answers)
        self.open_brainly_links_thread.start()

        self.relate_questions_to_answers_thread = Thread(target=self.relate_questions_to_answers)
        self.relate_questions_to_answers_thread.start()

        self.relate_file_to_question_and_answer_set_thread = Thread(target=self.relate_file_to_question_and_answer_set)
        self.relate_file_to_question_and_answer_set_thread.start()

    def terminate(self):
        self.browser.quit()
        self.notify()

    def download(self, url):
        print("[+] Downloading " + str(url))
        if isinstance(url, types.ListType):
            file_names = []
            for link in url:
                response = requests.get(link)
                file_name = link.split("/")[-1]
                with open(file_name, "wb") as file_to_download:
                    file_to_download.write(response.content)
                file_names.append(file_name)
            return file_names
        else:
            response = requests.get(url)
            file_name = url.split("/")[-1]
            with open(file_name, "wb") as file_to_download:
                file_to_download.write(response.content)
            return file_name

    # def get_proxies(self):
    #     print("[+] Getting proxies to avoid captcha...")
    #     ip_address_regex = r'\d*\.\d*'
    #     proxy_webpage = requests.get("https://free-proxy-list.net/").content
    #     bs4_tool = BeautifulSoup(proxy_webpage, "lxml")
    #     td_Tags = bs4_tool.find_all("td")
    #     for element in bs4_tool.find_all("td"):
    #         if re.match("\d*\.\d*", element.text):             
    #             for element in bs4_tool.find_all("td"):
    #                 if re.match("\d*\.\d*", element.text):
    #                         element_index = bs4_tool.find_all("td").index(element)
    #                         ip = element.text
    #                         port = bs4_tool.find_all("td")[element_index+1].text
    #                         self.proxies.append("{}:{}".format(str(ip), str(port)))
        
    #     print("[+] Generated a total amount of {} proxies".format(str(len(proxies))))

    def delete_downloaded_homework_files(self):
        while True:
            if self.homework_files_names != [] or self.homework_files_names != "":
                if isinstance(self.homework_files_names, types.ListType):
                    for file in self.homework_files_names:
                        os.remove(file)
                else:
                    os.remove(self.homework_files_names)
                break
            
            else:
                continue

    def open_brainly_links_and_capture_answers(self):
        while self.brainly_links != [] and self.proxies != []:
            for link in self.brainly_links:
                try:
                    firefox_options = webdriver.FirefoxOptions()
                    proxy = next(cycle(self.proxies))
                    print(self.proxies)
                    firefox_options.add_argument('--proxy-server=%s' % proxy)
                    brainly_browser = webdriver.Firefox(firefox_options=firefox_options)
                    print("[+] Using proxy : " + proxy)
                    brainly_browser.get(link)
                    try:
                        for content in brainly_browser.find_elements_by_class_name("sg-text.js-answer-content.brn-rich-content"):
                            for answer_line in content.find_elements_by_tag_name("p"):
                                if self.content_of_valid_brainly_links.has_key(link):
                                    self.content_of_valid_brainly_links[link] = self.content_of_valid_brainly_links[link] + answer_line.text.encode("utf-8")
                                else:
                                    self.content_of_valid_brainly_links[link] = answer_line.text.encode("utf-8")
                    except NoSuchElementException:
                        continue
                except TimeoutException:
                    print("[-] Connection Lost")
                    exit()
                brainly_browser.close()
                time.sleep(5.0)



    def download_homework_of_each_week_section(self):
        print("[+] Downloading homework of each section")
        for section in self.week_sections:
            section.click() # Click the section
            extra_resources_to_download = []
            homework_hrefs = []
            homework_a_tags = self.browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
                "resources__week__section")[1].find_elements_by_tag_name("a") 
            for a_tag in homework_a_tags:
                homework_hrefs.append(a_tag.get_attribute("href")) # The href link of the homework
            try:
                extra_resources = self.browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
                "resources__week__section")[0].find_elements_by_tag_name("a")
                for resource in extra_resources:
                    # We need to split the url to found out if it is a pdf file
                    if "pdf" in resource.get_attribute("href").split("/")[-1]:
                        extra_resources_to_download.append(resource)

            except NoSuchElementException:
                pass
            
            homework_pdfs = self.download(homework_hrefs) 

            for homework_name in homework_pdfs:
                self.homework_files_names.append(homework_name)

            for resource in extra_resources_to_download:
                resource_pdf_file_name = self.download(resource.get_attribute("href"))
                self.homework_files_names.append(resource_pdf_file_name)

    def extract_text_from_pdf_file(self, pdf_file_name):
        print("[+] Extracting text from pdf file(s) " + str(pdf_file_name))
        possible_subjects = []
        if isinstance(pdf_file_name, types.ListType):
            for file_name in pdf_file_name:
                total_pdf_text_extraction = ""
                pdf_file = open(file_name, "rb")
                pdfReader = PyPDF2.PdfFileReader(pdf_file)
                
                for page in pdfReader.pages: 
                    total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "")
                self.file_extraction_dict[file_name] = total_pdf_text_extraction
                
                for i in range(0, 3):
                    possible_subjects.append(self.file_extraction_dict[file_name].replace("\n", "").split()[i])
                
                self.doc_subject[file_name] = possible_subjects
        else:
            total_pdf_text_extraction = ""
            pdf_file = open(pdf_file_name, "rb")
            pdfReader = PyPDF2.PdfFileReader(pdf_file)
            for page in pdfReader.pages: 
                total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "")
            
            for i in range(0, 3):
                possible_subjects.append(page.extractText().replace("\n", "").split()[i])
            self.doc_subject[pdf_file_name] = possible_subjects
            self.file_extraction_dict[pdf_file_name] = total_pdf_text_extraction

    def extract_spanish_questions_from_text(self, text):
        homework_questions_not_complete = []
        questions_disorganized_encoded = re.findall("¿[^-_/.,\\\\]+\?", (text).encode(encoding="utf-8"))
        questions_to_add = []
        for encoded_question in questions_disorganized_encoded:
            homework_questions_not_complete.append(encoded_question)

        for question in homework_questions_not_complete:
            implanted_questions = question.replace("\xc2\xbf", "¿").split("¿")
            for implanted_question in implanted_questions:
                self.homework_questions.append(implanted_question)
                questions_to_add.append(implanted_question.replace("\xc2\xbf", "¿").decode("utf-8"))

    def lookup_questions_and_store_brainly_links(self):
        try:
            # Search questions on google
            for question in self.homework_questions:
                try:
                    if question != "" and question not in self.lookuped_questions:
                        self.browser.get("https://www.google.com/")
                        search_bar = self.browser.find_elements_by_tag_name("input")[3]
                        search_bar.click()
                        search_bar.send_keys(question.replace("\xc2\xbf", "¿").decode("utf-8"))
                        search_bar.send_keys(Keys.ENTER)
                        print("[+] Google Searching Question :  " + question.replace("\xc2\xbf", "¿").decode("utf-8"))
                        self.lookuped_questions.append(question)
                        time.sleep(5.0)
                        for site in self.browser.find_elements_by_class_name("r"):
                            try:
                                url_link = site.find_element_by_tag_name("a").get_attribute("href")
                                text_below_or_onTopof_url = site.find_element_by_tag_name("cite").text
                                self.websites_of_first_page_search_result[url_link] = text_below_or_onTopof_url
                                
                                if "brainly" in self.websites_of_first_page_search_result[url_link]:
                                    self.brainly_links.append(url_link)

                                if "brainly" in text_below_or_onTopof_url:
                                    if self.data_set_questions_and_links.has_key(url_link):
                                        data = self.data_set_questions_and_links[url_link] + question.replace("\xc2\xbf", "¿").decode("utf-8")
                                    else:
                                        self.data_set_questions_and_links[url_link] = question.replace("\xc2\xbf", "¿").decode("utf-8")
                                self.total_amount_of_urls_found = self.total_amount_of_urls_found + 1
                            
                            except (NoSuchElementException, KeyboardInterrupt) as error:
                                if error == KeyboardInterrupt:
                                    break
                                elif error == NoSuchElementException:
                                    continue
                        else:
                            continue
                except TimeoutException:
                    print("[-] Connection Lost")
                    exit()
        except KeyboardInterrupt:
            pass

    def relate_questions_to_answers(self):
        while True:
            if self.brainly_links != []:
                for link in self.brainly_links:
                    if self.data_set_questions_and_links.has_key(link): # If the brainly link has a question
                        if self.content_of_valid_brainly_links.has_key(link): # If the brainly link has an answer
                            question = self.data_set_questions_and_links[link]
                            answer = self.content_of_valid_brainly_links[link]
                            if self.questions_answers.has_key(question):
                                self.questions_answers[question] = self.questions_answers[question] + answer
                            else:
                                self.questions_answers[question] = answer
                break
            else:
                continue
        
    def relate_file_to_question_and_answer_set(self):
        while True:
            if self.homework_files_names != [] and self.brainly_links != []:
                for homework_file in self.homework_files_names:
                    print("[+] Relating " + str(homework_file) + " to its corresponding questions and answers")
                    dict_questions_answers = {}
                    text_of_homework_file = self.file_extraction_dict[homework_file]
                    for link in self.brainly_links:
                        question = self.data_set_questions_and_links[link]
                        if question != "" and question in text_of_homework_file:
                            try:
                                dict_questions_answers[question] = self.questions_answers[question.replace("\xc2\xbf", "¿").decode("utf-8")]
                            except KeyError:
                                continue
                        self.docs_questions_answers[homework_file] = dict_questions_answers 
                break
            else:
                continue

    def get_homework_result(self): # The Gold of The program
        for doc in sorted(self.docs_questions_answers):
            print("Document : " + doc + "\n")
            print("Possible Subjects : " + str(self.doc_subject[doc]) + "\n")
            for question in self.docs_questions_answers[doc]:
                print(question + "\n")
                for content in self.docs_questions_answers[doc][question].split(":"):
                    print(content)
                print("\n\n")

    def get_extra_data(self):
        print("\n\n-------------Data-------------\n\n")
        print("Amount of Brainly Links Captured : " + str(len(self.brainly_links)) + self.space_between_lines)
        print("Amount of Homework Answers Extracted : " + str(len(self.content_of_valid_brainly_links)) + self.space_between_lines)
        print("Elapsed Time : {} minutes ({} seconds) {}".format(((time.time() - self.start_time)/60.0), (time.time() - self.start_time), self.space_between_lines))
        print("Filtered : " + str(self.total_amount_of_urls_found) + " links" + self.space_between_lines)
        print("Brainly Links Extracted : " + str(self.brainly_links) + self.space_between_lines)
        print("Amount of Homework Questions Captured : " + str(len(self.homework_questions)) + self.space_between_lines)
        print("Homework Files : "  + str(self.homework_files_names) + self.space_between_lines)
        print("Deleted Files : " + str(self.homework_files_names) + self.space_between_lines)
        print("Extracted Text : " + str(self.total_pdf_text_extraction.encode(encoding="utf-8")) + self.space_between_lines)
        print("Questions Extracted : " + str(self.homework_questions) + self.space_between_lines)
        print("Homework Answers : " + str(self.content_of_valid_brainly_links) + self.space_between_lines)
        print("Websites of First Page Results : " + str(self.websites_of_first_page_search_result) + self.space_between_lines)


    def return_answers_by_url(self, email, password, homework_url, sections_to_click_through, verbose):
        self.homework_url = homework_url
        self.resource_homework_url = self.homework_url
        try:
            self.browser.get(self.resource_homework_url)
        except TimeoutException:
            print("[-] Connection Lost")
            exit()
        self.week_sections = []
        sections = []
        if sections_to_click_through != [] and (len(sections_to_click_through) > 1):
            try:
                section_index = range(sections_to_click_through[0], sections_to_click_through[1])
                section_index.append(int(sections_to_click_through[-1]))
                sections = self.browser.find_element_by_class_name("resources__week__weeks").find_elements_by_tag_name("button")
                for index in section_index:
                    self.week_sections.append(sections[index - 1])
            except IndexError:
                print("[-] Session Cancelled Due To Range Error")
        elif len(sections_to_click_through) == 1:
            sections = self.browser.find_element_by_class_name("resources__week__weeks").find_elements_by_tag_name("button")
            self.week_sections.append(sections[sections_to_click_through[0] - 1])
        

        # Step 1. Go through each week section, and download the pdf files.
        self.download_homework_of_each_week_section()

        # Step 2. Extract text from the pdf files.
        self.extract_text_from_pdf_file(self.homework_files_names)

        # Step 3. Extract the questions from the text of each pdf file.
        print("[+] Extracting questions from text") 
        for name in self.homework_files_names:
            self.extract_spanish_questions_from_text(self.file_extraction_dict[name])

        # Step 4. Lookup all the questions of the text of each homework file.
        self.lookup_questions_and_store_brainly_links()

        # Step 5
        self.get_homework_result()

        # Check if extra data should be printed
        if verbose == True:
            self.get_extra_data()

        # Check if email notification should be sent
        if email != "" and password != "":
            self.send_mail(email, password, "Homework Task Successful")

    
    def return_answers_by_document(self, document_name, email, password, verbose):
        # Append the document to the homework files 
        self.homework_files_names.append(document_name)

        # Step 1
        self.extract_text_from_pdf_file(document_name)
        
        # Step 2
        for name in self.homework_files_names:
            self.extract_spanish_questions_from_text(self.file_extraction_dict[name], name)

        # Step 3 
        self.lookup_questions()

        # Step 4
        self.general_return_answers()

        if verbose == True:
            self.get_extra_data()

        if email != "" and password != "":
            self.send_mail(email, password, "Homework Task Successful")

        # Step 5
        self.terminate()

    def run(self, method_to_apply, homework_url, document_name, sections, verbose):

        if ((homework_url == "") and (document_name != "") and (method_to_apply == "1")):
            self.return_answers_by_document(document_name, self.email, self.password, verbose)

        elif ((homework_url != "") and (document_name == "") and (method_to_apply == "2" or method_to_apply == "3" or method_to_apply == "4")):
            self.return_answers_by_url(self.email, self.password, homework_url, sections, verbose)
