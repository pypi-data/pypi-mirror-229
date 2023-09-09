import io
import re
import sys
from cfntagger import Tagger


cfn_template = "../tests/templates/comments.yml"

cfn_tagger = Tagger(filename=cfn_template, simulate=True)
cfn_tagger.tag()

#print(cfn_tagger.resource_comments)
