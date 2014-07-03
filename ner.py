from nltk.tag.stanford import NERTagger

ALL_CASELESS = '/home/azureuser/edu/stanford/nlp/models/ner/english.all.3class.caseless.distsim.crf.ser.gz'
NOWIKI_CASELESS = '/home/azureuser/edu/stanford/nlp/models/ner/english.nowiki.3class.caseless.distsim.crf.ser.gz'

TRAINING_MOD = ALL_CASELESS
NER_JAR = '/home/azureuser/stanford-ner-2014-01-04/stanford-ner.jar'

st = NERTagger(TRAINING_MOD, NER_JAR)

def get_named_entities(text):
	tagged = st.tag(text.split())
	return [t for t in tagged if t[1] is not 'O']

