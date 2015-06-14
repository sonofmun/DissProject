from Data_Production.sem_extract_pipeline import SemPipeline
for x in (12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29):
    if x > 20:
        a = 'LL'
    else:
        a = 'PPMI'
    pipe = SemPipeline(win_size=x, lemmata=False, algo=a, svd=1.0, files='/cluster/shared/mmunso01/diss_Data/LXX', c=30, occ_dict='/cluster/shared/mmunso01/diss_Data/LXX_word_occurrence_dict.pickle', min_count=1, jobs=1)
    pipe.runPipeline()
