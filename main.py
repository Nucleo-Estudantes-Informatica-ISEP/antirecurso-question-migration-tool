import json
import os
import subprocess

LIB_PATH = 'lib/jdeserialize.jar'
BIN_PATH = 'bin/'

QUESTION_CLASS_SUFFIX = 'd'
ANSWER_CLASS_SUFFIX = 'g'


def get_class_name(file_name):
    return file_name.split('antirecurso017_')[1].split('.bin')[0]


def get_address(line):
    return line.split('instance ')[1].split('/')[0].replace(':', '')


def get_list(lists, list_addr):
    return next(
        (_list['answers'] for _list in lists if _list['address'] == list_addr),
        None,
    )


def get_answer_text(answers, answer_addr):
    return next(
        (
            answer['text']
            for answer in answers
            if answer['address'] == answer_addr
        ),
        None,
    )


def main():
    classes_questions = {}
    for file in os.listdir(BIN_PATH):
        args = ['java', '-jar', LIB_PATH,
                "-noclasses", BIN_PATH+file]
        result = subprocess.check_output(args)
        questions = []
        object = []

        for line in result.splitlines():
            line = line.decode('utf-8')
            if line.startswith('['):
                object = [line]
                questions.append(object)
            elif not line.startswith(']'):
                object.append(line.strip())
        classes_questions[get_class_name(file)] = questions

    questions = {}
    answers = {}
    lists = {}

    for _class, value in classes_questions.items():
        questions[_class] = []
        answers[_class] = []
        lists[_class] = []

        for object in value:
            if object[2].endswith(f'{QUESTION_CLASS_SUFFIX}:'):
                list_address = object[3].split('_h')[1].split(';')[
                    0].replace('= r_', '')
                questions[_class].append(
                    {"address": get_address(object[0]), "list_address": list_address, "question": object[4].split('\"')[1]})
            elif object[2].endswith(f'{ANSWER_CLASS_SUFFIX}:'):
                answers[_class].append({"address": get_address(
                    object[0]), "text": object[3].split('\"')[1]})
            elif object[2].endswith('ArrayList'):
                a = object[4:]
                for i in range(len(a)):
                    if a[i].strip() == '':
                        a = a[:i]
                        break
                a = [x.split('_h')[1].split(';')[0].replace('= r_', '')
                     for x in a]
                lists[_class].append(
                    {"address": get_address(object[0]), "answers": a})

    data = {}

    for _class in classes_questions:
        data[_class] = []
        for question in questions[_class]:
            list_addr = question['list_address']
            data[_class].append(
                {"question": question['question'], "answers": []})

            question_list = get_list(lists[_class], list_addr)
            for q in question_list:
                answer_text = get_answer_text(answers[_class], q)
                data[_class][-1]['answers'].append(answer_text)

            data[_class][-1]['correct_index'] = 0

    json.dump(data, open('data.json', 'w'),
              indent=2, ensure_ascii=False)


main()
