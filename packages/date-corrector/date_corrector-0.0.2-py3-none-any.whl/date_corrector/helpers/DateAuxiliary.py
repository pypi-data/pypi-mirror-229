similarChars_en = {
    '0': ['O', 'o', 'D', 'Q', 'n'],
    '1': ['l', 'I', 'i', 'L', 'j', 'J', 't', '|', '/', '\\'],
    '2': ['Z', 'z'],
    '3': ['E'],
    '4': ['R', 'A'],
    '5': ['S', 's', '$'],
    '6': ['b', 'G', 'o'],
    '7': ['T', 'J', 'Z'],
    '8': ['B'],
    '9': ['g'],
    '1/': ['V']
}
similarSeps_en = {
    '/': ['l', 'I', 'i', 'L', 'T', 'j', 'J', '|', '\\', ',', '1', '7'],
    '-': ['_'],
    '.': [' '],
    ' ': []
}
similarAlpha_en = {
    'A': ['4'],
    'D': ['G', 'R', 'B'],
    'F': ['T', 'P', 'E'],
    'J': ['1', 'I', ')'],
    'M': ['V'],
    'N': ['W', 'K'],
    'O': ['0', 'o', 'Q'],
    'S': ['5', 's'],

    'a': ['g', 'o'],
    'b': ['6', 'p'],
    'c': ['e', 'C', 'G'],
    'e': ['G', 'c'],
    'g': ['9', 'a'],
    'h': ['n'],
    'i': ['I', '1', 'L', 'l', '|', '/', '\\', 't', 'j', 'J'],
    'l': ['L', '1', 'I', 'i', '|', '/', '\\', 't', 'j', 'J'],
    'm': ['n'],
    'n': ['m', 'h'],
    'o': ['0', 'O', 'a'],
    'p': ['9', 'b', 'R'],
    'r': ['f', 't'],
    's': ['S', '5'],
    't': ['l', 'L', 'j', 'J', 'f'],
    'u': ['y', 'v'],
    'v': ['y', 'u', 'x'],
    'y': ['u', 'v', 'x']
}
similarNums_en = {
    '0': ['9', '8', '6'],
    '1': ['4', '7'],
    '2': ['3', '1'],
    '3': ['8'],
    '4': ['1'],
    '5': ['6', '9'],
    '6': ['0', '6'],
    '7': ['1'],
    '8': ['9', '6', '0', '5', '3'],
    '9': ['8', '0'],
}
months_en = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
dateFormats_en = [
    'nnsnnsnnnn', 'nnnnsnnsnn', 'nnsnnsnn',

    'nsnnsnnnn', 'nnsnsnnnn', 'nsnsnnnn',
    'nsnnsnn', 'nnsnsnn', 'nsnsnn',

    'nnsaaasnnnn', 'nnsaaasnn',

    'nnsaaaaaaaaasnnnn'
]
possibleOrders_en = ['dmy', 'mdy', 'ymd']



similarChars_ar = {
    '٠': ['.', ',', '-', 'ء', 'ن', '،', '؛'],
    '١': ['l', 'ا', 'إ', 'أ', 'آ', 'ل', 'ر', 'ز'],
    '٢': ['ا', 'إ', 'أ', 'آ', 'ل', '؟'],
    '٣': ['ا', 'إ', 'أ', 'آ', 'ل'],
    '٤': ['ك', 'ع', 'غ', 'ح', 'خ'],
    '٥': ['o', 'ه', 'و', 'م', 'ؤ', 'ة', 'د'],
    '٦': ['ا', 'إ', 'أ', 'آ'],
    '٧': ['V', 'ل', 'ك'],
    '٨': ['ا', 'إ', 'أ', 'آ'],
    '٩': ['و', 'ف', 'ق']
}
similarSeps_ar = {
    '/': ['ا', 'إ', 'أ', 'آ', 'ل', 'ر', 'ز', '؛'],
    '-': ['_', '،'],
}
similarAlpha_ar = {
    'أ': ['ا', 'ل'],
    'ا': ['أ', 'ل'],
    'ب': ['ت', 'ن', 'ي'],
    'ت': ['ب', 'ن', 'ة'],
    'د': ['ر', 'و', 'ذ', 'ز', 'ه', 'ة'],
    'ر': ['د', 'ز', 'ذ'],
    'س': ['ت', 'ش', 'ن'],
    'ط': ['ف', 'ظ'],
    'غ': ['ف', 'ع'],
    'ف': ['ط', 'غ', 'ق'],
    'ك': ['ل', 'ح', 'خ', 'ج'],
    'ل': ['ا', 'أ', 'ك'],
    'م': ['ت', 'ن'],
    'ن': ['ب', 'ت', 'م', 'س', 'ة'],
    'و': ['ر', 'ز'],
    'ي': ['ب']
}
similarNums_ar = {
    '٠': [],
    '١': [
        '٩', '٨', '٧', '٦', '٢', '٣'
    ],
    '٢': [
        '٣', '٦', '١'
    ],
    '٣': [
        '٢', '٦', '١'
    ],
    '٤': [],
    '٥': [
        '٩'
    ],
    '٦': [
        '٩', '١'
    ],
    '٧': [
        '١'
    ],
    '٨': [
        '١'
    ],
    '٩': [
        '٦', '١'
    ]
}
months_ar = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
]
dateFormats_ar = [
    'nnsnnsnnnn',
    'nsnnsnnnn', 'nnsnsnnnn', 'nsnsnnnn',
    'nnnnsnnsnn',
    'nnnnsnnsn', 'nnnnsnsnn', 'nnnnsnsn',

    'nnnnsaaaaaasnn', 'nnsaaaaaasnnnn', 'nnnnsaaaaaasn', 'nsaaaaaasnnnn'
]
possibleOrders_ar = ['dmy', 'ymd']


aux_data = {
    'en': {
        'similarChars': similarChars_en,
        'similarAlpha': similarAlpha_en,
        'similarSeps': similarSeps_en,
        'similarNums': similarNums_en,
        'dateFormats': dateFormats_en,
        'months': months_en,
        'possibleOrders': possibleOrders_en,
    },
    'ar': {
        'similarChars': similarChars_ar,
        'similarAlpha': similarAlpha_ar,
        'similarSeps': similarSeps_ar,
        'similarNums': similarNums_ar,
        'dateFormats': dateFormats_ar,
        'months': months_ar,
        'possibleOrders': possibleOrders_ar,
    }
}