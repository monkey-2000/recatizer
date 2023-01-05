# -*- coding: utf-8 -*-
import os

import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from dataset_maker import make_cat_individual_images_base

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info("making final data set from raw data")

    images_base = make_cat_individual_images_base(input_filepath)

    images_base.to_csv(output_filepath + "images_database.csv")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    #  project_dir = os.getcwd()

    load_dotenv()
    input_filepath = os.environ["CAT_INDIVIDUALS_DS_PATH"]
    output_filepath = str(project_dir.absolute()) + "/data/raw/"

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables

    main(input_filepath, output_filepath)
# main(input_filepath, output_filepath)
