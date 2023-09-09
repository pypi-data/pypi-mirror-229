from cfntagger import Tagger
cfn_template = "../tests/templates/nocfntags.yml"

cfn_tagger = Tagger(filename=cfn_template, simulate=True)
cfn_tagger.tag()
