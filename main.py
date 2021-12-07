from flask import Flask
app = Flask(__name__)

@app.route('/')
def dummy_endpoint():
    return 'Testing!'

if __name__ == '__main__':
    app.run() #run app (for testing, on localhost)