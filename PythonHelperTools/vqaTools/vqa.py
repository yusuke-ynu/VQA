__author__ = 'aagrawal'
__version__ = '0.9'

# Interface for accessing the VQA dataset.

# This code is based on the code written by Tsung-Yi Lin for MSCOCO Python API available at the following link: 
# (https://github.com/pdollar/coco/blob/master/PythonAPI/pycocotools/coco.py).

# The following functions are defined:
#  VQA        - VQA class that loads VQA annotation file and prepares data structures.
#  getQuesIds - Get question ids that satisfy given filter conditions.
#  getImgIds  - Get image ids that satisfy given filter conditions.
#  loadQA     - Load questions and answers with the specified question ids.
#  showQA     - Display the specified questions and answers.
#  loadRes    - Load result file and create result object.

# Help on each function can be accessed by: "help(COCO.function)"

import json
import datetime
import copy

class VQA:
	def __init__(self, annotation_file=None, question_file=None):
		"""
       	Constructor of VQA helper class for reading and visualizing questions and answers.
        :param annotation_file (str): location of VQA annotation file
        :return:
		"""
        # load dataset
		self.dataset = {}
		self.questions = {}
		self.qa = {}
		self.qqa = {}
		self.imgToQA = {}
		if annotation_file is not None and question_file is not None:
			print('loading VQA annotations and questions into memory...')
			time_t = datetime.datetime.now(datetime.timezone.utc)
			dataset = json.load(open(annotation_file, 'r'))
			questions = json.load(open(question_file, 'r'))
			print(datetime.datetime.now(datetime.timezone.utc) - time_t)
			self.dataset = dataset
			self.questions = questions
			self.createIndex()

	def createIndex(self):
        # create index
		print('creating index...')
		# annotation -> {img_id, Q_id} はjsonで定義されている (何に対する回答か)
		# question -> img_id はjsonで定義されている (何に対する質問か)
		imgToQA = {ann['image_id']: [] for ann in self.dataset['annotations']} # annotations: annotationのリスト(10個?)
		qa =  {ann['question_id']:       [] for ann in self.dataset['annotations']}
		qqa = {ann['question_id']:       [] for ann in self.dataset['annotations']}
  
		for ann in self.dataset['annotations']:
			# annotationで定義されたimg_id -> annotation(辞書)の紐づけ
			imgToQA[ann['image_id']] += [ann]
			# annotationで定義されたQ_id -> annotation(辞書)の紐づけ
			qa[ann['question_id']] = ann
   
		for ques in self.questions['questions']:
			# annotation又はquestionで定義されたQ_id -> question(辞書)の紐づけ
			# （辞書型より，annotationにquestion fileのQ_idが無い場合は辞書に追加されるため）
			'''
			NOTE: 
   				annotation fileにquestion fileのQ_idが無い場合は，初期値よりquestion=[]
				仮に全img_idにannotationとquestionが定義されており，
				全annotationと全questionがそれぞれ1ファイルで読み込まれるなら，
				question_idに対してquestionが定義されない(question=[])という問題は生じない
			'''
			qqa[ques['question_id']] = ques
   
		print ('index created!')

 		# create class members
		self.qa = qa
		self.qqa = qqa
		self.imgToQA = imgToQA

	def info(self):
		"""
		Print information about the VQA annotation file.
		:return:
		"""
		# .items()ですべてのキーと値のペアを取得
		for key, value in self.dataset['info'].items():
			print ('%s: %s'%(key, value))

	def getQuesIds(self, imgIds=[], quesTypes=[], ansTypes=[]):
		"""
		Get question ids that satisfy given filter conditions. default skips that filter
		:param 	imgIds    (int array)   : get question ids for given imgs
				quesTypes (str array)   : get question ids for given question types
				ansTypes  (str array)   : get question ids for given answer types
		:return:    ids   (int array)   : integer array of question ids
		"""
		imgIds 	  = imgIds    if type(imgIds)    == list else [imgIds]
		quesTypes = quesTypes if type(quesTypes) == list else [quesTypes]
		ansTypes  = ansTypes  if type(ansTypes)  == list else [ansTypes]

		if len(imgIds) == len(quesTypes) == len(ansTypes) == 0:
			anns = self.dataset['annotations']
		else:
			if len(imgIds) != 0:
				# imgIdsのうち，img_id -> annotationsが定義されているannotationを抽出
				anns = sum([self.imgToQA[imgId] for imgId in imgIds if imgId in self.imgToQA],[])  # リストの結合
			else:
				anns = self.dataset['annotations']
			# さらに，そのうちquesTypes, ansTypesで定義されたものを満たすannotationのみを抽出
			# 定義が無ければ，すべて満たすとする
			anns = anns if len(quesTypes) == 0 else [ann for ann in anns if ann['question_type'] in quesTypes]
			anns = anns if len(ansTypes)  == 0 else [ann for ann in anns if ann['answer_type'] in ansTypes]
		
		# 抽出されたannotationから，question_idを取得
		ids = [ann['question_id'] for ann in anns]
		return ids

	def getImgIds(self, quesIds=[], quesTypes=[], ansTypes=[]):
		"""
		Get image ids that satisfy given filter conditions. default skips that filter
		:param quesIds   (int array)   : get image ids for given question ids
               quesTypes (str array)   : get image ids for given question types
               ansTypes  (str array)   : get image ids for given answer types
		:return: ids     (int array)   : integer array of image ids
		"""
		quesIds   = quesIds   if type(quesIds)   == list else [quesIds]
		quesTypes = quesTypes if type(quesTypes) == list else [quesTypes]
		ansTypes  = ansTypes  if type(ansTypes)  == list else [ansTypes]

		if len(quesIds) == len(quesTypes) == len(ansTypes) == 0:
			anns = self.dataset['annotations']
		else:
			if not len(quesIds) == 0:
				# quesIdsのうち，Q_id -> annotationsが定義されているannotationを抽出
				anns = sum([self.qa[quesId] for quesId in quesIds if quesId in self.qa],[]) # リストの結合
			else:
				anns = self.dataset['annotations']
			anns = anns if len(quesTypes) == 0 else [ann for ann in anns if ann['question_type'] in quesTypes]
			anns = anns if len(ansTypes)  == 0 else [ann for ann in anns if ann['answer_type'] in ansTypes]
		
		# 抽出されたannotatioinから，image_idを取得
		ids = [ann['image_id'] for ann in anns]
		return ids

	# Q_idに該当するannotation(辞書)のリストを返却
	def loadQA(self, ids=[]):
		"""
		Load questions and answers with the specified question ids.
		:param ids (int array)       : integer ids specifying question ids
		:return: qa (object array)   : loaded qa objects
		"""
		if type(ids) == list:
			return [self.qa[id] for id in ids]
		elif type(ids) == int:
			return [self.qa[ids]]

	def showQA(self, anns):
		"""
		Display the specified annotations.
		:param anns (array of object): annotations to display
		:return: None
		"""
		if len(anns) == 0:
			return 0
		for ann in anns:
			quesId = ann['question_id']
			# quesIdを持つQの辞書(qqaの要素)から，質問文(str)を取得
			print ("Question: %s" %(self.qqa[quesId]['question']))
			for ans in ann['answers']:
				print ("Answer %d: %s" %(ans['answer_id'], ans['answer']))
		
	def loadRes(self, resFile, quesFile):
		"""
		Load result file and return a result object.
		:param   resFile (str)     : file name of result file
		:return: res (obj)         : result api object
		"""
		# copy.deepcopy: 元のオブジェクトと独立してコピー
		# copy.copy: 元のオブジェクト（辞書の要素など）を変更すると，コピーの要素も変更される
  
		res = VQA()
		res.questions = json.load(open(quesFile))
		# res.datasetにres.questionsの情報をコピー
		res.dataset['info'] = copy.deepcopy(self.questions['info']) 
		res.dataset['task_type'] = copy.deepcopy(self.questions['task_type'])
		res.dataset['data_type'] = copy.deepcopy(self.questions['data_type'])
		res.dataset['data_subtype'] = copy.deepcopy(self.questions['data_subtype'])
		res.dataset['license'] = copy.deepcopy(self.questions['license'])

		print ('Loading and preparing results...     ')
		time_t = datetime.datetime.now(datetime.timezone.utc)
		anns    = json.load(open(resFile)) # annsはresult(辞書)のリスト(result format)
		assert type(anns) == list, 'results is not an array of objects'
		
		# 予測(result)のQ_idをすべて取得
		annsQuesIds = [ann['question_id'] for ann in anns]
		# 予測(result)のQ_id群と教師(annotation file)のQ_id群は一致する必要
		assert set(annsQuesIds) == set(self.getQuesIds()), \
		'Results do not correspond to current VQA set. Either the results do not have predictions for all question ids in annotation file or there is at least one question id that does not belong to the question ids in the annotation file.'
		
		# annは予測(result)
		for ann in anns:
			quesId 			     = ann['question_id']
			if res.dataset['task_type'] == 'Multiple Choice':
				# v2では'multiple_choices'キーがannotation filesから削除されている？
				assert ann['answer'] in self.qqa[quesId]['multiple_choices'], 'predicted answer is not one of the multiple choices'
			qaAnn                = self.qa[quesId] # annotatioin(辞書型)
			# resultに要素を追加？
			ann['image_id']      = qaAnn['image_id'] 
			ann['question_type'] = qaAnn['question_type']
			ann['answer_type']   = qaAnn['answer_type']
		print ('DONE (t=%0.2fs)'%((datetime.datetime.now(datetime.timezone.utc) - time_t).total_seconds()))

		res.dataset['annotations'] = anns
		res.createIndex() # resultをannotationとして定義
		return res
