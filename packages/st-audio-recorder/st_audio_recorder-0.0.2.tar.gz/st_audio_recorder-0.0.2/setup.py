# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_audio_recorder', 'streamlit_audio_recorder.st_audiorec']

package_data = \
{'': ['*'],
 'streamlit_audio_recorder.st_audiorec': ['frontend/*',
                                          'frontend/build/*',
                                          'frontend/build/static/*',
                                          'frontend/build/static/css/*',
                                          'frontend/build/static/js/*',
                                          'frontend/public/*',
                                          'frontend/src/*']}

install_requires = \
['numpy>=1.25.2,<2.0.0', 'streamlit>=1.26.0,<2.0.0']

setup_kwargs = {
    'name': 'st-audio-recorder',
    'version': '0.0.2',
    'description': '',
    'long_description': "# streamlit_audio_recorder (Custom Component)\n\nImplemented by [Stefan Rummer](https://www.linkedin.com/in/stefanrmmr/) - (work in progress)<br/>\nBased on [doppelgunner](https://github.com/doppelgunner/audio-react-recorder)'s [Audio-React-Recorder](https://www.npmjs.com/package/audio-react-recorder)<br/>\n\n![Screenshot 2022-05-16 at 16 58 36](https://user-images.githubusercontent.com/82606558/168626886-de128ffa-a3fe-422f-a748-395c29fa42f9.png)<br/>\n\n## Features & Outlook\n- Managing access to your microphone via the browser's Media-API\n- Record, playback and revert audio-captures within the streamlit app\n- Download the final recording to your local system (WAV, 16 bit, 44.1 kHz)\n- Directly return audio recording-data to Python backend! (arrayBuffer)<br><br>\n- **NEW:** Reduced repo size by removal of redundant node-modules! (393Mb --> 70Mb)\n- **NEW:** Simplified SETUP TUTORIAL, that will get you to record audio within no time!\n\n\n## Component Setup - step by step\n**1.** Import and install relevant libraries to your Python project. \n```\nimport os\nimport numpy as np\nimport streamlit as st\nfrom io import BytesIO\nimport streamlit.components.v1 as components\n```\n**2.** Add the folder `/st_audiorec` to the top level directory of your project.<br><br>\n**3.** Add the file `st_custom_components.py` to your project wherever you like.<br><br>\n**4.** Import the function `st_audiorec()` to your main streamlit application code.\n```\nfrom st_custom_components import st_audiorec\n```\n**5.** Add an instance of the audio recorder component to your streamlit app's code.\n```\nwav_audio_data = st_audiorec()\n\nif wav_audio_data is not None:\n    # display audio data as received on the backend\n    st.audio(wav_audio_data, format='audio/wav')\n    \n# INFO: by calling the function an instance of the audio recorder is created\n# INFO: once a recording is completed, audio data will be saved to wav_audio_data\n```\n**6. Enjoy recording audio inside your streamlit app! 🎈**\n\nFeel free to reach out to me in case you have any questions! <br>\nPls consider leaving a `star` ☆ with this repository to show your support.\n",
    'author': 'Stefan Rummer',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
