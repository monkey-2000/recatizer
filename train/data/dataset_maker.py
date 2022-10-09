import os
import logging
import pandas as pd

def make_cat_individual_images_base(dataset_path):
    """
    create DataFrame from Cat Individual Images dataset
     https://www.kaggle.com/datasets/timost1234/cat-individuals

     This data set contains 13536 images of 518 cats. The images were acquired using regular digital cameras or
     smartphones. The resolutions of the images ranged between 195 x 261 and 4608 x 3453 pixels.
    """

    dataset_base = []
    for dirpath, dirnames, filenames in os.walk(dataset_path):
        for filename in filenames:
            id_ = os.path.split(dirpath)[-1]
            #print(filename)
            dataset_base.append({'cat_id': id_,
                                 'img': filename,
                                 'path': os.path.join(id_, filename)})
    return pd.DataFrame(dataset_base)


def make_dataset_base(dataset_path, name='CatIndividualImages'):

    if name=='CatIndividualImages':
        dataset_base = make_cat_individual_images_base(dataset_path)
    else:
        raise ValueError('no such dataset')

    return dataset_base


if __name__ == '__main__':
    # logger = logging.getLogger('logger')
    # res_hanler_text = logging.FileHandler('results1.log')
    # res_hanler_text.setLevel(logging.INFO)
    # logger.setLevel(logging.INFO)
    # logger.addHandler(res_hanler_text)


    dataset_path = 'D:\\30 LOGS\\datasets\\chinas_uav\\raw data\\'
    print(make_dataset_base(dataset_path))

        # for dirname in zip(dirnames, filenames):
        #     print('Каталог', os.path.join(dirpath, dirname))
        #     print('Каталог', dirname)
        # for file in filenames:
        #     print('Файл:', os.path.join(dirpath, file))
