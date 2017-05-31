import jinja2
import csv
import subprocess
import sys

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
\setkomavar{date}{\today}
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

As promised, here are your qutebrowser stickers. According to my records, your
pledge does not include a t-shirt.

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

addrs = []


def process(line):
    if line['Backer Name'] != line['Shipping Name']:
        print('name "{}" != shipping "{}"'.format(
            line['Backer Name'], line['Shipping Name']))

    if line['Shipping Delivery Notes']:
        print('NOTES: {} - {}'.format(line['Backer Name'],
                                      line['Shipping Delivery Notes']))

    line['zip_and_city'] = '{} {}'.format(line['Shipping Postal Code'],
                                          line['Shipping City'])

    line['state_and_zip'] = '{} {}'.format(line['Shipping State'],
                                           line['Shipping Postal Code'])

    line['city_state_zip'] = '{} {} {}'.format(line['Shipping City'],
                                               line['Shipping State'],
                                               line['Shipping Postal Code']).upper()

    if line['Shipping Country Code'] == 'US':
        addr_parts = [
            'Shipping Name',
            'Shipping Address 1',
            'Shipping Address 2',
            'Shipping City',
            'state_and_zip',
            'Shipping Country Name',
        ]
    elif line['Shipping Country Code'] == 'GB':
        addr_parts = [
            'Shipping Name',
            'Shipping Address 1',
            'Shipping Address 2',
            'Shipping City',
            #'Shipping State',
            'Shipping Postal Code',
            'Shipping Country Name',
        ]
    elif line['Shipping Country Code'] in ['DE', 'CH']:
        addr_parts = [
            'Shipping Name',
            'Shipping Address 1',
            'Shipping Address 2',
            'zip_and_city',
            'Shipping Country Name',
        ]
    elif line['Shipping Country Code'] == 'AU':
        addr_parts = [
            'Shipping Name',
            'Shipping Address 1',
            'Shipping Address 2',
            'city_state_zip',
            'Shipping Country Name',
        ]
    else:
        addr_parts = [
            'Shipping Name',
            'Shipping Address 1',
            'Shipping Address 2',
            'zip_and_city',
            'Shipping State',
            'Shipping Country Name',
        ]

    parts = [line[e].replace('#', '\\#') for e in addr_parts if line[e].strip()]
    if not parts:
        print("EMPTY! {}".format(line['Backer Name']))
        return

    addr = r' \\ '.join(parts)
    addrs.append(addr)


with open(sys.argv[1]) as f:
    reader = csv.DictReader(f)

    for line in reader:
        process(line)

print()
print()
print()

out = jinja2.Template(template).render(addrs=addrs)

with open('letters.tex', 'w', encoding='utf-8') as f:
    f.write(out)

subprocess.call(['latexmk', '-pdf', 'letters.tex'])
