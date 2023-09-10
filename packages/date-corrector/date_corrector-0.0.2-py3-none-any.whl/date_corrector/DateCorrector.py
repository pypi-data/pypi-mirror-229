from datetime import datetime
import heapq
from .helpers.DateAuxiliary import aux_data
from .helpers.Suggestion import Suggestion

REPLACE_W = 1
REMOVE_W = 1.2
ADD_W = 1.2

DAY_RANGE = [1, 31]
MONTH_RANGE = [1, 12]
YEAR_RANGE = [1950, datetime.now().year]

def correct_date_char(char, format, months_chars):
    corrected_chars = []

    if format[0] == 'n':
        for key in similarChars:
            if char in similarChars[key]:
                if len(key) == 1 or format[:2] == 'ns':
                    corrected_chars.append(key)
    if format[0] == 's':
        for key in similarSeps:
            if char in similarSeps[key]:
                corrected_chars.append(key)
    if format[0] == 'a':
        for key in similarAlpha:
            if char in similarAlpha[key] and key in months_chars:
                corrected_chars.append(key)

    if len(corrected_chars) == 0:
        return [None]
    else:
        return corrected_chars
    

def verify_number(char, format):
    char = int(char)
    if format[:4] == 'nnnn':
        if char == 1 or char == 2:
            return True
    elif format[:3] == 'nnn':
        if char == 0 or char == 9:
            return True
    elif format[:2] == 'nn':
        if char <= 3 and char >= 5:
            return True
    else:
        return True
    return False


def correct_date_num(char, format):
    corrected_nums = []

    if format[0] == 'n':
        for key in similarNums:
            if char in similarNums[key] and verify_number(key, format):
                corrected_nums.append(key)
        
    return corrected_nums


def get_min_suggestions(suggestions, minimums_cnt):
    suggestions = set(suggestions)
    accuracies = set(map(lambda x: x.accuracy, suggestions))
    minimums = heapq.nsmallest(minimums_cnt, accuracies)
    new_suggestions = list(filter(lambda x: x.accuracy <= minimums[-1], suggestions))

    return new_suggestions


def update_months(months, char):
    new_months = []
    for month in months:
        if month[0] == char:
            new_months.append(month[1:])
    return new_months
   

def get_status(date, format, months):
    status = {
        'condition': False,
        'corrected': None,
        'added': None
    }
    months_chars = []

    if format[0] == 'n':
        if format[:4] == 'nnnn':
            status['added'] = list(similarNums)[1:3]
        elif format[:3] == 'nnn':
            status['added'] = list(similarNums)[0]
        else:
            status['added'] = list(similarNums)[1]
        status['condition'] = (date[0] in similarChars)

    elif format[0] == 's':
        status['added'] = list(similarSeps)[-2]
        status['condition'] = (date[0] in similarSeps)

    elif format[0] == 'a':
        months_chars = list(set(map(lambda x: x[0], months)))
        status['added'] = months_chars
        status['condition'] = (date[0] in months_chars)

    if status['condition']:
        status['corrected'] = [date[0]] + correct_date_num(date[0], format)
    else:
        status['corrected'] = correct_date_char(date[0], format, months_chars)

    return status


def update_correction_dict(correctionDict, actual, corrected):
    if actual is not None:
        if corrected in similarSeps:
            if corrected in correctionDict['similarSeps']:
                if actual in correctionDict['similarSeps'][corrected]:
                    correctionDict['similarSeps'][corrected][actual] += 1
                else:
                    correctionDict['similarSeps'][corrected][actual] = 1
            else:
                correctionDict['similarSeps'][corrected] = {actual: 1}

        elif corrected.isdigit() and actual.isdigit():
            if corrected in correctionDict['similarNums']:
                if actual in correctionDict['similarNums'][corrected]:
                    correctionDict['similarNums'][corrected][actual] += 1
                else:
                    correctionDict['similarNums'][corrected][actual] = 1
            else:
                correctionDict['similarNums'][corrected] = {actual: 1}

        elif corrected.isdigit() and not actual.isdigit():
            if corrected in correctionDict['similarChars']:
                if actual in correctionDict['similarChars'][corrected]:
                    correctionDict['similarChars'][corrected][actual] += 1
                else:
                    correctionDict['similarChars'][corrected][actual] = 1
            else:
                correctionDict['similarChars'][corrected] = {actual: 1}

        elif not corrected.isdigit() and not actual.isdigit():
            if corrected in correctionDict['similarAlpha']:
                if actual in correctionDict['similarAlpha'][corrected]:
                    correctionDict['similarAlpha'][corrected][actual] += 1
                else:
                    correctionDict['similarAlpha'][corrected][actual] = 1
            else:
                correctionDict['similarAlpha'][corrected] = {actual: 1}

    return correctionDict


def form_new_sugg(suggestion, char, weight):
    return Suggestion(
        char + suggestion.date,
        weight + suggestion.accuracy,
    )


def get_combined_results(possibilities, conditions, correct_chars, added_chars):
    results = []

    if conditions == True:
        for sugg in possibilities['replaced'][0]:
            results.append(
                form_new_sugg(sugg, correct_chars[0], 0)
            )
        for i in range(1, len(possibilities['replaced'])):
            for sugg in possibilities['replaced'][i]:
                results.append(
                    form_new_sugg(sugg, correct_chars[i], REPLACE_W)
                )
    else:
        for i in range(len(possibilities['replaced'])):
            if correct_chars[i] != None:
                for sugg in possibilities['replaced'][i]:
                    results.append(
                        form_new_sugg(sugg, correct_chars[i], REPLACE_W)
                    )
    
    for i in range(len(possibilities['added'])):
        for sugg in possibilities['added'][i]:
            results.append(
                form_new_sugg(sugg, added_chars[i], ADD_W)
            )

    for sugg in possibilities['removed']:
        results.append(
            form_new_sugg(sugg, '', REMOVE_W)
        )

    return results


def get_possibilities(date, format, months, dp=dict()):
    # stopping condition
    if len(date) == 0:
        if len(format) == 0:
            return [Suggestion('', 0)]
        elif len(format) == 1:
            return [Suggestion(list(similarNums)[1], ADD_W*len(format))]
        return []
    if len(format) == 0:
        return [Suggestion('', REMOVE_W*len(date))]
    
    # dynamic programming restoring
    if date in dp:
        if format in dp[date]:
            if str(months) in dp[date][format]:
                return dp[date][format][str(months)]
    
    # get necessary information for recursive call
    status = get_status(date, format, months)
    conditions = status['condition']
    corrected_chars = status['corrected']
    added_chars = status['added']

    # initialize possibilities dictionary
    possibilities = {
        'replaced': [],
        'added': [],
        'removed': None
    }

    # recursive call for replacement
    for i in range(len(corrected_chars)):
        date_jump = 1
        format_jump = 1
        if corrected_chars[i] != None:
            date_jump = len(corrected_chars[i])
            format_jump = date_jump      

        if format[0] == 'a':
            months_corrected = update_months(months, corrected_chars[i])
            if len(months_corrected) == 1 and months_corrected[0] == '':
                format_jump = format.index('s')
        else:
            months_corrected = months

        possibilities['replaced'].append(
            get_possibilities(date[date_jump:], format[format_jump:], months_corrected, dp)
        )

    # recursive call for adding
    for i in range(len(added_chars)):
        format_jump = 1
        if format[0] == 'a':
            months_added = update_months(months, added_chars[i])
            if len(months_added) == 1 and months_added[0] == '':
                format_jump = format.index('s')
        else:
            months_added = months

        possibilities['added'].append(
            get_possibilities(date, format[format_jump:], months_added, dp)
        )

    # recursive call for removal
    possibilities['removed'] = get_possibilities(date[1:], format, months, dp)

    # combining and minimizing suggestions
    suggestions = get_combined_results(possibilities,
                                       conditions, corrected_chars, added_chars)
    suggestions = get_min_suggestions(suggestions, 2)

    # dynamic programming storing
    if date in dp:
        if format in dp[date]:
            dp[date][format][str(months)] = suggestions
        else:
            dp[date][format] = {str(months): suggestions}
    else:
        dp[date] = {format: {str(months): suggestions}}
    return suggestions


def fix_separations(suggestions):
    filtered = []

    for sugg in suggestions:
        firstSep = ''
        secondSep = ''
        for char in sugg.date:
            if char in similarSeps:
                if firstSep == '':
                    firstSep = char
                else:
                    secondSep = char
                    break
        if firstSep != secondSep:
            if list(similarSeps).index(firstSep) < list(similarSeps).index(secondSep):
                new_sugg = sugg.date.replace(secondSep, firstSep)
            else:
                new_sugg = sugg.date.replace(firstSep, secondSep)
            edits = REPLACE_W + sugg.accuracy
            filtered.append(
                Suggestion(new_sugg, edits)
            )
        else:
            filtered.append(sugg)

    return filtered


def edits_to_accuracy(suggestions, date):
    new_suggestions = []

    for sugg in suggestions:
        edits_cnt = sugg.accuracy
        cer_value = edits_cnt/len(date)
        accuracy = round((1-cer_value) * 100, 2)
        if accuracy > 0:
            new_suggestions.append(
                Suggestion(sugg.date, accuracy)
            )

    return new_suggestions


def get_separation_type(date):
    for char in date:
        if not char.isdigit():
            return char


def get_possible_section_types(section):
    types = []
    if len(section) == 3:
        if section in map(lambda x: x[:3], months):
            types.append('m')
    elif section in months:
        types.append('m')
    else:
        section_int = int(section)
        if len(section) == 4:
            if section_int in range(YEAR_RANGE[0], YEAR_RANGE[1]+1):
                types.append('y')
        elif section_int in range(DAY_RANGE[0], DAY_RANGE[1]+1):
            types.append('d')
            if section_int <= YEAR_RANGE[1] % 100:
                types.append('y')
                if section_int <= 12:
                    types.append('m')
        elif YEAR_RANGE[0] < 2000 and section_int >= YEAR_RANGE[0] % 100:
            types.append('y')
    
    return types


def estimate_date_order(date):
    sep = get_separation_type(date)
    splitted = date.split(sep)

    new_orders = possibleOrders

    for i in range(len(splitted)):
        types = get_possible_section_types(splitted[i])

        if len(types) == 0:
            return []

        new_orders = list(filter(lambda x: x[i] in types, new_orders))

    return new_orders


def filter_suggestions(suggestions):
    new_suggestions = []
    for sugg in suggestions:
        estimations = estimate_date_order(sugg.date)
        
        if len(estimations) != 0:
            new_suggestions.append(sugg)

    return new_suggestions


def round_suggestion_edits(suggestions):
    new_suggestions = []
    for sugg in suggestions:
        new_suggestions.append(
            Suggestion(sugg.date, round(sugg.accuracy,4))
        )

    return new_suggestions


def correctDate(date:str, language:str) -> list:
    global aux_data

    if not isinstance(date, str):
        raise TypeError('date must be a string!!')
    if not isinstance(language, str):
        raise TypeError('language must be a string!!')
    if language not in aux_data:
        raise ValueError('invalid language value!!')

    date = date.strip()
    if date == '':
        return date
    
    data = aux_data[language]

    global similarChars
    global similarAlpha
    global similarSeps
    global similarNums
    global months
    global possibleOrders

    similarChars = data['similarChars']
    similarAlpha = data['similarAlpha']
    similarSeps = data['similarSeps']
    similarNums = data['similarNums']
    dateFormats = data['dateFormats']
    months = data['months']
    possibleOrders = data['possibleOrders']
    
    suggestions = []
    dp = dict()
    for format in dateFormats:
        suggestions.extend(get_possibilities(date, format, months, dp))
    
    suggestions = get_min_suggestions(suggestions, 2)
    suggestions = fix_separations(suggestions)
    suggestions = filter_suggestions(suggestions)
    suggestions = round_suggestion_edits(suggestions)
    suggestions = get_min_suggestions(suggestions, 1)

    suggestions = edits_to_accuracy(suggestions, date)
    suggestions.sort(key=lambda x: (x.accuracy, len(x.date)), reverse=True)

    new_suggestions = []
    for sugg in suggestions:
        new_suggestions.append(sugg.listify())

    return new_suggestions


def listLanguages() -> list:
    return list(aux_data)