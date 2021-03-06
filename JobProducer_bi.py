#! /usr/bin/env python
#coding=utf-8
'''
Created on 2011-3-22

@author: wangyujie
'''
import sys
import time
import os

HADOOP_HOME = '/home/users/wangxiao10/workspace/soft_install/hadoop-client-stoff/'
HADOOP_BIN = HADOOP_HOME + "hadoop/bin/hadoop"
PATH_DICT = {"newquerysort":"/log/20682/newquerysort/$day/0000/szwg-rank-hdfs.dmop/$file"
			,"detailnewquerysort":"/log/20682/detailnewquerysort/$day/0000/szwg-rank-hdfs.dmop/$file"
			,"newcookiesort":"/log/20682/newcookiesort/$day/0000/szwg-rank-hdfs.dmop/$file"
			,"distributary":"/log/20682/distributary/20120812/0000/szwg-rank-hdfs.dmop/$file"
			,"mergelog":"/log/20682/mergelog_v1/$day/0000/szwg-rank-hdfs.dmop/$file"
			,"mergelog-v2":"/log/20682/mergelog_v2_daily_to_stoff/$day/0000/szwg-ecomon-hdfs.dmop/part-*-A"
			,"mergelog-v2-rank":"hdfs://szwg-rank-hdfs.dmop.baidu.com:54310/app/ps/rank/ubs/mergelog-v2/mergelog-out/$day/all/part-*-A"
			,"mergelog-v2-rank-all":"hdfs://szwg-ecomon-hdfs.dmop.baidu.com:54310/app/ps/rank/ubs/mergelog-v2-all/mergelog-out/$day/all/part-*-A"
			,"mergelog-v2-hour":"/log/20682/mergelog_v2_hourly_to_stoff/$day/1200/szwg-ecomon-hdfs.dmop/part-*-A"
			,"mergelog-v2-hour-rank":"hdfs://szwg-rank-hdfs.dmop.baidu.com:54310/app/ps/rank/ubs/mergelog-v2/mergelog-out/$day/15/part-*-A"
			,"bws_access":"/log/20682/bws_access/$day/0000/szwg-rank-hdfs.dmop/*/*"
			,"accesslog":"/log/20682/accesslog_to_stoff/$day/0000/szwg-rank-hdfs.dmop/*/*.log*"
			,"jym":"/ps/ubs/jinyingming/ubsOutput/caipu/log/*"}
MAX_TRIES = 1

class HadoopJobProducer_bi:
	"""to produce hadoop job shecll string"""
	def __init__(self):
		self._file_list = []
		self._map_str = ""
		self._reduce_str = ""
		self._combiner_str = ""
		self._reduce_num = -1
		self._input = []
		self._output = None
		self._other_str = None
		self._hadoop_cmd = HADOOP_BIN +  " ustreaming -mapinstream binary -inputformat org.apache.hadoop.mapred.SequenceFileAsBinaryInputFormat "
		self._job_name = "default job"
		self._priority = "NORMAL"

	def addFile(self,files):
		"""add files to produce"""
		if type(files) == type("1"):
			self._file_list.append(files)
		elif type(files) == type([1,2]):
			for file in files:
				self._file_list.append(file)

	def setMapstr(self,map_str):
		"""set map shell command"""
		self._map_str = map_str

	def setReducestr(self,reduce_str):
		"""set reduce shecll command"""
		self._reduce_str = reduce_str

	def setCombinerstr(self,_combiner_str):
		"""set combiner shecll command"""
		self._combiner_str = _combiner_str

	def setReduceNum(self, reduce_num):
		"""set reduce shecll num"""
		self._reduce_num = reduce_num

	def addInput(self,input_path,day=None,file=None,hour=None):
		""" add input """
		path=input_path
		if(file==None):
			file="*"
		if input_path.lower() in PATH_DICT:
			path = PATH_DICT[input_path.lower()]
			if day != None:
				path = path.replace("$day", str(day))
			else:
				path = path.replace("$day", time.strftime("%Y%m%d",time.localtime()))
			if(hour!=None):
				path = path.replace("$hour", str(hour))
			#self._input.append(path)
		#else:
			#path = input_path + "/" + day
			#self._input.append(path)
			#self._input.append(input_path)
		elif day != None:
			path = path.replace("$day", str(day))
		path = path.replace("$file",file)
		self._input.append(path)

	def emptyInput(self):
		self._input = []

	def addOtherInfomation(self,other_inf):
		"""add other information"""
		if self._other_str == None:
			self._other_str = other_inf
		else:
			self._other_str += " " + other_inf

	def setJobName(self,jobname):
		self._job_name = jobname

	def setJobPriority(self,priority):
		self._priority = priority


	def setOutput(self,output_path,day = None):
		"""set output path"""
		self._output = output_path
		if day:
			self._output += "/" + str(day)

	def produceHadoopStr(self):
		"""produce hadoop string"""
		sz = self._hadoop_cmd
		if len(self._file_list) > 0:
			for file_str in self._file_list:
				sz += " -file " + file_str
		sz += " -mapper \"" + self._map_str + "\""
		if(len(self._reduce_str)>0):
			sz += " -reducer \"" + self._reduce_str + "\""
		if(len(self._combiner_str)>0):
			sz += " -combiner \"" + self._combiner_str + "\""
		if(self._reduce_num>=0):
			sz += " -jobconf mapred.reduce.tasks=" + str(self._reduce_num)
		if len(self._input) == 0:
			print >> sys.stderr,"no input paht"
			sys.exit(-1)
		else:
		    for input_file in self._input:
		        sz += " -input " + input_file
		if self._output == None:
			print >> sys.stderr,"no output path"
			sys.exit(-1)
		else:
			sz += " -output " + self._output

		sz += " -jobconf mapred.job.priority=" + self._priority
		#sz += " -jobconf mapred.job.queue.name=ps-ubs-off  "
                if self._other_str:
			sz += " " + self._other_str

		sz += " -jobconf mapred.job.name=" +  "\"" + self._job_name + "\""

		return sz

	def runJob(self):
		ret_1 = -1
		tries = 0
		while ret_1 != 0 and tries < MAX_TRIES:
			print self.produceHadoopStr()
			ret_1 =os.system(self.produceHadoopStr())
			tries += 1
		if ret_1 != 0:
			print self._job_name+" is error!"
		return ret_1
