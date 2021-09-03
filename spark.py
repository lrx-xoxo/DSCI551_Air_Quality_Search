from pyspark import SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as fc
import sys
import pandas as pd
#sc = SparkSession.builder.appName("example").getOrCreate()
#dataframe = sc.read.json('cleaned.json')
#df = dataframe[dataframe.pollutant_standard=='PM25 Annual 2012'].groupBy('city').agg(fc.mean('aqi'))
#df.coalesce(1).write.format("csv").option("header","false").mode("append").save("output2.csv")

sc = SparkContext.getOrCreate()
lines = sc.textFile('cleaned.csv')
results = lines.filter(lambda line:"PM25 Annual 2012" in line.split(",")[11])\
         .map(lambda line: (line.split(",")[4], float(line.split(",")[0])))\
         .aggregateByKey((0,0), lambda a,b:(a[0]+b, a[1] + 1), \
         lambda a,b: (a[0] + b[0], a[1] + b[1]))\
         .mapValues(lambda v: v[0]/v[1])\
         .collect()

#print(results)
df = pd.DataFrame(results, columns=['city','average_aqi'])
df.to_csv("average.csv")
