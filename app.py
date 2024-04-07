import csv
import os
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfReader
from flask import Flask, request, render_template, Response
from geocode import geocode_address

app = Flask(__name__)

def extract_text_from_pdf(pdf_file_path):
    text = ''
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_address(text):
    address_start_marker = "Address:"
    address_end_marker = "Phone:"
    
    address_start_index = text.find(address_start_marker)
    address_end_index = text.find(address_end_marker)
    
    if address_start_index != -1 and address_end_index != -1:
        address = text[address_start_index + len(address_start_marker):address_end_index].strip()
        return address
    else:
        return "Address not found"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return render_template('index.html', error="No file part")
        
        files = request.files.getlist('files[]')
        geocoded_locations = []  # Store geocoded locations
        
        for file in files:
            if file.filename == '':
                continue
            
            if file and file.filename.endswith('.pdf'):
                with NamedTemporaryFile(delete=False) as temp_pdf:
                    file.save(temp_pdf)
                    temp_pdf_path = temp_pdf.name
                
                text = extract_text_from_pdf(temp_pdf_path)
                address = extract_address(text)
                latitude, longitude = geocode_address(address)
                os.unlink(temp_pdf_path)
                
                geocoded_locations.append((address, latitude, longitude))
        
        csv_data = 'lng,lat\n'
        for location in geocoded_locations:
            csv_data += f'{location[2]},{location[1]}\n'  # lng,lat
        
        return render_template('index.html', geocoded_locations=geocoded_locations, csv_data=csv_data)
    
    return render_template('index.html', csv_data='')  # Ensure csv_data is passed as an empty string for initial render


@app.route('/download-csv')
def download_csv():
    csv_data = request.args.get('csv_data', '')
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition":
                    "attachment; filename=geocoded_addresses.csv"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False) 