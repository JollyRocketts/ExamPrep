from question_generation_main import QuestionGeneration

def txt2questions(doc: str, n=5, o=4) -> dict:
    """ Get all questions and options """

    qGen = QuestionGeneration(n, o)
    q = qGen.generate_questions_dict(doc)
    for i in range(len(q)):
        temp = []
        for j in range(len(q[i + 1]['options'])):
            temp.append(q[i + 1]['options'][j + 1])
        # print(temp)
        q[i + 1]['options'] = temp
    return q