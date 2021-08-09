import os, subprocess
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename

# Modified from theeko74/pdfc
# MIT license
def compress_pdf(f, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }
    outputfile = 'outputfile.pdf'
    print("Compress PDF...")
    initial_size = os.path.getsize(f)
    subprocess.call(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(outputfile),
                     f]
    )
    final_size = os.path.getsize(outputfile)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    return outputfile

def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config['UPLOAD_FOLDER'] = '/tmp'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/', methods=['POST'])
    def compress():
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            dst = secure_filename(uploaded_file.filename)
            uploaded_file.save(secure_filename(uploaded_file.filename))
            output = open(compress_pdf(dst), 'rb')
            return Response(output, mimetype="application/pdf")

    return app
