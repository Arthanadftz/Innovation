# flake8: noqa
import os
import warnings


# TOKEN DISABLE
c.NotebookApp.token = ''
# PASSWORD - root
c.NotebookApp.password = os.getenv("JUPYTER_PASSWORD")  # pylint: disable=undefined-variable
# SSL
# c.NotebookApp.certfile = '/opt/innovation/jupyter_config/mycert.pem'  # pylint: disable=undefined-variable
# c.NotebookApp.keyfile = '/opt/innovation/jupyter_config/mykey.key'  # pylint: disable=undefined-variable
# SOCKET
c.NotebookApp.ip = '0.0.0.0'  # pylint: disable=undefined-variable
c.NotebookApp.port = 8181  # pylint: disable=undefined-variable
# BROWSER
c.NotebookApp.base_url = '/jupyter/'  # pylint: disable=undefined-variable
c.NotebookApp.open_browser = False  # pylint: disable=undefined-variable


warnings.filterwarnings("ignore", category=DeprecationWarning)
