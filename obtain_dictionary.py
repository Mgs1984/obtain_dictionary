__author__ = 'Moises Lorenzo'

# This software pretends to obtain a dictionary in the selected language (spanish or english) from the Wordreference.com
# website
#
# The idea is to use the urllib library to obtain the words from the letter "a", and from the html code of the website,
# obtain the next word. The dictionary shall write the word and the definition in a text file.
#

import httplib2

import os

# Create the function


def untag(word):

    # Every tag is sourrounded by '<' and '>'. Find them, and remove them
    temp_word = word
    while True:

        if temp_word.find('<') == -1:
            break

        else:
            tag_init = temp_word.find('<')
            tag_end = temp_word.find('>')
            tag_word = temp_word[tag_init:tag_end+1]
            temp_word_list = temp_word.split(tag_word)
            temp_word = ''.join(temp_word_list)

    return temp_word


# End of the function

# Create the file where the dictionary will go
used_path = os.getcwd()
output_file = used_path + 'spanish_dictionary.txt'
temp_file = used_path + 'temp.txt'

file_fid = open(output_file, 'w')


first_word = 'a'  # First word in the dictionary
last_word = 'zutano'  # Last word in this dictionary

word_site = 'http://www.wordreference.com/definicion/a'

def_reference = '<div id="article">'
reference_tag = '<li>'
end_of_def = ':'
end_of_def_ftintro = "<div id='FTintro'>"
end_of_def_supr1 = '<span class=supr1>'
next_def_tag = 'See Also:'

# Make a loop to go through every word

act_word = first_word
definition_word = ''
nxt_line_def = 0
nxt_definition_flag = 0
act_def_found = 0
nxt_def_passed = 0

while True:

    found = 0

    # Import directly the website for 'a'
    resp, content = httplib2.Http().request(word_site)
    content_text = content.decode('utf-8')
    if '\u21d2' in content_text:
        content_text = ''.join(content_text.split('\u21d2'))
    temp_fid = open(temp_file,'w')
    while True:
        try:
            temp_fid.write(content_text)
            break
        except UnicodeEncodeError as wr_err:
            # Look for the position
            wr_err_pos = content_text.find('pronunciation')
            content_text_temp = content_text[wr_err_pos:]
            wr_last_pos = content_text_temp.find('</span>')
            content_text = content_text[:wr_err_pos] + content_text[wr_err_pos+wr_last_pos:]

    temp_fid.close()
    temp_fid2 = open(temp_file,'r')
    while True:
        dict_line = temp_fid2.readline()
        if dict_line == '':
            break
        if dict_line == '\n':
            continue
        #Check if the line is the correct one
        if nxt_line_def == 1:
            # Correct one
            definition_line_text = dict_line
            # Now look for the the definition.The definition comes after reference_tag
            try:
                pos_def = definition_line_text.find(reference_tag)
                if pos_def == -1:
                    raise AssertionError
            except AssertionError:
                print('The code had a problem with the word' + act_word)
                raise
            pos_after_def = pos_def + len(reference_tag)
            line_of_def = definition_line_text[pos_after_def:]
            # Loop to look for the first uppercase of the definition
            first_letter = 0
            while True:
                try:
                    if line_of_def[first_letter].isupper():
                        break
                    else:
                        first_letter += 1
                except IndexError:
                    first_letter = line_of_def.find('=b>')+3
                    break

            # Found the first letter, we need to get the end of the definition. This comes with the
            # character ':'
            last_letter = line_of_def.find(end_of_def)
            last_letter_ft = line_of_def.find(end_of_def_ftintro)
            last_letter_supr1 = line_of_def.find(end_of_def_supr1)
            if (last_letter_ft) < last_letter and last_letter_ft != -1:
                last_letter = last_letter_ft
            if ((last_letter_supr1) < last_letter and last_letter_supr1 != -1) or (last_letter_supr1 != -1 and last_letter == -1):
                last_letter = last_letter_supr1
            definition_word_w_tag = line_of_def[first_letter:last_letter]

            # We have now the word defined. But it can be that it contain tags from html. Let's remove them

            definition_word = untag(definition_word_w_tag)
            nxt_line_def = 0

            if nxt_def_passed == 1:
                temp_fid2.seek(0,0)

        elif nxt_definition_flag == 1:
            # Obtain the next word of the dictionary and the url address
            act_def_tag = '>' + act_word + '<'
            nxt_definition_flag = 1
            if act_def_found == 1:
                #Look for the next word
                pos_dict_line = dict_line.find('">')
                last_dict_line = dict_line.find('</a>')
                nxt_word = dict_line[pos_dict_line + 2:last_dict_line]
                # If the word has any kind of strange character, let's go to the next one. If not, stop the for loop
                if nxt_word.find('!') != -1 or (nxt_word.find(' ') != -1) or (nxt_word.find('-') != -1):
                    act_def_found = 1
                    continue
                else:
                    act_def_found = 0
                    nxt_definition_flag = 0
                    site_first = dict_line.find('="')
                    word_site = 'http://www.wordreference.com' + dict_line[site_first + 2:pos_dict_line]
                    act_word = nxt_word
                    break

            if act_def_tag in dict_line:
                act_def_found = 1
            else:
                act_def_found = 0

        else:
            def_line_text = ''
            nxt_definition_flag = nxt_definition_flag

        # Look for the line where the definitions is
        # The definition comes after the sentence <div id="article">

        if def_reference in dict_line:
            nxt_line_def = 1
            found = 1
            nxt_definition_flag = 0
            continue
        elif next_def_tag in dict_line and found == 0:
            nxt_line_def = 0
            nxt_definition_flag = 0
            nxt_def_passed = 1
            continue
        elif next_def_tag in dict_line and found == 1:
            nxt_line_def = 0
            nxt_definition_flag = 1
            continue
        elif nxt_definition_flag == 1:
            nxt_line_def = 0
            nxt_definition_flag = 1
            continue
        else:
            nxt_line_def = 0
            nxt_definition_flag = 0
            continue

    # Write in the dictionary
    definition_line = act_word + ' : ' + definition_word +'\n'
    nxt_def_passed = 0
    # Last sentence. If the last word is reached, break the loop

    print(act_word)

    if act_word == last_word:
        break

    if found == 1:
        file_fid.write(definition_line)
    else:
        print("La palabra " + act_word + " no pudo ser encontrada")

    temp_fid2.close()

os.remove(temp_file)

file_fid.close()