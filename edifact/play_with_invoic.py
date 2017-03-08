#!/usr/bin/env python3

import sys
import edifact

with open(sys.argv[1], encoding='iso8859-1') as infile:
    msg = edifact.from_string(infile.read())
    print('elements:',msg.elements)
    print('data:',msg.data)
#    help(msg.data['SG2'][0])
#    print(msg.data['SG2'][0].__dict__)
    print()
    print('name and address:', msg.data['SG2'][0].elements['Name and address'][0].data[4])
#    print(msg.data['SG2'][0].elements)
    print()
    print('SGG2/0/SG3:',msg.data['SG2'][0].elements['SG3'])
    print()
    print('SG2/1/elements:',msg.data['SG2'][1].elements)

#    print('Faktura:', msg.__dict__)
#    print('Faktura:', msg.data.items())

    print('Lieferant:', msg.data['SG2'][0].elements['SG3'][0].elements['Reference'][0].data[0][1])

    print('Kunde:', msg.data['SG2'][1].elements['SG3'][0].elements['Reference'][0].data[0][1])
    print('SG27:', msg.data['SG27'])

    print('alle SG level 0:', msg.data.keys())
