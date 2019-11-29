from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval
import datetime
from trytond.model import Workflow
from trytond.pool import Pool, PoolMeta

__all__ = ['HrSalaryRule']


class HrSalaryRule(ModelSQL, ModelView):
    'Salary Rule'

    __name__ = 'hr.salary.rule'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active')
    category = fields.Many2One('hr.salary.rule.category', 'Category')
    condition_select = fields.Selection(
        [
            ('always_true', 'Always True'),
            ('range', 'Range'),
            ('python_code', 'Python Code'),
        ], 'Condition Type', required=True)
    condition_range_max = fields.Float('Maximum Range', states={
            'invisible': ~Eval('condition_select').in_(['range'])
    }, depends=['condition_select'])
    condition_range_min = fields.Float('Minimum Range', states={
            'invisible': ~Eval('condition_select').in_(['range'])
    }, depends=['condition_select'])
    amount_select = fields.Selection(
        [
            ('percentage', 'Percentage'),
            ('fix', 'Fix'),
            ('code', 'Code')
        ], 'Amount Type' , required=True)
    amount_fix = fields.Float('Fix Amount', states={
            'invisible': ~Eval('amount_select').in_(['fix'])
        }, depends=['amount_select'])
    amount_percentage = fields.Float('Percentage(%)', states={
            'invisible': ~Eval('amount_select').in_(['percentage'])
        }, depends=['amount_select'])
    percentage_based = fields.Many2One('hr.salary.rule', 'Percentage Based on', states={
            'invisible': ~Eval('amount_select').in_(['percentage'])
        }, depends=['amount_select'])
    note = fields.Text('Description')
    priority = fields.Integer('Priority' , required=True)

    @staticmethod
    def default_active():
        return True
    
    @classmethod
    def validate(cls, records):
        super(HrSalaryRule,cls).validate(records)
        for record in records:
            if record.amount_select == 'amount_percentage':
                if record.amount_percentage not in range(0,101):
                    cls.raise_user_error('Invalid Amount')
    
    @staticmethod
    def default_condition_select():
        return 'always_true'

    def check(self, payslip, employee, contract):
        if self.condition_select == 'always_true':
            return True
        if self.condition_select == 'range':
            pass
            #TODO: Write the code for range here
            return True
        if self.condition_select == 'python_code':
            method_name = "check_" + str(self.code)
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                res = method(payslip, employee, contract)
                return res
            else:
                #TODO: Raise error that the rule has python_code as condition but there is no method
                return True

    def calculate(self, payslip, employee, contract):
        method_name = "calculate_" + str(self.code)
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            print(method, "methodmethod")
            res = method(payslip, employee, contract)
            print(res, "RESESE")
            return res

    def calculate_GROSS(self, payslip, employee, contract):
        amount = 0
        payslip_line = Pool().get('hr.payslip.line')
        payslip_lines = payslip_line.search([
            ('category.code', 'in', ('BASIC','ALW'))])
        if payslip_lines:
            for line in payslip_lines:
                if line.payslip == payslip:
                    amount += line.amount
        return amount
    
    def calculate_BASIC(self, payslip, employee, contract):
        return self.calculate_NEW_BASIC(payslip, employee, contract)

    def calculate_NET(self, payslip, employee, categories):
        amount = 0
        '''
        Takes Parameters - payslip, employee and #categories

        returns the value of Non Practicing Allowance to be added
        '''
        # TODO: categories to be corrected
        gross = self.calculate_GROSS(payslip, employee, categories)
        payslip_line = Pool().get('hr.payslip.line')
        payslip_lines = payslip_line.search([
            ('category.code', '=', 'DED')])
        if payslip_lines:
            for line in payslip_lines:
                if line.payslip == payslip:
                    amount += line.amount
        return gross - amount
    
    def calculate_NPA(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Non Practicing Allowance to be added
        '''
        if employee.designation.name in ("Scientist I",
                                         "Scientist I (Absorption)" ,
                                         "Scientist II",
                                         "Scientist II (Absorption)",
                                         "Scientist III",
                                         "Scientist III (Absorption)" ,
                                         "Scientist IV",
                                         "Scientist IV (Absorption)", 
                                         "Scientist V (Absorption)", 
                                         "Assistant Professor", 
                                         "Associate Professor", 
                                         "professor", 
                                         "Lecturer", 
                                         "Principal", 
                                         "Director",
                                    ):
            # TODO: Check for faculty designations, might 
            # coincide with nursing faculty. Requires only MBBS
            npa = (0.2 * contract.basic)
            return npa
        else:
            npa = 0
            return npa

    def calculate_NEW_BASIC(self, payslip, employee, contract):
        npa = self.calculate_NPA(payslip, employee, contract)
        if npa:
            # TODO: change the rules for new_basic if any
            new_basic = npa + contract.basic
            if new_basic > 23750:
                new_basic = 23750
            return new_basic
        else:
            new_basic = contract.basic
            return new_basic

    def calculate_DA(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Dearness Allowance to be added
        '''
        if self.calculate_NEW_BASIC(payslip, employee, contract):
            # TODO: change the rules for new_basic
            dear_alw = (0.12 * self.calculate_NEW_BASIC(payslip, employee, contract))
            return dear_alw
        else:
            dear_alw = (0.12 * contract.basic)
            return dear_alw

    def calculate_NURSING_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Nursing Allowance to be added
        '''
        if employee.designation.name in ("Assistant Nursing Superintendent",
                                         "Chief Nursing Officer",
                                         "Deputy Nursing Superintendent",
                                         "Nursing Officer",
                                         "Nursing Superintendent",
                                         "Sr. Nursing Officer",
                                         "Public Health Nurse",
                                         "Public Health Nurse (Supervisor)",
                                         "Tutor in Nursing",
                                         "Senior Nursing Tutor",
                                         "Senior Nursing Officer",
                                    ):
            nurse_alw = 7200
            return nurse_alw
        return None

    def calculate_TRANSPORT_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Transport Allowance to be added
        '''
        # TODO: Write the condition if the employee is handicapped
        # if employee.handicap_status == True:
        trans_alw = 0
        if int(employee.grade_pay.name) >= 5400:
            trans_alw = 7200 + self.calculate_DA(payslip, employee, contract)
        elif int(employee.grade_pay.name) < 5400:
            trans_alw = 3600 + self.calculate_DA(payslip, employee, contract)
        elif (employee.pay_in_band) > 17:
            trans_alw = 14400 + self.calculate_DA(payslip, employee, contract)
        elif (employee.designation.name) == 'Centre Chief':
            trans_alw = 15750 + self.calculate_DA(payslip, employee, contract)
        if employee.category == "ph":
            trans = trans_alw * 2
            trans_alw = trans
        else:
            trans_alw = trans_alw
        return trans_alw

    def calculate_HPCA(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Hospital Patient Care Allowance to be added
        '''
        if employee.group == "C" or employee.group == "D":
            if employee.grade_pay >= 1800 and  \
               employee.grade_pay <= 2800:
                hpca = 4100
                return hpca
        return None

    def calculate_ACAD_ALW(self, payslip, employee, contract):
        # TODO: Check for Faculty designations
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Academic Allowance to be added
        '''
        if employee.designation.name in ("Assistant Professor", 
                                         "Associate Professor", 
                                         "Professor", 
                                         "Lecturer", 
                                         "Principal", 
                                         "Director",
                                    ):
            acad_alw = 22500
            return acad_alw
        return None

    def calculate_UNIFORM_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Uniform Allowance to be added
        '''
        if employee.designation.name in ("Assistant Nursing Superintendent",
                                         "Chief Nursing Officer",
                                         "Deputy Nursing Superintendent",
                                         "Nursing Officer",
                                         "Sr. Nursing Officer",
                                         "Nursing Superintendent",
                                         "Public Health Nurse",
                                         "Public Health Nurse (Supervisor)",
                                         "Tutor in Nursing",
                                         "Senior Nursing Tutor",
                                         "Senior Nursing Officer",
                                    ):
            uni_alw = 1800
            return uni_alw
        return None

    def calculate_DEP_ALW(self, payslip, employee, contract):
        
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Deputation Allowance to be added
        '''
        pass

    def calculate_TOOL_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Tool Allowance to be added
        '''
        if employee.group == "D" and employee.department == "Engineering Services Division (ESD)":
            if employee.designation.name in ("Plumber",
                                             "Meson",
                                             "Electrician",
                                             "Wireman",
                                             "Foreman",
                                             "Mechanic",
                                        ):
                tool_alw = 10
                return tool_alw
            elif employee.designation.name == "Carpenter":
                tool_alw = 15
                return tool_alw
            elif employee.designation.name == "Mali":
                tool_alw = 180
                return tool_alw
        return None

    def calculate_OT(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Overtime Allowance to be added
        '''
        pass

    def calculate_QPAY(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Qualification Pay Allowance to be added
        '''
        pass


    def calculate_DRESS_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Dress Allowance to be added
        '''
        if datetime.date.today().month == 7:
            if employee.designation.name in ("Hospital Attendant Grade I",
                                             "Hospital Attendant Grade II",
                                             "Hospital Attendant Grade III",
                                             "Sanitary Attendant Grade I",
                                             "Sanitary Attendant Grade II",
                                             "Sanitary Attendant Grade III",
                                        ):
                dress_alw = 5000
                return dress_alw
        else:
            dress_alw = 0
            return dress_alw

    def calculate_ICU_ALW(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of ICU Allowance to be added
        '''
        pass

    def calculate_CHTA(self, payslip, employee, contract):
        pass


    def calculate_EHS(self, payslip, employee, contract):
        '''
        Takes parameters - payslip, employee and contract

        returns the value of EHS to be deducted
        '''
        if int(employee.grade_pay.name) >= 7600:
            ehs = 1000
            return ehs
        elif int(employee.grade_pay.name) >= 4600 and \
            int(employee.grade_pay.name) <= 6600:
            ehs = 650
            return ehs
        elif int(employee.grade_pay.name) == 4200:
            ehs = 450
            return ehs
        elif int(employee.grade_pay.name) < 4200:
            ehs = 250
            return ehs

    def calculate_KU(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of KARMCHARI UNION to be deducted
        '''
        if employee.employee_group in ("C", "D"):
            karmchari_ded = 10
            return karmchari_ded
        return None

    def calculate_OA(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of OFFICER ASSOCIATION to be deducted
        '''
        if employee.employee_group in ("A", "B"):
            officer_ded = 20
            return officer_ded
        return None

    def calculate_NU(self, payslip, employee, contract):
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of NURSING UNION to be deducted
        '''
        if employee.designation.name in ("Assistant Nursing Superintendent",
                                         "Chief Nursing Officer",
                                         "Deputy Nursing Superintendent",
                                         "Nursing Officer",
                                         "Nursing Superintendent",
                                         "Sr. Nursing Officer",
                                         "Public Health Nurse",
                                         "Public Health Nurse (Supervisor)",
                                         "Tutor in Nursing",
                                         "Senior Nursing Tutor",
                                         "Senior Nursing Officer",
                                    ):
            nurse_ded = 20
            return nurse_ded
        return None

    def calculate_FAC_FUND_CLUB(self, payslip, employee, contract):
        # TODO : In which month Faculty Fund will be deducted
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of Faculity Fund to be deducted
        '''
        if employee.employee_group in ("A", "B", "C", "D"):
            faculity_fund = 500
            return faculity_fund
        return None

    def calculate_EIS_DED(self, payslip, employee, contract):
        # TODO : In which year EIS deduction stopped
        '''
        Takes Parameters - payslip, employee and contract

        returns the value of EIS to be deducted
        '''
        if employee.employee_group == 'A':
            eis = 100
            return eis
        elif employee.employee_group == 'B':
            eis = 60
            return eis
        elif employee.employee_group == 'C':
            eis = 30
            return eis
        elif employee.employee_group == 'D':
            eis = 20
            return eis

    def check_BASIC(self, payslip, employee, contract):
        return contract.basic

    def check_NET(self, payslip, employee, categories):
        #categories.name.BASIC + categories.ALW + categories.DED
        return True
    
    def check_NPA(self, payslip, employee, contract):
        if employee.employee_group == 'A':
            npa = (0.2 * contract.basic)
            return contract.basic + npa
    
    def check_NEW_BASIC(self, payslip, employee, contract):
        pass

    def check_UNIFORM_ALW(self, payslip, employee, contract):
        pass

    def check_DA(self, payslip, employee, contract):
        pass

    def check_NURSE_ALW(self, payslip, employee, contract):
        pass

    def check_TRANSPORT_ALW(self, payslip, employee, contract):
       pass

    def check_HPCA(self, payslip, employee, contract):
        pass

    def check_ACAD_ALW(self, payslip, employee, contract):
        pass

    def check_DEP_ALW(self, payslip, employee, contract):
        pass
    
    def check_TOOL_ALW(self, payslip, employee, contract):
        pass

    def check_QPAY(self, payslip, employee, contract):
        pass

    def check_DRESS_ALW(self, payslip, employee, contract):
        pass

    def check_CHTA(self, payslip, employee, contract):
        pass

    def check_EHS(self, payslip, employee, contract):
        pass

    def check_ASSN_FEE(self, payslip, employee, contract):
        pass

    def check_KARAMCHARI(self, payslip, employee, contract):
        pass

    def check_NURSE_UNION(self, payslip, employee, contract):
        pass

    def check_OF_ASSN(self, payslip, employee, contract):
        pass

    def check_FAC_CLUB(self, payslip, employee, contract):
        pass

    def check_RDA(self, payslip, employee, contract):
        pass

    def check_LEAVES(self, payslip, employee, contract):
        pass

    def check_COURT_RECOVERY(self, payslip, employee, contract):
        pass
