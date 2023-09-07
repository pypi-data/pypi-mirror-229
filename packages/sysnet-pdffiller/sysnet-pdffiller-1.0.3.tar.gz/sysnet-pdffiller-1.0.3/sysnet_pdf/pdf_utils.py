#  Copyright (c) 2022. SYSNET s.r.o.
#  All rights reserved.
#
#
from __future__ import annotations

import os
import shutil
import sysnet_pyutils.utils as pu
from datetime import datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import PyPDF3
from PyPDF3 import PdfFileWriter, PdfFileMerger
from PyPDF3.generic import NameObject, IndirectObject, BooleanObject, NumberObject
from fillpdf.fillpdfs import write_fillable_pdf

from settings import PDF_OUTPUT_DIR, PDF_TEMP_FILE, PDF_OWNER_PASSWORD, \
    PDF_TEMPLATES_DIR, LOG, CONFIG, CC
from sysnet_pdf.config import PdfError

EXTENSION_PDF = 'pdf'
EXTENSION_JASPER = 'jrxml'
TEMPLATE_TYPE_PDF = 'pdf'
TEMPLATE_TYPE_JASPER = 'jasper'
TEMPLATE_TYPE_OTHER = 'other'
KEY_TEMPLATES_PDF = 'pdf_templates'
KEY_TEMPLATES_JASPER = 'jasper_templates'


def xfdf_to_dict(filename=None):
    if filename is None:
        raise PdfError(module=__name__, message='Data filename is missing')
    if not os.path.exists(filename):
        raise PdfError(module=__name__, message='Data file not found: {}'.format(filename))
    try:
        tree = ElementTree.parse(filename)
        root = tree.getroot()
        fields = None
        for child in root:
            if 'fields' in child.tag:
                fields = child
        field_list = []
        data = {}
        for child in fields:
            if 'field' in child.tag:
                field_list.append(child)
                key = child.attrib['name']
                for child2 in child:
                    val = child2.text
                    if val is None:
                        val = ''
                    elif val.startswith('D:'):
                        val = fdf_date(val)
                    data[key] = val
        return data
    except ParseError as e:
        raise PdfError(message=str(e), module=__name__)


def fdf_date(date_str):
    date_time_obj = datetime.strptime(date_str, 'D:%Y%m%d')
    return '{}.{}.{}'.format(date_time_obj.day, date_time_obj.month, date_time_obj.year)


def set_need_appearances_writer(writer_object):
    """

    :type writer_object: PdfFileWriter
    """
    # basically used to ensured there are not
    # overlapping form fields, which makes printing hard
    try:
        catalog = writer_object._root_object
        # get the AcroForm tree and add "/NeedAppearances attribute
        if "/AcroForm" not in catalog:
            writer_object._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer_object._objects), 0, writer_object)})
        need_appearances = NameObject("/NeedAppearances")
        writer_object._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
    return writer_object


def flatten_pdf(input_pdf=PDF_TEMP_FILE, data_dict=None, output_pdf=None, user_password=None):
    try:
        input_stream = open(input_pdf, "rb")
        pdf_reader = PyPDF3.PdfFileReader(input_stream, strict=False)
        if "/AcroForm" in pdf_reader.trailer["/Root"]:
            pdf_reader.trailer["/Root"]["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)})
        pdf_writer: PdfFileWriter = PyPDF3.PdfFileWriter()
        set_need_appearances_writer(pdf_writer)
        if "/AcroForm" in pdf_writer._root_object:
            # Acro form is form field, set needs appearances to fix printing issues
            pdf_writer._root_object["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)})
        pdf_writer.addPage(pdf_reader.getPage(0))
        page = pdf_writer.getPage(0)
        # update form fields
        # pdf_writer.updatePageFormFieldValues(page, data_dict)
        for j in range(0, len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()
            for field in data_dict:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/Ff"): NumberObject(1)  # make ReadOnly
                    })
        if user_password is None:
            user_password = ''
        pdf_writer.encrypt(user_pwd=user_password, owner_pwd=PDF_OWNER_PASSWORD)
        path = os.path.dirname(output_pdf)
        if not os.path.exists(path=path):
            os.makedirs(path)
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
        output_stream = open(output_pdf, 'wb')
        pdf_writer.write(output_stream)
        output_stream.close()
        input_stream.close()
        return output_pdf
    except Exception as e:
        raise PdfError(message=str(e), module=__name__)


def parse_template_type(source_path=None):
    if source_path is None:
        return ''
    filename = os.path.split(source_path)[-1]
    ext = filename.split('.')[-1]
    if ext.lower() == EXTENSION_PDF:
        return TEMPLATE_TYPE_PDF
    elif ext.lower() == EXTENSION_JASPER:
        return TEMPLATE_TYPE_JASPER
    else:
        return TEMPLATE_TYPE_OTHER


class PdfFactory(object, metaclass=pu.Singleton):
    def __init__(self):
        self.pdf_templates = CONFIG['templates']['pdf']
        self.jasper_templates = CONFIG['templates']['jasper']
        LOG.logger.info('PdfFactory created')

    def _identify_template_type(self, source_path=None):
        template_type = parse_template_type(source_path=source_path)        # PDF/JASPER
        if template_type == TEMPLATE_TYPE_PDF:
            templates = self.pdf_templates
            templates_key = KEY_TEMPLATES_PDF
        elif template_type == TEMPLATE_TYPE_JASPER:
            templates = self.jasper_templates
            templates_key = KEY_TEMPLATES_JASPER
        else:
            raise PdfError(message='Invalid template type {}.'.format(template_type), module=__name__)
        return template_type, templates, templates_key

    def add_template(self, source_path=None, remove_source=False):
        if not os.path.exists(path=source_path):
            raise PdfError(message='Template source not found: {}'.format(source_path), module=__name__)
        if not os.path.isfile(path=source_path):
            raise PdfError(message='Template source is not file: {}'.format(source_path), module=__name__)
        template_type, templates, templates_key = self._identify_template_type(source_path=source_path)
        filename = os.path.split(source_path)[-1]
        if filename in templates:
            raise PdfError(message='Template filename {} already exists.'.format(filename), module=__name__)
        if source_path is None:
            raise PdfError(message='Template source path is missing', module=__name__)
        target_path = os.path.join(PDF_TEMPLATES_DIR, filename)
        if not os.path.exists(path=target_path):
            target_path = shutil.copy2(source_path, PDF_TEMPLATES_DIR)
        else:
            remove_source = False
        if filename not in CONFIG['templates'][template_type]:
            CONFIG['templates'][template_type].append(filename)
            CC.store()
        if filename not in templates:
            templates.append(filename)
        if remove_source:
            os.remove(source_path)
        LOG.logger.info('Added {} template {}: {}'.format(template_type.upper(), filename, target_path))

    def replace_template(self, source_path=None, remove_source=False):
        if source_path is None:
            raise PdfError(message='Template source path is missing', module=__name__)
        if not os.path.exists(path=source_path):
            raise PdfError(message='Template source not found: {}'.format(source_path), module=__name__)
        if not os.path.isfile(path=source_path):
            raise PdfError(message='Template source is not file: {}'.format(source_path), module=__name__)
        template_type, templates, templates_key = self._identify_template_type(source_path=source_path)
        filename = os.path.split(source_path)[-1]
        if filename not in templates:
            raise PdfError(message='Template {} does not exist.'.format(filename), module=__name__)
        target_path = os.path.join(PDF_TEMPLATES_DIR, filename)
        orig_path = target_path
        if os.path.exists(path=orig_path):
            os.remove(path=orig_path)
        if os.path.exists(path=target_path):
            os.remove(path=target_path)
        target_path = shutil.copy2(source_path, PDF_TEMPLATES_DIR)
        if remove_source:
            os.remove(source_path)
        LOG.logger.info('Replaced {} template {}: {}'.format(template_type.upper(), filename, target_path))

    def remove_template(self, filename=None):
        if filename is None:
            raise PdfError(message='Template filename is missing', module=__name__)
        template_path = os.path.join(PDF_TEMPLATES_DIR, filename)
        template_type, templates, templates_key = self._identify_template_type(source_path=template_path)
        if not os.path.exists(path=template_path):
            raise PdfError(message='Template not found: {}'.format(template_path), module=__name__)
        if not os.path.isfile(path=template_path):
            raise PdfError(message='Template is not file: {}'.format(template_path), module=__name__)
        if filename in templates:
            templates.remove(filename)
        if filename in CONFIG['templates'][template_type]:
            CONFIG['templates'][template_type].remove(filename)
            CC.store()
        orig_path = template_path
        if os.path.exists(path=orig_path):
            os.remove(path=orig_path)
        LOG.logger.info('Deleted {} template: {}'.format(template_type.upper(), filename))

    def fill_pdf_form(self, template_filename, data=None, out_filename=PDF_TEMP_FILE):
        if data is None:
            raise PdfError(module=__name__, message='Data is missing')
        templates = self.pdf_templates
        if template_filename is None:
            raise PdfError(module=__name__, message='PDF template filename missing')
        if template_filename not in templates:
            raise PdfError(module=__name__, message='PDF template {} not found'.format(template_filename))
        if out_filename is None:
            out_filename = PDF_TEMP_FILE
        out_filename = os.path.join(PDF_OUTPUT_DIR, out_filename)
        try:
            if os.path.exists(out_filename):
                os.remove(out_filename)
            write_fillable_pdf(os.path.join(PDF_TEMPLATES_DIR, template_filename), out_filename, data)
            return out_filename
        except KeyError:
            return None

    def create_pdf_from_xfdf(self, template_filename=None, xfdf_file_path=None, pdf_file_name=None):
        """
        Creates read and print only PDF form XFDF data and PDF template. Main function.
        :param template_filename:    PDF template filename
        :param xfdf_file_path:   XFDF file full path
        :param pdf_file_name:    Output PDF file name. File is stored to PDF_OUTPUT_DIR
        :return:    Created PDF file full path
        """

        pdf_file_path = os.path.join(PDF_OUTPUT_DIR, pdf_file_name)
        data = xfdf_to_dict(filename=xfdf_file_path)
        self.fill_pdf_form(template_filename=template_filename, data=data)
        return flatten_pdf(data_dict=data, output_pdf=pdf_file_path)

    def check_templates(self):
        out = {'pdf': [],  'jasper': []}
        for item in self.pdf_templates:
            fname = item
            fpath = os.path.join(PDF_TEMPLATES_DIR, fname)
            exists = os.path.exists(fpath)
            t = (fname, fpath, exists)
            out['pdf'].append(t)
        for item in self.jasper_templates:
            fname = item
            fpath = os.path.join(PDF_TEMPLATES_DIR, fname)
            exists = os.path.exists(fpath)
            t = (fname, fpath, exists)
            out['jasper'].append(t)
        return out


def pdf_merge(pdf_list, delete_parts=False):
    if pdf_list is None:
        return None
    if not bool(pdf_list):
        return None
    if len(pdf_list) == 1:
        return pdf_list[0]
    dirname = os.path.dirname(pdf_list[0])
    basename = os.path.basename(pdf_list[0])
    out_filename = '{}_merged.pdf'.format(basename.split('.')[0])
    out_filepath = os.path.join(dirname, out_filename)
    merger = PdfFileMerger()
    for item in pdf_list:
        merger.append(item)
    merger.write(out_filepath)
    merger.close()
    if delete_parts:
        for item in pdf_list:
            if os.path.exists(item):
                os.remove(item)
    return out_filepath


PDF_FACTORY = PdfFactory()
