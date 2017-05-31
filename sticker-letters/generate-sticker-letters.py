import jinja2
import csv

template = r"""
\documentclass[paper=a4]{scrlttr2}
\usepackage[utf8]{inputenc}

\makeatletter
\@setplength{toaddrvpos}{3.5cm}
\@setplength{toaddrhpos}{-2cm}
\makeatother

\setkomavar{fromname}{Florian Bruhin}
\setkomavar{fromaddress}{Ruchwiesenstrasse 36 \\ 8404 Winterthur \\ Switzerland}
\setkomavar{signature}{Florian Bruhin / The Compiler}
\setkomavar{date}{6th July 2016}
\setkomavar{fromemail}{me@the-compiler.org}

\setkomavar{subject}{
{{what}} crowdfunding stickers}

\setlength{\parindent}{0em}
\setlength{\parskip}{1em}

\begin{document}
{% for addr in addrs %}
\begin{letter}{ {{addr}} }
\opening {Hi!}

\vspace{1em}

As promised some months ago, here are the {{what}} stickers you selected with
your pledge on Indiegogo. According to my records, your pledge does not include
a t-shirt.

If you think this is wrong, please contact me ASAP on me@the-compiler.org. If
you need more stickers (like for a local hackerspace), don't hesitate to
contact me either!

\vspace{1em}

Thanks again for your support!

\closing{Greetings from Switzerland,}
\end{letter}
{% endfor %}
\end{document}
"""

pytest_addr = []
qute_addr = []


def process(line, what):
    if line['Name'] != line['Shipping Name']:
        print('{}: name {:35} != shipping {:35}'.format(
            what, line['Name'], line['Shipping Name']))

    line['zip_and_city'] = '{} {}'.format(line['Shipping Zip/Postal Code'],
                                          line['Shipping City'])

    line['state_and_zip'] = '{} {}'.format(line['Shipping State/Province'],
                                           line['Shipping Zip/Postal Code'])
                                          

    country_mapping = {
        'UK': 'United Kingdom',
        'US': 'United States',
        'USA': 'United States',
    }

    try:
        line['Shipping Country'] = country_mapping[line['Shipping Country']]
    except KeyError:
        pass

    if line['Shipping Country'] == 'United States':
        addr_parts = [
            'Shipping Name',
            'Shipping Address',
            'Shipping Address 2',
            'Shipping City',
            'state_and_zip',
            'Shipping Country',
        ]
    elif line['Shipping Country'] == 'United Kingdom':
        addr_parts = [
            'Shipping Name',
            'Shipping Address',
            'Shipping Address 2',
            'Shipping City',
            'Shipping State/Province',
            'Shipping Zip/Postal Code',
            'Shipping Country',
        ]
    else:
        addr_parts = [
            'Shipping Name',
            'Shipping Address',
            'Shipping Address 2',
            'zip_and_city',
            'Shipping State/Province',
            'Shipping Country',
        ]

    addr = r' \\ '.join(line[e].replace('#', '\\#') for e in addr_parts if line[e])
    if what == 'pytest':
        pytest_addr.append(addr)
    elif what == 'qutebrowser':
        qute_addr.append(addr)
    else:
        assert False, what


with open('pytest.csv') as ptf, open('qutebrowser.csv') as qf:
    ptreader = csv.DictReader(ptf)
    qreader = csv.DictReader(qf)

    for line in ptreader:
        if line['shirt color'] not in ['no', 'N/A']:
            continue
        assert line['shirt size'] == line['shirt color']
        process(line, 'pytest')

    for line in qreader:
        if line['T-Shirt'] not in ['no', 'N/A']:
            continue
        if line['Stickers']  == 'no':
            continue
        process(line, 'qutebrowser')

print()

pytest_out = jinja2.Template(template).render(addrs=pytest_addr, what='pytest')
qute_out = jinja2.Template(template).render(addrs=qute_addr,
                                            what='qutebrowser')

with open('qute.tex', 'w', encoding='utf-8') as f:
    f.write(qute_out)


with open('pytest.tex', 'w', encoding='utf-8') as f:
    f.write(pytest_out)
