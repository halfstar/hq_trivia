# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import requests
import json
import time
import subprocess
from selenium import webdriver
import readline

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done")
args = vars(ap.parse_args())

question_x = 120
question_y = 200
question_width = 250
question_length = 150

answers_x = question_x
answers_y = question_y + question_length
answers_width = question_width
answers_length = 200

stop_words = ["which ", "what ", "who ","has ", "have ", "had ",
				"is ", "are ", "was ", "were ",
				"these ", "those ", "this ", "that ", "the ",
				"of ", "a ", "an ", "?"]

def captureScreen(x, y, wide, length, output):
    subprocess.run(
        ["screencapture", "-R{},{},{},{}".format(x, y, wide, length), output])

def ocr(image_file, tmp_file_name):
	# load the example image and convert it to grayscale
	image = cv2.imread(image_file)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# check to see if we should apply thresholding to preprocess the
	# image
	if args["preprocess"] == "thresh":
		gray = cv2.threshold(gray, 0, 255,
							cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	# make a check to see if median blurring should be done to remove
	# noise
	elif args["preprocess"] == "blur":
		gray = cv2.medianBlur(gray, 3)

	# write the grayscale image to disk as a temporary file so we can
	# apply OCR to it
	cv2.imwrite(tmp_file_name, gray)
	text = pytesseract.image_to_string(Image.open(tmp_file_name))
	#os.remove(filename)
	lines = text.splitlines()
	return lines


def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()


# step 2: extract & clean question and answers
def extractQuestion(lines):
	question = ""
	# extract
	is_question_done = False
	for line in lines:
		line = line.strip().lower()
		if len(line) > 3:
			question += " " + line
			if line.find('?') != -1:
				is_question_done = True
	# clean
	for word in stop_words:
		question = question.replace(word, "")
	confirmed = rlinput("Confirm the question :", question)
	print("question = {}".format(confirmed))
	return confirmed

def extractAnswers(lines):
	answers = []
	for line in lines:
		line = line.strip().lower()
		if len(line) > 3:
			answers.append(line)
	
	for i, ans in enumerate(answers):
		print("ans{} = {}".format(i, ans))
	return answers	

# step 3: using custom search api question + answer
# drivers = []
# desiredWidth = (1851+70)/3; desiredHeight = 1060; initialX = 69; initialY = 23
# for i in range(0,3,1):
#     driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
#     driver.set_window_rect(initialX + desiredWidth * i, initialY,desiredWidth,desiredHeight)
#     drivers.append(driver)



def searchNcount(question, answers):

	for i, ans in enumerate(answers):
		url = "https://www.googleapis.com/customsearch/v1"
		param = {
			"key": "AIzaSyBiekaJy2dX-hFzmU5lBa0PzhlnznGVkcg",
			"cx": "015030761589660041921:evlnx4ljbn8",
			"num":"10",
			"q":"{}".format(question+" "+ans),
			}
		r = requests.get(url, param)
		res = json.loads(r.content)
		print ("search question+ans{} : num of results{}".format(i, res["searchInformation"]["totalResults"]))
		if not res["items"]:
			print("ans {} no result".format(i))
		else:
			print ("ans {} top record: {}".format(i, res["items"][0]["title"]))	
		# driverTemp = drivers[i]
		# driverTemp.switch_to_window(driverTemp.current_window_handle) #bring to foreground 
		# driverTemp.get('http://www.google.com/search?q={}'.format(question+" "+ans));
		# driverTemp.execute_script("document.body.style.zoom='90%'") #zoom to show more content
		# driverTemp.execute_script("window.scrollTo(130, 100)")
		# #print(json.dumps(res,indent=4))

# for ans in answers:
# 	driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
# 	driver.get('http://www.google.com/search?q={}'.format(question+" "+ans))

# done=input('done:')
# driver.quit()

def solveQuestion(image_name):
	captureScreen(question_x, question_y, question_width, question_length, "question.png")
	lines = ocr("question.png", "q_tmp.png")
	print("question content:{}".format(lines))
	question = extractQuestion(lines)

	captureScreen(answers_x, answers_y, answers_width, answers_length, "answers.png")
	lines = ocr("answers.png", "a_tmp.png")
	print("answers content:{}".format(lines))
	answers = extractAnswers(lines)

	print("step 3: search google")
	searchNcount(question, answers)


def winHqTrivia():
	now = "y"
	count = 0

	while True:
		now = input("take snap shot now?")
		if now == "n":
			break
		image_name = "{}_{}.png".format(args["image"], str(count))
		count+=1
		solveQuestion(image_name)
		print("next question\n")

winHqTrivia()
# for driver in drivers:
# 	driver.quit()