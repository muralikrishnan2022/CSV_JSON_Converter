from flask import Flask, request, redirect, url_for, render_template, send_file, flash
import csv
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def json_to_csv(json_file_path, csv_file_path):
    with open(json_file_path, mode='r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if data:
        csv_columns = data[0].keys()
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        json_path = os.path.join(app.config['CONVERTED_FOLDER'], file.filename.rsplit('.', 1)[0] + '.json')
        file.save(csv_path)
        csv_to_json(csv_path, json_path)
        return redirect(url_for('download_file', filename=os.path.basename(json_path)))

    elif file and file.filename.endswith('.json'):
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        csv_path = os.path.join(app.config['CONVERTED_FOLDER'], file.filename.rsplit('.', 1)[0] + '.csv')
        file.save(json_path)
        json_to_csv(json_path, csv_path)
        return redirect(url_for('download_file', filename=os.path.basename(csv_path)))

    else:
        flash('Invalid file format. Please upload a CSV or JSON file.')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
