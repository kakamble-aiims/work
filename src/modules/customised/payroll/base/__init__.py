from trytond.pool import Pool

def register():
    Pool.register(
        
        module='base', type_='model')