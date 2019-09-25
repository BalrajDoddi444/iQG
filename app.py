import os
from flask import Flask, render_template, url_for, json, request, redirect
from bs4 import BeautifulSoup
import re
import requests
import AquaWithObject as awo
from random import shuffle
import os.path
import PyPDF2
from werkzeug import secure_filename 
import urllib.request as url 

app = Flask(__name__)

#########################################################################################
@app.route("/")
@app.route("/home", methods=['GET','POST'])
def home():
	return render_template('home.html', title="iQGenerator - Home")


#########################################################################################
@app.route("/")
@app.route("/HowItWorks")
def HowItWorks():
	return render_template('HowItWorks.html', title="iQGenerator - How It Works")


#########################################################################################
@app.route("/TutorialList", methods=['GET', 'POST'])
def TutorialList():
	data = readTutorialListJson()
	return render_template('TutorialList.html', title="iQGenerator - TutorialList", posts=data)


#########################################################################################
@app.route("/TopicContent/<id>", methods=['GET', 'POST'])
def TopicContent(id):
	try:
		data = {"Id":(id.replace('_',' ')).title(),"sample_text":wikiScrapping(id)}
	#	return str(data)
		return render_template("TopicContent.html", title="iQGenetator - Topic" ,message=data)
	except:
		return redirect('/TutorialList')

#########################################################################################
global scraped_questionSet
scraped_questionSet = []
@app.route("/Questions/<Topic_name>")
def Questions(Topic_name):
	try:
		# SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
		# json_url = os.path.join(SITE_ROOT, "static/json", "Quiz.json")
		# data = json.load(open(json_url))
		# data = data.get("Quiz","")
		
		############	Getting data from Topic Content    ############
		scraped_data = url.urlopen('https://en.wikipedia.org/wiki/'+Topic_name)
		article = scraped_data.read()
		
		parsed_article = BeautifulSoup(article,'lxml')
		sample_text = ""
		paragraphs = parsed_article.find_all('p')
		
		for p in paragraphs:
			sample_text += p.text
			
		aqua = awo.Aqua(sample_text)
		json_url = aqua.finalQuestions()
		data = json.loads(json_url)
		data = data.get("quiz","")

		############		   	Shuffling  			   ############ 
		shuffle(data)
		for x in data:
			shuffle(x['Options'])

		global scraped_questionSet
		scraped_questionSet = data
		# return str(scraped_questionSet)
		return render_template("Questions.html",title="iQGenerator - Quiz",posts=scraped_questionSet)	
	except:
		return redirect('/TopicContent/'+Topic_name)

########################################################################################
@app.route("/Result/<data>")
def Result(data):
	global scraped_questionSet

	dataArray = data.split(',')
	actual_answer = []

	for questionSet in scraped_questionSet:
		actual_answer.append(questionSet['Answer'])
	
	count = 0
	for actual, answered in zip(dataArray,actual_answer):
		if(actual == answered):
			count+=1
	result = {
		'NOQuestions' : len(actual_answer),
		'correctAns' : count,
		'worngAns' : len(actual_answer)-count,
		'score' : round(count/len(actual_answer)*100,2)
	}
	return render_template("Result.html",title="iQGenerator - Result", result=result)


########################################################################################
# External Functions
########################################################################################

def readTutorialListJson():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "static/json", "tutorialList.json")
	data = json.load(open(json_url))
	data = data.get("Topics","")
	return data


########################################################################################
def wikiScrapping(id):
	tpoint = requests.get('https://en.wikipedia.org/wiki/'+id)
	soup = BeautifulSoup(tpoint.text,'html.parser')
	contents = soup.find(class_='mw-body').find_all(['p','h2','h3'])
	lst =[]
	contentwrapper = []
	topicName = "Home"
	for i in range(len(contents)):
		if(str(contents[i])[1:3]=='p>' or str(contents[i])[1:3]=='h3'):
			para = contents[i].text
			para = re.sub(r'\[[0-9]*\]','',para)
			para = re.sub(r".*?\{(.*?)\}", '', para)
			para = re.sub(r'\[[a-z_ ]*\]', '', para)
			para = re.sub("\n","",para)
			if(str(contents[i])[1:3]=='p>'):
				temp ={}
				temp["type"] = "P"
				temp["text"] = para
				lst.append(temp)
			else:
				temp = {}
				temp["type"] = "h3"
				temp["text"] = para
				lst.append(temp)
		if(str(contents[i])[1:3]=='h2'):
			if(str(contents[i].text)!='Contents'):
				tempDict = {}
				topicName = re.sub(r'\[[a-z]*\]', '', topicName)
				tempDict["TopicName"] = topicName
				tempDict["Content"] = lst
				topicName = contents[i].text
				lst = []
				contentwrapper.append(tempDict)
	outlist = []
	for cont in contentwrapper:
		if len(str(cont))>400:
			outlist.append(cont)
	return outlist
	#############################################
# UPLOAD_FOLDER = './mark'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# @app.route('/upload')
# def upload_file():
#    return render_template('TutorialList.html')
	
# @app.route('/uploader', methods = ['GET', 'POST'])
# def uploafile():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
#       x=f.filename
#       extension=x.split(".")[-1]
#       print(extension)
#       sample_text=""
#       count=0
#       if extension == 'pdf':
#          pdfFileObj = open(x, 'rb')
#          pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
#          num_pages=pdfReader.numPages
#          while count < num_pages:
#              pageObj = pdfReader.getPage(count)
#              count +=1
#              sample_text += pageObj.extractText()
#          sample_text+=pageObj.extractText()
#          return render_template("resultfile.html",message = sample_text)
UPLOAD_FOLDER = './mark'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploafile():
	try:
		if request.method == 'POST':
			f = request.files['file']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
			x=f.filename
			extension=x.split(".")[-1]
		  
		#   print(extension)
			sample_text=""
			count=0
			if extension == 'pdf':
				pdfFileObj = open('mark/'+x, 'rb')
				pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
				num_pages=pdfReader.numPages
				while count < num_pages:
					pageObj = pdfReader.getPage(count)
					count +=1
					sample_text += pageObj.extractText()
			 # creating a page object 
			# pageObj = pdfReader.getPage(1) 
			 # extracting text from page 
			sample_text+=pageObj.extractText()


			# return sample_text

			aqua = awo.Aqua(sample_text)
			json_url = aqua.finalQuestions()
			data = json.loads(json_url)
			data = data.get("quiz","")

			############		   	Shuffling  			   ############ 
			shuffle(data)
			for x in data:
				shuffle(x['Options'])

			global scraped_questionSet
			scraped_questionSet = data
			# return str(scraped_questionSet)
			# return sample_text
			return render_template("Questions.html",title="iQGenerator - Quiz",posts=scraped_questionSet)
	except:
		return redirect("/TutorialList")
		# return render_template("resultfile.html",message = sample_text)
         
      #mark = open(x, "r")
      #fin =mark.readline()
      #return fin
         

if __name__ == '__main__':
	app.run(debug=True)
