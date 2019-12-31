#!/bin/bash

# It is assumed that your virtual environment is active before you run this script, If not, it is requested
# that you kindly activate your virtual environment before doing so

git pull origin dev

array=(
    "base" "hr_contract" "hr_payroll" "hr_bank" "hr_gpf" "hr_payroll_gpf" "hr_hda" "hr_payroll_hda"
    "hr_arrear" "hr_payroll_arrear" "hr_bills" "hr_payroll_bills" "hr_cash" "hr_cea" "hr_payroll_cea"
    "hr_conveyance" "hr_payroll_conveyance" "hr_emb" "hr_estate" "hr_payroll_estate" "hr_exam_section"
    "hr_payroll_exam_section" "hr_hra" "hr_payroll_hra" "hr_icu" "hr_payroll_icu" "hr_loan"
    "hr_payroll_loan" "hr_nps" "hr_payroll_nps" "hr_ota" "hr_payroll_ota"
)

for d in ${array[@]} ; do
    cd $d && python3 setup.py install && cd ..
done
