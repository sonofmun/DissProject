__author__ = 'matt'

import pandas as pd
from sklearn.cluster import KMeans

def Clusterer(sub_domain, num_cluster):
	df1 = pd.read_csv('Data/Chapter_2/{0}_word_pairs_CS.csv'.format(sub_domain))
	df2 = pd.DataFrame(index=set(df1['Source']), columns=set(df1['Target']))
	for row in df1.index:
		df2.ix[df1.ix[row, 'Source'], df1.ix[row, 'Target']] = df1.ix[row, 'Weight']
	df2 = 1-df2.fillna(1)
	df_c = pd.DataFrame(KMeans(n_clusters=num_cluster).fit_transform(df2),
						index=df2.index, columns=list(range(num_cluster)))
	df_p = pd.Series(KMeans(n_clusters=num_cluster).fit_predict(df2),
						index=df2.index)
	df_p.to_csv('Data/Chapter_2/{0}_word_{1}_cluster_predictions.csv'.format(sub_domain, num_cluster))
	with open('Data/Chapter_2/{0}_word_{1}_clusters.csv'.format(sub_domain, num_cluster), mode='w', encoding='utf-8') as f:
		f.write('Source,Target,Weight,Type\n')
		for word in df_c.index:
			for cluster in df_c.columns:
				f.write('{0},{1},{2},Undirected\n'.format(word, cluster, df_c.ix[word, cluster]))