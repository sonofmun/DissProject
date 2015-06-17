from Data_Production.sem_extract_pipeline import SemPipeline
for x in (.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.1, 1.2, 1.3, 1.4, 1.5):
    a = 'PPMI'
    pipe = SemPipeline(win_size=16, lemmata=False, algo=a, svd=x, files='/cluster/shared/mmunso01/diss_Data/LXX', c=30, occ_dict='/cluster/shared/mmunso01/diss_Data/LXX_word_occurrence_dict.pickle', min_count=1, jobs=1)
    pipe.runPipeline()
