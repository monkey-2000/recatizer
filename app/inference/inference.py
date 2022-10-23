class database:

    def __init__(self):
        pass

    def find(self, embedding, mode):

        if mode == 'saw':
            #match with find
            pass

        if mode == 'find':
            #match with saw
            pass

    def delete(self, match, mode):
        # delete from mode dataset (find saw)
        pass

    def update(self, info, ):
        # update
        pass



def get_embedding(img_path):
    #model.predict(img_path)
    pass


def ask_cat_owner(img_path, owner_id):
    """send match result to owner via tg bot. Return oner answer: bool"""
    pass

def inference(msg):
    ## Сделать один консьюмер для одного топика. Свой инференс для каждого консьюмера
    ## Геопозиция? Сахар
    ## json - много памяти? Что в замен
    # database -> embedding_matcher - spatial (
    ## base monogo
    ##
    embedding = get_embedding(msg['img_path'])

    is_match_correct = False
    if msg['status'] == 'saw':
        match, owner_id = database.find(embedding, 'saw')

        if match:
            is_match_correct = ask_cat_owner(msg['img_path'], owner_id)

    elif msg['status'] == 'find':
        match, chat_id = database.find(embedding, 'find')

        if match:
            is_match_correct = ask_cat_owner(match, msg['chat_id'])

    if is_match_correct: ### удаляется только
        database.delete(match, msg['status'])
    else:
        database.update(msg['img_path'], msg['status'])

    database.update([msg, match, is_match_correct], 'train')


