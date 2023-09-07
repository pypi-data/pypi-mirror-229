#  Copyright (c) 2022. SYSNET s.r.o.
#  All rights reserved.
#
import os

from pyreportjasper import PyReportJasper

from settings import PDF_TEMPLATES_DIR
from tests.test_suite import TEST_DATA_DIRECTORY


def json_to_pdf():
    input_file = os.path.join(PDF_TEMPLATES_DIR, 'picture_cert.jrxml')
    output_file = os.path.join(TEST_DATA_DIRECTORY, 'jasper_out')
    conn = {
        'driver': 'json',
        'data_file': os.path.join(TEST_DATA_DIRECTORY, 'picture_cert_data.json'),
        'json_query': ''
    }
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
        input_file,
        output_file,
        output_formats=["pdf"],
        db_connection=conn
    )
    pyreportjasper.process_report()
    del pyreportjasper
    print('Result is the file below.')
    print(output_file + '.pdf')
