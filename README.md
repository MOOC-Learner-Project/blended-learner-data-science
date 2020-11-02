# blended-learner-data-science
Blended Learner Data Science (BLDS). Use-case for AppInventor

Analyse and visualize data from the appinventor course and the corresponding EDX server and AppInventor server data.

### Requirements
Python 3, Pandas, Numpy, Colorspacious, Dill, Networkx, Pillow, Python_dateutil, Python_Lenvenshtein, Matplotlib, Seaborn, SKLearn, Textstat, Jupyter, PyGraphviz

For the packages installable through pip, you may use the `requirements.txt` to install them.

## aggregated_sessions
Visualize appinventor sessions aggregated among all students.

## click_frequencies
Visualize the number of days students have clickstream activity.

## knowledge_type_transitions
Quanitfy how students move between knowledge types that resources contain.

## levenshtein
Look at levenshtein similarity between the resources students use and the knowledge type categories they use.

## link_edx_appinventor
Visualize, anonymize and link data between the EDX server and the AppInventor Server.

## resource_timelines
Visualize resource usage for students over the time that the course is offered.

## resource_transitions
Visualize how students move between resources.

## reviews
Determine resource reviews based on two metrics.

## scm_bky
Visualize aggregated SCM and BKY usage.

## scm_bky_node_types
Visualize nodes used by students in BKY and SCM.

## scm_bky_pairs
Visualize aggregated SCM-BKY transitions.

## signup_dropout
Visualize aggregated signups and dropouts of students.

## user_and_course_dfs
Generate necessary dataframes for other notebooks. Generates a serialized pickle file that the other notebooks load. Must run before other notebooks.

## Run
You must modify the variables in `config.ini`, run `user_and_course_dfs`. To get the necessary resource data from the course, you must run https://github.com/18goldr/web-crawler.

By default, all files will display the graphs inline. To save the graphs to a file, you must modify the variable `to_file` in `config.ini` to be `True`. You may also modify `to_file` anywhere within the scripts. This allows to save to file on a per-graph basis and is easier than having to reload external modules in Jupyter/IPython.

# References

```
@inproceedings{gold2020analyzing,
  title={Analyzing K-12 Blended MOOC Learning Behaviors},
  author={Gold, Robert and Hemberg, Erik and O'Reilly, Una-May},
  booktitle={Proceedings of the Seventh ACM Conference on Learning@ Scale},
  pages={345--348},
  year={2020}
}
```