import pandas as pd
import requests
import lxml
from lxml import html
import time
import json
from tqdm import tqdm




# Functions

def get_my_set(data, set_no):
    '''
    Parameters: 
    
    data:- gregmat excel sheet dataframe
    set_no:- int, set no. which you want to get
    
    Returns: Series of 30 words
    '''
    column_name = 'Group '+ str(set_no)
    columns = data.columns
    for col in columns:
        if data[col].astype(str).str.fullmatch(column_name).any():
            found = True
            match_col = col
            for index, row in enumerate(data[col]):
                if row == column_name:
                    match_row = index
    
    selected = data[match_col][match_row+2 : match_row+2+30] # match_row + 2 because we don't want (Group no# or Take Test no#)
    return selected.reset_index(drop=True)

def get_data(word):
    url = 'https://mnemonicdictionary.com/?word='+word

    page = requests.get(url)
    tree = html.fromstring(page.content)
    definition = tree.xpath('//li[@class="media list-group-item p-4"]/div[1]//text()')[12].strip()
    synonyms = ','.join(tree.xpath('//li[@class="media list-group-item p-4"]/div[1]/div/div//a/text()'))
    mnemonic_ranks = {}

    mnemonic_slides = tree.xpath('.//div[@class="mnemonics-slides"]/div/div/div')

    for index, element in enumerate(mnemonic_slides):
        mnemonic = ''.join(element.xpath('.//div[@class="card-text"]/p/text()')[-1].strip().split('\n'))
        uncleaned_votes = element.xpath('./div[@class="card-footer"]//text()')
        upvotes = int(uncleaned_votes[0].strip('\n '))
        downvotes = int(uncleaned_votes[1].strip()) #.strip('\\xao ')

        if downvotes != 0:
            pass
        else:
            downvotes = 1
            rank_score = upvotes / downvotes


        if upvotes < downvotes or upvotes == 0 or upvotes == downvotes:
            continue

        rank_score = upvotes / downvotes
        mnemonic_ranks.update({rank_score:[mnemonic, upvotes, downvotes]})

#         print('Upvotes: {}\nDownvotes: {}\nMnemonic: {}\n'.format(upvotes, downvotes, mnemonic))
    
#     print(mnemonic_ranks)
    mnemonics_list = []
    count = 1
    for index, score in enumerate(sorted(mnemonic_ranks.keys(), reverse = True)):
        mnemonics_list.append('Mnemonic {}: {}'.format(index+1, mnemonic_ranks[score][0]))
        count+=1

        if count>4:
            break
    
    top_mnemonics = '\n'.join(mnemonics_list)
    return definition, synonyms, top_mnemonics

def get_image(word):
    image_url = '{}{}{}'.format('https://dailyvocab.com/photos/', word, '/')
    page = requests.get(image_url)
    tree = html.fromstring(page.content)
    image_url = tree.xpath('//meta[@name ="twitter:image"]/@content')
    return image_url

def add_set(data, word_list, set_no, sleep = True):
    if all([word in list(data['words']) for word in word_list ]):
        return data
    
    for word in word_list:
        try:
            definition, synonyms, mnemonics = get_data(word)
        except IndexError as error:
            print("{} not found at mnemonicdictionary.com!".format(word))
            
        image_url = get_image(word)
        
        if sleep == True:
            time.sleep(2)
        data = data.append({'words':word,'definition':definition,'synonyms':synonyms,'mnemonics':mnemonics,'image_url':image_url, 'Set':'Set_'+str(set_no)}, ignore_index=True)
        data['image_url'] = data['image_url'].apply(lambda x: x.strip('[]\'') if isinstance(x, str) else x) # Removing '[', ']', ''' (comma) from omage_url
        data['image_url'] = data['image_url'].apply(lambda x: None if isinstance(x, list) and len(x)==0 else x ) # Removing empty lists from url
        data['image_url'] = data['image_url'].apply(lambda x: x[0] if isinstance(x, list) else x ) # list to string
        data['image_url'] = data['image_url'].apply(lambda x: '<img src="{}">'.format(x) if isinstance(x, str) and not x.startswith("<img src=") else None)
        
        print("Added Word {}.".format(word))
    return data

def mnemo_str_to_list(mnemonic_string):
    if mnemonic_string is not None:
        return mnemonic_string.strip('[]').split(',')
    
def mnemo_list_to_string(mnemo_list):
    mnemo_string = ''
    for index, mnemonic in enumerate(mnemo_list):
        mnemo_string += 'Mnemonic {}: {}\n'.format(index+1, mnemonic)
    return mnemo_string