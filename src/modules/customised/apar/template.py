from datetime import datetime
from trytond.model import (ModelSQL, ModelView, ModelSingleton, fields)
from trytond.pyson import Bool
from trytond.pool import PoolMeta


__all__ = [
    'AparFormTemplate', 'EmployeeDesignation',
    'AparFormTemplatePart', 'AparFormTemplateSection',
    'AparFormTemplateQuestions'
]


class AparFormTemplate(ModelSQL, ModelView):
    'Apar Form Template'

    __name__ = 'apar.form.template'

    name = fields.Char('Name', required=True)
    form_number = fields.Integer('Form Number', required=True)
    designations = fields.One2Many(
        'employee.designation', 'template', 'Designations', readonly=True)
    parts = fields.One2Many(
       'apar.form.template.part', 'template', 'Parts for APAR')


class EmployeeDesignation(metaclass=PoolMeta):
    "Employee Designation"

    __name__ = "employee.designation"

    is_apar_generate = fields.Boolean('Is APAR to be Generated ?')
    template = fields.Many2One('apar.form.template', 'APAR Template')

    @staticmethod
    def default_is_apar_generate():
        return False



class AparFormTemplatePart(ModelSQL, ModelView):
    'Apar Form Template Part'

    __name__ = 'apar.form.template.part'

    name = fields.Char("Name")
    number = fields.Char("Number")
    questions = fields.One2Many(
        'apar.form.template.question', 'part', 'Descriptions')
    template = fields.Many2One(
        'apar.form.template', 'Template', required=True)
    sections = fields.One2Many(
        'apar.form.template.section', 'part', 'Sections')
    type_ = fields.Selection(
        [
            ('self_appraisal', 'Self Appraisal'),
            ('appraisal', 'Appraisal'),
            ('reviewing', 'Reviewing'),
            ('accepting','Accepting')
        ], 'Type'
    )

    def get_rec_name(self, name):
        """<Template Name> - <Part Name>"""
        return ("%s - %s" % (self.template.name, self.name))


class AparFormTemplateSection(ModelSQL, ModelView):
    'Apar Form Template Section'

    __name__ = 'apar.form.template.section'

    name = fields.Char('Section Name')
    number = fields.Char('Section Number')
    weightage = fields.Integer('Weightage (in percentage)')
    questions = fields.One2Many(
        'apar.form.template.question', 'section', 'Questions')
    part = fields.Many2One('apar.form.template.part', 'Part')


class AparFormTemplateQuestions(ModelSQL, ModelView):
    'Apar Form Template Questions'

    __name__ = 'apar.form.template.question'

    question_no = fields.Text('Question Number', required=True)
    name = fields.Text('Question', required=True)
    section = fields.Many2One('apar.form.template.section', 'Section')
    part = fields.Many2One('apar.form.template.part', 'Part')
