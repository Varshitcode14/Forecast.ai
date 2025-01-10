from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
from analytics.insights import DataAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        try:
            # Read the file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Get basic preview
            preview = df.head(5).to_dict(orient='records')
            columns = df.columns.tolist()
            
            # Get basic stats
            basic_stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_types': df.dtypes.astype(str).to_dict()
            }
            
            # Initialize analyzer and get insights
            analyzer = DataAnalyzer(df)
            insights = analyzer.get_all_insights()
            
            return jsonify({
                'preview': preview,
                'columns': columns,
                'basic_stats': basic_stats,
                'insights': insights
            })
            
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/insights')
def insights():
    return render_template('insights.html')

if __name__ == '__main__':
    app.run(debug=True)