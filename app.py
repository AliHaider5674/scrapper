from flask import Flask, jsonify, request, send_file, after_this_request
from validate_email import validate_email
import pandas as pd
import asyncio
import tracemalloc
# from pyppeteer import launch
# import pyshorteners
import io
import os

app = Flask(__name__)

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    print('uploading file')
    uploaded_file = request.files['file']
    result_array= []
    
    if uploaded_file and allowed_file(uploaded_file.filename):
        destination = os.path.join('uploads/',uploaded_file.filename)
        uploaded_file.save(destination)
        dataset = pd.read_excel(destination)
        column_name = 'Email'
        if column_name in dataset.columns:
            emails = dataset[column_name].tolist()
            # print(column_data)
        else:
            os.remove(destination)
            return "There is no Email column in excel file and file is deleted."
        
        for email in emails:
            result = validate_email(email_address=email,check_smtp = True,check_format=True, check_dns=True, smtp_from_address='nisar.khokar@focusteck.com', smtp_helo_host='smtp.mail.google.com', smtp_timeout=10, dns_timeout=10, check_blacklist=True, smtp_debug=False)
            # dataset['Validity'] = result
            result_array.append(result)
            
        #
        # dataset['Validity'] = result_array
        print(len(result_array))
        dataset['Validity'] = pd.Series(result_array)
        
        dataset.to_excel(destination, index=False)
        # column_data.to_excel(os.path.join('uploads/','emails.xlsx'), index=False)
        return "Data added"
        
    else:
        return {'error':'File upload failed, or invalid file type'}

def allowed_file(filename):
    ALLOWED_EXTS = ['xlsx']
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTS

@app.route('/hiturls' , methods = ['POST'])
async def main():
    try: 
        # type_tiny = pyshorteners.Shortener()
        tracemalloc.start()
        uploaded_file = request.files['file']
    
        if uploaded_file and allowed_file(uploaded_file.filename):
            destination = os.path.join('urluploads/',uploaded_file.filename)
            uploaded_file.save(destination)
            dataset = pd.read_excel(destination)

            url_column = 'url'
            if url_column in dataset.columns:
                urls = dataset[url_column].tolist()
                print(urls)
            else:
                os.remove(destination)
                return "There is no 'url' column in excel file and file is deleted."
        
            browser = await launch(
                headless = False,
                handleSIGINT=False,
                handleSIGTERM=False,
                handleSIGHUP=False)
            page = await browser.newPage()
            
            titles = []
            links = []
            for url in urls:
                await page.goto(f'http://www.google.com/search?q={url}+ceo+linkedin+ceo')
                print(f'Fetching data for {url}...')
                elements = await page.querySelectorAll('a')
                hrefs = []
                for element in elements:
                    href, title = await asyncio.gather(
                    element.getProperty('href'),
                    element.getProperty('innerText')
                    )
                    href_value = await href.jsonValue()
                    title_value = await title.jsonValue()
                    hrefs.append({
                        'href': href_value,
                        'title': title_value
                    })
                # links[len(links):] = hrefs[12][href]
                links.append(hrefs[12]['href']) 
                titles.append(hrefs[12]['title']) 
                   
                print(hrefs[12]['href'])
                
            dataset['link'] = pd.Series(links)
            dataset['name'] = pd.Series(titles)
            
            
            dataset.to_excel(destination, index=False)
            
            # short_url = type_tiny.tinyurl.short(long_url)
                
            await browser.close()
            
            return "Data Added"
            # asyncio.get_event_loop().run_until_complete(main())
        else:
            return "Data not updated"
        
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while processing the file"}), 500

 
def allowed_file(filename):
    ALLOWED_EXTS = ['xlsx']
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTS  

@app.route('/dnldurlfile', methods = ['GET'])
def dnldurlfile():
    try:
        args = request.args
        file_name = args.get('name')
        file_path = os.path.join('urluploads/', file_name)
        
        return_data = io.BytesIO()
        with open(file_path, 'rb') as fo:
            return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
        return_data.seek(0)

        os.remove(file_path)
        
        return send_file(return_data, as_attachment=True, mimetype='application/vnd.ms-excel', download_name='Ids.xlsx')
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while downloading the file"}), 500
    
@app.route('/dnldemailfile', methods = ['GET'])
def dnldemailfile():
    try:
        args = request.args
        file_name = args.get('name')
        file_path = os.path.join('uploads/', file_name)
        
        return_data = io.BytesIO()
        with open(file_path, 'rb') as fo:
            return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
        return_data.seek(0)

        os.remove(file_path)
    
        return send_file(file_path, as_attachment=True, mimetype='application/vnd.ms-excel', download_name='updated.xlsx')
        # print("Helloo")
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while downloading the file"}), 500 

# Run the flask App
if __name__ == '__main__':
    app.run(debug=True)