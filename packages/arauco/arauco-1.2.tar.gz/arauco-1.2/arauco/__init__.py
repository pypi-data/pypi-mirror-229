import numpy as np
import pandas as pd
import unicodedata

def sanitize_spaces(string):
    return ' '.join(string.split())


def convert_case(string, case='original'):
    #Deja el case requerido
    if case == 'original':
        return string
    elif case == 'upper' or case == 'uppercase' or case == 'mayus':
        string = string.upper()

    elif case =='lower' or case == 'lowercase' or case == 'minus':
        string = string.lower()

    elif case == 'capitalize' or case == 'capital':
        string = string.capitalize()

    else:
        ValueError("El argumento de 'case' = ['original', 'upper', 'lower', 'capitalize']")
    
    return string


def to_ascii(string, enie=False):
    if enie == True:
        string = string.replace("ñ", "#!#").replace("Ñ", "$!$")
        string = unicodedata.normalize('NFKD', string).encode('ascii','ignore').decode('ascii')
        string = string.replace("#!#", "ñ").replace("$!$", "Ñ")
    else:
        string = unicodedata.normalize('NFKD', string).encode('ascii','ignore').decode('ascii')
    return string


def magic(string, case='original', enie=False):
    string = sanitize_spaces(string)
    string = convert_case(string, case=case)
    string = to_ascii(string, enie=enie)
    return string



def aplanar_tabla(df, fixed_headers, fixed_cols):
    '''
    df: dataframe a aplanar
    fixed_headers: cantidad de headers de la tabla.
    fixed_cols: cantidad de columnas fijas.
    '''

    fixed_headers = list(range(2))
    aux =  np.array([df.loc[ix, :].values for ix in fixed_headers]).T
    aux = [';'.join([str(x) for x in item]) for item in aux]
    df.columns = aux
    df = df.drop(fixed_headers, axis=0)

    df = pd.melt(df, id_vars=df.columns[:fixed_cols], value_vars=df.columns[fixed_cols:], var_name='aux_var', value_name='aux_value')

    for ix in range( len(fixed_headers) ):
        df.insert(loc=fixed_cols+ix, column='var_' + str(ix), value=df['aux_var'].apply(lambda x: x.split(';')[ix]))
    df = df.drop(columns=['aux_var'])

    return df