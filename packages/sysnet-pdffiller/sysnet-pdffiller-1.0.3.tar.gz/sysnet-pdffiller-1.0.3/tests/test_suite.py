#  Copyright (c) 2022. SYSNET s.r.o.
#  All rights reserved.
#
import os
from unittest import TestCase
from sysnet_pdf.pdf_utils import xfdf_to_dict, PDF_FACTORY
from settings import TEST_XFDF, TEST_PDF_OUT_FILE


class Test(TestCase):
    def test_xfdf_to_dict(self):
        d = xfdf_to_dict(TEST_XFDF)
        self.assertIsNotNone(d, 'xfdf_to_dict: OK')

    def test_fill_form(self):
        f = PDF_FACTORY
        out = f.create_pdf_from_xfdf(
            template_filename='051-certificate_form.pdf',
            xfdf_file_path=TEST_XFDF,
            pdf_file_name=TEST_PDF_OUT_FILE)
        self.assertIsNotNone(out, 'test_fill_form: Filled PDF')


