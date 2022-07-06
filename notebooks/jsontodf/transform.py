import pandas as pd
import json


def transform(filename):
    path = filename
    print('step 1')
    df = read_file(path)
    print('step 2')
    df = replace_answers(df)
    print('step 3')
    df = replace_questions(df)
    print('step 4')
    #get_statistics(df, question=38)
    df.sort_values('question_id_text_left', inplace=True)
    print('step 5')
    return df 

def transform_from_file(file):
    df = read_file_from_file(file)
    print(df)
    df = replace_answers(df)
    print(df)
    df = replace_questions(df)
    print(df)
    #get_statistics(df, question=38)
    #print(df.columns)
    df.sort_values('question_id_text_left', inplace=True)
    print(df)
    return df 
    #df.to_excel('/tmp/'+filename.replace('.json', '')+".xlsx")


def flatten_nested_json_df(df):
    df = df.reset_index()
    #df['response_content'] = df['response_content'].astype(list)
    s = (df.applymap(type) == list).all()
    #print(s)
    list_columns = s[s].index.tolist() #['response_content'] #
    #print(list_columns)
    s = (df.applymap(type) == dict).all()
    dict_columns = s[s].index.tolist()
    while len(list_columns) > 0 or len(dict_columns) > 0:
        #print(list_columns)
        new_columns = []
        for col in dict_columns:
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            horiz_exploded.index = df.index
            df = pd.concat([df, horiz_exploded], axis=1).drop(columns=[col])
            new_columns.extend(horiz_exploded.columns) 
        for col in list_columns:
            df = df.drop(columns=[col]).join(df[col].explode().to_frame())
            new_columns.append(col)
        s = (df[new_columns].applymap(type) == list).all()
        list_columns = s[s].index.tolist()
        s = (df[new_columns].applymap(type) == dict).all()
        dict_columns = s[s].index.tolist()
    return df

def split_inner_dict(val):
    #print(val)
    if val == 0: 
        return val
    elif type(val)==list:
        if len(val)>0:
            return str(val[0]['name'])
    elif type(val)==dict: 
        return str(val['name'])
    else:
        return val

def read_file(file = None): 
    #f = open(file)
    #data = json.loads(file)
    print('before reading dict')
    df = pd.DataFrame.from_dict(file)
    print('after reading dict')
    #print(df)
    df = flatten_nested_json_df(df)
    df.fillna(0, inplace=True)
    #print( df[['response_content']].dtypes)

    #df['response_content'] = df['response_content'].apply(set_list)
    df['response_content'] = df['response_content'].apply(split_inner_dict)
    return df

def replace_answers(df): 
    df2 = pd.read_csv('../maestro_alternativas.csv')
    df = df.merge(df2, how='left', on='answerId',suffixes=('_left', '_right'))
    return df

def set_list(val): 
    #print(val)
    if val==0:
        val = []
    val = str(val)
    return val

def replace_questions(df): 
    df2 = pd.read_csv('../questions.csv')
    #print(df.columns)
    #print(df2.columns)
    df = df.merge(df2, how='left', on='question_id',suffixes=('_left', '_right'))
    return df

def get_statistics(df, question=[38]):
    question=[36, 38, 39, 41, 47, 50]
    for q in question:
        #print(df[df.question_id==q]['Questions Text Name'].unique()[0])
        links=df[df.question_id==q].answerId.value_counts().values[0]
        n = df[df.question_id==q].enrollmentId.nunique()
        #print('links:  ', str(links))
        #print('links by student: ', str(links/n))

def file_valid(file):
  return '.' in file and \
    file.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS