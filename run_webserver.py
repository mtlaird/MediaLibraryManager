from MediaLibraryManager.Web.WebApp import app
from os import getcwd

from MediaLibraryManager.config import MediaLibraryManagerConfig, set_up_logging

if __name__ == '__main__':

    config = MediaLibraryManagerConfig()
    app.config['mlm-config'] = config
    logger = set_up_logging(config, single_run=False)
    logger.info("Loaded config from {} ...".format(config.filename))

    if config.web_working_directory != "":
        app.root_path = getcwd()
    else:
        app.root_path = config.web_working_directory
    app.run(host=config.web_host, port=config.web_port)
