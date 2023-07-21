#!/opt/local/bin/python3.8

import sqlite3
import json
import errno
import re
import os
import uuid
import shutil

from pandas import DataFrame
from tabulate import tabulate
Usage = """exportSnips.py

This script has functions for writing out snippets for specific text editors.
It opens and reads a sqlite database.
The calls to these specific functions are below the __main__ function.

writeAtom():    Write Atom snippets.
writeST3():     Writes Sublime Text 3 snippets.
writeTM():      Writes TextMate snippets.
writeUS():      Writes UltiSnip snippets for neovim.
writeVSC():     Writes snippets for Visual Studio Code

To be done:

gedit
jedit
nedit


Blaine Mooers, Ph.D.
OUHSC
8 July 2018

Updated numerous times in the spring of 2019.

30 August 2019
Added the writeJupyterClippingBody() function.

16 November 2019
Added neosnippets.

11 August 2020
Converted from exportSnips.py to exportPySnips.py to export with commands inside cmd.do('').



"""


def fetchsnips(table_name, cn):
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    print(all_rows)
    return all_rows


def countSelected(table_name, cn, print_out=False):
    c.execute(
        'SELECT COUNT(*) FROM {tn} WHERE {cn}="text.pml"'.format(tn=table_name, cn=col_3))
    count = c.fetchall()
    if print_out:
        print('\n Number of selected rows: {}'.format(count[0][0]))
    return count[0][0]


def values_in_col(cursor, table_name, print_out=True):
    """ Returns a dictionary with columns as keys
    and the number of not-null entries as associated values.
    """
    cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = cursor.fetchall()
    col_dict = dict()
    for col in info:
        col_dict[col[1]] = 0
    for col in col_dict:
        c.execute('SELECT ({0}) FROM {1} '
                  'WHERE {0} IS NOT NULL'.format(col, table_name))
        # In my case this approach resulted in a
        # better performance than using COUNT
        number_rows = len(c.fetchall())
        col_dict[col] = number_rows
    if print_out:
        print("\nNumber of entries per column:")
        for i in col_dict.items():
            print('{}: {}'.format(i[0], i[1]))
    return col_dict


def printCats(cursor, table_name, print_out=True):
    """Returns list of unique category names."""
    cursor.execute('SELECT DISTINCT category FROM {} WHERE {cn}="text.pml" ORDER BY category'.format(
        table_name, cn=col_3))
    distinct = cursor.fetchall()
    if print_out:
        numCat = len(distinct)
        print("\n" + "There are " + str(numCat) + " distinct categories of snippets" + 
              "\n" + "(in format for pasting as a list into Rmarkdown:)" + "\n")
        for dis in distinct:
            print("- " + str(dis[0]))
    return distinct


def total_rows(cursor, table_name, print_out=False):
    """ Returns the total number of rows in the database """
    cursor.execute('SELECT COUNT(*) FROM {}'.format(table_name))
    count = cursor.fetchall()
    if print_out:
        print('\nTotal rows: {}'.format(count[0][0]))
    return count[0][0]


def table_col_info(cursor, table_name, print_out=False):
    """ Returns a list of tuples with column informations:
    (id, name, type, notnull, default_value, primary_key)
    """
    cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = cursor.fetchall()
    if print_out:
        print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
        for col in info:
            print(col)
    return info


def reindent(s, numSpaces):
    """source: http://code.activestate.com/recipes/66055-changing-the-indentation-of-a-multi-line-string/ """
    s = str.split(s, '\n')
    s = [(numSpaces * ' ') + str.lstrip(line) for line in s]
    s = str.join(s, '\n')
    return s


def lsSnips(table_name, cn):
    """Print the tab triggers and the caption of what they do.
    The returned values will be entered into the tab trigger called lsSnips
    so the that tab triggers and their captions can be printed to the top or bottom of
    an open script file for fast look-up of the commands.
    The list of list all_rows is read into a Pandas dataframe and then
    two columns are written out to strings as a list of lists, lol.
    Then lol is sorted alphabetically by using a lambda function that sorts on the first column to give lols.
    Next, the sorted slol is prettified with the tabulate command to give a decent ascii table with the elements left justified.
    I was not able to left justified the elements of the pandas dataframe.

    Need additional functions to write out the table in the format for the different bodies
    which will then be pasted into the pymolsnips.db.
    """
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    df = DataFrame(all_rows, columns=['tabtrigger', 'language', 'scope', 'category', 'caption',
                                      'body', 'body4json', 'body4bbedit', 'pythonYN',
                                      'hasPythonVersionYN', 'indexTag', 'citekey', 'pageNumber'])
    df1 = df[['tabtrigger', 'caption']]
    table = df1.to_string(index=False, justify='left', col_space=25)
    lol = df1.values
    lols = sorted(lol, key=lambda x: x[0])
    titles = ['Tab trigger', 'caption']
    newTable = lols
    print(tabulate(newTable, headers=titles))
    return all_rows


def lsSnipsGitHubmd(table_name, cn):
    """Print the tab triggers and the caption of what they do in a GitHub markdown table.
    The returned values will be entered into the tab trigger called lsSnips
    so the that tab triggers and their captions can be printed to the top or bottom of
    an open script file for fast look-up of the commands.
    The list of list all_rows is read into a Pandas dataframe and then
    two columns are written out to strings as a list of lists, lol.
    Then lol is sorted alphabetically by using a lambda function that sorts on the first column to give lols.
    Next, the sorted slol is prettified with the tabulate command to give a decent ascii table with the elements left justified.
    I was not able to left justified the elements of the pandas dataframe.

    Need additional functions to write out the table in the format for the different bodies
    which will then be pasted into the pymolsnips.db.
    """
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    df = DataFrame(all_rows, columns=['tabtrigger', 'language', 'scope', 'category', 'caption',
                                      'body', 'body4json', 'body4bbedit', 'pythonYN',
                                      'hasPythonVersionYN', 'indexTag', 'citekey', 'pageNumber'])
    df1 = df[['tabtrigger', 'caption']]
    table = df1.to_string(index=False, justify='left', col_space=25)
    lol = df1.values
    lols = sorted(lol, key=lambda x: x[0])
    titles = ['Tab trigger', 'caption']
    newTable = lols
    print(tabulate(newTable, headers=titles, tablefmt="pipe"))
    return all_rows


def subtablesGitHubmd(table_name, cn):
    """Print the tab triggers and the caption of what they do in a GitHub markdown table.
    The returned values will be entered into the tab trigger called lsSnips
    so the that tab triggers and their captions can be printed to the top or bottom of
    an open script file for fast look-up of the commands.
    The list of list all_rows is read into a Pandas dataframe and then
    two columns are written out to strings as a list of lists, lol.
    Then lol is sorted alphabetically by using a lambda function that sorts on the first column to give lols.
    Next, the sorted slol is prettified with the tabulate command to give a decent ascii table with the elements left justified.
    I was not able to left justified the elements of the pandas dataframe.

    Need additional functions to write out the table in the format for the different bodies
    which will then be pasted into the pymolsnips.db.
    """
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    df = DataFrame(all_rows, columns=['tabtrigger', 'language', 'scope', 'category', 'caption',
                                      'body', 'body4json', 'body4bbedit', 'body4jupyter',
                                      'hasPythonVersionYN', 'indexTag', 'citekey', 'pageNumber'])
    grouped_df = df.sort_values(
        ['category', 'tabtrigger'], ascending=True).groupby('category')
    for key, item in grouped_df:
        # print(grouped_df.get_group(key), "\n\n")
        print("\n")
        print("## " + key + ":")
        # print(grouped_df.get_group(key)[['tabtrigger','caption']])
        table = grouped_df.get_group(key)[['tabtrigger', 'caption']].to_string(
            index=False, justify='left', col_space=25)
        lol = grouped_df.get_group(key)[['tabtrigger', 'caption']].values
        lols = sorted(lol, key=lambda x: x[0])
        titles = ['Tab trigger', 'caption']
        newTable = lols
        print(tabulate(newTable, headers=titles, tablefmt="pipe"))
    return all_rows


def catfreq(table_name, cn):
    """Print the number of tab triggers per category.
    The returned values are formatted for a LaTeX table.
    They can be copied and pasted into the body of an existing table in a tex document.
    """
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    df = DataFrame(all_rows, columns=['tabtrigger', 'language', 'scope', 'category', 'caption',
                                      'body', 'body4json', 'body4bbedit', 'pythonYN',
                                      'hasPythonVersionYN', 'indexTag', 'citekey', 'pageNumber'])
    grouped_df = df.sort_values(
        ['category', 'tabtrigger'], ascending=True).groupby('category')
    for key, item in grouped_df:
        table = grouped_df.get_group(key)[['tabtrigger', 'caption']].to_string(
            index=False, justify='left', col_space=25)
        lol = grouped_df.get_group(key)[['tabtrigger', 'caption']].values
        lols = sorted(lol, key=lambda x: x[0])
        catf = len(lols)
        print(key + " & " + str(catf) + " \\\\")
    return all_rows

######################### Functions for formatting for different text editors  ##################################
"""
I need functions that convert from one body to another to be able to fix damage done to the database by accidents
like the pasting of multi-line bodies over multiple fields.

The functions can print the lines to the terminal for copying in and pasting of select lines or another function
could load these reformated cells directly into the database.

body2body4jason
body2body4bbedit
body4bbedit2body
body4bbedit2body4jason
body4jason2body
body4jason2body4bbedit

"""


def bbeditBody2OtherBodies(table_name, cn):
    """ """
    c.execute('SELECT * FROM {tn} WHERE {cn}="text.pml"'.
              format(tn=table_name, cn=col_3))
    all_rows = c.fetchall()
    df = DataFrame(all_rows, columns=['tabtrigger', 'language', 'scope', 'category', 'caption',
                                      'body', 'body4json', 'body4bbedit', 'pythonYN',
                                      'hasPythonVersionYN', 'indexTag', 'citekey', 'pageNumber'])
    df1 = df[['body4bbedit']]
    df2 = df1.replace(regex={r'%{': '${', '%0': '$0'})
    print(list(df2['body4bbedit'][0:98]))
    df3 = df1.replace(regex={r'%{': '${', '%0': '$0', '^': '"', '\n': '",\n"'})
    print(list(df3['body4bbedit'][0:98]))
    # Table = df2.to_string(index=False,justify='left')
    # print(Table)
    # Table2 = df3.to_string(index=False,justify='left')
    # print(Table2)
#    titles = ['body','body4json']
#    print(tabulate(Table, headers=titles))
    return all_rows

######################### Functions for exporting to text editors ##################################
""" The functions below export snippets in libraires for various text editors.
    See this blogpost for information about what was desired in a text editor in 2011
    https://code.tutsplus.com/articles/are-textmate-and-coda-yesterdays-editors--net-22423
"""


def writeAtom(scopeAtom, args):
    r"""
    Atom is a free, open-source code editor that was developed for GitHub url{https://
    atom.io/}. Atom was designed to be readily extensible. It is advertised as being the hackable
    text editor for the 21st century.

    All of the user-supplied code snippets are stored in one file called "snippets.cson" which is
    stored in the r\url{/Users/blaine-mooers/.atoms}. This is a javascript file. This file's format is
    sensitive to line indentation. The scope for the "pml" type files is called ".source.pymol". This
    goes on the first line of the section of the snippet file that contains all of the “pml” snippets.
    The scope limits the availability of the snippets to “pml” files. The available snippets are
    shown with their full name and "prefix" by using the using the pull-down cascade of
    “Package/Snippets/Available”. The "prefix" is used to invoke insertion of the snippet upon
    entering tab. Alternatively, the snippets are listed by “Alt-Shift-S”. The desired snippet can
    also be selected with the mouse to insert it into the text at the cursor. We inserted over 30
    snippets in alphabetical order. All of the "pml" snippets are indented by a tab under the line
    ".source.pymol", which is shown only once. The "prefix" is the shorthand that inserts into the
    script the snippet after hitting the tab. The customized “snippet.cson” file is available at our
    GitHub site.

    The "language-pymol" (\url{https://atom.io/packages/language-pymol}) PyMOL package
    for Atom provides syntax highlighting of PyMOL "pml" scripts. This package was adapted
    from the Sublime Text bundle for PyMOL \url{https://atom.io/packages/language-pymol}.
    This package needs to be installed to activate the pml scope.

      Atom snippets are stored in ~/.atom/snippets.scon.
      Append the file pml_snippets.cson to your existing snippets.cson file:
          cat pmlsnippets.cson snippet.cson > snippets.cson
      CSON means CoffeeScript Object Notation.
      CSON maps to JSON with tabs replacing braces.
      Single quotes in the body will have to be escaped.
      Multi-line bodies require flanking triple single quotes.
      The scope is defined once. 
    
    The language-pymol package for Atom provides syntax highlighting and defines the scope as 
    .source.pymol for pml files and source.py2pml for python files that write pymol code.
    The ${0} needs to be written outside of the cmd.do(). 
    This means that all of the body's have to have the ${0} removed.
    """
    selected = args
    home = r'/Users/blaine/Manuscripts/PyMOLsnippets/pymolpysnips/atompymolsnips/'
    output1 = open(home + 'pymolsnippets.cson', 'w')
    outp1 = "'.source.python': \n"
    output1.write(outp1)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces = 0
        s = body
        sbody = "      cmd.do('" + "')\n      cmd.do('".join((numSpaces * "") + i for i in s.splitlines()) + "')" + "\n      \n" + "      ${0}"
        outp2 = "  '" + caption + "':\n"\
            "    'prefix': '" + tabtrigger + "'\n"\
            "    'body': '''\n"\
            +sbody +  "\n"\
            "    '''\n"
        output1.write(outp2)
    output1.close()
    return


def writeGedit(scopeGedit, args):
    """
    The snippets are stored in a single file.
    The gedit3 snippets are stored in ~/.config/gedit/snippets/pymol.xml.
    The snippets are stored in xml code.

    Good introduction to snippets in gedit(http://www.tuxradar.com/content/save-time-geditsnippets)
    
    code boneyard:
    sbody = "\n".join((numSpaces0 * " ") + i for i in s.splitlines())

    """
    selected = args
    home = r'/Users/blaine/Manuscripts/PyMOLsnippets/pymolpysnips/geditpypymolsnips/'
    output1 = open(home + 'pymol.xml', 'w')
    outp1 = "<?xml version='1.0' encoding='utf-8'?> \n" + \
        '  <snippets language="pymol"> \n'
    output1.write(outp1)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces2 = 2
        numSpaces4 = 4
        numSpaces0 = 0
        s = body
        sbody = "      cmd.do('" + "')\n      cmd.do('".join((numSpaces0 * "") + i for i in s.splitlines()) + "')" + "\n      \n" + "      ${0}"
        outp2 = "  <snippet>" + "\n"\
            "    <caption>" + caption + "</caption>" + "\n"\
            "    <tag>" + tabtrigger + "</tag>" + "\n"\
            "    <text><![CDATA[" + sbody + "\n"\
            "]]></text>" + "\n"\
            "  </snippet>" + "\n"
        output1.write(outp2)
    output1.close()
    return


def writeSnipMate(scopeSnipMate, args):
    """
    SnipMate snippets are stored in one file called pymol.snippets.
    Each snippet's body is indented by seven spaces using function.
    code boneyard:
    # sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines())
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/snipmatepymolsnips/'
    output1 = open(home + 'pymol.snippets', 'w')
    outp1 = "# PyMOL snippets \n"
    output1.write(outp1)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces = 7
        s = body
        sbody = "       cmd.do('" + "')\n      cmd.do('".join((numSpaces * "") + i for i in s.splitlines()) + "')" + "\n       \n" + "       ${0}"
        outp2 = "snippet " + tabtrigger + "\n" + sbody + "\n"
        output1.write(outp2)
    output1.close()
    return


def writeST3all(args):
    r"""Snippets for Sublime Text 3. One file per snippet.
    Sublime Text is a proprietary text editor designed for the writing of computer code. Others
    have developed a PyMOL syntax highlighter for it ( \url{https://atom.io/packages/
    language-pymol}). The pymol.tmlanguage and Comments.tmPreferences files are stored in
    the folder \url{~/Library/Application Support/Sublime Text 3/Packages} to activate the
    syntax highlighting. The parameter values are highlighted differently from parameter names
    which can add the editing of new and recycled code. Several other text editors (e.g. Atom and
    Text Mate) will accept Sublime Text syntax coloring files. These syntax highlighting files need
    to be installed to make available the scope for PyMOL “pml” files. Take care to add a
    carriage return at the end of the last line.

    Sublime Text allows users to create snippets. The program provides a template under the
    tools pull-down. The template is printed to the screen when the GUI option "new snippet" is
    selected. The snippet template has commented out directions on how to edit it. The code is
    pasted between a pair of lines that mark the beginning and the end of the snippet.

    There are three optional tags for the snippet. The first is a TagTrigger that is for a shortcut
    that you type and then hit tab to have the snippet inserted into your current document. The
    shortcut can be as short as a single letter. The second is the scope tag that limits the snippet to
    certain kinds of files like source files ending with the file extension "pml". There is a list of
    sanctioned scopes. There is not a "pml" scope in the default list, so the initial use of this tag
    will lead to the hiding of the snippets when trying to add them to a pml file. Use
    “<scope>.source.pymol</scope>" for the scope after installing the syntax highlighting files
    mentioned above. The third tag is a caption tag that displays a caption of the snippet
    when it is selected from the pull-down or when the TagTrigger is typed inside the script file.

    The snippet files have the extension ".sublime-snippet". They can be stored anywhere in the
    Packages directory. This directory is in the user's library which is found in the following
    location on the mac (\url{~/Library/Application Support/Sublime Text 3/Packages}). The
    snippets can be stored in separate subfolders but the name of the subfolder will not be
    displayed in the list of snippets. The list of snippets is displayed in a GUI after selecting
    "Tools/Snippets". The GUI has a text window that can be used to search for snippets after
    the list becomes too long to show all of the snippets on one page. About 40 snippet names are
    be displayed vertically in this GUI before scrolling is required to see additional snippet names.
    The rest of the shortcut key is displayed and can be selected to speed completion.
    
    code boneyard
    #            + body + "\n\n" + "${0}" + "\n"\
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolpysnips/st3pymolsnips/'
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home + tabtrigger + '.sublime-snippet', 'w')
        s = body
        sbody = "       cmd.do('"\
              + "')\n      cmd.do('".join((numSpaces * "")\
              + i for i in s.splitlines())\
              + "')"\
              + "\n       \n"\
              + "       ${0}" 
        outp1 = "<snippet>" + "\n"\
            + "<content><![CDATA[" + "\n" \
            + sbody + "]]></content>" + "\n"\
            + "<tabTrigger>" + tabtrigger + "</tabTrigger>" + "\n"\
            + "<scope>" + '' + "</scope>" + "\n"\
            + "<caption>" + caption + "</caption>" + "\n"\
            + "</snippet>"
        output1.write(outp1)
        output1.close()
    return


def writeBlueFish(scopeBlueFish, args):
    r"""Snippets for bluefish.
    The snippets are written to a single file that is stored in the file called .bluefish/snippets.
    The file are in xml format.
     """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/bluefishpymolsnips/'
    output1 = open(home + 'snippets', 'w')
    outp0 = '<?xml version="1.0"?>' + '\n'
    output1.write(outp0)
    outp00 = '<snippets>' + '\n'
    output1.write(outp00)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        outp000 = '<leaf type="insert" title="' + tabtrigger + '" tooltip="' + caption + '">' + '\n'\
            '<before/>' + '\n'\
            '<after>' + '\n'\
            +body + "\n\n" + "${0}" + "\n"\
            '</after>' + '\n'\
            '</leaf>' + '\n'
        output1.write(outp000)
    outp3 = '</snippets>' + '\n'
    output1.write(outp3)
    outp2 = '<branch title="PyMOL pml">'
    output1.write(outp2)
    output1.close()
    return


def writeCudaText(scopeCudaText, args):
    r"""Snippets for CudaText. One file per snippet.
    Sublime Text is a proprietary text editor designed for the writing of computer code. Others
    have developed a PyMOL syntax highlighter for it ( \url{https://atom.io/packages/
    language-pymol}). The pymol.tmlanguage and Comments.tmPreferences files are stored in
    the folder \url{~/Library/Application Support/Sublime Text 3/Packages} to activate the
    syntax highlighting. The parameter values are highlighted differently from parameter names
    which can add the editing of new and recycled code. Several other text editors (e.g. Atom and
    Text Mate) will accept Sublime Text syntax coloring files. These syntax highlighting files need
    to be installed to make available the scope for PyMOL “pml” files. Take care to add a
    carriage return at the end of the last line.

    Sublime Text allows users to create snippets. The program provides a template under the
    tools pull-down. The template is printed to the screen when the GUI option "new snippet" is
    selected. The snippet template has commented out directions on how to edit it. The code is
    pasted between a pair of lines that mark the beginning and the end of the snippet.

    There are three optional tags for the snippet. The first is a TagTrigger that is for a shortcut
    that you type and then hit tab to have the snippet inserted into your current document. The
    shortcut can be as short as a single letter. The second is the scope tag that limits the snippet to
    certain kinds of files like source files ending with the file extension "pml". There is a list of
    sanctioned scopes. There is not a "pml" scope in the default list, so the initial use of this tag
    will lead to the hiding of the snippets when trying to add them to a pml file. Use
    “<scope>.source.pymol</scope>" for the scope after installing the syntax highlighting files
    mentioned above. The third tag is a caption tag that displays a caption of the snippet
    when it is selected from the pull-down or when the TagTrigger is typed inside the script file.

    The snippet files have the extension ".sublime-snippet". They can be stored anywhere in the
    Packages directory. This directory is in the user's library which is found in the following
    location on the mac (\url{~/Library/Application Support/Sublime Text 3/Packages}). The
    snippets can be stored in separate subfolders but the name of the subfolder will not be
    displayed in the list of snippets. The list of snippets is displayed in a GUI after selecting
    "Tools/Snippets". The GUI has a text window that can be used to search for snippets after
    the list becomes too long to show all of the snippets on one page. About 40 snippet names are
    be displayed vertically in this GUI before scrolling is required to see additional snippet names.
    The rest of the shortcut key is displayed and can be selected to speed completion.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/cudatextpymolsnips/'
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home + tabtrigger + '.cuda-snippet', 'w')
        outp1 = "name=" + caption + "\n"\
            "id=" + tabtrigger + "\n"\
            "lex=PML_" + "\n"\
            "text=" + "\n"\
            +body + "\n\n" + "${0}" + "\n"
        output1.write(outp1)
        output1.close()
    return


def writeKomodoEdit(scopeKomodoEdit, args):
    r"""
    Snippets for Komodo Edit.
    This is a proprietary program wtih a free Community Edition, which is still feature rich.
    There is one file per snippet.
    The filename has the extension ktf.
    There are tab stops.
    The cursor advances sequentially.
    The tab stops are not numbered.
    There is no mirror of tab stops with identical values.
    The abbreviations in the pml folder do not work in script files for other languages.
    They only work in files with the pml file extension.
    Through the gui invoked by right clicking on the snippet name, you can click on another button called properties.
    These properties can aid the autopopulation of tab stops with various parameters like the current directory and the current filename.
    The informatoin about the formatting is found here: http://docs.activestate.com/komodo/11/manual/shortcuts.html.
    The snippets are stored on the Mac in
    \url{/Users/blaine/Library/Application\ Support/KomodoEdit/11.1/tools/Abbreviations/PML}.
    I left the language in the header of the snippet set to 'Text' becuase this worked without defining the pml language.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/komodoeditpymolsnips/'
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home + tabtrigger + '.ktf', 'w')
        if body is not None:
            myregex1 = r"\$\{\d+:(:?.+?)\}"
            mysub1 = r"[[%tabstop:\1]]"
            body1 = re.sub(myregex1, mysub1, body)
            myregex2 = r"\$0"
            mysub2 = r"!@#_currentPos!@#_anchor"
            body2 = re.sub(myregex2, mysub2, body1)
            myregex3 = r"\$\{0\}"
            mysub3 = r"!@#_currentPos!@#_anchor"
            body3 = re.sub(myregex3, mysub3, body2)
        outp1 = "// komodo tool: " + tabtrigger + "\n"\
            r"// ==================" + "\n"\
            r"// auto_abbreviation: false" + "\n"\
            r"// indent_relative: false" + "\n"\
            r"// language: Text" + "\n"\
            r"// set_selection: false" + "\n"\
            r"// treat_as_ejs: false" + "\n"\
            r"// type: snippet" + "\n"\
            r"// version: 1.1.5" + "\n"\
            r"// ==================" + "\n"\
            + body3 + "\n\n" + "${0}" + "\n"
        output1.write(outp1)
        output1.close()
    return


def writeLightTable(scopeLightTable, args):
    r"""
    Light Table is a text editor targeting web development.
    In particular, it targets develiopment for javascript.
    It is written in ClojureScript.
    ClojureScript is related to Lisp.
    The snippets are stored in indvidudal files.
    Each of these files ends with the file extension ".snip"
    These files are read in by a master file with the extension .end.
    The snips are stored in $HOME/.lighttable/User/snippets/
    This function writes out both the master file and the snip files.
    I need to write a pml language for Light Table.
    In the mean time, scripts files can be treated as python scripts.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/lighttablepymolsnips/'
    output0 = open(home + scopeLightTable + '.edn', 'w')
    """ Replace the word python with pml once a pml editor is deployed for Light Table """
    outpA = '{:modes {:+ #{:editor.python}}' + '\n'\
        ':snippets [' + '\n'
    output0.write(outpA)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        outpB = ('           {:name "' + 
                 caption + '"' + 
                 '\n' + 
                 '            :key "' + 
                 tabtrigger + 
                 '"' + 
                 '\n' + 
                 '            :snippet-file "' + 
                 tabtrigger + 
                 '.snip"}' + 
                 '\n')
        output0.write(outpB)
        output1 = open(home + tabtrigger + '.snip', 'w')
        outp1 = body + "\n\n" + "${0}" + "\n"
        output1.write(outp1)
        output1.close()
    outpZ = r'           ]}' + '\n'
    output0.write(outpZ)
    output0.close()
    return


def writeBBEdit(scopeBBEdit, args):
    r"""
    Snippets for BBEdit.
    One file per snippet.
    These snippets are known as clippings.
    Their tab triggers use a percent sign rather than a dollar sign.
    They are stored in ~/Library/Application Support/BBedit/Clippings/PyMOL.pml.

    In the proprietary text editor BBEdit that is available for Mac OSX, code snippets are called
    clippings. The clippings are stored in the user home directory \url{~/Library/Application
    Support/BBEdit/Clippings}. We put them in a subfolder called "PyMOL.pml". The
    clippings are pml code stored in plain text files. These plain text files have the file extension of
    "pml". The clipping file can hold one or more lines of pml code. The code clippings are
    accessed from the top bar via the "C" pulldown. The "C" pulldown reveals a "PyMOL.pml"
    pulldown. The "PyMOL.pml" pulldown reveals the snippets. A snippet is selected with the
    mouse to insert it into the current document. The user changes the parameter values in the
    clipping to those needed for the current task.

    The holding capacity for clippings of the "PyMOL.pml" pulldown is about 2500 on a laptop
    computer screen. The "PyMOL.pml" pulldown lists 50 snippets. The "PyMOL.pml"
    subfolder can hold subsubfolders. These subsubfolders appear in the "PyMOL.pml" pulldown
    along with the snippets. The pulldown has room for 50 subsubfolders in the pulldown after
    moving the snippets into subsubfolders. Each subsubfolder can hold 50 snippets. The
    subsubfolders are useful for organizing the clippings when there are too many of them to fit in
    the cascading pull-down. The subsubfolders cannot hold subsubsubfolders, so the addition of
    more clippings requires new subfolders. We used a separate subfolder called "PyMOL.py" to
    store PyMOL python code snippets such as classes and functions.

    Snippets were very easy to add to BBEdit. Existing “pml” files were simply copied to the
    "Clippings/PyMOL.pml subfolder". There was no need to embedded the snippet code inside
    flanking code in a master snippet file “snippets.cson” as for Atom or to create additional file
    types as in the case of Sublime Text 3 or Text Mate as described below. In fact, we used
    BBEdit to assemble the library file for Atom. However, BBEdit has no option of a GUI
    interface for parameters values as in the case of the Bluefish editor (Table 1).
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/bbeditpymolsnips/'
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home + tabtrigger + ".pml", 'w')
        outp1 = body4bbedit + "\n\n" + "${0}" + "\n"
        output1.write(outp1)
        output1.close()
    return


def writeJupyterClippingBody(scopeJupyterClippingBody, args):
    """
    Reformats the ST3 body for Jupyter and Jupyter-Lab clippings that can be loaded with the load majic.

    The body is first written a comment to provide a visual guide to the sites to be edited.
    The last tab stop is deleted from this body.
    I put the whole body between triple quotes because I was too lazy to use parse the body and use hashmarks
    to comment out each line.

    Then the body is written again with regexes used to remove the tabstops while leaving the default value.

    This website was helpful for testing regexes https://regex101.com/.

    """
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/jupyterclippingspymolsnips/'
    selected = args
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home + tabtrigger + '.pml', 'w')
        if body is not None:
            myregex0 = r"\$0"
            mysub0 = r""
            body0 = re.sub(myregex0, mysub0, body)
            outp1 = '""""' + "\n" + body0 + '""""' + "\n"
            output1.write(outp1)
#           myregex1 = r"\$\{\d+:.+\}"
            myregex1 = "\$\{\d:"
            mysub1 = r""
            body1 = re.sub(myregex1, mysub1, body)
            myregex2 = r"\}"
            body2 = re.sub(myregex2, mysub1, body1)
            myregex3 = r"\$0"
            body3 = re.sub(myregex3, mysub1, body2)
            output1.write(body3)
        output1.close()
    return


def writeJupyter2(scopeJupyter, args):
    """A single file per scope is written out for Jupyter notebooks.
       The snippets are in a format for the common.js file.
       The intent is for the snippets to appear clustered in submenus
       of the eqml menu.
       Eventually an outer for loop is needed to step through each
       member of a category or cluster of snippets.
       The for loop could walk through a list of categories.

       This function does not write out the required flanking code
       to give a functional common.js file. I
       I still need to add this code to make it useful for others.

       This function includes the LaTeX markup that would be
       useful for writing a book about PyMOL.

       TBD:
       The tabstops need to be removed from the body via deleciate regex commands.
       The '${n:' and only the enclosing '}' need to be removed while leaving the
       default parameter value.

    """

    c.execute('SELECT DISTINCT category FROM {} WHERE {cn}="text.pml" ORDER BY category'.format(
        table_name, cn=col_3))
    distinct = c.fetchall()
    # if print_out:
    #     numCat = len(distinct)
    #     print("\n"+"There are " + str(numCat) + " distinct categories of snippets" +
    #           "\n"+"(in format for pasting as a list into Rmarkdown:)"+"\n")
    #     for dis in distinct:
    #         print("- " + str(dis[0]))
    # return distinct

    selected = args

    home1 = r'/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/'
    home = home1 + r'jupyterpymolsnips/'
    output1 = open(home + 'pml.js', 'w')

    # cats = ['DNN', 'classification']

    output1.write("    var pymolpml = {" + "\n")
    output1.write("        'name' : 'pymolpml'," + "\n")
    output1.write("        'sub-menu' : [" + "\n")

    for x in distinct:
        xx = str(x[0])
        output1.write("            {" + "\n")
        output1.write("            'name' : '" + xx + "'," + "\n")
        output1.write("            'sub-menu' : [" + "\n")

        for (tabtrigger,
             language,
             scope,
             category,
             caption,
             body,
             body4json,
             body4bbedit,
             pythonYN,
             hasPythonVersionYN,
             indexTag,
             citekey,
             pageNumber) in selected:
            if category == xx:
                myregex1 = r"\\"
                mysub1 = r"\\\\"
                body1 = re.sub(myregex1, mysub1, body)
                myregex2 = r"\n"
                mysub2 = r"\\n"
                body0 = re.sub(myregex2, mysub2, body1)
                # myregex3 = r"\n${0}"
                # mysub3 = r"\\n"
                # body0 = re.sub(myregex3, mysub3, body2)
                output1.write("                {" + "\n" + 
                              "                      'name': " + 
                              "'" + 
                              tabtrigger + 
                              "'," + 
                              "\n" + 
                              "                      'snippet': " + 
                              r"['%\\begin{code}{}" + 
                              r" \n" + 
                              r"%\\begin{minted}{python}" + 
                              r" \n" + 
                              body0 + 
                              r"\\end{minted}" + r" \n" + 
                              r"%\\caption{" + 
                              caption + 
                              r"\cite{" + 
                              citekey + 
                              r"}" + 
                              r"} \n" + 
                              r"%\\label{eq:" + 
                              tabtrigger + 
                              r"} \n" + 
                              r"%\\index{" + 
                              indexTag + 
                              r"}" + 
                              r"%\\end{code}" + 
                              r"',]," + 
                              "\n" + 
                              r"                }," + 
                              "\n")
        output1.write("                ]," + "\n")
        output1.write("            }," + "\n")

    output1.write("            ]," + "\n")
    output1.write("        };" + "\n")
    output1.close()
    return


def writeWing(scopeWing, args):
    """ Snippets in Wing follow Python's percentsign(varname)s string substituion syntax. 
    The body of the snippet marker has the folowing syntax: %(varname|type|default)s.
    Both type and default are optional but the vertical bars must be present 
    if omitting type but including default. To write a snippet that includes 
    Python style string formats, escape each % by writing %% instead.
    
    The varname is the variable name. It is used in place of numbers in other snippet systems.
    This varname is only internal to the snippet.
    If varname is mirrored at multiple sites, the change at one site is propagated to other sites.
    ! prepended to the variable name indicates that the value should act as a tab stop even if 
    its value is mirrored from an earlier field with the same varname. 
    This has no effect if the field name is unique.
    
    Snippets can contain |!| to indicate the final resting position of the cursor
    after all other fields have been filled. 
    
    The snippets are stored one per file.
    The file name has the same file extension as the language.
    
    Snippets are stored in the directory *snippets* inside the Settings Directory.
    Snippets stored at the top level of this directory can be used with any file in the editor. 
    These global snippets are shown in the * tab of the Snippets tool.
    
    Snippets designed for a particular file type are stored in directories named with 
    the most common extension for the file type, for example py for Python.  
    
    Snippets designed for a particular file type are stored in directories named with 
    the most common extension for the file type, for example py for Python.
    
    Each of the file type directories may contain snippets that apply to any context 
    in files of that type and sub-directories named <context>.ctx for snippets designed
    for a particular context. <context> is replaced with the desired context name.
    
    On Windows the settings directory is called Wing Pro 7 and is placed within the 
    per-user application data directory. For Windows running on c: with an English localization 
    the location is: c:\\Users\\username\\AppData\\Roaming\\Wing Pro 7
    In Wing Personal the settings directory is instead named Wing Personal 7.2 and 
    in Wing 101 it is called`` Wing 101 7.2``.
    
    On Linux and OS X the settings directory is a sub-directory of your home directory:
    ~/.wingpro7
    ~/.wing-personal7
    ~/.wing-101-7
    
    ~/.wingpro7/snippets/pml
    
    Wing writes a .config file in the snippets directory. 
    Do not delete nor edit this file.
    Doing so could lead to the deletion of your files.
    
    The pml files will not have syntax highlighting at present in Wing.
    The pymolpysnips will have syntax highlighting of the Python syntax.
    
    The pml snippets should all start at the left column.
 
    We have to replace in body the tab stop markdown '${1:' with '%('  and '}' with ')s'.
    We have to duplicate the default value and have it serve as the variable name.
    The two values are to be separated by ||.
    The regex code below does this.
    
    The myregex1 rawstring is the search string.
    It has the special characters escaped with backspaces.
    The dot after the first brace is for the tab stop index number which we are removing.
    The (.*) expression captures the default parameter value.
    
    The mysub1 is the subsitution. 
    The \1 represent the default parameter value which we will repeat after ||.
    The value that goes between the pipes is the data type, string or date.
    I chose to leave this blank.
    
    We have to escape '%' with '%%' to avoid the confusion with the start of tab stops.
    
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolpysnips/wingspymolpysnips/pml/'
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces0 = 0
#        myregex0 = r'%'
#        mysub0 = r'%%'
#        body0= re.sub(myregex0, mysub0, body)
        myregex0 = r'python;'
        mysub0 = r''
        body0= re.sub(myregex0, mysub0, body)
        myregex00 = r'python'
        mysub00 = r''
        body00= re.sub(myregex0, mysub0, body0)
        myregex01 = r'python end;'
        mysub01 = r''
        body01= re.sub(myregex01, mysub01, body0)
        myregex02 = r'python end'
        mysub02 = r''
        body02= re.sub(myregex02, mysub02, body01)
        myregex1 = r'\$\{.\:(.*)\}'
        mysub1 = r'%(\1||\1)s'
        body1= re.sub(myregex1, mysub1, body02)
        output1 = open(home + tabtrigger, 'w')
        sbody = "cmd.do('" + "')\ncmd.do('".join((numSpaces0 * "") + i for i in body1.splitlines()) + "')" + '\n\n' + '|!|'
        output1.write(sbody)
        output1.close()
    return



def PascalCase(s):
    """Convert the string s into 
    PascalCase without regard to 
    the terminal punctuation.
    If you want to omit the terminal
    punctuation, change the 0 after len(s)
    to a 1."""
    if(len(s) == 0):
        return
    s1 = ''
    s1 += s[0].upper()
    for i in range(1, len(s) - 0):
        if (s[i] == ' '):
            s1 += s[i + 1].upper()
            i += 1
        elif(s[i - 1] != ' '):
            s1 += s[i]
    return(s1)


def writeJupyterLabLaTeX(scopeJupyterLab, args):
    """
    Reformats the 'body' for clippings used by JupyterLab.
    The clippings are written out to subfolders with 
    the category name. This name is rewritten in PascalCase
    using the above PascalCase() function.

    This version of the function writes out the metadata 
    required for writing a book in LaTeX.

    This website was helpful for testing regexes https://regex101.com/.

    The elements of distinct are in a list of strings with a comma in an expected place.
    The use of str(x[0]) was to extracting from distinct a string in a useful
    Converting an element to a string with the str() function
    leads to parenthesis around the string, which is bad for a
    subdirectory name. Instead, use join to remove the ().

    This function extracts the list of categories from the database
    so there is no need to worry about adding more categories nor 
    changes in category names. 

           Are they stored here?

       ~/.jupyter/lab/user-settings/jupyterlab_snippets/

       or here?

       ~/Library/jupyter/snippets/

    """
    home1 = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/jupyterlablatexpymolsnips/'
    selected = args
    c.execute('SELECT DISTINCT category FROM {} WHERE {cn}="text.pml" ORDER BY category'.format(
        table_name, cn=col_3))
    distinct = c.fetchall()

    selected = args
    print('Distinct = ', distinct)

    for x in distinct:
        xx = str(x[0])
        xxxx = PascalCase(xx)
        dirName = home1 + ''.join(xxxx)

        # Create target directory & all intermediate directories if don't exists
        try:
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        except FileExistsError:
            print("Directory ", dirName, " already exists")

        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(dirName):
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        else:
            print("Directory ", dirName, " already exists")

        for (tabtrigger,
             language,
             scope,
             category,
             caption,
             body,
             body4json,
             body4bbedit,
             pythonYN,
             hasPythonVersionYN,
             indexTag,
             citekey,
             pageNumber) in selected:
            if category == ''.join(x):
                output1 = open(dirName + '/' + tabtrigger + '.tex', 'w')
                myregex0 = r"\$0"
                mysub0 = r""
                body0 = re.sub(myregex0, mysub0, body)
                outp1 = '"""' + "\n" + body0 + '"""' + "\n"
                output1.write(outp1)
    #           myregex1 = r"\$\{\d+:.+\}"
                myregex1 = "\$\{\d:"
                mysub1 = r""
                body1 = re.sub(myregex1, mysub1, body)
                myregex2 = r"\}"
                body2 = re.sub(myregex2, mysub1, body1)
                myregex3 = r"\${0"
                body3 = re.sub(myregex3, mysub1, body2)
                outp1 = (r"%\begin{code}{}" + 
                         "\n" + 
                         r"%\begin{minted}{python}" + 
                         "\n" + 
                         body3 + 
                         "\n" + 
                         r"%\end{minted}" + 
                         "\n" + 
                         r"%\caption{" + 
                         caption + 
                         r"\cite{" + 
                         citekey + 
                         r"}" + 
                         r"}" + 
                         "\n" + 
                         r"%\label{eq:" + 
                         tabtrigger + 
                         r"}" + 
                         "\n" + 
                         r"%\index{" + 
                         indexTag + 
                         r"}" + 
                         "\n" + 
                         r"%\end{eqfloat}" + 
                         "\n")
                # print("The content of outp1 is as follows:" + "\n" + outp1)
                output1.write(outp1)
                output1.close()
    return


def writeJupyterLab2(scopeJupyterLab, args):
    """
    Writes code for JupyterLab multimenu pymolpysnips library.
    
    Reformats the 'body' for snippets used by JupyterLab.
    The clippings are written out to subfolders with 
    the category name. This name is rewritten in PascalCase
    using the above PascalCase() function.

    This version of the function writes out the metadata 
    required for writing a book in LaTeX. Use the function
    without LaTeX in the name for use in Python.

    This website was helpful for testing regexes https://regex101.com/.

    The elements of distinct are in a list of strings with a comma in an expected place.
    The use of str(x[0]) was to extracting from distinct a string in a useful
    Converting an element to a string with the str() function
    leads to parenthesis around the string, which is bad for a
    subdirectory name. Instead, use join to remove the ().

    This function extracts the list of categories from the database
    so there is no need to worry about adding more categories nor 
    changes in category names. 
    
    Need to pass the python --- python end code blocks without modification.
    Seems if then, while construct would do the trick.
    
    

    Blaine Mooers and OU Board of Regents
    26 April 2020
    """
    home1 = '/Users/blaine/Manuscripts/CCTBXsnips/cctbxsnips/jupyterlabcctbx2/'
    selected = args
    c.execute('SELECT DISTINCT category FROM {} WHERE {cn}="source.python" ORDER BY category'.format(
        table_name, cn=col_3))
    distinct = c.fetchall()

    selected = args
    print('Distinct = ', distinct)

    for x in distinct:
        xx = str(x[0])
        xxxx = PascalCase(xx)
        dirName = home1 + ''.join(xxxx)

        # Create target directory & all intermediate directories if don't exists
        try:
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        except FileExistsError:
            print("Directory ", dirName, " already exists")

        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(dirName):
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        else:
            print("Directory ", dirName, " already exists")

        for (tabtrigger,
             language,
             scope,
             category,
             caption,
             body,
             body4json,
             body4bbedit,
             pythonYN,
             hasPythonVersionYN,
             indexTag,
             citekey,
             pageNumber) in selected:
            if category == ''.join(x):
                output1 = open(dirName + '/' + tabtrigger + '.py', 'w')
                numSpaces = 0
                myregex1 = "\$\{\d:"
                mysub1 = r""
                body1 = re.sub(myregex1, mysub1, body)
                myregex2 = r"\}"
                body2 = re.sub(myregex2, mysub1, body1)
                myregex3 = r"\${0"
                body3 = re.sub(myregex3, mysub1, body2)
                if pythonYN == "N":
                    body4 = "cmd.do('" + "')\ncmd.do('".join((numSpaces * "") + i for i in body3.splitlines()) + "')"
                    outp1 = (body4 + "\n")
                # print("The content of outp1 is as follows:" + "\n" + outp1)
                    output1.write(outp1)
                    output1.close()
                elif pythonYN == "Y":
                    outp1 = (body3 + "\n")
                    output1.write(outp1)
                    output1.close()
                else:
                    print("The column 'pythonYN' is missing a value. Edit the database.")
    return

def writeJupyterLabAnnotatedpy(scopeJupyterLab, args):
    """
    Writes code for JupyterLab multimenu pymolpysnips library.

    Reformats the 'body' for snippets used by JupyterLab.
    The clippings are written out to subfolders with
    the category name. This name is rewritten in PascalCase
    using the above PascalCase() function.

    This version of the function writes out the metadata
    required for writing a book in LaTeX. Use the function
    without LaTeX in the name for use in Python.

    This website was helpful for testing regexes https://regex101.com/.

    The elements of distinct are in a list of strings with a comma in an expected place.
    The use of str(x[0]) was to extracting from distinct a string in a useful
    Converting an element to a string with the str() function
    leads to parenthesis around the string, which is bad for a
    subdirectory name. Instead, use join to remove the ().

    This function extracts the list of categories from the database
    so there is no need to worry about adding more categories nor
    changes in category names.

    Need to pass the python --- python end code blocks without modification.
    Seems if then, while construct would do the trick.



    Blaine Mooers and OU Board of Regents
    26 April 2020
    """
    home1 = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolpysnips/jupyterlab2pymolpysnips/'
    selected = args
    c.execute('SELECT DISTINCT category FROM {} WHERE {cn}="text.pml" ORDER BY category'.format(
        table_name, cn=col_3))
    distinct = c.fetchall()

    selected = args
    print('Distinct = ', distinct)

    for x in distinct:
        xx = str(x[0])
        xxxx = PascalCase(xx)
        dirName = home1 + ''.join(xxxx)

        # Create target directory & all intermediate directories if don't exists
        try:
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        except FileExistsError:
            print("Directory ", dirName, " already exists")

        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(dirName):
            os.makedirs(dirName)
            print("Directory ", dirName, " Created ")
        else:
            print("Directory ", dirName, " already exists")

        for (tabtrigger,
             language,
             scope,
             category,
             caption,
             body,
             body4json,
             body4bbedit,
             pythonYN,
             hasPythonVersionYN,
             indexTag,
             citekey,
             pageNumber) in selected:
            if category == ''.join(x):
                output1 = open(dirName + '/' + tabtrigger + '.py', 'a+')
                numSpaces = 0
                myregex0 = r"\$0"
                mysub0 = r""
                s = re.sub(myregex0, mysub0, body)
                sbody = "cmd.do('" + "')\ncmd.do('".join((numSpaces * "") + i for i in s.splitlines()) + "')" + "\n"
                outp1 = '"""' + "\n" + sbody + '"""' + "\n"
                output1.write(outp1)
                # myregex1 = r"\$\{\d+:.+\}"
                myregex1 = "\$\{\d:"
                mysub1 = r""
                body1 = re.sub(myregex1, mysub1, body)
                myregex2 = r"\}"
                body2 = re.sub(myregex2, mysub1, body1)
                myregex3 = r"\${0"
                body3 = re.sub(myregex3, mysub1, body2)
                body4 = "cmd.do('" + "')\ncmd.do('".join((numSpaces * "") + i for i in body3.splitlines()) + "')" + "\n"
                outp1 = (body4 +
                         "\n" +
                         r"# Description:  " +
                         caption +
                         "\n" +
                         r"# Source:  " +
                         citekey +
                         "\n" +
                         "\n")
                # print("The content of outp1 is as follows:" + "\n" + outp1)
                output1.write(outp1)
                output1.close()
    return


def writeTM(scopeTM, args):
    """
    Snippets for Textmate.
    One file per snippet.
    The snippets have an unique uuid code generated for each one.
    The snippets are stored in a folder called Snippets.
    The Snippets folder is stored in a bayeseq.tmbundle that is a folder too.
    This bundle folder also has a plist file with a uuid and a dependences.json file.
    The dependency is pygments.

    I may add the citation key to the comment or desciption key.

    '% ' + 'Source: ' + citekey + '\n'\
    '% ' + 'Page number: ' + pageNumber + ' Eq no.: ' + equationNumber + '\n' + body + '\n' +'</string>' + '\n'\

    """
    home3 = r'PyMOL.tmbundle/'
    libpath = home1 + home2 + home3
    if not os.path.exists(os.path.dirname(libpath)):
        try:
            os.makedirs(os.path.dirname(libpath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    home4 = r'Snippets/'
    libpath2 = home1 + home2 + home3 + home4

    if not os.path.exists(os.path.dirname(libpath2)):
        try:
            os.makedirs(os.path.dirname(libpath2))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    selected = args
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        output1 = open(home1 + home2 + home3 + home4 + 
                       tabtrigger + '.tmSnippet', 'w')
        outp1 = '<?xml version="1.0" encoding="UTF-8"?>' + '\n' \
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' + '\n'\
            '<plist version="1.0">' + '\n'\
            '<dict>' + '\n'\
            '    <key>content</key>' + '\n'\
            '    <string>' + '\n' + '% ' + caption + '\n' + body + '\n' + '</string>' + '\n'\
            '    <key>keyEquivalent</key>' + '\n'\
            '    <string>' + tabtrigger + '</string>' + '\n'\
            '    <key>name</key>' + '\n'\
            '    <string>' + caption + '</string>' + '\n'\
            '    <key>scope</key>' + '\n'\
            '    <string>' + scope + '</string>' + '\n'\
            '    <key>tabTrigger</key>' + '\n'\
            '    <string>' + tabtrigger + '</string>' + '\n'\
            '    <key>uuid</key>' + '\n'\
            '    <string>' + str(uuid.uuid4()) + '</string>' + '\n'\
            '</dict>' + '\n'\
            '</plist>' + '\n'
        output1.write(outp1)
        output1.close()

        output2 = open(libpath + 'info.plist', 'w')
        outp2 = '<?xml version="1.0" encoding="UTF-8"?>' + '\n'\
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' + '\n'\
            '<plist version="1.0">' + '\n'\
            '<dict>' + '\n'\
            '	<key>contactEmail</key>' + '\n'\
            '	<string>blaine-mooers@ouhsc.edu</string>' + '\n'\
            '	<key>contactName</key>' + '\n'\
            '	<string>Blaine Mooers</string>' + '\n'\
            '	<key>caption</key>' + '\n'\
            '	<string>Customized snippets for working more efficiently in LaTeX.</string>' + '\n'\
            '	<key>name</key>' + '\n'\
            '	<string>PyMOL</string>' + '\n'\
            '	<key>uuid</key>' + '\n'\
            '	<string>' + str(uuid.uuid4()) + '</string>' + '\n'\
            '</dict>' + '\n'\
            '</plist>' + '\n'
        output2.write(outp2)
        output2.close()

        output3 = open(libpath + 'dependencies.json', 'w')
        outp3 = '{' + '\n'\
            '    "*": {' + '\n'\
            '        "*": [' + '\n'\
            '           "pygments"' + '\n'\
            '        ]' + '\n'\
            '    }' + '\n'\
            '}' + '\n'
        output3.write(outp3)
        output3.close()
    return


def writeUS(scopeUS, args):
    """A single file per scope is written out for the UltiSnips of Vim."""
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/ultisnippymolsnips/'
    selected = args
    output1 = open(home + scopeUS + '_bhmm.snippets', 'w')
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         citekey,
         pageNumber) in selected:
        outp1 = 'snippet ' + tabtrigger + ' "' + caption + '" b \n' \
            +body + "\n\n" + "${0}" + "\n"\
            'endsnippet' + '\n \n'
        output1.write(outp1)
    output1.close()
    return


def writeNeoSnippets(scopeNeoSnippets, args):
    """
    NeoSnippets snippets are stored in one file called pymol.snippets.
    Each snippet's body is indented by seven spaces using function.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/neosnippetspymolsnips/'
    output1 = open(home + 'pymol.snip', 'w')
    # outp1 = "# PyMOL snippets \n"
    # output1.write(outp1)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces = 4
        s = body
        sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines())
        outp2 = ("snippet " + tabtrigger
                            +"\n"
                            +"abbr    "
                            +tabtrigger
                            +"\n"
                            +"alias   "
                            +tabtrigger
                            +"\n"
                            +sbody 
                            + "\n\n" + "${0}" + "\n\n")
        output1.write(outp2)
    output1.close()
    return


def writeGeany(scopeGeany, args):
    """A single file for all pml snippets for the text editor Geany. 
    The snippets are written one per line.
    """
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/geanypymolsnips/'
    selected = args
    output1 = open(home + 'geanypymolsnippets.conf', 'w')
    outpA = '[PyMOL]' + '\n'
    output1.write(outpA)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        if body is not None:
            myregex1 = r"\$\{\d+:.+\}"
            mysub1 = r"%cursor%"
            body1 = re.sub(myregex1, mysub1, body)
            myregex2 = r"\$0"
            mysub2 = r"%cursor%"
            body2 = re.sub(myregex2, mysub2, body1)
            myregex3 = r"\n"
            mysub3 = r"\\n"
            body3 = re.sub(myregex3, mysub3, body2)
            myregex4 = r"\$\{0\}"
            mysub4 = r"%cursor%"
            body4 = re.sub(myregex4, mysub4, body3)
            outp1 = tabtrigger + '=' + body4 + "\n\n" + "${0}" + "\n"
            output1.write(outp1)
    outpB = '\n'
    output1.write(outpB)
    output1.close()
    return


def writeEspresso(scopeEspresso, args):
    """A single file for all snippets is written out for Espresso."""
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/espressopymolsnips/'
    selected = args
    output1 = open(home + 'espressoymolsnippets.xml', 'w')
    outpA = r'<?xml version="1.0" encoding="UTF-8"?>' + '\n'
    output1.write(outpA)
    outpB = r'<action-recipes>' + '\n \n'
    output1.write(outpB)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        if body is not None:
            numSpaces = 12
            s = body
            sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines()) + "\n\n" + "${0}" + "\n"
            outpC = '        <snippet id="' + tabtrigger + '" category="' + category + '"> \n'\
                '            <title>' + caption + r'</title>' + '\n'\
                    '            <text><![CDATA[' + sbody + r']]></text>' + '\n'\
                    '            <syntax-context>' + scope + r'</syntax-context>' + '\n'\
                    '            <key-equivalent>' + 'control shift option' + r'</key-equivalent>' + '\n'\
                    '        </snippet>' + '\n \n'
            output1.write(outpC)
    outpD = r'</action-recipes>' + '\n'
    output1.write(outpD)
    outpE = '\n'
    output1.write(outpE)
    output1.close()
    return


def writeKate(scopeKate, args):
    """
    A single file for all snippets is written out for Kate.
    Install by double clicking on file with Kate open.
    """
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/katepymolsnips/'
    selected = args
    output1 = open(home + 'katepmlsnippets.xml', 'w')
    outpA = r'<snippets namespace="" license="GPL v3+" filetypes="pml" authors="Blane Mooers" name="PyMOL Snippets">' + '\n'\
        ' <script></script>' + '\n'
    output1.write(outpA)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        if body is not None:
            numSpaces = 1
            s = body
            sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines()) + "\n\n" + "${0}" + "\n"
            myregex2 = r"\$0"
            mysub2 = r"%cursor%"
            body2 = re.sub(myregex2, mysub2, sbody)
            outpC = ' <item>' + '\n'\
                '  <displayprefix></displayprefix>' + '\n'\
                    '  <match>' + tabtrigger + '</match>' + '\n'\
                    '  <displaypostfix></displaypostfix>' + '\n'\
                    '  <displayarguments></displayarguments>' + '\n'\
                    '  <fillin>' + body2 + '</fillin>' + '\n'\
                    ' </item>' + '\n'
            output1.write(outpC)
    outpD = r'</snippets>' + '\n'
    output1.write(outpD)
    outpE = '\n'
    output1.write(outpE)
    output1.close()
    return


def writeVSC(scopeVSC, args):
    """A single file per scope is written out for Visual Studio Code."""
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/vscpymolsnips/'
    output1 = open(home + scopeVSC + '.json', 'w')
    output1.write('{' + '\n')
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        outp1 = '"' + tabtrigger + '": {' + '\n'\
            '    "prefix": "' + tabtrigger + '",' + '\n'\
            '    "body": ' + body4json + ',' + "\n\n" + "${0}" + "\n"\
            '    "caption": "' + caption + '",' + '\n'\
            '    "scope": "' + scope + '"' + '\n'\
            '},' + '\n'
        output1.write(outp1)


def writeBrackets(scopeBrackets, args):
    """
    A single yml file is written out for the Brackets text editor.
    This is a remake (9 March 2019) of the Old Brackets exporter.
    It is inspired by the brackets-snippets extension by edc.
    https://github.com/chuyik/brackets-snippets

    Store the yml file in ~/Library/Application\ Support/Brackets/extensions/user

    The multi line code block has to be indented by 8 spaces.
    The terminal tabe stop seems need to be enclosed by braces.
    I think the braces are optional for other text editors.
    If not, I can write a regex to replace the ${0} with $0.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/bracketspymolsnips/'
    output1 = open(home + 'bracketspymolsnips.yml', 'w')
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces = 8
        s = body
        sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines())
        outp1 = '- trigger: ' + tabtrigger + '\n'\
            '  scope: python' + '\n'\
            '  caption: ' + caption + '\n'\
            '  tag: ' + category + '\n'\
            '  tagHide: true' + '\n'\
            '  source: github/MooersLab/pymolsnips' + '\n'\
            '  text: |' + '\n'\
            +sbody + "\n\n" + "${0}" + "\n"\
            '\n'
        output1.write(outp1)
    output1.close()
    return


def writeBracketsOld(scopeBrackets, args):
    r"""
    Brackets is free. open source, and avialabe for multiple platforms (Mac OS, Windows, most Linux).
    It is created and distributed by Adobe Systems.
    Brackets focuses  on developement of JavaScript, CSS and HTML code for webpages.
    Brackets has a live html, css and js editing functionality.
    This means that a preview pane is available to see the output as the code is changed.
    This is like the preview pane for latex in Atom.
    Brackets looks like the a good choice for editing html files.
    More about its features can be found here https://en.wikipedia.org/wiki/Brackets_(text_editor).

    A single file for all snippets is written out to a yml file.
    This file has different sections for different programming languages.
    Brackets supports 38 programming languages out of the box.
    I may have to write an extension for pml.
    The snippets extension needs to be installed via the extension manager.
    This action leaves a shortcut on the right margin of the gui in the form a lightbulb.
    The snippets are stored in a subfolder in ~/Library/Application\ Support/Brackets/extensions/user
    This YouTube video is a useful introducton to the snippet extension: https://www.youtube.com/watch?v=oleenIQ-5gk.

    Several snippet managers are available.
    The [Text Mate inspired snippet manager](https://github.com/chuyik/brackets-snippets) was used to make user had made a snippet manager.
    """
    selected = args
    home = '/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/bracketspymolsnips/'
    output1 = open(home + scopeBrackets + '.yml', 'w')
    outp1 = '# ---' + '\n'\
        +'# PyMOL-pml' + '\n'\
        +'# From ' + '\n'\
        +'# ---' + '\n'
    output1.write(outp1)
    for (tabtrigger,
         language,
         scope,
         category,
         caption,
         body,
         body4json,
         body4bbedit,
         pythonYN,
         hasPythonVersionYN,
         indexTag,
         citekey,
         pageNumber) in selected:
        numSpaces = 8
        s = body
        sbody = "\n".join((numSpaces * " ") + i for i in s.splitlines())
        outp2 = '- trigger: ' + tabtrigger + '\n'\
            '  scope: ' + scopeBrackets + '\n'\
            '  caption: ' + caption + '\n'\
            '  text: |' + '\n'\
                +sbody + "\n\n" + "${0}" + "\n"
        output1.write(outp1)
    output1.write('}' + '\n')
    output1.close()
    return


def writeNpp():
    r"""Notepad++ is a freely available and designed for Windows.
    It can be run on Linux and Mac OS after being packaged by wine.

    The NppSnippets Plugin\footnote{\url{https://www.fesevur.com/nppsnippets/}} is used to manage snippets.
    You can dock the plugin after selecting it from the Plugin pulldown.
    A submenu of the available snippets will appear.

    Then you can select a specific language.
    The snippets for that language will appear.
    The user can then select the snippet that is desired by its name.

    The snippets are broken in half so that they can surround selected text.
    This is the first time that I have found this feature.

    I am not sure yet if tabtriggers are available for Notepad++.
    Then right click on the name of the language.
    The option to export the snippets for that language will appear.

    The NppSnippet plugin stores snippets in a sqlite database for each language.
    A database for a language can be exported by right clicking on it.
    I exported the library for the PHP language.
    The library is a relational database with multiple tables.

    I found a 26 page manual on NppSnippets.
    It describes the snippet database structure.
    I need to read this manual before I write a writeNpp() function that uses the sqlite module.

    The PyMOL language is not available in the default distribution of Notepad++.
    Fortunately, a user define a new language\footnote{\url{http://docs.notepad-plus-plus.org/index.php/User_Defined_Languages}}.
    """
    return

# ********************** Utitlities **********************


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

# ********************** __main__ **********************


if __name__ == '__main__':
    table_name = 'pml'
    col_1 = 'tabtrigger'
    col_2 = 'language'
    col_3 = 'scope'
    cn = 'scope'
    col_4 = 'category'
    col_5 = 'caption'
    col_6 = 'body'
    col_7 = 'body4json'
    col_8 = 'body4bbedit'
    col_9 = 'pythonYN'
    col_10 = 'hasPythonVersionYN'
    col_11 = 'indexTag'
    col_12 = 'citekey'
    col_13 = 'pageNumber'

    conn = sqlite3.connect('pymolsnips.db')
    selected = 'all_rows'
    c = conn.cursor()
    fetchsnips(table_name, cn)
    # writeST3all(args=fetchsnips(table_name, cn))
    # writeTM(args=fetchsnips(table_name, cn))
    # write one file of UltiSnip snippets
    scopeUS = 'python'
    scopeVSC = 'python'
    scopeAtom = 'python'
    scopeSnipMate = 'python'
    scopeYaSnippet = 'python'
    scopeTM = 'python'
    scopeGedit = 'python'
    scopeBBEdit = 'python'
    scopeBrackets = 'python'
    scopeNpp = 'python'
    scopejEdit = 'python'
    scopeCudaText = 'python'
    scopeLightTable = 'python'
    scopeBrackets = 'python'
    scopeGeany = 'python'
    scopeKate = 'python'
    scopeEspresso = 'python'
    scopeKomodoEdit = 'python'
    scopeBlueFish = 'python'
    scopeJupyterLabpy = 'python'
    scopeJupyterLab = 'python'
    scopeJupyterLabAnnotatedpy = 'python'
    scopeJupyterClippingBody = 'python'
    scopeJupyter = 'python'
    scopeNeoSnippets = 'python'
    scopeWing ='python'
    # home1 = r'/Users/blaine/Manuscripts/PyMOLsnippets/'
    # home2 = r'pymolsnips/'
    # writeAtom(scopeAtom, args=fetchsnips(table_name, cn))
    
    # writeJupyterClippingBody(scopeJupyterClippingBody,args=fetchsnips(table_name, cn))
    # writeBlueFish(scopeBlueFish,args=fetchsnips(table_name, cn))
    # writeKomodoEdit(scopeKomodoEdit,args=fetchsnips(table_name, cn))
    # writeEspresso(scopeEspresso,args=fetchsnips(table_name, cn))
    # writeKate(scopeKate,args=fetchsnips(table_name, cn))
    # writeGeany(scopeGeany, args=fetchsnips(table_name, cn))
    # writeGedit(scopeGedit, args=fetchsnips(table_name, cn))
    # writeLightTable(scopeLightTable, args=fetchsnips(table_name, cn))
    # writeCudaText(scopeCudaText, args=fetchsnips(table_name, cn))
    # write out UltiSnip library
    # writeUS(scopeUS, args=fetchsnips(table_name, cn))
    # writeNeoSnippets(scopeNeoSnippets, args=fetchsnips(table_name, cn))
    # writeVSC(scopeVSC, args=fetchsnips(table_name, cn))
    # writeSnipMate(scopeSnipMate,args=fetchsnips(table_name, cn))
    # writeYaSnippet(scopeYaSnippet,args=fetchsnips(table_name, cn))
    # writeBBEdit(scopeBBEdit, args=fetchsnips(table_name, cn))
    # 
    # write with tabstops
    writeJupyterLabpy(scopeJupyterLabpy, args=fetchsnips(table_name, cn))
    #writeJupyterLabAnnotatedpy(scopeJupyterLabAnnotatedpy, args=fetchsnips(table_name, cn))
    # writeJupyterLab(scopeJupyterLab, args=fetchsnips(table_name, cn))
    # printCats(c, table_name, print_out=True)
    # writeJupyterLab(scopeJupyter, args=fetchsnips(table_name, cn))
    # writeJupyterLabLaTeX(scopeJupyter, args=fetchsnips(table_name, cn))
    # writeBrackets(scopeBrackets, args=fetchsnips(table_name, cn))
    # writeNpp(scopeNpp,args=fetchsnips(table_name, cn))
    # writejEdit(scopejEdit,args=fetchsnips(table_name, cn))
    # writeTM(scopeTM,args=fetchsnips(table_name, cn))
    #############writeWing(scopeWing,args=fetchsnips(table_name, cn))
    # shutil.rmtree("/Users/blaine/Library/Application Support/TextMate/Bundles/pml.tmbundle")
    # copy('/Users/blaine/Manuscripts/PyMOLsnippets/pymolsnips/PyMOL.tmbundle/Snippets','/Users/blaine/Library/Application Support/TextMate/Bundles/PyMOL.tmbundle/Snippets')
    # countSelected(table_name, cn, print_out=True)
    # Need a function selected_rows
    # total_rows(c, table_name, print_out=True)
    # table_col_info(c, table_name, print_out=True)

    # lsSnips(table_name, cn)
    # lsSnipsGitHubmd(table_name, cn)

    # bbeditBody2OtherBodies(table_name, cn)
    # next line might be slow on large databases
    # values_in_col(c, table_name, print_out=True)
    # subtablesGitHubmd(table_name, cn)
    catfreq(table_name, cn)
    conn.close()
