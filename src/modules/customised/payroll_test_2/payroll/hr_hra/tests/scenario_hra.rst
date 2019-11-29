======================
Hr_Hra Replace Scenario
======================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company
    
Install hr_hra::

    >>> config = activate_modules('hr_hra')

Create a employee::
    >>> company = create_company()
    >>> employee = Model.get('company.employee')
    >>> party = Model.get('party.party')
    >>> party_cur = party(name='Prashasti')
    >>> party_cur.save()
    >>> employee1 = employee(company=company,
    ...                      party=party_cur,
    ...                      primary_phone='9935164850',
    ...                      employee_status='Regular',
    ...                      employee_group='A',
    ...	)
    >>> employee1.save()
   


