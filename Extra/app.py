from flask import Flask, render_template, request, url_for, redirect
import json
app = Flask(__name__)

@app.route("/", methods = ['POST','GET'])
def hello():
	if(request.method == 'POST'):
		return 'ac'
	return render_template('char.html')
	
@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return jsdata
	
#@app.route("/page")
#def page():
#	if(request.method == "POST"):
#		return render_template('abc.html')

#@app.route('/postmethod', methods = ['POST','GET'])
#def get_post_javascript_data():
#	if(request.method == "POST"):
#		jsdata = request.form['javascript_data']
#		return jsdata

#@app.route('/getpythondata')
#def get_python_data():
#	pythondata = {'name' : 'Balraj'}
#	return json.dumps(pythondata)

if __name__ == '__main__':
    app.run(debug=True)