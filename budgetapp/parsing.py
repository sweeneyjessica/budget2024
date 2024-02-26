import pandas as pd
import sqlite3
import re

# 269 total rows

# Parsing assumptions
#  - only one asterisk per merchant name
#  - about a third have asterisks at all
#  - colons do not appear in merchant names
#  - numbers can be removed without affecting semantics
#    - exceptions: 5280 burger bar, first ascent block 37, 30th st station
#    - esp unfortunate for RADI8 FLOAT CENTER which chops off to 'RADI'
#    - 2nd ave disappears actually
#  1. split on asterisk
#  2. if first element is 3 char or less, take second, otherwise take first
#  3. on whatever's left, remove numbers/# (using regex split)
#  4. ? nothing else for now

def get_df():
    db = sqlite3.connect(
        'instance/budgetapp.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    data = db.execute(
        'SELECT DISTINCT descr'
        ' FROM debit'
        ).fetchall()

    df = pd.DataFrame(data)
    df.columns = ['descr']

    return df

def parse_value(value):
    values = value.split("*")
    if len(values[0]) <=3 and len(values) > 1:
        value = values[1]
    else:
        value = values[0]

    value = re.split(r'(?<!^)\s?#?[0-9]+', value)[0]

    return value
    

def parse_col(descr_col):
    df = pd.DataFrame(descr_col)

    df['asterisk'] = descr_col.str.split("*")

    def get_name(col):
        if len(col[0]) <= 3 and len(col) > 1:
            return col[1]
        else:
            return col[0]
        
    df['asterisk'] = df['asterisk'].apply(get_name)

    df['numbers'] = df['asterisk'].str.split('(?<!^)\s?#?[0-9]+', regex=True)
    df['parsed_descr'] = df['numbers'].apply(get_name)

    return df['parsed_descr']


def auto_label(df):
    dining_meals = ['[Pp]izza|PIZZA', '[Bb]urgers?|BURGERS?', '[Ss]ushi|SUSHI', '[Tt]acos?|TACOS?']
    dining_coffee = ['[Cc]offee|COFFEE', '[Cc]afe|CAFE', '[Bb]agels?|BAGELS?', '[Tt]ea|TEA', '[Dd]unkin|DUNKIN', '[Ss]tarbucks|STARBUCKS']
    entertainment_museum = ['[Mm]useum|MUSEUM']

    def check_for_keywords(value):
        possibilities = []
        for keyword in dining_meals:
            if re.search(keyword, value):
                possibilities.append(('Dining', 'Meal'))
        for keyword in dining_coffee:
            if re.search(keyword, value):
                possibilities.append(('Dining', 'Coffee'))
        for keyword in entertainment_museum:
            if re.search(keyword, value):
                possibilities.append(('Entertainment', 'Museum'))

        if len(possibilities) != 1:
            return False
        else:
            return {'Category': possibilities[0][0], 'Information': possibilities[0][1], 'Tags': 'Autolabeled'}
        
    df['labels'] = df['parsed_descr'].apply(check_for_keywords)

    def assign_misc(labels, num_txns, average_amount):
        if num_txns == 1 and average_amount < 25:
            if labels == False:
                return {'Category': 'Misc', 'Information': '', 'Tags': 'Autolabeled'}
        
        return labels
            
    df['labels'] = df.apply(lambda x: assign_misc(x['labels'], x['num_txns'], x['average_amount']), axis=1)
    
    labeled_df = df[df['labels']!= False]

    split_columns = labeled_df['labels'].apply(pd.Series)
    labeled_df = pd.concat([split_columns, labeled_df], axis=1)
    labeled_df = labeled_df.drop('labels', axis=1)
    # split = pd.DataFrame(labeled_df['labels'].to_list(), columns=['Category', 'Information', 'Tags'])
    # labeled_df = pd.concat([labeled_df, split], axis=1).drop('labels', axis=1)

    # # labeled_df.to_csv('labeled.csv')

    return labeled_df, df[df['labels'] == False]
