#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8  
import requests, PyPDF2, os, re, time, types, sys, smtplib
start_time = time.time()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from playsound import playsound

def send_mail(email, password, message):
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

reload(sys)  
sys.setdefaultencoding('utf8')
space_between_lines = "\n\n\n\n\n\n\n"
questions_answers = {} # For each question there is a corresponding answer. Question is key, answer is value.
homeworks = {}

# Step 1 variables
dpcc_resource_homework_url = "https://aprendoencasa.pe/#/nivel/secundaria/grade/3/speciality/37/resources"
browser = webdriver.Firefox()
browser.get(dpcc_resource_homework_url)
week_sections = browser.find_element_by_class_name("resources__week__weeks").find_elements_by_tag_name("button")
homework_files_names = []


# Step 2 variables
total_pdf_text_extraction = ""


# Step 3 variables
homework_questions = []


# Step 5 variables
websites_of_first_page_search_result = {}
data_set_questions_and_links = {} # For each brainly link there is a corresponding question. Link is key, question is value
amount_of_homework_questions = 0


# Step 6 variables
brainly_links = []
amount_of_brainly_links = 0
total_amount_of_urls_found = 0
content_of_valid_brainly_links = {} # For each brainly link, there is a corresponding answer. Link is key, answer is value
amount_of_homework_answers = 0


def download(url):
    response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as file_to_download:
        file_to_download.write(response.content)
    return file_name

def delete_file(file_name):
    if isinstance(file_name, types.ListType):
        for file in file_name:
            os.remove(file)
    else:
        os.remove(file_name)

def download_homework_of_each_week_section():
    for section in week_sections:
        section.click() # Click the section
        extra_resources_to_download = []
        dpcc_homework_href = browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
            "resources__week__section")[1].find_element_by_tag_name("a").get_attribute("href") # The href link of the homework
        try:
            extra_resources = browser.find_element_by_class_name("resources__week__sections").find_elements_by_class_name(
            "resources__week__section")[0].find_elements_by_tag_name("a")
            for resource in extra_resources:
                # We need to split the url to found out if it is a pdf file
                if "pdf" in resource.get_attribute("href").split("/")[-1]:
                    extra_resources_to_download.append(resource)

        except NoSuchElementException:
            pass
        homework_pdf_file_name = download(dpcc_homework_href) # Download the homework and return the homework name
        homework_files_names.append(homework_pdf_file_name)
        for resource in extra_resources_to_download:
            resource_pdf_file_name = download(resource.get_attribute("href"))
            homework_files_names.append(resource_pdf_file_name)

def extract_text_from_pdf_file(pdf_file_name):
    global total_pdf_text_extraction
    if isinstance(pdf_file_name, types.ListType):
        for file_name in pdf_file_name:
            pdf_file = open(file_name, "rb")
            pdfReader = PyPDF2.PdfFileReader(pdf_file)
            for page in pdfReader.pages: 
                total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "").replace("\t", "")
    else:
        pdf_file = open(pdf_file_name, "rb")
        pdfReader = PyPDF2.PdfFileReader(pdf_file)
        for page in pdfReader.pages: 
            total_pdf_text_extraction = total_pdf_text_extraction + page.extractText().replace("\n", "").replace("\t", "")

def extract_spanish_questions_from_text(text):
    homework_questions_not_complete = []
    questions_disorganized_encoded = re.findall("¿[^-_/.,\\\\]+\?", (text).encode(encoding="utf-8"))
    for encoded_question in questions_disorganized_encoded:
        homework_questions_not_complete.append(encoded_question)
    for question in homework_questions_not_complete:
        implanted_questions = question.replace("\xc2\xbf", "¿").split("¿")
        for implanted_question in implanted_questions:
            homework_questions.append(implanted_question)

def lookup_questions():
    global websites_of_first_page_search_result, amount_of_homework_questions, data_set_questions_and_links
    try:
    # Search questions on google
        for question in homework_questions:
            if question != "":
                browser.get("https://www.google.com/")
                search_bar = browser.find_elements_by_tag_name("input")[3]
                search_bar.click()
                search_bar.send_keys(question.replace("\xc2\xbf", "¿").decode("utf-8"))
                search_bar.send_keys(Keys.ENTER)
                time.sleep(5.0)
                amount_of_homework_questions = amount_of_homework_questions + 1
                for site in browser.find_elements_by_class_name("r"):
                    try:
                        url_link = site.find_element_by_tag_name("a").get_attribute("href")
                        text_below_or_onTopof_url = site.find_element_by_tag_name("cite").text
                        websites_of_first_page_search_result[url_link] = text_below_or_onTopof_url
                        if "brainly" in text_below_or_onTopof_url:
                            if data_set_questions_and_links.has_key(url_link):
                                data = data_set_questions_and_links[url_link] + question.replace("\xc2\xbf", "¿").decode("utf-8")
                            else:
                                data_set_questions_and_links[url_link] = question.replace("\xc2\xbf", "¿").decode("utf-8")
                    except (NoSuchElementException, KeyboardInterrupt) as error:
                        if error == KeyboardInterrupt:
                            break
                        elif error == NoSuchElementException:
                            continue
    except KeyboardInterrupt:
        pass

def filter_brainly_links_and_store_them_in_a_list():
    global brainly_links, amount_of_brainly_links, total_amount_of_urls_found
    for url_link in websites_of_first_page_search_result:
        if "brainly" in websites_of_first_page_search_result[url_link]:
            brainly_links.append(url_link)
            time.sleep(5.0)
            amount_of_brainly_links = amount_of_brainly_links + 1
        total_amount_of_urls_found = total_amount_of_urls_found + 1

def open_brainly_links_catch_answer_text():
    global content_of_valid_brainly_links, amount_of_homework_answers
    for link in brainly_links:
        browser.get(link)
        try:
            for content in browser.find_elements_by_class_name("sg-text.js-answer-content.brn-rich-content"):
                for answer_line in content.find_elements_by_tag_name("p"):
                    if content_of_valid_brainly_links.has_key(link):
                        content_of_valid_brainly_links[link] = content_of_valid_brainly_links[link] + answer_line.text.encode("utf-8")
                        amount_of_homework_answers = amount_of_homework_answers + 1
                    else:
                        content_of_valid_brainly_links[link] = answer_line.text.encode("utf-8")
                        amount_of_homework_answers = amount_of_homework_answers + 1
        except NoSuchElementException:
            continue
        time.sleep(5.0)

def organize_questions_and_answers():
    # questions_answers[question] = answer
    for link in brainly_links:
        if data_set_questions_and_links.has_key(link): # If the brainly link has a question
            if content_of_valid_brainly_links.has_key(link): # If the brainly link has an answer
                question = data_set_questions_and_links[link]
                answer = content_of_valid_brainly_links[link]
                if questions_answers.has_key(question):
                    questions_answers[question] = questions_answers[question] + answer
                else:
                    questions_answers[question] = answer

def return_answers():
    filter_brainly_links_and_store_them_in_a_list()
    open_brainly_links_catch_answer_text()
    organize_questions_and_answers()

print("Week Sections : " + str(week_sections) + space_between_lines)

# Step 1
download_homework_of_each_week_section()
print("Homework Files : "  + str(homework_files_names) + space_between_lines)


# Step 2
extract_text_from_pdf_file(homework_files_names)
print("Extracted Text : " + str(total_pdf_text_extraction.encode(encoding="utf-8")) + space_between_lines)


# Step 3
extract_spanish_questions_from_text(total_pdf_text_extraction)
print("Questions Extracted : " + str(homework_questions) + space_between_lines)


# Step 4
delete_file(homework_files_names)
print("Deleted Files : " + str(homework_files_names) + space_between_lines)


# Step 5
lookup_questions()
print("Websites of First Page Results : " + str(websites_of_first_page_search_result) + space_between_lines)


# Step 6
return_answers()
print("Amount of Homework Questions Captured : " + str(amount_of_homework_questions) + space_between_lines)

print("The Brainly Links Extracted : " + str(brainly_links) + space_between_lines)

print("Filtered " + str(total_amount_of_urls_found) + " links" + space_between_lines)

print("Homework Answers : " + str(content_of_valid_brainly_links) + space_between_lines)

# print("Homework Answers : " + str(homework_answers) + "\n\n\n\n\n\n\n")

print("Amount of Brainly Links Captured : " + str(amount_of_brainly_links) + space_between_lines)

for data_set in questions_answers:
    answer = questions_answers[data_set].decode('utf-8', 'ignore')
    question = data_set.decode('utf-8', 'ignore')
    print("The answer of " + question + " is " + answer + space_between_lines)

print("Amount of Homework Answers Extracted : " + str(amount_of_homework_answers))

print("This program took %s seconds (%s minutes) to run" % ((time.time() - start_time), ((time.time() - start_time)/60.0)))

browser.quit()

playsound("time-is-now.wav")

message_to_send = """
The extraction is complete\n\n\n\n\n\n\n\n
""".format(questions_answers)
send_mail("vlackvincent936@gmail.com", "darkroses990", message_to_send)