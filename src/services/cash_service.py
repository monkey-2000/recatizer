import time
from bson.objectid import ObjectId


class CatsCash():

    def __init__(self, answer_time_dely):
        self.queiries = {}
        self.sent_answers = {}# храняться id
        self.dont_sent_answers = {} # храняться готовые ответы
        self.answer_time_dely = answer_time_dely
            # {'queiries': {}, # queiry_id queiries (photo_cag ) and answer (cat_id), chat_id
            #          'answers': {}} # id_person answer answer time

    def check_answer(self, person):
        # Was there already such an answer?
        return False

    def delete_sent_cats(self, person_id, cats):
        # TODO write this logic
        # delete sent_cats, Then add cats from ans
        sending_cats = []
        for i, cat in enumerate(cats):
            if str(cat._id) not in self.sent_answers[person_id]['cats']:
                sending_cats.append(cat)
        return sending_cats

    def make_cats_id_set(self, cats):
        return set(
                [str(cat._id) for cat in cats]
            )
    def update_sent_answers(self, person_id, cats: list):
        self.sent_answers[person_id]['cats'].update(self.make_cats_id_set(cats))
        self.sent_answers[person_id]['last_ans_time'] = time.time()


    def update_dont_sent_answers(self, person_id, cats: list):
        self.dont_sent_answers[person_id]['cats'].extend(cats)
        self.dont_sent_answers[person_id]['last_ans_time'] = time.time()

    def answer_editor(self, answer):
        # do not send too often;
        # do not send the same;
        # save ans

        person_id = str(answer.person._id)
        if person_id not in self.sent_answers:
            self.sent_answers[person_id] = {}
            self.sent_answers[person_id]['cats'] = set()
            self.update_sent_answers(person_id, answer.cats)
            return answer

        dt = time.time() - self.sent_answers[person_id]['last_ans_time']
        answer.cats = self.delete_sent_cats(person_id, answer.cats)
        if len(answer.cats) > 0:
            if dt > self.answer_time_dely:
                self.update_sent_answers(person_id, answer.cats)

            else:
                if person_id not in self.dont_sent_answers:
                    self.dont_sent_answers[person_id] = {}
                    self.dont_sent_answers[person_id]['cats'] = []
                self.update_dont_sent_answers(person_id, answer.cats)
                answer.cats = []

        return answer
