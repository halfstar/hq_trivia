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

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done")
args = vars(ap.parse_args())


def captureScreen(x, y, wide, length, output):
    subprocess.run(
        ["screencapture", "-R{},{},{},{}".format(x, y, wide, length), output])


def ocr(image_file):
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
	filename = "{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)
	text = pytesseract.image_to_string(Image.open(filename))
	os.remove(filename)
	lines = text.splitlines()
	return lines


# step 2: extract & clean question and answers
def extractNclean(lines):
	question = ""
	answers = []
	# extract
	is_question_done = False
	for line in lines:
		line = line.strip().lower()
		if len(line) > 3:
			if is_question_done:
				answers.append(line)
			else:
				question += " " + line
				if line.find('?') != -1:
					is_question_done = True
	# clean
	stop_words = ["which ", "what ", "has ", "have ", "had ",
				"is ", "are ", "was ", "were ",
				"these ", "those ", "this ", "that ",
				"of ", "a ", "an ", "?"]
	for word in stop_words:
		question = question.replace(word, "")
	print("question = {}".format(question))

	for i, ans in enumerate(answers):
		print("ans{} = {}".format(i, ans))
	print("\n")
	return question, answers

print("step 3: search google")
# step 3: using custom search api question + answer

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
		#print(json.dumps(res,indent=4))

# for ans in answers:
# 	driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
# 	driver.get('http://www.google.com/search?q={}'.format(question+" "+ans))

# done=input('done:')
# driver.quit()

def solveQuestion(image_name):
	print("step 1: OCR")
	captureScreen(20, 100, 500, 500, image_name)
	lines = ocr(image_name)
	print("image content:{}".format(lines))

	print("step 2: extracting info")
	question, answers = extractNclean(lines)

	print("step 3: search google")
	searchNcount(question, answers)


def winHqTrivia():
	now = "y"
	count = 0
	while now == "y" :
		now = input("take snap shot now?")
		image_name = "{}_{}.png".format(args["image"], str(++count))
		solveQuestion(image_name)
		print("\n next question\n")

winHqTrivia()