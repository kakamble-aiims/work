#!/bin/bash

# It is assumed that your virtual environment is active before you run this script, If not, it is requested
# that you kindly activate your virtual environment before doing so

# In case you want to abort the script, press Ctrl+C if any module installation is going on or if you are 
# still on the git pull section, or just press an invalid character(any key other than y and n) when
# presented with module installation choice 

read -p "Pull latest code from dev branch?(y/n): " pull_choice
if [ $pull_choice == 'y' ]
then
    git pull origin dev
elif [ $pull_choice == 'n' ]
then
    echo -e "Moving on........ \n\n\n\n\n\n\n\n\n"
else
    echo -e "Invalid choice, but moving on........ \n\n\n\n\n\n\n\n\n"
fi

array=(
    "base" "hr_contract" "hr_payroll" "hr_bank" "hr_gpf" "hr_payroll_gpf" "hr_hda" "hr_payroll_hda"
    "hr_arrear" "hr_payroll_arrear" "hr_bills" "hr_payroll_bills" "hr_cash" "hr_cea" "hr_payroll_cea"
    "hr_conveyance" "hr_payroll_conveyance" "hr_emb" "hr_estate" "hr_payroll_estate" "hr_exam_section"
    "hr_payroll_exam_section" "hr_hra" "hr_payroll_hra" "hr_icu" "hr_payroll_icu" "hr_loan"
    "hr_payroll_loan" "hr_nps" "hr_payroll_nps" "hr_ota" "hr_payroll_ota"
)

for d in ${array[@]} ; do
    cd $d
    read -p "Current module is $d, install module?(y/n): " choice
    if [ $choice == 'y' ]
    then
        python3 setup.py install
        echo -e "\n\n\n\n\n\n\n\n\n"
    elif [ $choice == 'n' ]
    then
        echo -e "Moving on to next module\n\n\n\n\n\n"
    else
        echo "Invalid choice, exiting"
        break
    fi
    cd ..
done
