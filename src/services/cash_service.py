import time


class CatsCash():

    def __init__(self, answer_time_dely):
        self.queiries = {}
        self.sent_answers = {}# храняться id
        self.dont_sent_answers = {} # храняться готовые ответы
        self.answer_time_dely = answer_time_dely
            # {'queiries': {}, # queiry_id queiries (photo_cag ) and answer (cat_id), chat_id
            #          'answers': {}} # id_person answer answer time

    def delete_sent_cats(self, answer):
        # TODO write this logic
        # delete sent_cats, Then add cats from ans
        #
        return answer

    def make_cats_id_set(self, cats):
        return set(
                [id(cat) for cat in cats]
            )

    def answer_editor(self, answer):
        # do not send too often;
        # do not send the same;
        # save ans
        person_id = id(answer.person)

        if person_id not in self.sent_answers:
            self.sent_answers[person_id]['cats'] = self.make_cats_id_set(
                answer.cats)
            self.sent_answers[person_id]['last_ans_time'] = time.time()

            return answer

        #if self.answers[id(answer)]['last_ans_time'] -  what_time_now < self.answer_time_dely:
         #   r

        answer = self.delete_sent_cats(answer)
        dt = time.time() - self.answers[id(answer)]['last_ans_time']
        if answer:
            if dt > self.answer_time_dely:
                 self.answers[id(answer)]['last_ans_time'] = time.time()

            else:
                self.dont_sent_answers[id(answer)] = self.make_cats_id_set(
                            answer.cats) # make cats set(answer.cats)
                return False

        if person_id in self.dont_sent_answers:
            pass
            ## TODO добавить логику добавления неотправленных

        return answer




        # closest_cats_edited = closest_cats.copy()
        # return closest_cats_edited

    # TODO save answers in cash
    def __answers_to_cash(self, closest_cats):

        pass

    # TODO check answers in cash
    def check_answer(self, person):
        # Was there already such an answer?
        return False

    # # TODO
    # def emb_in_cach(self, img_hash_name):
    #     return False

