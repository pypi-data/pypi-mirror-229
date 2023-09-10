# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opal', 'opal.module']

package_data = \
{'': ['*'],
 'opal': ['models/*',
          'models/2023.9.5b/2023_09_01_performance_mania_top_10000_44e44645_84947aba.csv/lightning_logs/version_2/evaluation/model.ckpt']}

install_requires = \
['numpy>=1.25.2,<2.0.0',
 'pandas>=2.0.3,<3.0.0',
 'pytorch-lightning>=2.0.7,<3.0.0',
 'scikit-learn>=1.3.0,<2.0.0',
 'torch>=2.0.1,<3.0.0',
 'tqdm>=4.66.1,<5.0.0']

setup_kwargs = {
    'name': 'opal-net',
    'version': '2023.9.5b0',
    'description': 'osu!mania score prediction through AI collaborative filtering',
    'long_description': '# :arrow_forward: [**Try Out Opal on Streamlit**](https://opal-ai.streamlit.app/)\n![modelsize](https://img.shields.io/github/size/Eve-ning/opal/src/opal/models/V4/2023_08_01_performance_mania_top_10000_20230819163602.csv/lightning_logs/version_1/evaluation/model.ckpt)\n![version](https://img.shields.io/pypi/v/opal-net)\n![pyversions](https://img.shields.io/pypi/pyversions/opal-net)\n[![https://img.shields.io/pypi/dm/opal-net](https://img.shields.io/pypi/dm/opal-net)](https://pypi.org/project/opal-net/)\n\n[![Test Model Pipeline Inference](https://github.com/Eve-ning/opal/actions/workflows/pipeline-test.yml/badge.svg?branch=master)](https://github.com/Eve-ning/opal/actions/workflows/pipeline-test.yml)\n# :comet: opal-net\nopal is an accuracy-prediction model.\n\nIt uses a Matrix Factorization branch & Multi-layered Perceptron branch to learn associations between user and maps,\nthen use those associations to predict new scores never before seen.\n\n## :hourglass_flowing_sand: Project Status\nCurrently, it\'s in its early access, that means, it\'ll have many problems!\nHowever, we\'re working on it to minimize these issues o wo)b\n\n## :arrow_double_down: Dataset Used\n\nI used the top 10K mania users data from https://data.ppy.sh.\nAfter preprocessing, we use\n- ~10m scores for training\n- ~1m scores for validation and testing each\n\nAfter preprocessing, we found ~30K valid users, ~10K valid maps\nThis models can thus help predict ~300m unplayed scores!\n\n### Users\nWe deem a player on separate years as a different user. This is to reflect\nthe improvement of the player after time.\n\n## :high_brightness: Usage\n\nTo use this, install `opal-net`\n\n```bash\npip install opal-net\n```\n\nThen in a python script\n> Tip: GPU doesn\'t speed this up significantly, you can use a CPU.\n```py\nfrom opal import OpalNet\n\n# Load in the model\n# You can explicitly specify map_location=\'cpu\' or \'cuda\' in map_location=...\nopal = OpalNet.load()\n\n# You can predict a single instance.\n#\n# The 1st arg: "<USER_ID>/<YEAR>",\n# The 2nd arg: "<MAP_ID>/<SPEED>" \n#   <YEAR> is the year of the user to test.\n#   <SPEED> can be {-1, 0, or 1} for {HT, NT, DT}\n#\n# For example: \n# Predict Evening on Year 2020, on the map Triumph & Regret [Regret] at Double Time\npred = opal.predict("2193881/2020", "767046/1")\n\n# You can predict multiple entries at the same time. This is much faster that looping the above.\n# Note that both lists must be of the same length!\n# Note: If you\'re predicting millions, partition the predictions to reduce GPU memory usage!\npreds = opal.predict(["2193881/2020", "2193881/2017"], ["767046/0", "767046/1"])\n\n# Note that if the prediction doesn\'t exist, then it\'ll raise a ValueError\ntry:\n    opal.predict("2193881/2018", "767046/0")\nexcept ValueError:\n    print("Prediction Failed!")\n```\n\n## :brain: AlphaOsu!\nCurrently, opal doesn\'t provide recommendations, however, you can try out [AlphaOsu!](https://alphaosu.keytoix.vip/).\n- [AlphaOsu! GitHub](https://github.com/AlphaOSU)\n- [Support AlphaOsu!](https://alphaosu.keytoix.vip/support)\n\n## Annex\n\n### Why not Score Metric?\nScore is not straightforward to calculate, and may be difficult to debug. Furthermore, score isn\'t of interest when\ncalculating performance points anymore.\n\n[osu!mania ScoreV1 Reference](https://osu.ppy.sh/wiki/en/Gameplay/Score/ScoreV1/osu%21mania)\n',
    'author': 'Evening',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*',
}


setup(**setup_kwargs)
