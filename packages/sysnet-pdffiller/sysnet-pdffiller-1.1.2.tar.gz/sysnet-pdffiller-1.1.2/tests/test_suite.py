#  Copyright (c) 2022, 2023. SYSNET s.r.o.
#  All rights reserved.
#
from unittest import TestCase

from settings import TEST_XFDF, TEST_PDF_OUT_FILE
from sysnet_pdf.pdf_utils import PDF_FACTORY


class Test(TestCase):
    def test_xfdf_to_dict(self):
        d = PDF_FACTORY.xfdf_to_dict(TEST_XFDF)
        self.assertIsNotNone(d, 'xfdf_to_dict: OK')

    def test_fill_form(self):
        f = PDF_FACTORY
        out = f.create_pdf_from_xfdf(
            template_filename='051-certificate_form.pdf',
            xfdf_file_path=TEST_XFDF,
            pdf_file_name=TEST_PDF_OUT_FILE)
        self.assertIsNotNone(out, 'test_fill_form: Filled PDF')
